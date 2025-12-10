#!/usr/bin/env python
"""
Script mejorado para iniciar todos los servicios y hacer pruebas
"""
import subprocess
import time
import sys
import os
import requests
import threading

# Configuración de servicios
SERVICES = [
    {'name': 'Gateway', 'port': 5000, 'path': 'gateway_service/gateway.py'},
    {'name': 'Inventory', 'port': 5001, 'path': 'inventory_service/inventory.py'},
    {'name': 'Order', 'port': 5002, 'path': 'order_service/order.py'},
    {'name': 'Payment', 'port': 5003, 'path': 'payment_service/payment.py'}
]

processes = []
is_running = True

def check_service_health(port, max_retries=15):
    """Verificar si un servicio está respondiendo"""
    for attempt in range(max_retries):
        try:
            response = requests.get(f'http://localhost:{port}/health', timeout=3)
            if response.status_code in [200, 404]:  # 404 es OK si el endpoint no existe, solo queremos conexión
                return True
        except requests.exceptions.ConnectionError:
            # El servicio aún no está escuchando
            if attempt < max_retries - 1:
                time.sleep(1)
        except Exception:
            # Otro error, intentar de nuevo
            if attempt < max_retries - 1:
                time.sleep(1)
    return False

def start_services():
    """Iniciar todos los servicios"""
    print("🚀 Iniciando microservicios...\n")
    
    for service in SERVICES:
        try:
            print(f"📦 Iniciando {service['name']} (puerto {service['port']})...")
            
            # Cambiar a directorio workspace
            cwd = os.path.dirname(os.path.abspath(__file__))
            
            process = subprocess.Popen(
                [sys.executable, service['path']],
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            processes.append({'name': service['name'], 'process': process})
            
            # Esperar a que el servicio esté listo
            print(f"   ⏳ Esperando que {service['name']} responda...", end='', flush=True)
            if check_service_health(service['port']):
                print(f" ✅")
            else:
                print(f" ⚠️ (tardó más de lo esperado, puede necesitar más tiempo)")
            
            time.sleep(2)  # Dar más tiempo entre servicios
            
        except Exception as e:
            print(f"❌ Error al iniciar {service['name']}: {e}\n")
    
    print("\n✅ ¡Todos los servicios se han iniciado!")
    print("\n📍 URLs disponibles:")
    for service in SERVICES:
        print(f"   - {service['name']}: http://localhost:{service['port']}")
    print("\n" + "="*60)

def stop_services():
    """Detener todos los servicios"""
    print("\n\n🛑 Deteniendo servicios...")
    for proc_info in processes:
        try:
            proc_info['process'].terminate()
            proc_info['process'].wait(timeout=2)
            print(f"✅ {proc_info['name']} detenido")
        except:
            try:
                proc_info['process'].kill()
                print(f"✅ {proc_info['name']} forzado a cerrar")
            except:
                print(f"⚠️ Error al detener {proc_info['name']}")

def run_tests():
    """Ejecutar pruebas simples"""
    print("\n🧪 Ejecutando pruebas básicas...\n")
    
    # Esperar a que todos los servicios estén listos
    time.sleep(3)
    
    try:
        # Test 1: Health check del gateway
        print("1️⃣ Verificando salud del gateway...")
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("   ✅ Gateway respondiendo\n")
        else:
            print(f"   ⚠️ Status: {response.status_code}\n")
        
        # Test 2: Crear una orden
        print("2️⃣ Intentando crear una orden...")
        order_data = {
            'product_id': 1,
            'quantity': 1,
            'price': 999.99,
            'customer_email': 'test@example.com',
            'payment_method': 'credit_card'
        }
        
        print(f"   📤 Datos enviados: {order_data}")
        
        response = requests.post(
            'http://localhost:5000/process_order',
            json=order_data,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Orden creada exitosamente")
            print(f"      - Order ID: {result.get('order_id')}")
            print(f"      - Payment ID: {result.get('payment_id')}\n")
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"      - Response: {error_data}\n")
            except:
                print(f"      - Response: {response.text}\n")
        
        print("✅ ¡Pruebas completadas!")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout - Los servicios tardan demasiado en responder")
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - Verifica que todos los servicios estén corriendo")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    global is_running
    
    try:
        start_services()
        
        # Opción de ejecutar pruebas
        print("\n¿Ejecutar pruebas automáticas? (s/n): ", end='')
        sys.stdout.flush()
        time.sleep(1)  # Dar tiempo al usuario
        
        # Ejecutar pruebas automáticamente después de 3 segundos
        print("\nEjecutando pruebas en 3 segundos...")
        time.sleep(3)
        run_tests()
        
        print("\n" + "="*60)
        print("Los servicios siguen ejecutándose.")
        print("Presiona Ctrl+C para detener.\n")
        
        # Mantener servicios ejecutándose
        while is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        stop_services()
        print("\n✅ Servicios detenidos correctamente")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error fatal: {e}")
        stop_services()
        sys.exit(1)

if __name__ == '__main__':
    main()
