import requests

GATEWAY_URL = 'http://localhost:5000'

PRODUCTS = {
    1: ('Laptop', 999.99),
    2: ('Mouse', 29.99),
    3: ('Keyboard', 79.99),
    4: ('Monitor', 299.99),
}


def solicitar_entero(prompt, default=None):
    while True:
        try:
            v = input(prompt).strip()
            if v == '' and default is not None:
                return default
            return int(v)
        except ValueError:
            print('Entrada inválida, por favor ingresa un número entero.')


def solicitar_flotante(prompt, default=None):
    while True:
        try:
            v = input(prompt).strip()
            if v == '' and default is not None:
                return default
            return float(v)
        except ValueError:
            print('Entrada inválida, por favor ingresa un número (ej: 9.99).')


def mostrar_productos():
    print('\nProductos disponibles:')
    for pid, (name, price) in PRODUCTS.items():
        print(f"  {pid}) {name} - ${price}")


def realizar_orden():
    print('\n🛒 Realizar nueva orden')
    mostrar_productos()
    pid = solicitar_entero('Selecciona el ID del producto [1]: ', default=1)
    if pid not in PRODUCTS:
        print('Producto no encontrado, se seleccionará el producto 1 por defecto.')
        pid = 1
    name, default_price = PRODUCTS[pid]
    qty = solicitar_entero('Cantidad: ', default=1)
    price = solicitar_flotante(f'Precio por unidad [{default_price}]: ', default=default_price)
    email = input('Email del cliente [cliente@example.com]: ').strip() or 'cliente@example.com'
    metodo = input('Método de pago [credit_card]: ').strip() or 'credit_card'

    order_data = {
        'product_id': pid,
        'quantity': qty,
        'price': price,
        'customer_email': email,
        'payment_method': metodo,
    }

    print('\nEnviando orden al gateway...')
    try:
        response = requests.post(f'{GATEWAY_URL}/process_order', json=order_data, timeout=30)
        try:
            result = response.json()
        except Exception:
            print('Respuesta inválida del servidor')
            print('Status:', response.status_code)
            print(response.text)
            return

        if response.status_code == 200:
            print('\n✅ Orden procesada con éxito')
            print('Mensaje:', result.get('message'))
            print('Order ID:', result.get('order_id'))
            print('Payment ID:', result.get('payment_id'))
        else:
            print('\n❌ Error al procesar la orden')
            print('Status:', response.status_code)
            print('Detalle:', result.get('message'))

    except requests.exceptions.ConnectionError:
        print('\n❌ No se puede conectar con el gateway. Asegúrate de que los servicios estén en ejecución.')
    except requests.exceptions.Timeout:
        print('\n❌ Tiempo de espera agotado al comunicarse con el gateway.')
    except Exception as e:
        print('\n❌ Error inesperado:', str(e))


def main():
    print('Cliente de Tienda - Localhost')
    while True:
        print('\nMenú:')
        print('  1) Realizar una orden')
        print('  0) Salir')
        opcion = input('Selecciona una opción: ').strip()
        if opcion == '1':
            realizar_orden()
        elif opcion == '0':
            print('Adiós')
            break
        else:
            print('Opción inválida, intenta de nuevo.')


if __name__ == '__main__':
    main()