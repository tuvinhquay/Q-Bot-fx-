import time
from datetime import datetime
from firebase_client import db

COMMAND_COLLECTION = 'commands'
LOG_COLLECTION = 'logs'


def process_pending_commands():
    docs = db.collection(COMMAND_COLLECTION).where('status', '==', 'pending').stream()
    for doc in docs:
        data = doc.to_dict()
        print(f'Processing command {doc.id}: {data}')
        db.collection(COMMAND_COLLECTION).document(doc.id).update({
            'status': 'processing',
            'processedAt': datetime.utcnow(),
        })
        log_entry = {
            'timestamp': datetime.utcnow(),
            'content': f"Worker started processing command: {data.get('message')}",
            'status': 'success',
        }
        db.collection(LOG_COLLECTION).add(log_entry)


if __name__ == '__main__':
    print('Worker Bot started. Polling Firestore commands...')
    while True:
        try:
            process_pending_commands()
        except Exception as exc:
            print('Worker Bot error:', exc)
        time.sleep(5)
