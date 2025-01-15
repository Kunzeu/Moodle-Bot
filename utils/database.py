from firebase_admin import credentials, firestore, initialize_app
import os
from dotenv import load_dotenv

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        
        # Obtener las credenciales individuales desde variables de entorno
        cred_dict = {
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
            "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n') if os.getenv('FIREBASE_PRIVATE_KEY') else None,
            "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
            "client_id": os.getenv('FIREBASE_CLIENT_ID'),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL')
        }
        
        # Verificar que todas las credenciales necesarias estén presentes
        required_fields = ['project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if not cred_dict.get(field)]
        
        if missing_fields:
            raise ValueError(f"Faltan las siguientes variables de entorno: {', '.join(missing_fields)}")
            
        try:
            self.cred = credentials.Certificate(cred_dict)
            self.app = initialize_app(self.cred)
            self.db = firestore.client()
        except Exception as e:
            raise Exception(f"Error al inicializar Firebase: {str(e)}")
    
    async def get_document(self, collection, document_id):
        """Recuperar un documento de Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Error al recuperar el documento: {str(e)}")
            return None
    
    async def set_document(self, collection, document_id, data):
        """Establecer un documento en Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.set(data)
            return True
        except Exception as e:
            print(f"Error al establecer el documento: {str(e)}")
            return False