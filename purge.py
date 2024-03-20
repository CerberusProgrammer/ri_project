import pandas as pd
import requests
import json
import re

class Rack:
    def __init__(self, nombre):
        self.nombre = nombre

class Estante:
    def __init__(self, numero, rack):
        self.numero = numero
        self.rack = rack

class ProductoAlmacen:
    def __init__(self, nombre, identificador, costo, cantidad, divisa, posicion):
        self.nombre = nombre
        self.identificador = identificador
        self.costo = costo
        self.cantidad = cantidad
        self.divisa = divisa
        self.posicion = posicion

archivo = "C:\\Users\\cerbe\\Downloads\\NUEVO INVENTARIO 3.xlsx"

df = pd.read_excel(archivo)

rack_endpoint = "http://localhost:8000/api/rack/"
estante_endpoint = "http://localhost:8000/api/estantes/"

headers = {
    "Authorization": "Token 089d96db78fc86302f71358506f4595131f3338f"
}

productos_almacen = []

for index, row in df.iterrows():
    print(f"Procesando fila {index + 1}...")
    rack_nombre = row['RACK']
    estante_numero = row['REPISA']

    response = requests.get(rack_endpoint, params={"nombre": rack_nombre}, headers=headers)
    if response.status_code == 200 and response.text:
        try:
            rack_id = response.json()[0]['id']
        except IndexError:
            rack = Rack(rack_nombre)
            response = requests.post(rack_endpoint, data=rack.__dict__, headers=headers)
            if response.status_code == 201:
                rack_id = response.json()['id']
            else:
                print(f"Error al crear el rack: {response.text}")
                continue
    else:
        rack = Rack(rack_nombre)
        response = requests.post(rack_endpoint, data=rack.__dict__, headers=headers)
        if response.status_code == 201:
            rack_id = response.json()['id']
        else:
            print(f"Error al crear el rack: {response.text}")
            continue

    print(f"Rack ID: {rack_id}")

    response = requests.get(estante_endpoint, params={"estante": estante_numero, "rack": rack_id}, headers=headers)
    if response.status_code == 200 and response.text:
        try:
            estante_id = response.json()[0]['id']
        except IndexError:
            estante = Estante(estante_numero, rack_id)
            response = requests.post(estante_endpoint, data=estante.__dict__, headers=headers)
            if response.status_code == 201:
                estante_id = response.json()['id']
            else:
                print(f"Error al crear el estante: {response.text}")
                continue
    else:
        estante = Estante(estante_numero, rack_id)
        response = requests.post(estante_endpoint, data=estante.__dict__, headers=headers)
        if response.status_code == 201:
            estante_id = response.json()['id']
        else:
            print(f"Error al crear el estante: {response.text}")
            continue

    print(f"Estante ID: {estante_id}")

    if pd.isnull(row['No. Parte']):
        df.loc[index, 'No. Parte'] = row['Nombre del Material']
    
    if pd.isnull(row['PRECIO UNITARIO']):
        df.loc[index, 'PRECIO UNITARIO'] = 0
    
    if pd.isnull(row['DIVISA']):
        df.loc[index, 'DIVISA'] = 'MXN'

    cantidad = int(row['Total en Existencia'].split(' ')[0])

    producto = ProductoAlmacen(row['Nombre del Material'], row['No. Parte'], row['PRECIO UNITARIO'], cantidad, row['DIVISA'], estante_id)
    productos_almacen.append(producto.__dict__)
    
    print(f'producto: {producto.__dict__}')

print(json.dumps(productos_almacen, indent=4))
