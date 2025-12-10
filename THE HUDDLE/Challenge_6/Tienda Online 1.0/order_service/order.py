from flask import Flask, request, jsonify
import sqlite3
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'order-secret-key'

# Lista de servicios autorizados
AUTHORIZED_SERVICES = ['gateway', 'admin']

def init_order_db():
    conn = sqlite3.connect('order.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  product_id INTEGER NOT NULL,
                  quantity INTEGER NOT NULL,
                  total_price REAL NOT NULL,
                  customer_email TEXT NOT NULL,
                  status TEXT NOT NULL,
                  created_at TEXT)''')
    conn.commit()
    conn.close()

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if payload.get('service') in AUTHORIZED_SERVICES:
            return payload
        return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def authenticate():
    token = request.headers.get('Authorization')
    if not token:
        return None
    token = token.replace('Bearer ', '')
    return verify_token(token)

@app.route('/create_order', methods=['POST'])
def create_order():
    auth = authenticate()
    if not auth:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    price = data.get('price')
    customer_email = data.get('customer_email')
    
    if not all([product_id, quantity, price, customer_email]):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    total_price = quantity * price
    
    conn = sqlite3.connect('order.db')
    c = conn.cursor()
    c.execute('''INSERT INTO orders (product_id, quantity, total_price, customer_email, status, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (product_id, quantity, total_price, customer_email, 'completed', datetime.datetime.now().isoformat()))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'status': 'ok', 
        'message': 'Order created successfully', 
        'order_id': order_id,
        'total_price': total_price
    })

@app.route('/orders', methods=['GET', 'PUT', 'DELETE'])
def manage_orders():
    auth = authenticate()
    if not auth:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        conn = sqlite3.connect('order.db')
        c = conn.cursor()
        c.execute("SELECT * FROM orders")
        orders = c.fetchall()
        conn.close()
        
        return jsonify([{
            'id': o[0],
            'product_id': o[1],
            'quantity': o[2],
            'total_price': o[3],
            'customer_email': o[4],
            'status': o[5],
            'created_at': o[6]
        } for o in orders])
    
    elif request.method == 'PUT':
        data = request.json
        conn = sqlite3.connect('order.db')
        c = conn.cursor()
        c.execute("UPDATE orders SET status=? WHERE id=?", (data['status'], data['id']))
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok', 'message': 'Order updated'})
    
    elif request.method == 'DELETE':
        order_id = request.args.get('id')
        conn = sqlite3.connect('order.db')
        c = conn.cursor()
        c.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok', 'message': 'Order deleted'})

if __name__ == '__main__':
    init_order_db()
    app.run(port=5002, debug=True)