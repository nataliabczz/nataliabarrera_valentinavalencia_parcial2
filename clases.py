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
        print(f"Gráfico guardado en: {ruta_g}")
        plt.show()
    
    def operaciones(self):
        print("\nOperaciones disponibles")
        print("  [1] apply  – calcular logaritmo natural de una columna")
        print("  [2] map    – clasificar valores por umbral (bajo/alto)")
        print("  [3] Sumar o restar dos columnas")
        op = pedir_opcion("  Elija operación: ", ["1", "2", "3"])

        if op == "1":
            col = self._elegir_columna("apply (log)")
            serie = self.df[col].dropna()
            result = serie.apply(lambda x: np.log(x) if x > 0 else np.nan)
            col_nueva = f"log_{col}"
            self.df[col_nueva] = result
            print(f"\n Columna '{col_nueva}' creada con apply (log natural).")
            print(self.df[[col, col_nueva]].head(8))

        elif op == "2":
            col = self._elegir_columna("map (clasificación)")
            umbral = pedir_float(f"  Ingrese el umbral para '{col}': ")
            resultado = self.df[col].map(
                lambda x: "alto" if (not pd.isna(x) and x >= umbral) else "bajo"
            )
            col_nueva = f"clase_{col}"
            self.df[col_nueva] = resultado
            print(f"\n Columna '{col_nueva}' creada con map (umbral={umbral}).")
            print(self.df[[col, col_nueva]].head(8))
            print("\n  Distribución:")
            print(resultado.value_counts())

        elif op == "3":
            print("\n  Columna A:")
            col_a = self._elegir_columna("columna A")
            print("\n  Columna B:")
            col_b = self._elegir_columna("columna B")
            accion = pedir_opcion("  ¿Sumar (s) o restar (r)? ", ["s", "r"])
            if accion == "s":
                resultado = self.df[col_a] + self.df[col_b]
                op_str = f"{col_a}_+_{col_b}"
            else:
                resultado = self.df[col_a] - self.df[col_b]
                op_str = f"{col_a}_-_{col_b}"
            self.df[op_str] = resultado
            print(f"\n Columna '{op_str}' creada.")
            print(self.df[[col_a, col_b, op_str]].head(8))

    # ── Req. 6: resample + guardar ───────────
    def graficar_remuestreo(self):
        col = self._elegir_columna("remuestreo")
        serie = self.df[col].dropna()

        diario     = serie.resample("D").mean()
        mensual    = serie.resample("ME").mean()
        trimestral = serie.resample("QE").mean()

        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        fig.suptitle(f"Remuestreo de '{col}'  –  {self.nombre}", fontsize=13)

        for ax, datos, titulo, color in zip(
            axes,
            [diario, mensual, trimestral],
            ["Diario (D)", "Mensual (ME)", "Trimestral (QE)"],
            ["steelblue", "darkorange", "seagreen"]
        ):
            ax.plot(datos.index, datos.values, color=color,
                    marker="o", markersize=3, linewidth=1.2)
            ax.set_title(titulo)
            ax.set_xlabel("Fecha")
            ax.set_ylabel(col)
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.tick_params(axis='x', rotation=30)

        plt.tight_layout()

        ruta_g = os.path.join(self.CARPETA_GRAFICOS,
                              f"{self.nombre}_{col}_remuestreo.png")
        fig.savefig(ruta_g, dpi=150)
        print(f" Gráfico de remuestreo guardado en: {ruta_g}")
        plt.show()

    def __str__(self):
        return (f"SiataCSV | archivo: {self.nombre} | "
                f"filas: {len(self.df)} | cols: {list(self.df.columns)}")
    

class EEGMat:
    """
    Maneja archivos .mat de electroencefalografía (EEG).

    Estructura esperada:
      data  →  (canales, muestras_por_epoca, num_epocas)
            
    CARPETA_GRAFICOS = "graficos_eeg"
    FS = 1000 """

    def __init__(self, ruta):
        validar_ruta(ruta, ".mat")
        self.ruta = ruta
        self.nombre = os.path.splitext(os.path.basename(ruta))[0]
        self.data3d = None   # (canales, muestras, epocas)
        self.data2d = None   # (canales, muestras_total)
        self._cargar()
        os.makedirs(self.CARPETA_GRAFICOS, exist_ok=True)

    #cargar
    def _cargar(self):
        print(f"\n whosmat de '{self.nombre}' ")
        info = sio.whosmat(self.ruta)
        for nombre, forma, tipo in info:
            print(f"    Variable: '{nombre}'  |  forma: {forma}  |  tipo: {tipo}")

        mat = sio.loadmat(self.ruta)
        # Buscar la clave de datos (generalmente 'data')
        clave = None
        for k in mat:
            if not k.startswith("__"):
                clave = k
                break
        if clave is None:
            raise KeyError("No se encontró variable de datos en el archivo .mat")

        self.data3d = mat[clave]  # (ch, muestras, epocas)
        n_ch, n_muestras, n_epocas = self.data3d.shape
        print(f"\n Cargado '{clave}': {n_ch} canales, "
              f"{n_muestras} muestras/época, {n_epocas} épocas")
        # Convertir a 2D: (canales, muestras_total)
        self.data2d = self.data3d.reshape(n_ch, n_muestras * n_epocas)
        print(f"     Matriz 2D resultante: {self.data2d.shape}")

    # ── Propiedad: número de canales ─────────
    @property
    def n_canales(self):
        return self.data3d.shape[0]

    @property
    def n_muestras_total(self):
        return self.data2d.shape[1]

    # ── Req. 7a: suma de 3 canales en 2D ─────
    def sumar_canales(self):
        print(f"\n  Canales disponibles: 0 a {self.n_canales - 1}")
        canales = []
        for i in range(3):
            c = pedir_entero(f"  Canal {i+1}: ", 0, self.n_canales - 1)
            canales.append(c)

        total = self.n_muestras_total
        print(f"  Rango de muestras: 0 a {total - 1}")
        p_min = pedir_entero("  Muestra mínima: ", 0, total - 2)
        p_max = pedir_entero("  Muestra máxima: ", p_min + 1, total - 1)

        # Señales seleccionadas (en µV, de la matriz 2D)
        segmentos = [self.data2d[c, p_min:p_max] for c in canales]
        t = np.arange(p_max - p_min) / self.FS  # eje de tiempo en segundos

        suma = segmentos[0] + segmentos[1] + segmentos[2]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle(f"Suma de canales  –  {self.nombre}", fontsize=13)

        colores = ["steelblue", "darkorange", "seagreen"]
        for idx, (seg, c) in enumerate(zip(segmentos, canales)):
            ax1.plot(t, seg, color=colores[idx],
                     linewidth=0.8, label=f"Canal {c}")
        ax1.set_title("Canales seleccionados")
        ax1.set_xlabel("Tiempo (s)")
        ax1.set_ylabel("Amplitud (µV)")
        ax1.legend()
        ax1.grid(True, linestyle="--", alpha=0.4)

        ax2.plot(t, suma, color="crimson", linewidth=0.9, label="Suma")
        ax2.set_title(f"Resultado: Canal {canales[0]} + Canal {canales[1]} + Canal {canales[2]}")
        ax2.set_xlabel("Tiempo (s)")
        ax2.set_ylabel("Amplitud (µV)")
        ax2.legend()
        ax2.grid(True, linestyle="--", alpha=0.4)

        plt.tight_layout()

        ruta_g = os.path.join(
            self.CARPETA_GRAFICOS,
            f"{self.nombre}_suma_canales_{'_'.join(map(str, canales))}.png"
        )
        fig.savefig(ruta_g, dpi=150)
        print(f"Gráfico guardado en: {ruta_g}")
        plt.show()

    # ── Req. 7b: promedio y std sobre eje 3D ─
    def estadisticos_3d(self):
        n_ch, n_muestras, n_epocas = self.data3d.shape
        print(f"\n  Dimensiones de la matriz 3D: {self.data3d.shape}")
        print(f"    Eje 0 → canales ({n_ch})")
        print(f"    Eje 1 → muestras ({n_muestras})")
        print(f"    Eje 2 → épocas  ({n_epocas})")
        eje = pedir_entero("  Eje para promedio/std (0, 1 o 2): ", 0, 2)

        promedio = np.mean(self.data3d, axis=eje)
        std      = np.std(self.data3d, axis=eje)

        # Aplanar para graficar con stem (tomamos la primera fila/columna)
        prom_flat = promedio.flatten()
        std_flat  = std.flatten()

        # Limitar puntos para stem (máx 300 para visualización clara)
        N = min(300, len(prom_flat))
        x = np.arange(N)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle(f"Estadísticos 3D (eje={eje})  –  {self.nombre}", fontsize=13)

        ax1.stem(x, prom_flat[:N], linefmt="C0-", markerfmt="C0o",
                 basefmt="k-")
        ax1.set_title(f"Promedio a lo largo del eje {eje}")
        ax1.set_xlabel("Índice")
        ax1.set_ylabel("Promedio (µV)")
        ax1.grid(True, linestyle="--", alpha=0.4)

        ax2.stem(x, std_flat[:N], linefmt="C1-", markerfmt="C1o",
                 basefmt="k-")
        ax2.set_title(f"Desviación estándar a lo largo del eje {eje}")
        ax2.set_xlabel("Índice")
        ax2.set_ylabel("Std (µV)")
        ax2.grid(True, linestyle="--", alpha=0.4)

        plt.tight_layout()

        ruta_g = os.path.join(
            self.CARPETA_GRAFICOS,
            f"{self.nombre}_stats_eje{eje}.png"
        )
        fig.savefig(ruta_g, dpi=150)
        print(f"Gráfico guardado en: {ruta_g}")
        plt.show()

    def __str__(self):
        n_ch, n_m, n_e = self.data3d.shape
        return (f"EEGMat | archivo: {self.nombre} | "
                f"{n_ch} canales, {n_m} muestras/época, {n_e} épocas")
    
#extra

class Registro:
    """
    Almacena objetos SiataCSV y EEGMat y permite buscarlos por nombre.
    """

    def __init__(self):
        self._objetos = {}  # {nombre: objeto}

    def agregar(self, objeto):
        """Registra un objeto con su .nombre como clave."""
        self._objetos[objeto.nombre] = objeto
        print(f"Objeto '{objeto.nombre}' registrado en el Registro.")

    def buscar(self, nombre):
        """Devuelve el objeto si existe, None en caso contrario."""
        return self._objetos.get(nombre, None)

    def listar(self):
        if not self._objetos:
            print("  (Registro vacío)")
            return
        print("\n  ── Objetos en el Registro ──────────────────────────")
        for i, (nombre, obj) in enumerate(self._objetos.items()):
            print(f"  [{i}] {obj}")

    def eliminar(self, nombre):
        if nombre in self._objetos:
            del self._objetos[nombre]
            print(f"Objeto '{nombre}' eliminado del Registro.")
        else:
            print(f"{nombre}' no encontrado.")

    def __len__(self):
        return len(self._objetos)



 
    