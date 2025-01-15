from firebase_admin import credentials, firestore, initialize_app
import os
from dotenv import load_dotenv

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        
        # Obtener las credenciales individuales desde variables de entorno
        env_vars = {
            'FIREBASE_PROJECT_ID': os.getenv('FIREBASE_PROJECT_ID'),
            'FIREBASE_PRIVATE_KEY': os.getenv('FIREBASE_PRIVATE_KEY'),
            'FIREBASE_CLIENT_EMAIL': os.getenv('FIREBASE_CLIENT_EMAIL')
        }
        
        # Verificar cada variable de entorno e imprimir información de depuración
        for var_name, value in env_vars.items():
            if not value:
                print(f"⚠️ No se encontró la variable de entorno: {var_name}")
            else:
                print(f"✅ Variable {var_name} encontrada")
        
        cred_dict = {
            "type": "service_account",
            "project_id": env_vars['FIREBASE_PROJECT_ID'],
            "private_key": env_vars['FIREBASE_PRIVATE_KEY'].replace('\\n', '\n') if env_vars['FIREBASE_PRIVATE_KEY'] else None,
            "client_email": env_vars['FIREBASE_CLIENT_EMAIL'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        }
        
        # Verificar que todas las credenciales necesarias estén presentes
        missing_fields = [key for key, value in env_vars.items() if not value]
        
        if missing_fields:
            error_msg = "\n".join([
                "🚫 Error: Faltan variables de entorno requeridas",
                "Las siguientes variables no están configuradas:",
                ", ".join(missing_fields),
                "\nPor favor, configura estas variables en el panel de Render:",
                "1. Ve a tu dashboard de Render",
                "2. Selecciona tu servicio",
                "3. Ve a 'Environment'",
                "4. Haz clic en 'Add Environment Variable'",
                "5. Agrega cada variable faltante con su valor correspondiente"
            ])
            raise ValueError(error_msg)
            
        try:
            self.cred = credentials.Certificate(cred_dict)
            self.app = initialize_app(self.cred)
            self.db = firestore.client()
            print("✅ Conexión con Firebase establecida exitosamente")
        except Exception as e:
            error_msg = f"🚫 Error al inicializar Firebase: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

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

# Crear una instancia global del DatabaseManager
dbManager = DatabaseManager()