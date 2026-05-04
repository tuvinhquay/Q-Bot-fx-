require('dotenv').config();
const express = require('express');
const cors = require('cors');
const admin = require('firebase-admin');
const { db } = require('./firebase');
const { createPlan } = require('./geminiClient');

const app = express();

app.use(cors());
app.use(express.json());

app.post('/api/plan', async (req, res) => {
  const { message } = req.body;
  if (!message) {
    return res.status(400).json({ success: false, error: 'message is required' });
  }

  try {
    const plan = await createPlan(message);
    const command = {
      action: 'ai-plan',
      message,
      plan,
      status: 'pending',
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
    };
    await db.collection('commands').add(command);
    res.json({ success: true, plan });
  } catch (error) {
    console.error('AI Manager /api/plan error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.listen(3001, () => {
  console.log('AI Manager running on port 3001');
});