import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io as sio

def pedir_entero(mensaje, minimo=None, maximo=None):
    """Solicita un entero al usuario con validación de rango."""
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"Debe ser >= {minimo}")
                continue
            if maximo is not None and valor > maximo:
                print(f"Debe ser <= {maximo}")
                continue
            return valor
        except ValueError:
            print("Ingrese un número entero válido.")


def pedir_float(mensaje, minimo=None, maximo=None):
    """Solicita un float al usuario con validación de rango."""
    while True:
        try:
            valor = float(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"Debe ser >= {minimo}")
                continue
            if maximo is not None and valor > maximo:
                print(f"Debe ser <= {maximo}")
                continue
            return valor
        except ValueError:
            print("Ingrese un número válido.")


def pedir_opcion(mensaje, opciones_validas):
    """Solicita una opción dentro de una lista de valores válidos."""
    while True:
        resp = input(mensaje).strip()
        if resp in opciones_validas:
            return resp
        print(f"Opción inválida. Elija entre: {opciones_validas}")


def validar_ruta(ruta, extension=None):
    """Verifica que el archivo exista y tenga la extensión correcta."""
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")
    if extension and not ruta.lower().endswith(extension.lower()):
        raise ValueError(f"Se esperaba un archivo {extension}, se recibió: {ruta}")
    return True

class SiataCSV:
    """maneja los archivos CSV del SIATA de calidad del aire.
    atributos
    ruta   : str la ruta al archivo .csv
    df     : DataFrame son los datos cargados con índice de fechas
    nombre : str es el nombre base del archivo (sin extensión)
    """

    CARPETA_GRAFICOS = "graficos_siata"

    def __init__(self, ruta):
        validar_ruta(ruta, ".csv")
        self.ruta = ruta
        self.nombre = os.path.splitext(os.path.basename(ruta))[0]
        self.df = self._cargar()
        os.makedirs(self.CARPETA_GRAFICOS, exist_ok=True)
        print(f"\n Archivo '{self.nombre}' cargado correctamente.")
        print(f"    Filas: {len(self.df)} | Columnas: {list(self.df.columns)}")

    def _cargar(self):
        df = pd.read_csv(self.ruta)
        col_fecha = "fecha_hora"
        if col_fecha in df.columns:
            df[col_fecha] = pd.to_datetime(df[col_fecha])
            df = df.set_index(col_fecha)
        else:
            # Intenta detectar columna de fecha automáticamente
            for col in df.columns:
                if "fecha" in col.lower() or "date" in col.lower() or "time" in col.lower():
                    df[col] = pd.to_datetime(df[col])
                    df = df.set_index(col)
                    break
        return df