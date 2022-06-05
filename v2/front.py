from flask import Flask, render_template, jsonify
import requests, json


def mostrarMapa(mapa):
    try:
        with open("templates/index.html", "w") as file:
            file.write("<!DOCTYPE html><html><head><meta http-equiv=\"refresh\" content=\"1\"></head><body>" + str(mapa) + "</body></html>")
        
    except:
        print("No se pudo escribir el mapa en la BBDD.")


app = Flask(__name__)


@app.route('/')
def index():
    response = requests.get("http://127.0.1.1:4000/mapa")
    mostrarMapa(response.text)
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="192.168.137.1", debug=True, port=5000)