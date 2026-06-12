import sqlite3
import os

def update_database():
    # Ruta a tu base de datos
    db_path = os.path.join(os.getcwd(), 'instance', 'flaskr.sqlite')
    
    if not os.path.exists(db_path):
        print(f"No se encontró la base de datos en: {db_path}")
        return

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    print("Iniciando actualización de base de datos...")

    commands = [
        # 1. Añadir columna para fecha de fin
        "ALTER TABLE reservation ADD COLUMN end_datetime INTEGER;"
    ]

    for cmd in commands:
        try:
            cursor.execute(cmd)
            print(f"✅ Ejecutado: {cmd[:50]}...")
        except sqlite3.OperationalError as e:
            # Si la columna ya existe, SQLite lanzará un error. Lo ignoramos.
            if "duplicate column name" in str(e):
                print(f"ℹ️ La columna ya existe, saltando...")
            else:
                print(f"❌ Error: {e}")

    connection.commit()
    connection.close()
    print("Actualización completada.")

if __name__ == "__main__":
    update_database()