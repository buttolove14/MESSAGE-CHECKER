const { Client, LocalAuth } = require('whatsapp-web.js');
const moment = require('moment');
const express = require('express');
const path = require('path');
const fs = require('fs');
const app = express();

// Set up Express to serve the QR code image
app.use('/qr', express.static(path.join(__dirname, 'qr-images')));

// Set up a route for serving the status
app.get('/status', (req, res) => {
  res.json({ status: 'Running' });
});

const args = process.argv.slice(2);
if (args.length < 2) {
    console.error(JSON.stringify({ error: "Missing date or group. Please provide both." }));
    process.exit(1);
}

const [date, group] = args;

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--disable-features=site-per-process']
    }
});

client.on('qr', (qr) => {
    // Save the QR code image
    const filePath = path.join(__dirname, 'qr-images', 'qr.png');
    fs.writeFileSync(filePath, qr, 'base64');
    console.log('QR Code generated. Scan it!');
});

client.on('ready', () => {
    console.log('WhatsApp Web is ready!');
    // Continue with your logic...
});

// Start the Express server
app.listen(3000, () => {
    console.log('Express server is running at http://localhost:3000');
});

client.initialize();
