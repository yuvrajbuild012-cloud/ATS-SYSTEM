const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const admin = require('firebase-admin');

// Initialize Firebase admin using service account key file path from env
if (!process.env.FIREBASE_SERVICE_ACCOUNT) {
  console.warn('FIREBASE_SERVICE_ACCOUNT not set. Admin features will be disabled.');
}

if (process.env.FIREBASE_SERVICE_ACCOUNT) {
  const serviceAccount = require(path.resolve(process.env.FIREBASE_SERVICE_ACCOUNT));
  admin.initializeApp({ credential: admin.credential.cert(serviceAccount) });
}

const app = express();
app.use(cors());
app.use(express.json());

// Serve static files (frontend)
app.use(express.static(path.join(__dirname)));

// Protected endpoint example: verify Firebase ID token
app.get('/profile', async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) return res.status(401).json({ error: 'Missing token' });
  const idToken = authHeader.split('Bearer ')[1];

  if (!admin.apps.length) return res.status(500).json({ error: 'Admin not initialized. Set FIREBASE_SERVICE_ACCOUNT.' });

  try {
    const decoded = await admin.auth().verifyIdToken(idToken);
    return res.json({ uid: decoded.uid, email: decoded.email || null, phone: decoded.phone_number || null });
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token', details: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log('Server listening on', PORT));
