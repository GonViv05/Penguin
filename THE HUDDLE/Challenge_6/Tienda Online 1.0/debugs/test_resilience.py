"""
Script para probar la resiliencia del sistema cuando un servicio está caído
"""
import requests
import time
import json
from colorama import init, Fore, Style

# Inicializar colorama para colores en terminal
init(autoreset=True)

GATEWAY_URL = "http://localhost:5000"

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text.center(60)}")
    print(f"{Fore.CYAN}{'='*60}\n")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ {text}")

def test_health_check():
    """Verificar el estado de todos los servicios"""
    print_header("TEST 1: Verificación de Estado de Servicios")
    
    try:
        response = requests.get(f"{GATEWAY_URL}/health", timeout=5)
        data = response.json()
        
        print_info(f"Estado del Gateway: {data['status']}")
        
        # El endpoint simple solo devuelve status y message, no services individuales
        if 'services' in data:
            print("\nEstado de servicios individuales:")
            for service, status in data['services'].items():
                if status:
                    print_success(f"{service.capitalize()}: Operativo")
                else:
                    print_error(f"{service.capitalize()}: Caído")
            return data['services']
        else:
            print_info("Gateway operativo (endpoint simplificado)")
            # Verificar servicios manualmente
            services = {}
            for service_name, service_info in [('inventory', 5001), ('order', 5002), ('payment', 5003)]:
                try:
                    r = requests.get(f"http://localhost:{service_info}/health", timeout=2)
                    services[service_name] = r.status_code in [200, 404]
                    status_text = "Operativo" if services[service_name] else "Caído"
                    print_success(f"{service_name.capitalize()}: {status_text}")
                except:
                    services[service_name] = False
                    print_error(f"{service_name.capitalize()}: Caído")
            return services
            
    except Exception as e:
        print_error(f"Error conectando al gateway: {e}")
        return None

def test_fallback_inventory():
    """Probar el endpoint de inventario con fallback"""
    print_header("TEST 2: Inventario con Fallback")
    
    try:
        response = requests.get(f"{GATEWAY_URL}/inventory/view", timeout=5)
        
        if response.status_code == 404:
            print_warning("Endpoint /inventory/view no disponible en versión actual")
            print_info("Intentando obtener inventario directamente del servicio...")
            
            # Intentar directamente desde inventory service
            try:
                inv_response = requests.get("http://localhost:5001/products", timeout=5)
                if inv_response.status_code == 401:
                    print_warning("Servicio de inventario requiere autenticación")
                    return False
                else:
                    print_success("Inventario obtenido directamente del servicio")
                    return True
            except:
                print_error("No se pudo conectar al servicio de inventario")
                return False
        
        data = response.json()
        
        if data.get('source') == 'live':
            print_success("Inventario obtenido del servicio en vivo")
        else:
            print_warning("Usando inventario por defecto (fallback)")
        
        print(f"\n{Fore.WHITE}Mensaje: {data.get('message', 'N/A')}")
        print(f"\n{Fore.WHITE}Productos disponibles:")
        inventory = data.get('inventory', [])
        for product in inventory:
            print(f"  - {product['name']}: ${product['price']} (Stock: {product['quantity']})")
        
        return True
    except Exception as e:
        print_error(f"Error obteniendo inventario: {e}")
        return False

def test_order_with_service_down(services_status):
    """Intentar procesar una orden cuando hay servicios caídos"""
    print_header("TEST 3: Procesamiento de Orden con Servicios Caídos")
    
    order_data = {
        "product_id": 1,
        "quantity": 2,
        "price": 999.99,
        "customer_email": "test@example.com",
        "payment_method": "credit_card"
    }
    
    print_info("Intentando procesar orden:")
    print(json.dumps(order_data, indent=2))
    
    try:
        response = requests.post(
            f"{GATEWAY_URL}/process_order",
            json=order_data,
            timeout=30
        )
        
        data = response.json()
        
        print(f"\n{Fore.WHITE}Código de respuesta: {response.status_code}")
        print(f"{Fore.WHITE}Estado: {data.get('status')}")
        print(f"{Fore.WHITE}Mensaje: {data.get('message')}")
        
        if 'services_status' in data:
            print("\nEstado de servicios durante la petición:")
            for service, status in data['services_status'].items():
                if status:
                    print_success(f"{service.capitalize()}: Operativo")
                else:
                    print_error(f"{service.capitalize()}: Caído")
        
        if response.status_code == 200:
            print_success("\n¡Orden procesada exitosamente!")
            if 'order_id' in data:
                print(f"  Order ID: {data['order_id']}")
            if 'payment_id' in data:
                print(f"  Payment ID: {data['payment_id']}")
        elif response.status_code == 503:
            print_warning("\nServicio no disponible - Respuesta degradada recibida")
            if 'fallback_inventory' in data:
                print_info("Se proporcionó inventario por defecto como fallback")
            if 'order_created' in data and data['order_created']:
                print_info(f"La orden fue creada (ID: {data.get('order_id')}) pero el pago falló")
        else:
            print_error("\nError procesando la orden")
            if services_status:
                down = [s for s, st in services_status.items() if not st]
                if down:
                    print_warning(f"Servicios caídos detectados: {', '.join(down)}")
        
        return response.status_code
        
    except requests.exceptions.Timeout:
        print_error("Timeout: El gateway no respondió a tiempo")
        return None
    except requests.exceptions.ConnectionError:
        print_error("Error de conexión: No se pudo conectar al gateway")
        return None
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return None

def test_order_success():
    """Intentar procesar una orden cuando todos los servicios están activos"""
    print_header("TEST 4: Orden Normal (Todos los Servicios Activos)")
    
    order_data = {
        "product_id": 2,
        "quantity": 1,
        "price": 29.99,
        "customer_email": "test@example.com",
        "payment_method": "debit_card"
    }
    
    print_info("Intentando procesar orden normal:")
    print(json.dumps(order_data, indent=2))
    
    try:
        response = requests.post(
            f"{GATEWAY_URL}/process_order",
            json=order_data,
            timeout=30
        )
        
        data = response.json()
        
        if response.status_code == 200:
            print_success("\n¡Orden procesada exitosamente!")
            print(f"  Order ID: {data.get('order_id')}")
            print(f"  Payment ID: {data.get('payment_id')}")
            return True
        else:
            print_error(f"\nError: {data.get('message')}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def run_all_tests():
    """Ejecutar todos los tests de resiliencia"""
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     TEST DE RESILIENCIA - MICROSERVICIOS                  ║")
    print("║     Verificando comportamiento con servicios caídos       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Style.RESET_ALL)
    
    time.sleep(1)
    
    # Test 1: Health check
    services_status = test_health_check()
    if not services_status:
        print_error("\nNo se pudo conectar al gateway. Asegúrate de que esté corriendo.")
        return
    
    time.sleep(2)
    
    # Test 2: Inventario con fallback
    test_fallback_inventory()
    
    time.sleep(2)
    
    # Test 3: Orden con servicios caídos
    test_order_with_service_down(services_status)
    
    time.sleep(2)
    
    # Test 4: Orden normal (si todos están activos)
    if all(services_status.values()):
        test_order_success()
    
    # Resumen final
    print_header("RESUMEN")
    
    if services_status:
        down_services = [name for name, status in services_status.items() if not status and name != 'gateway']
        
        if down_services:
            print_warning(f"Servicios caídos detectados: {', '.join(down_services)}")
            print_info("\nCuando hay servicios caídos:")
            print("  • El gateway detecta errores de conexión")
            print("  • Se muestran mensajes de error descriptivos")
            print("  • Las órdenes fallan si algún servicio está caído")
            print("  • Se pueden implementar fallbacks para resiliencia")
        else:
            print_success("Todos los servicios están operativos")
            print_info("Para probar resiliencia, detén uno de los servicios y ejecuta este script nuevamente")
    else:
        print_warning("No se pudo determinar el estado de los servicios")
    
    print(f"\n{Fore.CYAN}Instrucciones para probar resiliencia:")
    print(f"{Fore.WHITE}1. Detén un servicio (Ctrl+C en su terminal)")
    print(f"{Fore.WHITE}2. Ejecuta este script nuevamente: python test_resilience.py")
    print(f"{Fore.WHITE}3. Observa los mensajes de error y cómo el sistema maneja las fallas\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Test interrumpido por el usuario")
    except Exception as e:
        print_error(f"\nError crítico: {e}")
