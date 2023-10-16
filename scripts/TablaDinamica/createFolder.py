from pathlib import Path
import getpass  # Importa la biblioteca getpass para obtener el nombre de usuario

# Obtén el nombre de usuario actual
nombre_usuario = getpass.getuser()

# Genera un identificador único, por ejemplo, el ID de la orden de compra
id_orden_compra = "12345"  # Reemplaza con el ID correcto

# Especifica la ruta de la carpeta que deseas crear
carpeta_nueva = f"C:/Users/a1749/ri_project/scripts/TablaDinamica/{nombre_usuario}_{id_orden_compra}"

# Crea un objeto Path y utiliza el método mkdir para crear la carpeta
carpeta_path = Path(carpeta_nueva)

if not carpeta_path.exists():
    carpeta_path.mkdir()
    print(f"La carpeta '{carpeta_nueva}' ha sido creada.")
else:
    print(f"La carpeta '{carpeta_nueva}' ya existe.")

