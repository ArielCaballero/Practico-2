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
                        
                        return render_template("Ingresar_Ingrediente.html", nombre_receta=request.form['nombre'], tiempo=request.form['tiempo'], descripcion=request.form['descripcion'], usuario_actual=session, ingredientes="", cantidadingredientes=0)
        else:
            return render_template("Ingresar_Receta.html", usuario_actual=session)
    else:
        return render_template('index.html') #El caso base lo redirecciona al Ingreso.html

@app.route('/Registrar_Ingrediente', methods=['GET', 'POST'])
def Registrar_Ingredientes():
    if 'nombre' in session:   
        if request.method=='POST':
            if not request.form['nombre']:
                return render_template("Error_Ingrediente.html", error="Debe ingresar nombre del Ingrediente.", usuario_actual=session)
            else: 
                if not request.form['cantidad']:
                    return render_template("Error_Ingrediente.html", error="Debe ingresar la cantidad del ingrediente", usuario_actual=session)
                else:
                    if not request.form['unidad']:
                        return render_template("Error_Ingrediente.html", error="Debe ingresar la unidad de medida.", usuario_actual=session)
                    else:
                        if (request.form['ingredientes']):
                            ingredientes=request.form['ingredientes']+";"+request.form['nombre']+"/"+request.form['cantidad']+"/"+request.form['unidad']
                        else:
                            ingredientes=request.form['nombre']+"/"+request.form['cantidad']+"/"+request.form['unidad']
                        return render_template("Ingresar_Ingrediente.html", nombre_receta=request.form['nombre_receta'], tiempo=request.form['tiempo'], descripcion=request.form['descripcion'], usuario_actual=session, ingredientes=ingredientes, cantidadingredientes=int(request.form['cantidadingredientes'])+1)
        else:
            return render_template("Ingresar_Ingrediente.html", usuario_actual=session)
    else:
        return render_template('index.html') #El caso base lo redirecciona al Ingreso.html

@app.route('/Guardar_Receta', methods=['GET', 'POST'])
def Guardar_Receta():
    if 'nombre' in session:
        if request.form['nombre_receta'] and request.form['ingredientes']:
            nueva_receta=Receta(nombre=request.form['nombre_receta'], tiempo=request.form['tiempo'], fecha=datetime.now(), elaboracion=request.form['descripcion'], cantidadmegusta=0, usuarioid=session['id'])
            db.session.add(nueva_receta)
            ingredientes=request.form['ingredientes'].split(";")
            for ingrediente in ingredientes:
                elementos=ingrediente.split("/")
                nuevo_ingrediente=Ingrediente(nombre=elementos[0], cantidad=elementos[1], unidad=elementos[2], recetaid=Receta.query.filter_by(fecha=nueva_receta.fecha).first().id)
                db.session.add(nuevo_ingrediente)
            db.session.commit()
            return redirect(url_for('ingreso'))
        else:
            return render_template("Error_Ingrediente.html",error="Error en guardado de receta",nombre_receta=request.form['nombre_receta'], tiempo=request.form['tiempo'], descripcion=request.form['descripcion'], usuario_actual=session, ingredientes=request.form['ingredientes'])
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
        return render_template('Ranking.html', tipo_busqueda="Recetas con mas 'me gusta'",usuario_actual=session, recetas=recetasamostrar, usuarios=Usuario.query.all())
    else:
        return render_template('index.html')

@app.route('/Recetas_por_tiempo', methods=['GET', 'POST'])
def Recetas_por_tiempo():
    if 'nombre' in session:
        if request.method=="POST":
            recetasordenadas=Receta.query.all()
            recetasamostrar=[]
            tiempo=request.form['tiempo']
            for receta in recetasordenadas:
                if receta.tiempo<int(tiempo):
                    recetasamostrar.append(receta)
            return render_template('Listado.html', tipo_busqueda="Recetas por tiempo menor a {} minutos".format(tiempo),usuario_actual=session, recetas=recetasamostrar, usuarios=Usuario.query.all(), ingredientes=Ingrediente.query.all()) #Redirecciona al usuario al template de Bienvenido.html
    else:
        return render_template('index.html') 

@app.route('/Recetas_por_ingrediente', methods=['GET', 'POST'])
def Recetas_por_ingrediente():
    if 'nombre' in session:
        if request.method=="POST":
            recetasordenadas=Ingrediente.query.all()
            recetasamostrar=[]
            ingredienterecibido=request.form['ingrediente']
            for ingrediente in recetasordenadas:
                if ingredienterecibido.lower() in ingrediente.nombre.lower():
                    receta=Receta.query.filter_by(id=ingrediente.recetaid).first()

                    recetasamostrar.append(receta)
            return render_template('Listado.html', tipo_busqueda="Recetas por ingrediente: '{}'".format(ingredienterecibido), usuario_actual=session, recetas=recetasamostrar, usuarios=Usuario.query.all(), ingredientes=Ingrediente.query.all()) #Redirecciona al usuario al template de Bienvenido.html
    else:
        return render_template('index.html')

@app.route('/megusta', methods=['GET', 'POST'])
def megusta():
    if 'nombre' in session:
        if request.method=="POST":
            if request.form['recetaid']:
                if Receta.query.get(request.form['recetaid']).usuarioid != session['id']:
                    Receta.query.get(request.form['recetaid']).cantidadmegusta+=1
                    db.session.commit()
            return redirect(url_for('ingreso'))
    else:
        return render_template('index.html') #El caso base lo redirecciona al Ingreso.html

if __name__=="__main__":
    db.create_all()
    app.run(debug = True)
    