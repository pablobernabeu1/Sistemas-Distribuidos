import cryptography
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from flask import Flask, render_template, jsonify, request
import json
import API_Registry as reg

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mapa')
def posts():
    
    with open("mapa.txt", 'r') as file:
       data = file.read()
    
    return data
    
    

@app.route('/crearusuario', methods=["GET", "POST"])
def crear_usuario():
    if request.method == "POST":  
        datos = request.get_json()
        usrname = datos["username"]
        simb = datos["simbolo"]
        passwd = datos["passwd"]
        
        usrname = usrname.encode("iso-8859-1")
        simb = simb.encode("iso-8859-1")
        passwd = passwd.encode("iso-8859-1")

        # DESCIFRADO
        with open("private_noshare.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        
        # USERNAME
        usrname = private_key.decrypt(
            usrname,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # SIMBOLO
        simb = private_key.decrypt(
            simb,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # PASSWD
        passwd = private_key.decrypt(
            passwd,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        usrname = usrname.decode()
        simb = simb.decode()
        passwd = passwd.decode()
        
        try: 
            created = reg.crear_user(usrname, simb, passwd) 
        
        except:
            return "Registry no disponible."
        
        return "Usuario creado correctamente."


@app.route('/editarusuario', methods=["GET", "POST"])
def editar_usuario():
    if request.method == "POST":  
        old_usrname = request.args.get('oldusrname')
        new_usrname = request.args.get('newusrname')
        simb = request.args.get('simbolo')
        passwd = request.args.get('passwd')

    try: 
        created = reg.editar_user(old_usrname, new_usrname, simb, passwd) 
    
    except:
        return "Registry no disponible."
    
    return "Usuario editado correctamente."


if __name__ == '__main__':
    app.run(host="127.0.1.1", debug=True, port=4000)