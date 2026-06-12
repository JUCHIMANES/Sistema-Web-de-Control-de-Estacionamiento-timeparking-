from math import ceil
from datetime import datetime
from flask import Blueprint, render_template, g, flash, send_from_directory, redirect, url_for
from flaskr.db import get_db
from . import auth
from .utils import parse_reservation, mexico_tz

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/home")
@auth.login_required
def home():
    db = get_db()
    user_id = g.user['id']
    user_have_reservation = False
    waiting_reservation = None
    cost = 0
    now = datetime.now(mexico_tz)
    timestamp_now = int(now.timestamp())

    try:
        cost = db.execute(
                'SELECT * FROM price WHERE id = 1'
            ).fetchone()["price"]
        waiting_reservation = db.execute(
        'SELECT * FROM reservation WHERE user_id = ?  AND (status = "waiting" OR status = "canceled" OR status = "reserved" OR status = "confirm-payment")', (user_id,)
        ).fetchone()
        user_have_reservation = waiting_reservation is not None

        if user_have_reservation:
            cost = waiting_reservation["cost"]

        if user_have_reservation and waiting_reservation["entry_datetime"] is not None:
            cost = waiting_reservation["cost"]
            rate_per_hour = db.execute(
                'SELECT * FROM price WHERE id = 1'
            ).fetchone()["price"]
            now = int(datetime.now(mexico_tz).timestamp())
            seconds_diff = now - waiting_reservation["entry_datetime"]
            hours_diff = ceil(seconds_diff / 3600)
            cost = max(1, hours_diff) * rate_per_hour
            db.execute(
                'UPDATE reservation SET cost = ? WHERE id = ?',
                (cost, waiting_reservation["id"])
            )
            db.commit()

        if user_have_reservation and waiting_reservation["entry_datetime"] is None:
            if  timestamp_now > waiting_reservation["reservation_datetime"]:
                db.execute(
                    'UPDATE reservation SET status = "canceled" WHERE id = ?',
                    (waiting_reservation["id"],)
                )
                db.commit()
                flash("Tu reservación ha sido cancelada por no haber ingresado a tiempo", "error")
            
    except Exception as e:
        print(e)
        flash("Error al obtener las reservaciones", "error")

    if user_have_reservation:
        waiting_reservation = parse_reservation(waiting_reservation)

    return render_template("home.html", user_have_reservation=user_have_reservation, reservation=waiting_reservation, cost=cost)

@bp.route("/history")
@auth.login_required
def history():
    db = get_db()
    user_id = g.user['id']
    parsed_reservations = []
    try:
        reservations = db.execute(
        'SELECT * FROM reservation WHERE user_id = ?', (user_id,)
        ).fetchall()
        
        for reservation in reservations:
            parsed_reservation = parse_reservation(reservation)
            parsed_reservations.append(parsed_reservation)
    except:
        flash("Error al obtener las reservaciones", "error")

    return render_template("history.html", reservations=parsed_reservations)

@bp.route("/reserve")
@auth.login_required
def reserve():
    db = get_db()
    
    # 1. Obtener IDs de espacios ocupados en ambas tablas
    occupied_app = db.execute(
        'SELECT space_id FROM reservation WHERE status IN ("reserved", "waiting", "confirm-payment") OR (entry_datetime IS NOT NULL AND exit_datetime IS NULL)'
    ).fetchall()
    
    occupied_assisted = db.execute(
        'SELECT space_id FROM assisted_reservation WHERE status = "active"'
    ).fetchall()
    
    occupied_ids = [r['space_id'] for r in occupied_app] + [r['space_id'] for r in occupied_assisted]

    # 2. Consultar solo los espacios que NO están en esa lista
    if occupied_ids:
        placeholders = ','.join(['?'] * len(occupied_ids))
        all_spaces = db.execute(
            f'SELECT * FROM space WHERE id NOT IN ({placeholders})', occupied_ids
        ).fetchall()
    else:
        all_spaces = db.execute('SELECT * FROM space').fetchall()

    try:
        current_price = db.execute('SELECT price FROM price WHERE id = 1').fetchone()["price"]
    except:
        current_price = 0
    
    return render_template("reserve.html", current_price=current_price, all_spaces=all_spaces)

@bp.route('/manifest.json')
def manifest():
    return send_from_directory('..', 'manifest.json')

@bp.route('/sw.js')
def service_worker():
    return send_from_directory('../static', 'sw.js')

def get_available_spaces():
    db = get_db()
    
    # 1. Buscamos IDs de espacios ocupados en reservaciones de usuarios
    # Un espacio está ocupado si el status NO es 'completed', 'canceled' o 'canceled-payment'
    occupied_app = db.execute('''
        SELECT space_id FROM reservation 
        WHERE status NOT IN ('completed', 'canceled', 'canceled-payment')
    ''').fetchall()
    
    # 2. Buscamos IDs de espacios ocupados en registros asistidos (admin)
    occupied_assisted = db.execute('''
        SELECT space_id FROM assisted_reservation 
        WHERE status != 'completed'
    ''').fetchall()
    
    # Unimos todos los IDs ocupados en una lista simple
    occupied_ids = [row['space_id'] for row in occupied_app] + \
                   [row['space_id'] for row in occupied_assisted]
    
    # 3. Traemos todos los espacios que NO estén en esa lista
    if not occupied_ids:
        return db.execute('SELECT * FROM space').fetchall()
    
    # Creamos un string de placeholders (?, ?, ?) para la consulta
    placeholders = ','.join(['?'] * len(occupied_ids))
    query = f'SELECT * FROM space WHERE id NOT IN ({placeholders})'
    
    return db.execute(query, occupied_ids).fetchall()