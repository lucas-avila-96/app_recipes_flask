
import hashlib 
from datetime import datetime
from flask import Flask
from flask import render_template, request, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import false

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Usuario, Receta, Ingrediente


@app.route('/', methods=['POST','GET'])
def home():
    if request.method == 'POST':
        if not request.form['email'] or not request.form['password']:
            return render_template('message.html', message="Por favor ingrese los datos requeridos")
        else:
            usuario_actual = Usuario.query.filter_by(correo=request.form['email']).first()
            if usuario_actual is None:
                return render_template('message.html', message="El correo no está registrado")
            else:
                clave = hashlib.md5(bytes(request.form['password'], encoding='utf-8'))
                if usuario_actual.clave == clave.hexdigest():
                    return render_template('home.html', usuario = usuario_actual)
                else:
                    return render_template('message.html', message="La contraseña no es válida")
    else:
        return render_template('home.html', usuario = None)
    

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        if not request.form['nombre'] or not request.form['email']:
            return render_template('message.html', message="Los datos ingresados no son correctos...")
        else:
            correo = request.form['email']
            pw = correo[:correo.find('@')]
            nuevo_usuario = Usuario(
            nombre=request.form['nombre'], correo=request.form['email'], clave=pw)
            db.session.add(nuevo_usuario)
            db.session.commit()
            return render_template('message.html', message="El usuario se registró exitosamente")
    return render_template('registration.html')

@app.route('/view_recipe/<receta_id>')
def view_recipe(receta_id):
    select_recipe = Receta.query.filter_by(id = receta_id).first()
    return render_template('view_recipe.html', receta = select_recipe)

@app.route('/ranking')
def ranking():
    recetas = Receta.query.all()
    band = True
    while band:
        band = False
        for i in range(len(recetas) - 1):
            if recetas[i].cantidadmegusta < recetas[i + 1].cantidadmegusta:
                recetas[i], recetas[i + 1] = recetas[i + 1], recetas[i]
                band = True
        top5 = recetas[0:5]
    return render_template('ranking.html', recetas = top5)

@app.route('/save_recipe')
def save_recipe():
    return render_template('message', message='La receta se registro correctamente')

@app.route('/consult_recipe_ingredient', methods = ['GET', 'POST'])
def consult_recipe_ingredient():
    if request.method == 'POST':
        if request.form['nombre']:
            ing_actual = Ingrediente.query.filter_by(nombre = request.form['nombre']).first()
            if ing_actual is None:
                return render_template('message.html', message="El ingrediente no se encontro")
            else:
                recetas = Receta.query.all()
                lista_recetas = []
                for receta in recetas:
                    band = True
                    i = 0
                    ingredientes = receta.ingrediente
                    while band and i < len(ingredientes):
                        if ingredientes[i].nombre == ing_actual.nombre:
                            lista_recetas.append(receta)
                            band = False
                        else:
                            i+=1
                return render_template('show_recipes.html', lista = lista_recetas)
        else:
            return render_template('message.html', message="Por favor ingrese los datos requeridos")
    return render_template('consult_recipe_ingredient.html')


@app.route('/consult_recipe_time', methods = ['GET', 'POST'])
def consult_recipe_time():
    if request.method == 'POST':
        if request.form['tiempo']:
            tiempo = int(request.form['tiempo'])
            recetas = Receta.query.all()
            lista_recetas = [receta for receta in recetas if receta.tiempo < tiempo]
            if len(lista_recetas) == 0:
                return render_template('message.html', message="No se encontraron recetas")
            else:
                return render_template('show_recipes.html', lista = lista_recetas)
        else:
            return render_template('message.html', message="Por favor ingrese los datos requeridos")
    return render_template('consult_recipe_time.html')

@app.route('/share_recipe/<userid>', methods = ['GET', 'POST'])
def share_recipe(userid):
    if request.method == 'POST':
        if  not request.form['nombre'] or not request.form['tiempo'] or not request.form['elaboracion']:
                return render_template('message.html', message="Por favor ingrese los datos requeridos")
        else:
            nueva_receta = Receta(nombre= request.form['nombre'], tiempo=request.form['tiempo'], elaboracion = request.form['elaboracion'], cantidadmegusta = 0, fecha=datetime.now(), usuarioid = userid)
            db.session.add(nueva_receta)
            db.session.commit()
            return render_template('share_recipe.html', receta = nueva_receta)
    return render_template('share_recipe.html', receta = None, i=0)

@app.route("/like/<nombre>")
def like(nombre):
    receta = Receta.query.get(nombre)
    receta.cantidadmegusta += 1
    db.session.commit()
    return render_template('view_recipe.html')
'''
@app.route("/unlike/<int:receta_id>")
def unlike(receta_id):
    receta = Receta.query.get(receta_id)
    current_user.unlike(receta)
    db.session.commit()
    return redirect(url_for('posts.post', receta_id=receta.id)) 

'''

@app.route('/add_ingredient/<recetaid>/<i>', methods = ['GET', 'POST'])
def add_ingredient(recetaid, i):
    if request.method == 'POST':
        if not request.form['nombre'] or not request.form['unidad'] or not request.form['cantidad']:
            return render_template('message.html', message="Falta completar datos")
        else:
            if i < 10:
                nuevo_ingrediente = Ingrediente(nombre = request.form['nombre'],cantidad = request.form['cantidad'], unidad= request.form['unidad'], recetaid = recetaid)    
                db.session.add(nuevo_ingrediente)
                db.session.commit()
                i+=1
                return render_template('share_recipe.html', i = i)
            else:
                return render_template('share_recipe.html', message='Alcanzaste el maximo de ingredientes')
    else: render_template('share_recipe.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
