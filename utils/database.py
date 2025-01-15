import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

class DatabaseManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._initialize_firebase()

    def _initialize_firebase(self):
        load_dotenv()
        
        firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
        
        if not firebase_credentials:
            raise ValueError('FIREBASE_CREDENTIALS no encontrada en variables de entorno')
        
        if not firebase_admin._apps:
            self.cred = credentials.Certificate(firebase_credentials)
            firebase_admin.initialize_app(self.cred)
        
        self.db = firestore.client()
        self.apiKeys = self.db.collection('api_keys')
        self.reminders = self.db.collection('reminders')

    async def setApiKey(self, userId, apiKey):
        try:
            # Establecer o actualizar la API Key en Firestore
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
            # Obtener la API Key de Firestore
            doc_ref = self.apiKeys.document(str(userId))
            doc = doc_ref.get()
            print(f"🔍 Buscando API key para usuario {userId}: {'Encontrada' if doc.exists else 'No encontrada'}")
            return doc.to_dict().get('api_key') if doc.exists else None
        except Exception as error:
            print('❌ Error obteniendo API key:', str(error))
            return None
    
    async def deleteApiKey(self, userId):
        try:
            # Eliminar la API Key de Firestore
            doc_ref = self.apiKeys.document(str(userId))
            doc_ref.delete()
            print(f"✅ API Key eliminada para usuario {userId}")
            return True
        except Exception as error:
            print('❌ Error eliminando API key:', str(error))
            return False
    
    async def hasApiKey(self, userId):
        try:
            # Verificar si el usuario tiene una API Key
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
        """Método sincrónico para guardar recordatorio"""
        try:
            # Asegurarnos de que 'time' sea un string ISO
            if isinstance(reminder_data['time'], datetime):
                reminder_data['time'] = reminder_data['time'].isoformat()
            
            doc_id = f"{reminder_data['user_id']}_{int(datetime.fromisoformat(reminder_data['time']).timestamp())}"
            
            # Crear una copia limpia de los datos
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
        """Método sincrónico para eliminar recordatorio"""
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
        """Método sincrónico para obtener todos los recordatorios"""
        try:
            docs = self.reminders.stream()
            reminders = []
            for doc in docs:
                data = doc.to_dict()
                # No convertir a datetime aquí, lo dejamos como string ISO
                reminders.append(data)
            return reminders
        except Exception as e:
            print(f"Error obteniendo recordatorios de Firebase: {e}")
            return []

# Instancia global del gestor de base de datos
dbManager = DatabaseManager()