const admin = require('firebase-admin');

const projectId = process.env.FIREBASE_PROJECT_ID;
const clientEmail = process.env.FIREBASE_CLIENT_EMAIL;
const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n');

if (!projectId || !clientEmail || !privateKey) {
  throw new Error('Missing Firebase Admin environment variables: FIREBASE_PROJECT_ID, FIREBASE_CLIENT_EMAIL, FIREBASE_PRIVATE_KEY');
}

const app = admin.initializeApp({
  credential: admin.credential.cert({
    type: 'service_account',
    project_id: projectId,
    private_key: privateKey,
    client_email: clientEmail,
  }),
  projectId,
});

const db = app.firestore();
const storage = admin.storage();

module.exports = { db, storage };
