const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const QRCode = require('qrcode');
const socketIO = require('socket.io');

const app = express();
const port = process.env.PORT || 3000;

let client;
let qrData = null; // Store QR code data for new connections

app.use(express.json());

// Initialize WhatsApp Client
function initializeWhatsAppClient() {
    client = new Client({
        authStrategy: new LocalAuth(),
        puppeteer: {
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        }
    });

    // QR Code Generation and Emission
    client.on('qr', async (qr) => {
        console.log("QR Received");
        qrData = await QRCode.toDataURL(qr); // Generate base64 QR image
        io.emit('qr', { qr: qrData }); // Emit QR code to connected clients
    });

    // WhatsApp Ready Event
    client.on('ready', () => {
        console.log("WhatsApp Client is ready!");
        qrData = null; // Clear QR code data after successful login
        io.emit('ready', { message: "WhatsApp is connected." });
    });

    // WhatsApp Disconnection Event
    client.on('disconnected', () => {
        console.log("WhatsApp Client disconnected.");
        io.emit('disconnected', { message: "WhatsApp is disconnected. Please reconnect." });
        initializeWhatsAppClient(); // Reinitialize client after disconnect
    });

    client.initialize();
}

// Start the WhatsApp Client
initializeWhatsAppClient();

// Add API Endpoint for Checking Messages
app.get('/check-messages', async (req, res) => {
    const { date, group } = req.query;

    if (!date || !group) {
        return res.status(400).json({ error: "Missing 'date' or 'group' parameter" });
    }

    try {
        const chats = await client.getChats();
        const groupChat = chats.find(chat => chat.name.trim().toLowerCase() === group.trim().toLowerCase());

        if (!groupChat) {
            return res.status(404).json({ error: `Group "${group}" not found.` });
        }

        // Time slots to check messages
        const timeSlots = {
            "09:00-10:00": { start: "09:00", end: "09:59" },
            "12:00-13:00": { start: "12:00", end: "12:59" },
            "15:00-16:00": { start: "15:00", end: "15:59" }
        };

        let messageStatus = {};
        Object.keys(timeSlots).forEach(slot => {
            messageStatus[slot] = { status: "⚠ No", senders: [] };
        });

        // Fetch and filter messages
        const allMessages = await groupChat.fetchMessages({ limit: 200 });
        for (const msg of allMessages) {
            const msgDate = new Date(msg.timestamp * 1000).toISOString().split('T')[0];
            const msgTime = new Date(msg.timestamp * 1000).toTimeString().split(' ')[0].slice(0, 5);

            if (msgDate === date) {
                for (const [slot, range] of Object.entries(timeSlots)) {
                    if (msgTime >= range.start && msgTime <= range.end) {
                        let sender = msg.author || msg.from;
                        if (!messageStatus[slot].senders.includes(sender)) {
                            messageStatus[slot].senders.push(sender);
                        }
                        messageStatus[slot].status = "✅ Yes";
                    }
                }
            }
        }

        res.json({ success: true, messageStatus });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start the Express Server
const server = app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

// Add WebSocket Support for QR Code
const io = socketIO(server, {
    cors: {
        origin: '*',
        methods: ['GET', 'POST']
    }
});

// Socket.IO for Real-Time QR Updates
io.on('connection', (socket) => {
    console.log("New client connected");

    // Send the QR code to the client if it exists
    if (qrData) {
        socket.emit('qr', { qr: qrData });
    }

    socket.on('disconnect', () => {
        console.log("Client disconnected");
    });
});
