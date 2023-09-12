import sqlite3

# Conéctate a tu base de datos
sqliteConnection = sqlite3.connect('app_ri_database.sqlite3')

# Crea un objeto cursor
cursor = sqliteConnection.cursor()

# Ejecuta una consulta SQL para obtener todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# Imprime todas las tablas
print("Lista de tablas:")
for table in cursor.fetchall():
    print(table)

# No olvides cerrar la conexión al final
sqliteConnection.close()
