from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Bienvenido, {user.nombre} ☕', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('login.html', titulo='Iniciar sesión', tab='login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        nombre      = request.form.get('nombre', '').strip()
        email       = request.form.get('email', '').strip().lower()
        password    = request.form.get('password', '')
        confirm     = request.form.get('confirm_password', '')
        departamento = request.form.get('departamento', '')

        # Validaciones
        if not nombre or not email or not password:
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('login.html', titulo='Crear cuenta', tab='register')

        if password != confirm:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('login.html', titulo='Crear cuenta', tab='register')

        if len(password) < 8:
            flash('La contraseña debe tener mínimo 8 caracteres.', 'danger')
            return render_template('login.html', titulo='Crear cuenta', tab='register')

        if User.query.filter_by(email=email).first():
            flash('Este correo ya está registrado.', 'danger')
            return render_template('login.html', titulo='Crear cuenta', tab='register')

        user = User(nombre=nombre, email=email, departamento=departamento)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Cuenta creada exitosamente. Bienvenido, {nombre} ☕', 'success')
        return redirect(url_for('main.index'))

    return render_template('login.html', titulo='Crear cuenta', tab='register')


@auth_bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = User.query.filter_by(email=email).first()
        # Siempre mostramos éxito por seguridad (no revelar si el email existe)
        flash('Si el correo está registrado, recibirás un enlace de recuperación.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('login.html', titulo='Recuperar contraseña', tab='forgot')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('main.index'))


# Necesario para Flask-Login: cargar el usuario por ID
from extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
