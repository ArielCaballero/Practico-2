from datetime import datetime
from string import hexdigits
from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
import hashlib


app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db, Usuario, Ingrediente, Receta

@app.route('/')
def Inicio():
    session.clear()
    return render_template("index.html")

@app.route('/Bienvenido', methods=['GET', 'POST'])
def ingreso():
    if request.method == 'POST':

        if not request.form['email'] or not request.form['password']: #Evalua si el usuario en si no ingreso nada
            return render_template('index.html')

        else:
            Usuario_actual= Usuario.query.filter_by(correo=request.form['email']).first() #Crea la variable Usuario_actual y le asigna el email ingresado en el form

            if Usuario_actual is None: #Comprueba si esta vacio
                return render_template('Error.html', error="Email no Registrado")
            else:
                password=(hashlib.md5(bytes(request.form['password'], encoding='utf-8'))).hexdigest() #Encripta la Password
                if (password==Usuario_actual.clave): #Compara el password ya hasheado con el de la base de datos
                    session['nombre']=Usuario_actual.nombre
                    session['id']=Usuario_actual.id
                    recetasrecientes=Receta.query.all()
                    recetasrecientes.reverse()
                    return render_template('Bienvenido.html', tipo_busqueda="Recetas Recientes", usuario_actual=Usuario_actual, recetas=recetasrecientes, usuarios=Usuario.query.all(), ingredientes=Ingrediente.query.all()) #Redirecciona al usuario al template de Bienvenido.html
                else:
                    return render_template('Error.html', error="Contraseña incorrecta")
    else:
        if ('nombre' in session):
            recetasrecientes=Receta.query.all()
            recetasrecientes.reverse()
            return render_template('Bienvenido.html', tipo_busqueda="Recetas Recientes", usuario_actual=session, recetas=recetasrecientes, usuarios=Usuario.query.all(), ingredientes=Ingrediente.query.all()) #Redirecciona al usuario al template de Bienvenido.html
        else:
            return render_template('index.html', error = 'User or Password wrong') #El caso base lo redirecciona al Ingreso.html


@app.route('/Registrar_Receta', methods=['GET', 'POST'])
def Registrar_Receta():
    if 'nombre' in session:   
        if request.method=='POST':
            if not request.form['nombre']:
                return render_template("Error_Receta.html", error="Debe ingresar nombre de la receta.", usuario_actual=session)
            else: 
                if not request.form['tiempo']:
                    return render_template("Error_Receta.html", error="Debe ingresar el tiempo de la receta.", usuario_actual=session)
                else:
                    if not request.form['descripcion']:
                        return render_template("Error_Receta.html", error="Debe ingresar la elaboración de la receta.", usuario_actual=session)
                    else:
                        nueva_receta=Receta(nombre=request.form['nombre'], tiempo=request.form['tiempo'], fecha=datetime.now(), elaboracion=request.form['descripcion'], cantidadmegusta=0, usuarioid=session['id'])
                        db.session.add(nueva_receta)
                        db.session.commit()
                        return render_template("Ingresar_Ingrediente.html", id=nueva_receta.id, usuario_actual=session)
        else:
            return render_template("Ingresar_Receta.html", usuario_actual=session)
    else:
        return render_template('index.html') #El caso base lo redirecciona al Ingreso.html

@app.route('/Registrar_Ingrediente', methods=['GET', 'POST'])
def Registrar_Ingredientes():
    if 'nombre' in session:   
        if request.method=='POST':
            if not request.form['nombre']:
                return render_template("Error_Ingrediente.html", error="Debe ingresar nombre de la receta.", usuario_actual=session)
            else: 
                if not request.form['cantidad']:
                    return render_template("Error_Ingrediente.html", error="Debe ingresar el tiempo de la receta.", usuario_actual=session)
                else:
                    if not request.form['unidad']:
                        return render_template("Error_Ingrediente.html", error="Debe ingresar la elaboración de la receta.", usuario_actual=session)
                    else:
                        nuevo_ingrediente=Ingrediente(nombre=request.form['nombre'], cantidad=request.form['cantidad'], unidad=request.form['unidad'], recetaid=request.form['id'])
                        db.session.add(nuevo_ingrediente)
                        db.session.commit()
                        return render_template("Ingresar_Ingrediente.html", id=request.form['id'], usuario_actual=session)
        else:
            return render_template("Ingresar_Ingrediente.html", usuario_actual=session)
    else:
        return render_template('index.html') #El caso base lo redirecciona al Ingreso.html

@app.route('/Consultar_Ranking', methods=['GET', 'POST'])
def Consultar_Ranking():
    if 'nombre' in session:
        recetasordenadas=Receta.query.all()
        recetasordenadas.sort(reverse=True)
        i=0
        recetasamostrar=[]
        while i<5 and i<len(recetasordenadas):
            recetasamostrar.append(recetasordenadas[i])
            i+=1
        print (recetasamostrar)
        return render_template('Bienvenido.html', tipo_busqueda="Recetas con mas 'me gusta'",usuario_actual=session, recetas=recetasamostrar, usuarios=Usuario.query.all(), ingredientes=Ingrediente.query.all()) #Redirecciona al usuario al template de Bienvenido.html
    else:
        return render_template('index.html') #El caso base lo redirecciona al Ingreso.html

@app.route('/Recetas_por_tiempo', methods=['GET', 'POST'])
def Recetas_por_tiempo():
    if 'nombre' in session:
        recetasordenadas=Receta.query.all()
        recetasamostrar=[]
        tiempo=request.form['tiempo']
        for receta in recetasordenadas:
            if receta.tiempo<int(tiempo):
                recetasamostrar.append(receta)
        return render_template('Bienvenido.html', usuario_actual=session, recetas=recetasamostrar, usuarios=Usuario.query.all(), ingredientes=Ingrediente.query.all()) #Redirecciona al usuario al template de Bienvenido.html
    else:
        return render_template('index.html') #El caso base lo redirecciona al Ingreso.html



if __name__=="__main__":
    db.create_all()
    app.run(debug = True)
    