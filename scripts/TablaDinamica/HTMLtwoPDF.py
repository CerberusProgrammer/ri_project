from datetime import datetime
from xhtml2pdf import pisa
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf.util import ErrorMsg

# Variables que deseas inyectar en el HTML
variables = {

    'Fecha_Actual' 
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

}

# Directorio donde se encuentra el archivo HTML
template_dir = 'C:/Users/a1749/ri_project/scripts/TablaDinamica/'

# Nombre del archivo HTML
template_file = 'miTabla.html'

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
file = f'{template_dir}{datetime.now().day}_{datetime.now().month}_{datetime.now().year}.pdf'

if pisa_status.err:  # type: ignore
    print("Error al generar el PDF")
else:
    # Guarda el PDF en un archivo
    with open(file, 'wb') as pdf_file:
        pdf_file.write(pdf_buffer.getvalue())
    print("PDF generado exitosamente")

    
