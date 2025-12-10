import requests
import time
import threading
import jwt
import datetime as dt

GATEWAY_URL = 'http://localhost:5000'

def generate_service_token(service_name, secret_key):
    """Generar token JWT válido para un servicio"""
    payload = {
        'service': 'gateway',
        'exp': dt.datetime.utcnow() + dt.timedelta(hours=24)
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def test_service_health():
    """Test if all services are running"""
    services = [
        ('Gateway', 'http://localhost:5000/admin/logs', None),
        ('Inventory', 'http://localhost:5001/products', 'inventory-secret-key'),
        ('Order', 'http://localhost:5002/orders', 'order-secret-key'), 
        ('Payment', 'http://localhost:5003/payments', 'payment-secret-key')
    ]
    
    print("🔍 Checking service health...")
    for name, url, secret_key in services:
        try:
            headers = {}
            if secret_key:
                token = generate_service_token('gateway', secret_key)
                headers['Authorization'] = f'Bearer {token}'
            
            response = requests.get(url, headers=headers, timeout=5)
            status = "✅ Running" if response.status_code == 200 else "❌ Issues"
            print(f"   {name}: {status} (Status: {response.status_code})")
        except Exception as e:
            print(f"   {name}: ❌ Not responding - {str(e)}")

def simulate_client(order_id, product_id=1, quantity=1):
    order_data = {
        'product_id': product_id,
        'quantity': quantity,
        'price': 999.99 if product_id == 1 else 29.99,  # Precios según el producto
        'customer_email': f'client{order_id}@example.com',
        'payment_method': 'credit_card'
    }
    
    print(f"🧪 Client {order_id} placing order for product {product_id}...")
    
    try:
        # Increased timeout from 10 to 30 seconds
        response = requests.post(f'{GATEWAY_URL}/process_order', json=order_data, timeout=30)
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ Client {order_id}: Order successful - {result['message']}")
            print(f"   Order ID: {result.get('order_id')}")
        else:
            print(f"❌ Client {order_id}: Order failed - {result['message']}")
            
    except Exception as e:
        print(f"💥 Client {order_id}: Error - {str(e)}")

def run_tests():
    print("🚀 Starting microservices test...")
    
    # Wait for services to start
    time.sleep(3)
    
    # Test service health first
    test_service_health()
    
    # Test single order
    print("\n1. Testing single order:")
    simulate_client(1)
    
    # Test multiple concurrent orders
    print("\n2. Testing concurrent orders:")
    threads = []
    for i in range(2, 5):
        thread = threading.Thread(target=simulate_client, args=(i,))
        threads.append(thread)
        thread.start()
        time.sleep(0.5)  # Stagger requests
    
    for thread in threads:
        thread.join()
    
    # Test order with different product
    print("\n3. Testing order with different product (Mouse):")
    simulate_client(5, product_id=2, quantity=2)  # Mouse
    
    # Test order with insufficient inventory
    print("\n4. Testing order with large quantity (should fail):")
    order_data = {
        'product_id': 1,
        'quantity': 100,  # More than available
        'price': 999.99,
        'customer_email': 'test@example.com',
        'payment_method': 'credit_card'
    }
    
    try:
        response = requests.post(f'{GATEWAY_URL}/process_order', json=order_data, timeout=10)
        result = response.json()
        print(f"📋 Result: {result['message']}")
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == '__main__':
    run_tests()