import subprocess
import time
import sys
import os

services = [
    {'name': 'Gateway Service', 'command': [sys.executable, 'gateway_service/gateway.py']},
    {'name': 'Inventory Service', 'command': [sys.executable, 'inventory_service/inventory.py']},
    {'name': 'Order Service', 'command': [sys.executable, 'order_service/order.py']},
    {'name': 'Payment Service', 'command': [sys.executable, 'payment_service/payment.py']}
]

processes = []

def start_services():
    print("🚀 Starting all microservices...")
    
    for service in services:
        try:
            print(f"📦 Starting {service['name']}...")
            # Use shell=True for Windows and capture output
            process = subprocess.Popen(
                service['command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            processes.append(process)
            time.sleep(2)  # Give each service time to start (increased from 1)
        except Exception as e:
            print(f"❌ Failed to start {service['name']}: {e}")
    
    print("\n✅ All services started!")
    print("📍 Gateway: http://localhost:5000")
    print("📍 Inventory: http://localhost:5001")
    print("📍 Order: http://localhost:5002")
    print("📍 Payment: http://localhost:5003")
    print("\nPress Ctrl+C to stop all services")
    time.sleep(2)  # Wait for services to fully initialize

def stop_services():
    print("\n🛑 Stopping all services...")
    for process in processes:
        process.terminate()
    for process in processes:
        process.wait()

if __name__ == '__main__':
    try:
        start_services()
        
        # Keep services running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        stop_services()
    except Exception as e:
        print(f"💥 Error: {e}")
        stop_services()