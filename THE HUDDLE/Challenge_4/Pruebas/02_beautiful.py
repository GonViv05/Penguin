from bs4 import BeautifulSoup
import requests

url = "https://www.apple.com/es/shop/buy-mac/macbook-air"
response = requests.get(url)

if response.status_code == 200:
    print('La peticion fue exitosa')

    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.title
    if title_tag:
        print(f"El titulo de la web es: {title_tag.text}")

price_span = soup.find_all('span', class_='rc-prices-fullprice')
'''for precios in price_span:
    print(f'El precio del producto es {precios.text}')'''
productos = soup.find_all(class_='rc-productselection-item')
'''for product in productos:
    name = product.find(class_='list_title')
    price = product.find(class_='rc-prices-fillprice')
    print(f'El producto con las caracteristricas: \n {name.text} \nPrecio de {price.attrs}\n\n'''
for product in productos:
    name = product.find(class_='list-title').text
    price = product.find(class_='rc-prices-fullprice').text
    print(f"el producto con las caracteristicas: \n {name}\n Precio de {price}")