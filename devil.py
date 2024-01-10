import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # Reemplaza 'myproject.settings' con la ruta a tu archivo de configuración de Django
django.setup()

from django.db import connection
from ri_compras.models import ProductoRequisicion, Requisicion  # Reemplaza 'ri_compras.models' con la ruta a tus modelos

def reset_sequences():
    with connection.cursor() as cursor:
        # cursor.execute("""
        #     SELECT setval(pg_get_serial_sequence('"ri_compras_productorequisicion"', 'id'), 
        #     COALESCE((SELECT MAX(id)+1 FROM ri_compras_productorequisicion), 1), false);
        # """)
        
        # cursor.execute("""
        #     SELECT setval(pg_get_serial_sequence('"ri_compras_requisicion"', 'id'), 
        #     COALESCE((SELECT MAX(id)+1 FROM ri_compras_requisicion), 1), false);
        # """)
        
        cursor.execute("""
            SELECT setval(pg_get_serial_sequence('"ri_compras_ordenes"', 'id'), 
            COALESCE((SELECT MAX(id)+1 FROM ri_compras_ordenes), 1), false);
        """)

reset_sequences()
