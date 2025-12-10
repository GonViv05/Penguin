from flask import Flask, request, jsonify
import sqlite3
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'payment-secret-key'

# Lista de servicios autorizados
AUTHORIZED_SERVICES = ['gateway', 'admin']

def init_payment_db():
    conn = sqlite3.connect('payment.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  order_id INTEGER NOT NULL,
                  amount REAL NOT NULL,
                  payment_method TEXT NOT NULL,
                  status TEXT NOT NULL,
                  processed_at TEXT)''')
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

@app.route('/process_payment', methods=['POST'])
def process_payment():
    auth = authenticate()
    if not auth:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    data = request.json
    order_id = data.get('order_id')
    amount = data.get('total_price')
    payment_method = data.get('payment_method', 'credit_card')
    
    if not order_id or not amount:
        return jsonify({'status': 'error', 'message': 'Missing order_id or amount'}), 400
    
    # Simulate payment processing
    if amount > 0:
        conn = sqlite3.connect('payment.db')
        c = conn.cursor()
        c.execute('''INSERT INTO payments (order_id, amount, payment_method, status, processed_at)
                     VALUES (?, ?, ?, ?, ?)''',
                  (order_id, amount, payment_method, 'completed', datetime.datetime.now().isoformat()))
        payment_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'ok', 
            'message': 'Payment processed successfully',
            'payment_id': payment_id
        })
    else:
        return jsonify({'status': 'error', 'message': 'Invalid payment amount'}), 400

@app.route('/payments', methods=['GET', 'DELETE'])
def manage_payments():
    auth = authenticate()
    if not auth:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        conn = sqlite3.connect('payment.db')
        c = conn.cursor()
        c.execute("SELECT * FROM payments")
        payments = c.fetchall()
        conn.close()
        
        return jsonify([{
            'id': p[0],
            'order_id': p[1],
            'amount': p[2],
            'payment_method': p[3],
            'status': p[4],
            'processed_at': p[5]
        } for p in payments])
    
    elif request.method == 'DELETE':
        payment_id = request.args.get('id')
        conn = sqlite3.connect('payment.db')
        c = conn.cursor()
        c.execute("DELETE FROM payments WHERE id=?", (payment_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok', 'message': 'Payment record deleted'})

if __name__ == '__main__':
    init_payment_db()
    app.run(port=5003, debug=True)