const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const moment = require('moment');
const app = express();
const port = 3000;

// Store the client globally for reuse
let client;

// Endpoint to generate the QR code
app.get('/qr', async (req, res) => {
    // Ensure the client is initialized
    if (!client) {
        client = new Client({
            authStrategy: new LocalAuth(),
            puppeteer: {
                headless: true,
                args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--disable-features=site-per-process']
            }
        });

        client.on('qr', async (qr) => {
            try {
                // Generate QR code as a data URL (Base64)
                const qrCodeDataUrl = await qrcode.toDataURL(qr);
                res.status(200).send(`<img src="${qrCodeDataUrl}" alt="QR Code"/>`);
            } catch (error) {
                res.status(500).send("Error generating QR code.");
            }
        });

        client.initialize();
    }
});

// Endpoint to check messages for a group on a specific date
app.get('/check-messages', async (req, res) => {
    const { date, group } = req.query;
    if (!date || !group) {
        return res.status(400).json({ error: 'Date and group are required.' });
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
            messageStatus[slot] = { status: "⚠ No", sender: "N/A" };
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

        // Process messages and update status
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

                            messageStatus[slot] = {
                                status: "✅ Yes",
                                sender: senderName
                            };
                        } catch (err) {
                            messageStatus[slot] = {
                                status: "✅ Yes",
                                sender: senderJID // Fallback if contact fetch fails
                            };
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

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
