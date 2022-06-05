import requests
import json

api_key = "53c6ca4afb5fd23a2d552de70d029b5f"
ciudad = "Orihuela"
url = "http://api.openweathermap.org/data/2.5/weather?q=" + ciudad + "&appid=53c6ca4afb5fd23a2d552de70d029b5f"

# Realizamos la petición
response = requests.get(url)
# Obtenenemos el json
data = json.loads(response.text) 
# Obtenemos la temperatura
temp = int(data["main"]["temp"]) 
# Conevertimos a grados centigrados
temp = temp - 273.15 

print(temp)