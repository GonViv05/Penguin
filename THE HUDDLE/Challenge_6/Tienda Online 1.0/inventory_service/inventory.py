from flask import Flask, request, jsonify
import sqlite3
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'inventory-secret-key'

# Lista de servicios autorizados
AUTHORIZED_SERVICES = ['gateway', 'admin']

def init_inventory_db():
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  quantity INTEGER NOT NULL,
                  price REAL NOT NULL)''')
    
    # Insert sample data
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", 
                 ("Laptop", 10, 999.99))
        c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", 
                 ("Mouse", 50, 29.99))
        c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", 
                 ("Keyboard", 30, 79.99))
        c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", 
                 ("Monitor", 15, 299.99))
    
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
    
    # Remove 'Bearer ' prefix if present
    token = token.replace('Bearer ', '')
    return verify_token(token)

@app.route('/check_inventory', methods=['POST'])
def check_inventory():
    auth = authenticate()
    if not auth:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    if not product_id or not quantity:
        return jsonify({'status': 'error', 'message': 'Missing product_id or quantity'}), 400
    
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("SELECT name, quantity, price FROM products WHERE id = ?", (product_id,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        return jsonify({'status': 'error', 'message': 'Product not found'}), 404
    
    product_name, available_quantity, price = result
    if available_quantity >= quantity:
        return jsonify({
            'status': 'ok', 
            'message': 'Inventory available',
            'product_name': product_name,
            'available_quantity': available_quantity,
            'price': price
        })
    else:
        return jsonify({
            'status': 'error', 
            'message': f'Insufficient inventory. Available: {available_quantity}, Requested: {quantity}'
        }), 400

@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    auth = authenticate()
    if not auth:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    
    if not product_id or not quantity:
        return jsonify({'status': 'error', 'message': 'Missing product_id or quantity'}), 400
    
    conn = sqlite3.connect('inventory.db')
    c = conn.cursor()
    c.execute("UPDATE products SET quantity = quantity - ? WHERE id = ? AND quantity >= ?", 
              (quantity, product_id, quantity))
    
    if c.rowcount == 0:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Failed to update inventory - insufficient quantity or product not found'}), 400
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'ok', 'message': 'Inventory updated successfully'})

@app.route('/products', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_products():
    auth = authenticate()
    if not auth:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        products = c.fetchall()
        conn.close()
        #(1, "Laptop", 10, 999.99)
        return jsonify([{
            'id': p[0],
            'name': p[1],
            'quantity': p[2],
            'price': p[3]
        } for p in products])
    
    elif request.method == 'POST':
        data = request.json
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)",
                 (data['name'], data['quantity'], data['price']))
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok', 'message': 'Product created'})
    
    elif request.method == 'PUT':
        data = request.json
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("UPDATE products SET name=?, quantity=?, price=? WHERE id=?",
                 (data['name'], data['quantity'], data['price'], data['id']))
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok', 'message': 'Product updated'})
    
    elif request.method == 'DELETE':
        product_id = request.args.get('id')
        conn = sqlite3.connect('inventory.db')
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'ok', 'message': 'Product deleted'})

if __name__ == '__main__':
    init_inventory_db()
    app.run(port=5001, debug=True)