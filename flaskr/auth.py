import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if not email:
            error = "El correo es requerido"
        elif not password:
            error = "la contraseña es requerida"
        elif not name:
            error = "El nombre es requerido"
        elif not last_name:
            error = "El apellido es requerido"

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (name, last_name, email, password, role) VALUES (?, ?, ?, ?, \"user\")",
                    (name.upper().strip(), last_name.upper().strip(), email.strip(), generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"El correo {email} ya esta registrado"
            else:
                flash("Usuario creado correctamente, ahora inicia sesión", "success")
                return redirect(url_for("auth.login"))

        flash(error, "error")

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None or not check_password_hash(user['password'], password):
            error = "Credenciales incorrectas"

        if error is None:
            session.clear()
            session['user_id'] = user['id']

            if user['role'] == 'admin':
                return redirect(url_for('admin.index'))
            
            elif user['role'] == 'user':
                return redirect(url_for('main.home'))

        flash(error, "error")

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def only_admin(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user['role'] != 'admin':
            return redirect(url_for('main.home'))

        return view(**kwargs)

    return wrapped_view

