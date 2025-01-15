from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        if not os.getenv('MONGODB_URI'):
            raise ValueError('MONGODB_URI no encontrada en variables de entorno')
        
        self.uri = os.getenv('MONGODB_URI')
        self.client = AsyncIOMotorClient(self.uri)
        self.dbName = 'kunzeubot'
        self.db = None
        self.apiKeys = None
    
    async def connect(self):
        try:
            # Verificar conexión
            await self.client.admin.command('ping')
            print('✅ Conectado a MongoDB Atlas')
            
            self.db = self.client[self.dbName]
            self.apiKeys = self.db.api_keys
            
            # Crear índice único para user_id si no existe
            await self.apiKeys.create_index('user_id', unique=True)
            
            print('📁 Base de datos lista:', self.dbName)
            return True
            
        except Exception as error:
            print('❌ Error de conexión MongoDB:', str(error))
            return False
    
    async def setApiKey(self, userId, apiKey):
        try:
            result = await self.apiKeys.update_one(
                {'user_id': userId},
                {
                    '$set': {
                        'api_key': apiKey,
                        'updated_at': datetime.now()
                    }
                },
                upsert=True
            )
            print(f"✅ API Key {'añadida' if result.upserted_id else 'actualizada'} para usuario {userId}")
            return True
            
        except Exception as error:
            print('❌ Error guardando API key:', str(error))
            return False
    
    async def getApiKey(self, userId):
        try:
            result = await self.apiKeys.find_one({'user_id': userId})
            print(f"🔍 Buscando API key para usuario {userId}: {'Encontrada' if result else 'No encontrada'}")
            return result['api_key'] if result else None
            
        except Exception as error:
            print('❌ Error obteniendo API key:', str(error))
            return None
    
    async def deleteApiKey(self, userId):
        try:
            result = await self.apiKeys.delete_one({'user_id': userId})
            return result.deleted_count > 0
            
        except Exception as error:
            print('Error eliminando API key:', str(error))
            return False
    
    async def hasApiKey(self, userId):
        try:
            result = await self.apiKeys.find_one({'user_id': userId})
            return bool(result)
            
        except Exception as error:
            print('Error verificando API key:', str(error))
            return False

# Instancia global del manejador de base de datos
dbManager = DatabaseManager()