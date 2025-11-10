import requests
#Request no puede saltarse paywalls ni captchas
#muy rapido y muy sencillo de implementar 
#muy manual para encontrar lo que te interesa
import re

url = 'https://www.apple.com/es/shop/buy-mac/macbook-air/'
 
response = requests.get(url)
 
if response.status_code == 200:
   print('La petición fue exitosa')
 
   html = response.text
   print(html)
 
   # Expresión regular para encontrar el precio
 
   price_pattern = r'<span class="rc-segmented-control-caption typography-caption">(./*?)</span>'
   match = re.search(price_pattern, html)
 
   if match:
       print(f"El precio del producto es: {match.group(1)}")
   else:
       print("No se encontró el precio")
     
    