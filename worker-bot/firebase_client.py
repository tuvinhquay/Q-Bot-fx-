import os
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app

load_dotenv()

project_id = os.getenv('FIREBASE_PROJECT_ID')
client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
private_key = os.getenv('FIREBASE_PRIVATE_KEY')

if not project_id or not client_email or not private_key:
    raise RuntimeError('Missing Firebase Admin env vars in worker-bot. Check FIREBASE_PROJECT_ID, FIREBASE_CLIENT_EMAIL, FIREBASE_PRIVATE_KEY.')

private_key = private_key.replace('\\n', '\n')

cred = credentials.Certificate({
    'type': 'service_account',
    'project_id': project_id,
    'private_key': private_key,
    'client_email': client_email,
})

app = initialize_app(cred, {'projectId': project_id})
db = firestore.client()
