#!/usr/bin/env python3
"""
Script de prueba para verificar la integración con Resend
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio src al path para importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from email_service import EmailService

def test_resend_integration():
    """Prueba el envío de un email usando Resend"""
    
    print("🧪 Iniciando prueba de integración con Resend...")
    
    try:
        # Crear instancia del servicio de email
        email_service = EmailService()
        print("✅ EmailService inicializado correctamente")
        
        # Datos de prueba
        test_data = {
            'file_id': 'TEST-123',
            'email': 'test@example.com',  # Cambia esto por tu email
            'processing_results': {
                'success': True,
                'file_id': 'TEST-123',
                'total_urls': 10,
                'processed': 8,
                'failed': 2,
                'status': 'PROCESSED'
            },
            'timestamp': '2025-07-30T12:00:00.000000'
        }
        
        print(f"📧 Enviando email de prueba a: {test_data['email']}")
        
        # Enviar email de prueba
        email_service.send_processing_complete_email(test_data)
        
        print("✅ Email de prueba enviado. Revisa tu bandeja de entrada.")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("PRUEBA DE INTEGRACIÓN CON RESEND")
    print("=" * 50)
    
    # Verificar variables de entorno requeridas
    required_vars = ['RESEND_API_KEY', 'FROM_EMAIL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("Por favor configura estas variables en tu archivo .env")
        sys.exit(1)
    
    # Ejecutar prueba
    success = test_resend_integration()
    
    if success:
        print("\n🎉 Prueba completada exitosamente!")
    else:
        print("\n💥 La prueba falló. Revisa la configuración.")
        sys.exit(1)
