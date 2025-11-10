"""
🐧 SERVIDOR CENTRAL DE LOGGING DISTRIBUIDO (SIN DECORADORES)
=============================================================
Este servidor recibe, valida, almacena y consulta logs de múltiples servicios.

Endpoints:
- POST /logs     -> Recibir logs (requiere autenticación)
- GET /logs      -> Consultar logs con filtros
- GET /stats     -> Estadísticas del sistema
- DELETE /logs   -> Limpiar logs antiguos
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

# CONFIGURACIÓN
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desactivar para evitar overhead
db = SQLAlchemy(app)

# Tokens válidos por servicio
VALID_TOKENS = {
    'token_api_service': 'API Service',
    'token_web_service': 'Web Service',
    'token_db_service': 'Database Service',
    'token_payment_service': 'Payment Service',
    'token_notification_service': 'Notification Service'
}


# MODELO DE DATOS
class Log(db.Model):
    """Modelo para almacenar logs en la base de datos"""
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    received_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    service = db.Column(db.String(100), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        """Convierte el log a diccionario para JSON"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'received_at': self.received_at.isoformat(),
            'service': self.service,
            'severity': self.severity,
            'message': self.message
        }


# FUNCIÓN DE VERIFICACIÓN DE TOKEN (reemplaza al decorador)
def verificar_token():
    """
    Verifica que el token en el header sea válido.
    Retorna (None, None) si es válido, o (error_dict, status_code) si falla.
    """
    # 1. Obtener el header Authorization
    auth_header = request.headers.get('Authorization')
    
    # 2. Verificar que exista
    if not auth_header:
        error_response = jsonify({
            'error': 'No Authorization header provided. ¿Quién sos, bro?'
        })
        return error_response, 401 
    # 401 es en http el código para "No autorizado"

    # 3. Verificar formato "Token XXXXX"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0] != 'Token':
        error_response = jsonify({
            'error': 'Invalid Authorization format. Use: Token YOUR_TOKEN'
        })
        return error_response, 401
    # Aquí también usamos 401 para formato inválido

    # 4. Extraer el token
    token = parts[1]
    
    # 5. Verificar si el token es válido
    if token not in VALID_TOKENS:
        error_response = jsonify({
            'error': 'Invalid token. Quién sos, bro?'
        })
        return error_response, 403
    # 403 es el código para "Prohibido" (token inválido)
    
    # 6. Todo OK - guardar el nombre del servicio (opcional)
    request.service_name = VALID_TOKENS[token]
    
    # 7. Retornar None, None indica que todo está OK
    return None, None


# ENDPOINTS

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint simple para verificar que el servidor está vivo"""
    return jsonify({
        'status': 'alive',
        'message': '🐧 Servidor de logging funcionando perfectamente',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/logs', methods=['GET'])
def get_logs():
    """
    Consulta logs con filtros opcionales.
    """
    # ===== VERIFICACIÓN DE TOKEN =====
    error_response, status_code = verificar_token()
    if error_response:
        return error_response, status_code
    # =================================
    
    query = Log.query # Consulta base
    #ver despues


    # Filtros por timestamp del evento
    if timestamp_start := request.args.get('timestamp_start'): #
        '''esto es un operador morsa, pero que pio es un operador morsa
        no tiene nada que ver con la pelicula esa de un tipo que se convierte en morsa
        esto sirve es una verificacion corta para asignar y verificar a la vez, si es'''
        try:
            ts = datetime.fromisoformat(timestamp_start)
            query = query.filter(Log.timestamp >= ts)
        except ValueError:
            return jsonify({'error': 'Invalid timestamp_start format'}), 400
    
    if timestamp_end := request.args.get('timestamp_end'):
        try:
            ts = datetime.fromisoformat(timestamp_end)
            query = query.filter(Log.timestamp <= ts)
        except ValueError:
            return jsonify({'error': 'Invalid timestamp_end format'}), 400
    
    # Filtros por cuándo se recibió el log
    if received_start := request.args.get('received_at_start'):
        try:
            ts = datetime.fromisoformat(received_start)
            query = query.filter(Log.received_at >= ts)
        except ValueError:
            return jsonify({'error': 'Invalid received_at_start format'}), 400
    
    if received_end := request.args.get('received_at_end'):
        try:
            ts = datetime.fromisoformat(received_end)
            query = query.filter(Log.received_at <= ts)
        except ValueError:
            return jsonify({'error': 'Invalid received_at_end format'}), 400
    
    # Filtro por servicio
    if service := request.args.get('service'):
        query = query.filter(Log.service == service)
    
    # Filtro por severidad
    if severity := request.args.get('severity'):
        query = query.filter(Log.severity == severity)
    
    # Paginación
    limit = min(int(request.args.get('limit', 100)), 1000)
    offset = int(request.args.get('offset', 0))
    
    # Ordenar por timestamp descendente (más recientes primero)
    query = query.order_by(Log.timestamp.desc())
    
    # Obtener total y logs
    total = query.count()
    logs = query.limit(limit).offset(offset).all()
    
    return jsonify({
        'total': total,
        'limit': limit,
        'offset': offset,
        'count': len(logs),
        'logs': [log.to_dict() for log in logs]
    })


@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Devuelve estadísticas del sistema de logging.
    
    Incluye:
    - Total de logs
    - Logs por servicio
    - Logs por severidad
    - Último log recibido por servicio
    """
    # ===== VERIFICACIÓN DE TOKEN =====
    error_response, status_code = verificar_token()
    if error_response:
        return error_response, status_code
    # =================================
    
    # Total de logs
    total_logs = db.session.query(db.func.count(Log.id)).scalar()
    
    # Logs por servicio
    logs_by_service = db.session.query(
        Log.service,
        db.func.count(Log.id).label('count')
    ).group_by(Log.service).all()
    
    # Logs por severidad
    logs_by_severity = db.session.query(
        Log.severity,
        db.func.count(Log.id).label('count')
    ).group_by(Log.severity).all()
    
    # Último log por servicio
    last_logs = {}
    services = db.session.query(Log.service).distinct().all()
    
    for (service,) in services:
        last_log = Log.query.filter_by(service=service)\
            .order_by(Log.received_at.desc())\
            .first()
        if last_log:
            last_logs[service] = last_log.to_dict()
    
    return jsonify({
        'total_logs': total_logs,
        'logs_by_service': {service: count for service, count in logs_by_service},
        'logs_by_severity': {severity: count for severity, count in logs_by_severity},
        'last_log_by_service': last_logs,
        'generated_at': datetime.utcnow().isoformat()
    })

# INICIALIZACIÓN
def init_db():
    """Crea las tablas si no existen"""
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada correctamente")


init_db()
print("\n🐧 Servidor de Logging Distribuido (SIN DECORADORES)")
print("=" * 50)
print(f"Tokens válidos registrados: {len(VALID_TOKENS)}")
print("\nEndpoints disponibles:")
print("  GET    /logs       - Consultar logs")
print("  GET    /stats      - Estadísticas")
print("  GET    /health     - Health check")
print("\n" + "=" * 50)

app.run(host='0.0.0.0', port=5000, debug=True)