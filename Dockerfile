# Usamos una imagen base de Python
FROM python:3.9

# Establecemos un directorio de trabajo
WORKDIR /app

# Copiamos el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install -r requirements.txt

# Copiamos el resto del código al contenedor
COPY . .

# Exponemos el puerto en el que se ejecutará Django
EXPOSE 8000

# Ejecutamos el servidor Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# name = ri_server0.1.0
# Execute: 
# docker build -t ri_server0.1.0 .
# docker run -p 8000:8000 ri_server0.1.0
# acces to: http://localhost:8000