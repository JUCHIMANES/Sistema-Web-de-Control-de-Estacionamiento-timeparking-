import re
from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db
from . import auth
from .utils import mexico_tz

bp = Blueprint('management', __name__, url_prefix='/management')

@bp.route('/make-reservation', methods=['POST'])
@auth.login_required
def make_reservation():
    db = get_db()
    user_id = g.user['id']
    status = "reserved"

    space_id = int(request.form['space_id'])
    reservation_datetime_str = request.form['reservation_datetime']

    reservation_naive = datetime.strptime(reservation_datetime_str, "%Y-%m-%dT%H:%M")
    reservation_local = mexico_tz.localize(reservation_naive)
    reservation_timestamp = int(reservation_local.timestamp())

    day_start = reservation_local.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = reservation_local.replace(hour=23, minute=59, second=59, microsecond=0)
    day_start_ts = int(day_start.timestamp())
    day_end_ts = int(day_end.timestamp())

    conflict = db.execute(
        '''
        SELECT * FROM reservation
        WHERE space_id = ? AND reservation_datetime BETWEEN ? AND ?
        ''',
        (space_id, day_start_ts, day_end_ts)
    ).fetchone()

    print("Conflict found:", conflict)
    if conflict:
        flash("Ese espacio ya fue reservado.", "error")
        return redirect(url_for("main.reserve"))

    code = f"{user_id}-{reservation_timestamp}"

    try:
        current_price = db.execute(
            'SELECT price FROM price WHERE id = 1'
        ).fetchone()["price"]

        db.execute(
            '''
            INSERT INTO reservation (user_id, space_id, status, reservation_datetime, code, cost)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (user_id, space_id, status, reservation_timestamp, code, current_price)
        )
        db.commit()
        flash("Reservación creada correctamente", "success")
    except Exception as e:
        print("Error:", e)
        flash("Error al crear la reservación", "error")
        return redirect(url_for("main.reserve"))

    return redirect(url_for("main.home"))


@bp.route('/cancel-reservation')
@auth.login_required
def cancel_reservation():
    db = get_db()
    user_id = g.user['id']
    try:
        reservation = db.execute(
        'SELECT * FROM reservation WHERE user_id = ?  AND status = "waiting"', (user_id,)
        ).fetchone()
        current_price = db.execute(
            'SELECT * FROM price WHERE id = 1'
        ).fetchone()["price"]
        db.execute(
                'UPDATE reservation SET status = ?, cost = ? WHERE id = ?',
                ("canceled",current_price, reservation["id"])
            )
        db.execute(
            'INSERT INTO message (message, readed) VALUES (?, ?)',
            (f"El usuario {user_id} ha cancelado la reservación con código {reservation['code']}", 0)
        )

        db.commit()
    except Exception as e:
        print("Ocurrió un error:", e)
        flash("Error al cancelar la reservación", "error")
        return redirect(url_for("main.home"))
    
    flash("Reservación cancelada correctamente", "success")
    return redirect(url_for("main.home"))

@bp.route("/payment-confirmation", methods=["POST"])
@auth.login_required
def payment_confirmation():
    db = get_db()
    card_number = request.form.get("card_number", "").replace(" ", "")
    card_holder = request.form.get("card_holder", "").strip()
    expiry_date = request.form.get("expiry_date", "").strip()
    cvv = request.form.get("cvv", "").strip()
    error = None

    if not re.fullmatch(r"\d{16}", card_number):
        error = "El número de tarjeta debe tener 16 dígitos."

    if not card_holder:
        error = "El nombre del titular es obligatorio."

    if not re.fullmatch(r"(0[1-9]|1[0-2])\/\d{2}", expiry_date):
        error = "La fecha de expiración debe tener el formato MM/AA."

    if not re.fullmatch(r"\d{3,4}", cvv):
        error = "El CVV debe tener 3 o 4 dígitos."
    
    if error:
        flash(error, "error")
        return redirect(url_for("main.home"))

    user_id = g.user['id']
    reservation_code = request.form.get("reservation_code")

    try:
        status = ""
        reservation = db.execute(
            'SELECT * FROM reservation WHERE user_id = ? AND code = ?',
            (user_id, reservation_code)
        ).fetchone()

        if reservation["status"] == "canceled":
            status = "canceled-payment"
        elif reservation["status"] == "reserved":
            status = "waiting"
        elif reservation["status"] == "waiting":
            status = "confirm-payment"
            
        db.execute(
            'UPDATE reservation SET status = ? WHERE user_id = ? AND code = ?',
            (status, user_id, reservation_code)
        )
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        message = f"El usuario {user['name']} ha confirmado el pago de la reservación con código {reservation_code}."
        db.execute(
            'INSERT INTO message (message, readed) VALUES (?, ?)',
            (message, 0)
        )

        db.commit()
        flash("Pago confirmado correctamente.", "success")
    except:
        flash("Error al confirmar el pago.", "error")

    return redirect(url_for("main.home"))

