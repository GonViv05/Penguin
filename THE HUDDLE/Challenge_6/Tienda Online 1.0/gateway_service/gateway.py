from flask import Flask, request, jsonify
import requests #hacer llamadas HTTP a otros servicios
import sqlite3
import logging #registra eventos y errores
from datetime import datetime, timedelta
from circuitbreaker import circuit
import time
import jwt

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuración de servicios y tokens
SERVICES = {
    'inventory': {
        'url': 'http://localhost:5001',
        'secret_key': 'inventory-secret-key'
    },
    'order': {
        'url': 'http://localhost:5002', 
        'secret_key': 'order-secret-key'
    },
    'payment': {
        'url': 'http://localhost:5003',
        'secret_key': 'payment-secret-key'
    }
}

def generate_service_token(service_name):
    secret_key = SERVICES[service_name]['secret_key']
    payload = {
        'service': 'gateway',
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def get_service_headers(service_name):
    token = generate_service_token(service_name)
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

# Inicializar base de datos de logs
def init_logs_db():
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  client_ip TEXT,
                  endpoint TEXT,
                  method TEXT,
                  request_data TEXT,
                  response_data TEXT,
                  status TEXT)''')
    conn.commit()
    conn.close()

def log_request(client_ip, endpoint, method, request_data, response_data, status):
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    c.execute('''INSERT INTO logs (timestamp, client_ip, endpoint, method, request_data, response_data, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (datetime.now().isoformat(), client_ip, endpoint, method, str(request_data), str(response_data), status))
    conn.commit()
    conn.close()

@circuit(failure_threshold=5, expected_exception=Exception)
def call_service(service_name, endpoint, method='POST', data=None, retries=3):
    for attempt in range(retries):
        try:
            url = f"{SERVICES[service_name]['url']}/{endpoint}"
            headers = get_service_headers(service_name)
            
            logging.info(f"Calling {url} with method {method}")
            
            # Increased timeout from 5 to 15 seconds to handle slow responses
            timeout = 15
            
            if method == 'GET':
                response = requests.get(url, json=data, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            
            logging.info(f"Response from {service_name}: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Service {service_name} returned {response.status_code}: {response.text}")
                
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed for {service_name}: {str(e)}")
            if attempt == retries - 1:
                raise e
            # Exponential backoff: 1s, 2s, 3s
            wait_time = (attempt + 1) * 1
            logging.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

@app.route('/process_order', methods=['POST'])
def process_order():
    client_ip = request.remote_addr
    order_data = request.json
    
    try:
        # Log initial request
        log_request(client_ip, '/process_order', 'POST', order_data, None, 'STARTED')
        
        # Call inventory service
        inventory_result = call_service('inventory', 'check_inventory', 'POST', order_data)
        if inventory_result.get('status') != 'ok':
            raise Exception(f"Inventory error: {inventory_result.get('message')}")
        
        # Call order service
        order_result = call_service('order', 'create_order', 'POST', order_data)
        if order_result.get('status') != 'ok':
            raise Exception(f"Order error: {order_result.get('message')}")
        
        # Prepare payment data with order_id and total_price
        payment_data = {
            'order_id': order_result.get('order_id'),
            'total_price': order_result.get('total_price'),  # Use total_price from order response
            'payment_method': order_data.get('payment_method', 'credit_card')
        }
        
        # Call payment service
        payment_result = call_service('payment', 'process_payment', 'POST', payment_data)
        if payment_result.get('status') != 'ok':
            raise Exception(f"Payment error: {payment_result.get('message')}")
        
        # If all services succeeded, update inventory
        update_result = call_service('inventory', 'update_inventory', 'POST', order_data)
        if update_result.get('status') != 'ok':
            raise Exception(f"Inventory update error: {update_result.get('message')}")
        
        response = {
            'status': 'success',
            'message': 'Order processed successfully',
            'order_id': order_result.get('order_id'),
            'payment_id': payment_result.get('payment_id')
        }
        
        log_request(client_ip, '/process_order', 'POST', order_data, response, 'COMPLETED')
        return jsonify(response), 200
        
    except Exception as e:
        error_response = {
            'status': 'error',
            'message': str(e)
        }
        log_request(client_ip, '/process_order', 'POST', order_data, error_response, 'FAILED')
        return jsonify(error_response), 400

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint without authentication"""
    return jsonify({'status': 'ok', 'message': 'Gateway is running'}), 200

@app.route('/admin/logs', methods=['GET'])
def get_logs():
    """Get request logs - public endpoint for monitoring"""
    conn = sqlite3.connect('logs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100')
    logs = c.fetchall()
    conn.close()
    
    return jsonify([{
        'id': log[0],
        'timestamp': log[1],
        'client_ip': log[2],
        'endpoint': log[3],
        'method': log[4],
        'request_data': log[5],
        'response_data': log[6],
        'status': log[7]
    } for log in logs])

if __name__ == '__main__':
    init_logs_db()
    app.run(port=5000, debug=False)