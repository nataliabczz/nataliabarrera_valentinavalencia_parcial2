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
    def mostrar_info(self):
        print("\n" + "="*55)
        print(f"  INFO  –  {self.nombre}")
        print("="*55)
        self.df.info()
        print("\ndescribe" )
        print(self.df.describe())

    #Columnas numéricas disponibles 
    def columnas_numericas(self):
        return list(self.df.select_dtypes(include=[np.number]).columns)

    def _elegir_columna(self, titulo="columna"):
        cols = self.columnas_numericas()
        print(f"\n  Columnas numéricas disponibles para {titulo}:")
        for i, c in enumerate(cols):
            print(f"    [{i}] {c}")
        idx = pedir_entero("  Elija el índice: ", 0, len(cols) - 1)
        return cols[idx]

    # 3 gráficos en subplots 
    def graficar_columna(self):
        col = self._elegir_columna("graficar")
        datos = self.df[col].dropna()

        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        fig.suptitle(f"Gráficos de '{col}'  –  {self.nombre}", fontsize=13)

        # Plot
        axes[0].plot(datos.index, datos.values, color="steelblue", linewidth=0.8)
        axes[0].set_title("Serie temporal (plot)")
        axes[0].set_xlabel("Fecha")
        axes[0].set_ylabel(col)
        axes[0].tick_params(axis='x', rotation=30)

        # Boxplot
        axes[1].boxplot(datos.values, patch_artist=True,
                        boxprops=dict(facecolor="lightyellow"))
        axes[1].set_title("Boxplot")
        axes[1].set_xlabel(col)
        axes[1].set_ylabel("Valor")

        # Histograma
        axes[2].hist(datos.values, bins=30, color="salmon", edgecolor="black")
        axes[2].set_title("Histograma")
        axes[2].set_xlabel(col)
        axes[2].set_ylabel("Frecuencia")

        plt.tight_layout()

        # Guardar
        ruta_g = os.path.join(self.CARPETA_GRAFICOS,
                              f"{self.nombre}_{col}_graficos.png")
        fig.savefig(ruta_g, dpi=150)
        print(f"  ✔ Gráfico guardado en: {ruta_g}")
        plt.show()