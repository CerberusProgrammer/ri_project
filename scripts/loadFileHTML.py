from xhtml2pdf import pisa

# Variables que deseas inyectar en el HTML
variables = {
    'nombre': 'Juan Pérez',
    'edad': 30,
}

# Ruta donde se guardará el archivo PDF resultante
archivo_pdf = 'C:\Users\a1749\ri_project\scripts\Test.pdf'

# Crea una cadena HTML con los marcadores de posición
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Ejemplo HTML</title>
</head>
<body>
    <p>Nombre: {nombre}</p>
    <p>Edad: {edad}</p>
</body>
</html>
""".format(**variables)

# Crear un archivo PDF vacío donde se escribirá la salida
with open(archivo_pdf, 'wb') as archivo_salida_pdf:
    # Utilizar pisa para convertir el HTML a PDF
    pisa.CreatePDF(html_template, archivo_salida_pdf)
        
print(f'Se ha creado el archivo PDF en: {archivo_pdf}')
