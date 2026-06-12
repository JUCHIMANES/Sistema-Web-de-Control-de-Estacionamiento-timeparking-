from datetime import datetime
import pytz

mexico_tz = pytz.timezone('America/Mexico_City')

def parse_reservation(reservation):
    reservation_datetime = datetime.fromtimestamp(reservation["reservation_datetime"], mexico_tz).strftime("%Y-%m-%d %H:%M:%S")
    entry_datetime = (
        datetime.fromtimestamp(reservation["entry_datetime"], mexico_tz).strftime("%Y-%m-%d %H:%M:%S")
        if reservation["entry_datetime"] else ""
    )

    exit_datetime = (
        datetime.fromtimestamp(reservation["exit_datetime"], mexico_tz).strftime("%Y-%m-%d %H:%M:%S")
        if reservation["exit_datetime"] else ""
    )

    status_mapping = {
        "waiting": "Pendiente",
        "reserved": "Reservada",
        "canceled": "Cancelada",
        "canceled-payment": "Cancelada",
        "completed": "Completada",
        "confirm-payment": "Pagada",
    }
    status = status_mapping.get(reservation["status"], "Desconocida")

    cost = (
        reservation["cost"]
        if reservation["cost"] is not None
        else "No disponible"
    )

    parsed_reservation = {
        "id": reservation["id"],
        "code": reservation["code"],
        "status": status,
        "reservation_datetime": reservation_datetime,
        "entry_datetime": entry_datetime,
        "exit_datetime": exit_datetime,
        "cost": cost,
        "space": reservation["space_id"],
        "user": reservation["user_id"],
    }

    return parsed_reservation