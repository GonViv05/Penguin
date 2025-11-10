"""
🐧 SERVICIOS SIMULADOS - CLIENTES DE LOGGING
=============================================
Simula múltiples servicios que generan logs y los envían al servidor central.

Cada servicio:
- Genera logs realistas con diferentes niveles de severidad
- Envía logs por HTTP POST con autenticación
- Puede ejecutarse de forma continua o enviar lotes
"""

import requests
import random
import time
from datetime import datetime
import threading
import json


# ============= CONFIGURACIÓN =============
SERVER_URL = 'http://localhost:5000'
SEND_INTERVAL = 5  # segundos entre envíos


# ============= DATOS DE SERVICIOS =============
SERVICES = {
    'API Service': {
        'token': 'token_api_service', #token de autenticación
        'messages': { 
            'DEBUG': [ 
                'Request received: GET /api/users', #mensaje de depuración
                'Response time: 45ms', #tiempo de respuesta
                'Cache hit for user profile', #caché de perfil de usuario
                'Rate limit check passed' #verificación de límite de tasa
            ],
            'INFO': [
                'New user registered: user_{id}',
                'API call successful: /api/products',
                'Authentication successful for user_{id}',
                'Data synced with external service'
            ],
            'WARNING': [
                'Slow query detected: 3.5s',
                'Rate limit approaching for IP {ip}',
                'Deprecated endpoint used: /api/v1/legacy',
                'High memory usage: 85%'
            ],
            'ERROR': [
                'Database connection timeout',
                'Failed to authenticate user_{id}',
                'External API returned 500',
                'Invalid JSON in request body'
            ],
            'CRITICAL': [
                'Database pool exhausted',
                'All retries failed for critical operation',
                'System running out of disk space',
                'Security breach attempt detected'
            ]
        }
    },
    
    'Web Service': {
        'token': 'token_web_service',
        'messages': {
            'DEBUG': [
                'Page rendered: /dashboard',
                'CSS loaded in 120ms',
                'WebSocket connection established',
                'Static asset served from CDN'
            ],
            'INFO': [
                'User logged in: user_{id}',
                'Form submitted successfully',
                'File uploaded: document_{id}.pdf',
                'Session created for new user'
            ],
            'WARNING': [
                'Slow page load time: 4.2s',
                'Browser compatibility issue detected: IE11',
                'Session about to expire',
                'Large image uploaded: 15MB'
            ],
            'ERROR': [
                '404 Not Found: /old-page',
                'Form validation failed',
                'Failed to upload file: size exceeded',
                'CSRF token mismatch'
            ],
            'CRITICAL': [
                'Server unresponsive',
                'Cannot establish WebSocket connection',
                'CDN unreachable',
                'Multiple 500 errors in last minute'
            ]
        }
    },
    
    'Database Service': {
        'token': 'token_db_service',
        'messages': {
            'DEBUG': [
                'Query executed: SELECT * FROM users',
                'Connection returned to pool',
                'Index used: idx_user_email',
                'Transaction committed successfully'
            ],
            'INFO': [
                'Backup completed successfully',
                'New connection established',
                'Table optimized: users',
                'Migration applied: v2.3.1'
            ],
            'WARNING': [
                'Query took longer than expected: 2.8s',
                'Connection pool 80 utilized',
                'Deadlock detected and resolved',
                'Replication lag: 3 seconds'
            ],
            'ERROR': [
                'Failed to execute query: syntax error',
                'Connection lost to replica',
                'Transaction rolled back',
                'Foreign key constraint violation'
            ],
            'CRITICAL': [
                'Primary database unreachable',
                'Disk space critically low',
                'Corruption detected in table: orders',
                'All connection pool exhausted'
            ]
        }
    },
    
    'Payment Service': {
        'token': 'token_payment_service',
        'messages': {
            'DEBUG': [
                'Payment request received',
                'Card validation passed',
                'Fraud check initiated',
                'Currency converted: USD to EUR'
            ],
            'INFO': [
                'Payment processed: ${amount}',
                'Refund issued: transaction_{id}',
                'Subscription renewed: user_{id}',
                'Payment method updated'
            ],
            'WARNING': [ 
                'Payment taking longer than usual',
                'Unusual transaction pattern detected',
                'Payment gateway response slow',
                'Card about to expire'
            ],
            'ERROR': [
                'Payment declined: insufficient funds',
                'Payment gateway timeout',
                'Invalid card number',
                'Duplicate transaction detected'
            ],
            'CRITICAL': [
                'Payment gateway unreachable',
                'Multiple failed transactions in short period',
                'Possible fraud attack detected',
                'Payment reconciliation mismatch'
            ]
        }
    },
    
    'Notification Service': {
        'token': 'token_notification_service',
        'messages': {
            'DEBUG': [
                'Email queued for sending',
                'Template rendered successfully',
                'Push notification prepared',
                'SMS message formatted'
            ],
            'INFO': [
                'Email sent successfully: user_{id}',
                'Push notification delivered',
                'SMS sent to +1234567890',
                'Webhook notification sent'
            ],
            'WARNING': [
                'Email sending delayed',
                'Push notification not delivered: device offline',
                'SMS provider rate limit approaching',
                'Bounce rate increasing'
            ],
            'ERROR': [
                'Failed to send email: invalid address',
                'Push notification failed: invalid token',
                'SMS delivery failed',
                'Webhook endpoint unreachable'
            ],
            'CRITICAL': [
                'Email provider unreachable',
                'All notification channels failed',
                'Message queue full',
                'Critical alert not delivered'
            ]
        }
    }
}


# ============= CLASE DEL CLIENTE =============
class LogClient:
    """Cliente que simula un servicio generando y enviando logs"""
    
    def __init__(self, service_name, config):
        self.service_name = service_name      # "API Service", "Web Service", etc
        self.token = config['token']          # Token para autenticarse
        self.messages = config['messages']    # Todos los mensajes posibles
        self.logs_sent = 0                    # Contador: cuántos logs envió
        self.errors = 0                       # Contador: cuántos errores tuvo
    
    def generate_log(self):
        """Genera un log aleatorio"""
        # Distribución de severidad (más INFO y DEBUG, menos CRITICAL)
        severity_weights = {
            'DEBUG': 0.35,
            'INFO': 0.40,
            'WARNING': 0.15,
            'ERROR': 0.08,
            'CRITICAL': 0.02
        }
        
        severity = random.choices(
            list(severity_weights.keys()),
            weights=list(severity_weights.values())
        )[0]
        
        #Para que carajo sirve esto?
        #En un sistema real hay mas logs de baja severidad que de alta severidad
        #Por eso usamos weights para simular esa distribución

        # Seleccionar mensaje aleatorio
        message_template = random.choice(self.messages[severity])
        
        # Reemplazar placeholders
        message = message_template.format(
            id=random.randint(1000, 9999),
            ip=f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            amount=random.randint(10, 1000)
        )
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'severity': severity,
            'message': message
        }
    
    def send_logs(self, logs):
        """Envía uno o múltiples logs al servidor"""
        headers = {
            'Authorization': f'Token {self.token}', # Autenticación con token
            'Content-Type': 'application/json' # Tipo de contenido JSON
        }
        
        try: 
            response = requests.post(
                f'{SERVER_URL}/logs',
                headers=headers,
                json=logs,
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                self.logs_sent += len(logs) if isinstance(logs, list) else 1
                print(f"✅ [{self.service_name}] Logs enviados: {self.logs_sent}")
                return True
            else:
                self.errors += 1
                print(f"❌ [{self.service_name}] Error {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.errors += 1
            print(f"❌ [{self.service_name}] Error de conexión: {e}")
            return False
    
    def run_continuous(self, batch_size=3, interval=SEND_INTERVAL):
        """Ejecuta el servicio de forma continua generando logs"""
        print(f"🚀 [{self.service_name}] Iniciado (batch: {batch_size}, interval: {interval}s)")
        
        while True:
            try:
                # Generar lote de logs
                logs = [self.generate_log() for _ in range(batch_size)]
                
                # Enviar al servidor
                self.send_logs(logs)
                
                # Esperar antes del próximo envío
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print(f"\n🛑 [{self.service_name}] Detenido por usuario")
                break
            except Exception as e:
                print(f"❌ [{self.service_name}] Error inesperado: {e}")
                time.sleep(interval)
    
    def run_single_batch(self, count=10):
        """Envía un lote único de logs (útil para testing)"""
        print(f"📤 [{self.service_name}] Enviando {count} logs...")
        logs = [self.generate_log() for _ in range(count)]
        success = self.send_logs(logs)
        
        if success:
            print(f"✅ [{self.service_name}] Lote enviado exitosamente")
        else:
            print(f"❌ [{self.service_name}] Falló el envío del lote")


# ============= FUNCIONES DE CONTROL =============

def run_all_services_threaded(batch_size=3, interval=5):
    """Ejecuta todos los servicios en threads separados"""
    print("\n" + "="*60)
    print("🐧 INICIANDO SISTEMA DE LOGGING DISTRIBUIDO")
    print("="*60)
    print(f"Servicios: {len(SERVICES)}")
    print(f"Batch size: {batch_size} logs por envío")
    print(f"Intervalo: {interval} segundos")
    print("="*60 + "\n")
    
    threads = []
    clients = []
    
    for service_name, config in SERVICES.items():
        client = LogClient(service_name, config)
        clients.append(client)
        
        thread = threading.Thread(
            target=client.run_continuous,
            args=(batch_size, interval),
            daemon=True
        )
        threads.append(thread)
        thread.start()
    
    try:
        # Mantener el programa corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("📊 RESUMEN FINAL")
        print("="*60)
        for client in clients:
            print(f"  {client.service_name}:")
            print(f"    - Logs enviados: {client.logs_sent}")
            print(f"    - Errores: {client.errors}")
        print("="*60)
        print("\n🛑 Sistema detenido. ¡Hasta luego!\n")


def test_single_service(service_name='API Service', count=5):
    """Prueba un servicio individual enviando un lote"""
    if service_name not in SERVICES:
        print(f"❌ Servicio '{service_name}' no encontrado")
        print(f"Servicios disponibles: {', '.join(SERVICES.keys())}")
        return
    
    client = LogClient(service_name, SERVICES[service_name])
    client.run_single_batch(count)


def send_stress_test(count=100):
    """Envía muchos logs en múltiples batches"""
    print(f"\n⚡ STRESS TEST: Enviando {count} logs desde cada servicio...\n")
    
    for service_name, config in SERVICES.items():
        client = LogClient(service_name, config)
        
        # Enviar en 5 lotes de 20
        for batch_num in range(5):  # 5 batches
            client.run_single_batch(20)  # 20 logs por batch
            print(f"  [{service_name}] Batch {batch_num + 1}/5 enviado")
            time.sleep(0.3)
        
        print(f"✅ [{service_name}] Total: {count} logs enviados\n")

# ============= MENÚ INTERACTIVO =============

def show_menu():
    """Muestra el menú de opciones"""
    print("\n" + "="*60)
    print("🐧 SIMULADOR DE SERVICIOS - CLIENTE DE LOGGING")
    print("="*60)
    print("1. Ejecutar todos los servicios (modo continuo)")
    print("2. Probar un servicio individual")
    print("3. Stress test (muchos logs de golpe)")
    print("4. Ver servicios disponibles")
    print("0. Salir")
    print("="*60)


def main():
    """Función principal con menú interactivo"""
    while True:
        show_menu()
        choice = input("\nElegí una opción: ").strip()
        
        if choice == '1':
            batch = int(input("Logs por batch (default: 3): ") or "3")
            interval = int(input("Intervalo en segundos (default: 5): ") or "5")
            run_all_services_threaded(batch_size=batch, interval=interval)
        
        elif choice == '2':
            print(f"\nServicios: {', '.join(SERVICES.keys())}")
            service = input("Nombre del servicio: ").strip()
            count = int(input("Cantidad de logs (default: 5): ") or "5")
            test_single_service(service, count)
        
        elif choice == '3':
            count = int(input("Logs por servicio (default: 100): ") or "100")
            send_stress_test(count)
        
        elif choice == '4':
            print("\n📋 Servicios configurados:")
            for name, config in SERVICES.items():
                print(f"  - {name} (token: {config['token']})")
        
        elif choice == '0':
            print("\n👋 ¡Hasta luego!\n")
            break
        
        else:
            print("❌ Opción inválida")



main()  # Menú interactivo
