import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Crear el diccionario de credenciales desde las variables de entorno
        cred_dict = {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
            "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN")
        }
        
        if not firebase_admin._apps:
            self.cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(self.cred)
        
        self.db = firestore.client()
        self.apiKeys = self.db.collection('api_keys')
        self.reminders = self.db.collection('reminders')
        
    async def setApiKey(self, userId, apiKey):
        try:
            doc_ref = self.apiKeys.document(str(userId))
            doc_ref.set({
                'api_key': apiKey,
                'updated_at': datetime.now()
            })
            print(f"✅ API Key {'añadida' if not doc_ref.get().exists else 'actualizada'} para usuario {userId}")
            return True
        except Exception as error:
            print('❌ Error guardando API key:', str(error))
            return False
    
    async def getApiKey(self, userId):
        try:
            doc_ref = self.apiKeys.document(str(userId))
            doc = doc_ref.get()
            print(f"🔍 Buscando API key para usuario {userId}: {'Encontrada' if doc.exists else 'No encontrada'}")
            return doc.to_dict().get('api_key') if doc.exists else None
        except Exception as error:
            print('❌ Error obteniendo API key:', str(error))
            return None
    
    async def deleteApiKey(self, userId):
        try:
            doc_ref = self.apiKeys.document(str(userId))
            doc_ref.delete()
            print(f"✅ API Key eliminada para usuario {userId}")
            return True
        except Exception as error:
            print('❌ Error eliminando API key:', str(error))
            return False
    
    async def hasApiKey(self, userId):
        try:
            doc_ref = self.apiKeys.document(str(userId))
            doc = doc_ref.get()
            return doc.exists
        except Exception as error:
            print('❌ Error verificando API key:', str(error))
            return False
    
    async def connect(self):
        try:
            doc_ref = self.db.collection('test').document('ping')
            doc_ref.set({'message': 'ping'})
            print('✅ Conectado a Firebase Firestore')
            return True
        except Exception as error:
            print('❌ Error de conexión Firestore:', str(error))
            return False

    def set_reminder(self, reminder_data):
        try:
            if isinstance(reminder_data['time'], datetime):
                reminder_data['time'] = reminder_data['time'].isoformat()
            
            doc_id = f"{reminder_data['user_id']}_{int(datetime.fromisoformat(reminder_data['time']).timestamp())}"
            
            clean_data = {
                'user_id': str(reminder_data['user_id']),
                'channel_id': str(reminder_data['channel_id']),
                'target_id': str(reminder_data['target_id']) if reminder_data.get('target_id') else None,
                'message': reminder_data['message'],
                'time': reminder_data['time'],
                'original_message': reminder_data.get('original_message', '')
            }
            
            self.reminders.document(doc_id).set(clean_data)
            return True
        except Exception as e:
            print(f"Error guardando recordatorio en Firebase: {e}")
            return False

    def delete_reminder(self, reminder_data):
        try:
            time_value = reminder_data['time']
            if isinstance(time_value, datetime):
                timestamp = time_value.timestamp()
            else:
                timestamp = datetime.fromisoformat(time_value).timestamp()
                
            doc_id = f"{reminder_data['user_id']}_{int(timestamp)}"
            self.reminders.document(doc_id).delete()
            return True
        except Exception as e:
            print(f"Error eliminando recordatorio de Firebase: {e}")
            return False

    def get_all_reminders(self):
        try:
            docs = self.reminders.stream()
            reminders = []
            for doc in docs:
                data = doc.to_dict()
                reminders.append(data)
            return reminders
        except Exception as e:
            print(f"Error obteniendo recordatorios de Firebase: {e}")
            return []

# Instancia global del gestor de base de datos
dbManager = DatabaseManager()