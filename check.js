const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const QRCode = require('qrcode');

const app = express();
const port = process.env.PORT || 3000;

let client;

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

    client.on('qr', async (qr) => {
        console.log("QR Received: ", qr);
        qrData = await QRCode.toDataURL(qr);
        io.emit('qr', { qr: qrData }); // Send QR code to clients via Socket.IO
    });

    client.on('ready', () => {
        console.log("WhatsApp Client is ready!");
        io.emit('ready', { message: "WhatsApp is connected." });
    });

    client.on('disconnected', () => {
        console.log("WhatsApp Client disconnected.");
        io.emit('disconnected', { message: "WhatsApp is disconnected." });
        initializeWhatsAppClient(); // Reinitialize client on disconnect
    });

    client.initialize();
}

// Start Client
initializeWhatsAppClient();

// Add API Endpoint to Check Messages
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

        const timeSlots = {
            "09:00-10:00": { start: "09:00", end: "09:59" },
            "12:00-13:00": { start: "12:00", end: "12:59" },
            "15:00-16:00": { start: "15:00", end: "15:59" }
        };

        let messageStatus = {};
        Object.keys(timeSlots).forEach(slot => {
            messageStatus[slot] = { status: "⚠ No", senders: [] };
        });

        let allMessages = [];
        let done = false;
        while (!done) {
            const messages = await groupChat.fetchMessages({ limit: 200, before: allMessages[0]?.id });
            allMessages = [...allMessages, ...messages];
            if (messages.length < 200 || messages.some(msg => moment.utc(msg.timestamp * 1000).format("YYYY-MM-DD") < date)) {
                done = true;
            }
        }

        for (const msg of allMessages) {
            const msgDate = moment.utc(msg.timestamp * 1000).local().format("YYYY-MM-DD");
            const msgTime = moment.utc(msg.timestamp * 1000).local().format("HH:mm");

            if (msgDate === date) {
                for (const [slot, range] of Object.entries(timeSlots)) {
                    if (msgTime >= range.start && msgTime <= range.end) {
                        let senderJID = msg.author || msg.from || "Unknown";
                        try {
                            const senderContact = await client.getContactById(senderJID);
                            let senderName = senderContact.pushname || senderContact.name || senderJID;

                            if (!messageStatus[slot].senders.includes(senderName)) {
                                messageStatus[slot].senders.push(senderName);
                            }
                            messageStatus[slot].status = "✅ Yes";
                        } catch {
                            if (!messageStatus[slot].senders.includes(senderJID)) {
                                messageStatus[slot].senders.push(senderJID);
                            }
                        }
                    }
                }
            }
        }

        res.json({ success: true, messageStatus });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start Express Server
const server = app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

// Add WebSocket Support for QR Code
const io = require('socket.io')(server, {
    cors: {
        origin: '*',
        methods: ['GET', 'POST']
    }
});

let qrData = null;

io.on('connection', (socket) => {
    console.log("New client connected");

    if (qrData) {
        socket.emit('qr', { qr: qrData });
    }

    socket.on('disconnect', () => {
        console.log("Client disconnected");
    });
});
