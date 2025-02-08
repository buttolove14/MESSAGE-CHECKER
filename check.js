const express = require("express");
const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");

const app = express();
const port = 3000;

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      "--disable-features=site-per-process",
    ],
  },
});

client.on("qr", (qr) => {
  // Generate and print the QR code to the console (for testing purposes)
  qrcode.generate(qr, { small: true });

  // When QR is ready, you can send it back as a response or save it to a file.
  app.get("/qr", (req, res) => {
    res.send(qr); // Send the QR code as a plain text (or as an image if you prefer)
  });
});

client.on("ready", () => {
  console.log("WhatsApp Web is ready!");
});

client.initialize();

app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});
