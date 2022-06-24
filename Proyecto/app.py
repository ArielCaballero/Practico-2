from string import hexdigits
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import hashlib


app=Flask(__name__)
app.config.from_pyfile('config.py')

from models import db, Usuario, Ingrediente, Receta

@app.route('/')
def Inicio():
    return render_template("Inicio.html")

@app.route('/Ingreso', methods=['GET', 'POST'])
def ingreso():
    if request.method=='POST':
        if not request.form['Usuario'] or not request.form['Contraseña']:
            return render_template('Error.html', error="Debe ingresar Email y Contraseña")
        else:
            Usuario_actual= Usuario.query.filter_by(correo=request.form['Usuario']).first()
            if Usuario_actual is None:
                return render_template('Error.html', error="Email no Registrado")
            else:
                contraseña=(hashlib.md5(bytes(request.form['Contraseña'], encoding='utf-8'))).hexdigest()
                if (contraseña==Usuario_actual.clave):
                    return render_template('Bienvenido.html', nombre=Usuario_actual.nombre)
                else:
                    return render_template('Error.html', error="Contraseña incorrecta")
    else:
        return render_template('Ingreso.html')

@app.route('/Bienvenido')
def Bienvenido():
    return render_template("Bienvenido.html")

if __name__=="__main__":
    db.create_all()
    app.run()
    