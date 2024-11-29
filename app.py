from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime

# Inicializar Flask, Bcrypt y LoginManager
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Configuración de MongoDB
app.config["MONGO_URI"] = "mongodb+srv://kevincj2415:e2BhakVv76vBMD7f@cluster0.hb2dv.mongodb.net/torneosDB?retryWrites=true&w=majority"
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Definir la vista de login

# Cargar el usuario desde MongoDB
@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user['_id']), user['email'], user['password'])
    return None

# Definir el modelo de usuario (sin necesidad de UserMixin)
class User:
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

# Formulario de Registro de Usuario
class RegistrationForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Registrar')


# Formulario de Inicio de Sesión
class LoginForm(FlaskForm):
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar si el correo ya está registrado
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user:
            flash("El correo ya está registrado. Intenta iniciar sesión.", "error")
            return redirect(url_for('login'))
        
        # Encriptar la contraseña
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Crear un nuevo usuario
        user_data = {
            "email": form.email.data,
            "password": hashed_password
        }
        user_id = mongo.db.users.insert_one(user_data).inserted_id
        new_user = User(str(user_id), form.email.data, hashed_password)
        login_user(new_user)  # Iniciar sesión automáticamente después del registro
        flash("¡Te has registrado con éxito!", "success")
        return redirect(url_for('home'))  # Redirige a la página de inicio

    return render_template('register.html', form=form)  # Muestra el formulario


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            logged_user = User(str(user['_id']), user['email'], user['password'])
            login_user(logged_user)  # Inicia sesión al usuario
            flash("Bienvenido de nuevo, ¡has iniciado sesión exitosamente!", "success")
            return redirect(url_for('home'))  # Redirige al usuario al inicio
        else:
            flash("Correo o contraseña incorrectos", "error")  # Error en las credenciales
    
    return render_template('login.html', form=form)  # Muestra el formulario


@app.route('/logout')
@login_required  # Asegura que solo los usuarios autenticados puedan cerrar sesión
def logout():
    logout_user()  # Cierra la sesión del usuario
    flash("Has cerrado sesión exitosamente.", "info")
    return redirect(url_for('login'))  # Redirige al inicio de sesión





# Ruta de inicio
@app.route('/')
def home():
    # Obtener torneos y partidos de la base de datos
    tournaments = mongo.db.tournaments.find()  # Obtener todos los torneos
    matches = mongo.db.matches.find()  # Obtener todos los partidos

    # Convertir los resultados en listas (puedes filtrarlos o limitarlos si lo deseas)
    tournaments_list = list(tournaments)
    matches_list = list(matches)

    return render_template('home.html', tournaments=tournaments_list, matches=matches_list)


# Ruta para ver los torneos disponibles
@app.route('/torneos')
def view_tournaments():
    # Obtener todos los torneos desde la base de datos
    all_tournaments = list(mongo.db.tournaments.find())
    return render_template('tournaments.html', tournaments=all_tournaments)

# Ruta para crear un nuevo torneo
@app.route('/crear_torneo', methods=['GET', 'POST'])
def create_tournament():
    if request.method == 'POST':
        # Datos del torneo desde el formulario
        data = {
            "nombre": request.form['nombre'],
            "formato": request.form['formato'],
            "fecha_inicio": request.form['fecha_inicio'],
            "fecha_fin": request.form['fecha_fin'],
            "equipos": []  # Inicialmente no hay equipos
        }
        # Insertar el torneo en la base de datos
        mongo.db.tournaments.insert_one(data)
        flash("Torneo creado con éxito", "success")
        return redirect(url_for('view_tournaments'))
    return render_template('create_tournament.html')

# Ruta para ver los detalles de un torneo
@app.route('/torneo/<id>')
def tournament_details(id):
    tournament = mongo.db.tournaments.find_one({"_id": ObjectId(id)})
    if not tournament:
        flash("Torneo no encontrado", "error")
        return redirect(url_for('view_tournaments'))

    return render_template('tournament_details.html', tournament=tournament)

# Ruta para editar un torneo
@app.route('/editar_torneo/<id>', methods=['GET', 'POST'])
def edit_tournament(id):
    tournament = mongo.db.tournaments.find_one({"_id": ObjectId(id)})
    if not tournament:
        flash("Torneo no encontrado", "error")
        return redirect(url_for('view_tournaments'))

    if request.method == 'POST':
        # Actualizar los datos del torneo
        updated_data = {
            "nombre": request.form['nombre'],
            "formato": request.form['formato'],
            "fecha_inicio": request.form['fecha_inicio'],
            "fecha_fin": request.form['fecha_fin']
        }
        mongo.db.tournaments.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        flash("Torneo actualizado con éxito", "success")
        return redirect(url_for('view_tournaments'))
    
    return render_template('edit_tournament.html', tournament=tournament)

# Ruta para eliminar un torneo
@app.route('/eliminar_torneo/<id>', methods=['POST'])
def delete_tournament(id):
    tournament = mongo.db.tournaments.find_one({"_id": ObjectId(id)})
    if not tournament:
        flash("Torneo no encontrado", "error")
        return redirect(url_for('view_tournaments'))

    mongo.db.tournaments.delete_one({"_id": ObjectId(id)})
    flash("Torneo eliminado con éxito", "success")
    return redirect(url_for('view_tournaments'))


# Ruta para registrar un nuevo equipo
@app.route('/registrar_equipo', methods=['GET', 'POST'])
def register_team():
    if request.method == 'POST':
        # Datos del equipo desde el formulario
        data = {
            "nombre": request.form['nombre'],
            "jugadores": []  # Inicialmente no hay jugadores
        }
        # Insertar el equipo en la base de datos
        mongo.db.teams.insert_one(data)
        flash("Equipo registrado con éxito", "success")
        return redirect(url_for('view_teams'))
    return render_template('register_team.html')


# Ruta para ver los equipos registrados
@app.route('/equipos')
def view_teams():
    # Obtener todos los equipos desde la base de datos
    all_teams = list(mongo.db.teams.find())
    return render_template('teams.html', teams=all_teams)


# Ruta para ver los detalles de un equipo
@app.route('/equipo/<id>')
def team_details(id):
    team = mongo.db.teams.find_one({"_id": ObjectId(id)})
    if not team:
        flash("Equipo no encontrado", "error")
        return redirect(url_for('view_teams'))

    return render_template('team_details.html', team=team)


# Ruta para editar un equipo
@app.route('/editar_equipo/<id>', methods=['GET', 'POST'])
def edit_team(id):
    team = mongo.db.teams.find_one({"_id": ObjectId(id)})
    if not team:
        flash("Equipo no encontrado", "error")
        return redirect(url_for('view_teams'))

    if request.method == 'POST':
        # Validaciones
        nombre = request.form['nombre']
        jugadores = request.form['jugadores'].split(',')  # Convertimos la lista de jugadores

        if not nombre or not jugadores:
            flash("El nombre del equipo y los jugadores son obligatorios.", "error")
            return redirect(url_for('edit_team', id=id))

        # Actualizar los datos del equipo
        updated_data = {
            "nombre": nombre,
            "jugadores": [{"nombre": jugador.strip()} for jugador in jugadores]  # Limpiar espacios y agregar jugadores
        }
        mongo.db.teams.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        flash("Equipo actualizado con éxito", "success")
        return redirect(url_for('view_teams'))

    return render_template('edit_team.html', team=team)



# Ruta para eliminar un equipo
@app.route('/eliminar_equipo/<id>', methods=['POST'])
def delete_team(id):
    team = mongo.db.teams.find_one({"_id": ObjectId(id)})
    if not team:
        flash("Equipo no encontrado", "error")
        return redirect(url_for('view_teams'))

    mongo.db.teams.delete_one({"_id": ObjectId(id)})
    flash("Equipo eliminado con éxito", "success")
    return redirect(url_for('view_teams'))


# Ruta para agregar un jugador a un equipo
@app.route('/equipo/<id>/agregar_jugador', methods=['GET', 'POST'])
def add_player(id):
    team = mongo.db.teams.find_one({"_id": ObjectId(id)})
    if not team:
        flash("Equipo no encontrado", "error")
        return redirect(url_for('view_teams'))

    if request.method == 'POST':
        # Datos del jugador desde el formulario
        jugador_data = {
            "nombre": request.form['nombre'],
            "edad": request.form['edad'],
            "posicion": request.form['posicion']
        }

        # Añadir el jugador al equipo
        mongo.db.teams.update_one(
            {"_id": ObjectId(id)}, 
            {"$push": {"jugadores": jugador_data}}
        )
        flash("Jugador agregado con éxito", "success")
        return redirect(url_for('team_details', id=id))

    return render_template('add_player.html', team=team)


# Ruta para editar un jugador dentro de un equipo
@app.route('/equipo/<team_id>/editar_jugador/<player_id>', methods=['GET', 'POST'])
def edit_player(team_id, player_id):
    team = mongo.db.teams.find_one({"_id": ObjectId(team_id)})
    if not team:
        flash("Equipo no encontrado", "error")
        return redirect(url_for('view_teams'))

    # Buscar al jugador en la lista de jugadores
    player = next((p for p in team['jugadores'] if str(p['_id']) == player_id), None)
    if not player:
        flash("Jugador no encontrado", "error")
        return redirect(url_for('team_details', id=team_id))

    if request.method == 'POST':
        # Actualizar datos del jugador
        updated_player = {
            "nombre": request.form['nombre'],
            "edad": request.form['edad'],
            "posicion": request.form['posicion']
        }

        # Actualizar jugador en el equipo
        mongo.db.teams.update_one(
            {"_id": ObjectId(team_id), "jugadores._id": ObjectId(player_id)},
            {"$set": {"jugadores.$": updated_player}}
        )
        flash("Jugador actualizado con éxito", "success")
        return redirect(url_for('team_details', id=team_id))

    return render_template('edit_player.html', team=team, player=player)


# Ruta para eliminar un jugador de un equipo
@app.route('/equipo/<team_id>/eliminar_jugador/<player_id>', methods=['POST'])
def delete_player(team_id, player_id):
    team = mongo.db.teams.find_one({"_id": ObjectId(team_id)})
    if not team:
        flash("Equipo no encontrado", "error")
        return redirect(url_for('view_teams'))

    # Eliminar el jugador del equipo
    mongo.db.teams.update_one(
        {"_id": ObjectId(team_id)},
        {"$pull": {"jugadores": {"_id": ObjectId(player_id)}}}
    )
    flash("Jugador eliminado con éxito", "success")
    return redirect(url_for('team_details', id=team_id))


# Ruta para crear un nuevo partido
@app.route('/crear_partido', methods=['GET', 'POST'])
def create_match():
    if request.method == 'POST':
        # Obtener datos del formulario
        equipo_local = request.form['equipo_local']
        equipo_visitante = request.form['equipo_visitante']
        fecha = request.form['fecha']
        
        # Crear un nuevo partido en la base de datos
        match_data = {
            "equipo_local": equipo_local,
            "equipo_visitante": equipo_visitante,
            "fecha": fecha,
            "resultado": {"equipo_local": None, "equipo_visitante": None}
        }
        mongo.db.matches.insert_one(match_data)
        flash("Partido creado con éxito", "success")
        return redirect(url_for('view_matches'))

    return render_template('create_match.html')


# Ruta para ver los partidos registrados
@app.route('/partidos')
def view_matches():
    # Obtener todos los partidos desde la base de datos
    all_matches = list(mongo.db.matches.find())
    return render_template('matches.html', matches=all_matches)


# Ruta para ver los detalles de un partido
@app.route('/partido/<id>')
def match_details(id):
    match = mongo.db.matches.find_one({"_id": ObjectId(id)})
    if not match:
        flash("Partido no encontrado", "error")
        return redirect(url_for('view_matches'))

    return render_template('match_details.html', match=match)


# Ruta para editar el resultado de un partido
@app.route('/editar_resultado_partido/<id>', methods=['GET', 'POST'])
def edit_match_result(id):
    match = mongo.db.matches.find_one({"_id": ObjectId(id)})
    if not match:
        flash("Partido no encontrado", "error")
        return redirect(url_for('view_matches'))

    if request.method == 'POST':
        # Obtener el resultado desde el formulario
        resultado_local = request.form['resultado_local']
        resultado_visitante = request.form['resultado_visitante']
        
        # Actualizar el resultado del partido
        mongo.db.matches.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"resultado": {"equipo_local": resultado_local, "equipo_visitante": resultado_visitante}}}
        )
        flash("Resultado actualizado con éxito", "success")
        return redirect(url_for('match_details', id=id))

    return render_template('edit_match_result.html', match=match)


# Ruta para eliminar un partido
@app.route('/eliminar_partido/<id>', methods=['POST'])
def delete_match(id):
    match = mongo.db.matches.find_one({"_id": ObjectId(id)})
    if not match:
        flash("Partido no encontrado", "error")
        return redirect(url_for('view_matches'))

    mongo.db.matches.delete_one({"_id": ObjectId(id)})
    flash("Partido eliminado con éxito", "success")
    return redirect(url_for('view_matches'))


@app.route('/crear_notificacion', methods=['GET', 'POST'])
@login_required
def create_notification():
    if request.method == 'POST':
        # Obtener los datos de la notificación desde el formulario
        title = request.form['title']
        message = request.form['message']
        recipient = request.form['recipient']  # El destinatario puede ser un usuario o un grupo
        
        # Crear la notificación en la base de datos (por ejemplo, en la colección "notifications")
        notification = {
            "title": title,
            "message": message,
            "recipient": recipient,
            "read": False,  # Asumimos que la notificación no ha sido leída
            "date": datetime.now()
        }
        mongo.db.notifications.insert_one(notification)
        flash("Notificación creada con éxito.", "success")
        return redirect(url_for('view_notifications'))

    return render_template('create_notification.html')


@app.route('/notificaciones')
@login_required
def view_notifications():
    # Obtener las notificaciones del usuario actual desde la base de datos
    user_notifications = mongo.db.notifications.find({"recipient": current_user.email})
    
    return render_template('view_notifications.html', notifications=user_notifications)


@app.route('/notificacion/<id>/marcar_como_leida', methods=['POST'])
@login_required
def mark_notification_as_read(id):
    # Actualizar la notificación en la base de datos
    mongo.db.notifications.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"read": True}}
    )
    flash("Notificación marcada como leída.", "success")
    return redirect(url_for('view_notifications'))


@app.route('/notificacion/<id>/eliminar', methods=['POST'])
@login_required
def delete_notification(id):
    # Eliminar la notificación de la base de datos
    mongo.db.notifications.delete_one({"_id": ObjectId(id)})
    flash("Notificación eliminada con éxito.", "success")
    return redirect(url_for('view_notifications'))


@app.route('/torneo/<id>/estadisticas')
@login_required
def tournament_stats(id):
    # Obtener los detalles del torneo
    tournament = mongo.db.tournaments.find_one({"_id": ObjectId(id)})
    if not tournament:
        flash("Torneo no encontrado", "error")
        return redirect(url_for('view_tournaments'))

    # Obtener los partidos relacionados con el torneo
    matches = mongo.db.matches.find({"tournament_id": ObjectId(id)})

    # Calcular estadísticas del torneo
    total_matches = 0
    total_goals_local = 0
    total_goals_visitor = 0
    teams_stats = {}

    for match in matches:
        total_matches += 1
        total_goals_local += match['resultado']['equipo_local'] if match['resultado']['equipo_local'] else 0
        total_goals_visitor += match['resultado']['equipo_visitante'] if match['resultado']['equipo_visitante'] else 0
        
        # Actualizar estadísticas por equipo
        local_team = match['equipo_local']
        visitor_team = match['equipo_visitante']

        if local_team not in teams_stats:
            teams_stats[local_team] = {"matches": 0, "goals": 0}
        if visitor_team not in teams_stats:
            teams_stats[visitor_team] = {"matches": 0, "goals": 0}

        teams_stats[local_team]["matches"] += 1
        teams_stats[local_team]["goals"] += match['resultado']['equipo_local'] if match['resultado']['equipo_local'] else 0

        teams_stats[visitor_team]["matches"] += 1
        teams_stats[visitor_team]["goals"] += match['resultado']['equipo_visitante'] if match['resultado']['equipo_visitante'] else 0

    # Calcular estadísticas adicionales
    average_goals_per_match = total_goals_local + total_goals_visitor / total_matches if total_matches else 0

    return render_template('tournament_stats.html', tournament=tournament, 
                           total_matches=total_matches, total_goals_local=total_goals_local,
                           total_goals_visitor=total_goals_visitor, teams_stats=teams_stats,
                           average_goals_per_match=average_goals_per_match)




# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
