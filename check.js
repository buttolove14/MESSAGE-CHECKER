const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const app = express();
const port = 3000;

let client;

app.get('/qr', async (req, res) => {
    // Initialize the client if not already done
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
                // Generate QR code as a Base64 string
                const qrCodeDataUrl = await qrcode.toDataURL(qr);
                res.status(200).send(`<img src="${qrCodeDataUrl}" alt="QR Code"/>`);
            } catch (error) {
                res.status(500).send("Error generating QR code.");
            }
        });

        client.initialize();
    } else {
        res.status(400).send("Client is already initialized.");
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
