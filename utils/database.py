from firebase_admin import credentials, firestore, initialize_app, get_app
import os
from dotenv import load_dotenv

class DatabaseManager:
    _instance = None
    _initialized = False
    _connected = False

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
        
        # Obtener las credenciales individuales desde variables de entorno
        self.env_vars = {
            'FIREBASE_PROJECT_ID': os.getenv('FIREBASE_PROJECT_ID'),
            'FIREBASE_PRIVATE_KEY': os.getenv('FIREBASE_PRIVATE_KEY'),
            'FIREBASE_CLIENT_EMAIL': os.getenv('FIREBASE_CLIENT_EMAIL')
        }

    async def connect(self):
        """Conectar a Firebase de manera asíncrona."""
        if self._connected:
            return True

        try:
            # Verificar variables de entorno
            missing_fields = [key for key, value in self.env_vars.items() if not value]
            if missing_fields:
                print(f"⚠️ Faltan variables de entorno: {', '.join(missing_fields)}")
                return False

            cred_dict = {
                "type": "service_account",
                "project_id": self.env_vars['FIREBASE_PROJECT_ID'],
                "private_key": self.env_vars['FIREBASE_PRIVATE_KEY'].replace('\\n', '\n'),
                "client_email": self.env_vars['FIREBASE_CLIENT_EMAIL'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }

            # Intentar obtener la app existente, si no existe, crear una nueva
            try:
                self.app = get_app()
            except ValueError:
                self.cred = credentials.Certificate(cred_dict)
                self.app = initialize_app(self.cred)
            
            self.db = firestore.client()
            self._connected = True
            print("✅ Conexión con Firebase establecida exitosamente")
            return True

        except Exception as e:
            print(f"🚫 Error al conectar con Firebase: {str(e)}")
            return False

    async def get_document(self, collection, document_id):
        """Recuperar un documento de Firestore."""
        if not self._connected:
            if not await self.connect():
                return None

        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Error al recuperar el documento: {str(e)}")
            return None
    
    async def set_document(self, collection, document_id, data):
        """Establecer un documento en Firestore."""
        if not self._connected:
            if not await self.connect():
                return False

        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"Error al establecer el documento: {str(e)}")
            return False

# Crear una instancia global del DatabaseManager
dbManager = DatabaseManager()