import requests
import jwt
import datetime
import sys
import json
from flask import Flask, request, jsonify, Response

try:
    from tabulate import tabulate
except Exception:
    tabulate = None

class AdminClient:
    def __init__(self):
        self.base_url = 'http://localhost:5000'
        # SERVICIO SECRET KEYS - deben coincidir con gateway.py
        self.service_secrets = {
            'inventory': 'inventory-secret-key',
            'order': 'order-secret-key', 
            'payment': 'payment-secret-key'
        }
        
        self.tokens = {}
        self.generate_tokens()
    
    def generate_tokens(self):
        for service_name in ['inventory', 'order', 'payment']:
            payload = {
                'service': 'gateway',
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            self.tokens[service_name] = jwt.encode(
                payload, 
                self.service_secrets[service_name], 
                algorithm='HS256'
            )
    
    
    def get_logs(self):
        return requests.get(f'{self.base_url}/admin/logs')
    
    def manage_inventory(self, action, data=None):
        headers = {
            'Authorization': f'Bearer {self.tokens["inventory"]}',
            'Content-Type': 'application/json'
        }
        url = 'http://localhost:5001/products'
        
        try:
            if action == 'GET':
                return requests.get(url, headers=headers, timeout=10)
            elif action == 'POST':
                return requests.post(url, json=data, headers=headers, timeout=10)
            elif action == 'PUT':
                return requests.put(url, json=data, headers=headers, timeout=10)
            elif action == 'DELETE':
                # Para DELETE, enviar ID en la URL o en el body según lo que espere el servicio
                delete_url = f"{url}/{data['id']}" if 'id' in data else url
                return requests.delete(delete_url, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            return type('MockResponse', (), {'status_code': 500, 'content': f'{{"error": "Connection failed: {str(e)}"}}'})()
        
        return None

    def manage_orders(self, action, data=None):
        headers = {'Authorization': f'Bearer {self.tokens["order"]}'}
        url = f'http://localhost:5002/orders'
        
        if action == 'GET':
            return requests.get(url, headers=headers)
        elif action == 'PUT':
            return requests.put(url, json=data, headers=headers)
        elif action == 'DELETE':
            return requests.delete(f"{url}?id={data['id']}", headers=headers)
        return None
    
    def manage_payments(self, action, data=None):
        headers = {'Authorization': f'Bearer {self.tokens["payment"]}'}
        url = f'http://localhost:5003/payments'
        
        if action == 'GET':
            return requests.get(url, headers=headers)
        elif action == 'DELETE':
            return requests.delete(f"{url}?id={data['id']}", headers=headers)
        return None
    

if __name__ == '__main__':
    # Run as a small Flask admin proxy so user can use Postman / localhost
    app = Flask(__name__)
    admin = AdminClient()

    @app.route('/')
    def index():
        return jsonify({
            'message': 'Admin proxy running',
            'endpoints': {
                'GET /logs': 'Proxy to gateway /admin/logs',
                'GET /inventory': 'GET products',
                'POST /inventory': 'Create product',
                'PUT /inventory': 'Update product (JSON body)',
                'DELETE /inventory/<id>': 'Delete product',
                'GET /orders': 'List orders',
                'PUT /orders': 'Update order status',
                'DELETE /orders/<id>': 'Delete order',
                'GET /payments': 'List payments',
                'DELETE /payments/<id>': 'Delete payment'
            }
        })

    @app.route('/logs', methods=['GET'])
    def logs():
        resp = admin.get_logs()
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))

    # Inventory
    @app.route('/inventory', methods=['GET', 'POST', 'PUT'])
    def inventory():
        if request.method == 'GET':
            resp = admin.manage_inventory('GET')
            return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
        elif request.method == 'POST':
            data = request.json
            resp = admin.manage_inventory('POST', data=data)
            return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
        elif request.method == 'PUT':
            data = request.json
            resp = admin.manage_inventory('PUT', data=data)
            return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))

    @app.route('/inventory/<int:item_id>', methods=['DELETE'])
    def inventory_delete(item_id):
        resp = admin.manage_inventory('DELETE', data={'id': item_id})
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))

    # Orders
    @app.route('/orders', methods=['GET', 'PUT'])
    def orders():
        if request.method == 'GET':
            resp = admin.manage_orders('GET')
            return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))
        elif request.method == 'PUT':
            data = request.json
            resp = admin.manage_orders('PUT', data=data)
            return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))

    @app.route('/orders/<int:order_id>', methods=['DELETE'])
    def orders_delete(order_id):
        resp = admin.manage_orders('DELETE', data={'id': order_id})
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))

    # Payments
    @app.route('/payments', methods=['GET'])
    def payments():
        resp = admin.manage_payments('GET')
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))

    @app.route('/payments/<int:payment_id>', methods=['DELETE'])
    def payments_delete(payment_id):
        resp = admin.manage_payments('DELETE', data={'id': payment_id})
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type', 'application/json'))

    print('Starting Admin proxy on http://127.0.0.1:5010')
    app.run(host='127.0.0.1', port=5010, debug=False)

