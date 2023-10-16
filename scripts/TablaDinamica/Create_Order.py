from datetime import datetime
from xhtml2pdf import pisa
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf.util import ErrorMsg
from pathlib import Path
import getpass

# Variables que deseas inyectar en el HTML
variables = {
 
    'Nombre': 'John Doe',
    'RFC': 'ABCD123456',
    'Domicilio': '123 Main St',
    'Telefono': '555-123-456',
    'Correo': 'john.doe@example.com',
    'Producto_1': 'Tornillo',
    'Producto_2': 'Tuerca',
    'Producto_3': 'Polin',
    'Cantidad': '1',
    'Precio': '100',
    'Subtotal_1': '1,000.00',

    'Productos': {
        'Producto_1': {
            'Cantidad': int(10),
            'Precio': float(100.00),
            'Subtotal': 10 * 100.00
        },
        'Producto_2': {
            'Cantidad': int(5),
            'Precio': float(200.00),
            'Subtotal': 5 * 100.00
        },

        'Producto_3': {
            'Cantidad': int(3),
            'Precio': float(300.00),
            'Subtotal': 3 * 300
        },

        'Producto_4': {
            'Cantidad': int(3),
            'Precio': float(300.00),
            'Subtotal': 3 * 300
        },

        'Producto_5': {
            'Cantidad': int(3),
            'Precio': float(300.00),
            'Subtotal': 3 * 300
        },

        'Producto_6': {
            'Cantidad': int(3),
            'Precio': float(300.00),
            'Subtotal': 3 * 300
        },

        'Producto_7': {
            'Cantidad': int(3),
            'Precio': float(300.00),
            'Subtotal': 3 * 300
        },

        'Producto_8': {
            'Cantidad': int(3),
            'Precio': float(300.00),
            'Subtotal': 3 * 300
        },

        'Producto_9': {
            'Cantidad': int(3),
            'Precio': float(300.00),
            'Subtotal': 3 * 300
        },

        'Producto_10': {
            'Cantidad': int(3),
            'Precio': float(300.00),
            'Subtotal': 3 * 300
       },

    }

    # ... (tus variables aquí)
}

# Directorio donde se encuentra el archivo HTML
template_dir = 'C:/Users/a1749/ri_project/scripts/TablaDinamica/'

# Nombre del archivo HTML
template_file = 'miTabla.html'

# Obtén el nombre de usuario actual
nombre_usuario = getpass.getuser()

# Genera un identificador único, por ejemplo, el ID de la orden de compra
id_orden_compra = "12345"  # Reemplaza con el ID correcto

# Especifica la ruta de la carpeta que deseas crear
carpeta_nueva = f'{template_dir}{nombre_usuario}_{id_orden_compra}'

# Crea un objeto Path y utiliza el método mkdir para crear la carpeta
carpeta_path = Path(carpeta_nueva)

if not carpeta_path.exists():
    carpeta_path.mkdir()
    print(f"La carpeta '{carpeta_nueva}' ha sido creada.")
else:
    print(f"La carpeta '{carpeta_nueva}' ya existe.")

# Carga el entorno de Jinja2
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template(template_file)

# Renderiza el HTML con las variables
html_content = template.render(variables=variables)

# Crea un objeto BytesIO para almacenar el PDF generado
pdf_buffer = BytesIO()

# Convierte el HTML en un archivo PDF
pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

# Nombre del archivo PDF
file = f'{carpeta_nueva}/{datetime.now().day}_{datetime.now().month}_{datetime.now().year}.pdf'

if pisa_status.err: # type: ignore
    print("Error al generar el PDF")
else:
    # Guarda el PDF en un archivo
    with open(file, 'wb') as pdf_file:
        pdf_file.write(pdf_buffer.getvalue())
    print("PDF generado exitosamente")
