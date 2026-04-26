import os
import glob
from clases import SiataCSV, EEGMat, Registro, pedir_entero, pedir_opcion


def buscar_archivos(extension):
    """
    Busca archivos de la extensión dada en la carpeta actual
    y en subcarpetas de un nivel (ej. datos_csv/, datos_mat/).
    Retorna lista de rutas relativas ordenadas.
    """
    patron_local = f"*.{extension}"
    patron_sub   = f"**/*.{extension}"
    archivos = glob.glob(patron_local) + glob.glob(patron_sub, recursive=True)
    # Quitar duplicados y ordenar
    archivos = sorted(set(archivos))
    return archivos


def seleccionar_archivo(extension):
    """
    Primero muestra los archivos detectados automáticamente.
    También permite escribir una ruta manual si el archivo
    está en otra carpeta.
    Retorna la ruta seleccionada o None.
    """
    archivos = buscar_archivos(extension)

    print(f"\n  ¿Cómo desea cargar el archivo .{extension}?")

    if archivos:
        print(f"  [1] Elegir de los archivos detectados en esta carpeta")
    print(f"  [2] Escribir la ruta manualmente (archivo en otra carpeta)")
    print(f"  [0] Cancelar")

    opciones = ["0", "2"] + (["1"] if archivos else [])
    op = pedir_opcion("  Opción: ", opciones)

    if op == "0":
        return None

    elif op == "1":
        print(f"\n  Archivos .{extension} encontrados:")
        for i, ruta in enumerate(archivos):
            nombre = os.path.basename(ruta)
            print(f"    [{i}] {nombre}")
        idx = pedir_entero("  Elige el número del archivo: ", 0, len(archivos) - 1)
        return archivos[idx]

    elif op == "2":
        ruta = input("  Ruta del archivo: ").strip().strip('"')
        if not ruta:
            print("No ingresaste ninguna ruta.")
            return None
        return ruta

# Registro global de objetos creados
registro = Registro()

# Listas de objetos activos en sesión
objetos_siata = []
objetos_eeg   = []

def separador(titulo=""):
    ancho = 58
    print("\n" + "="*ancho)
    if titulo:
        print(f"  {titulo}")
        print("="*ancho)


def pausar():
    input("\n  Presione ENTER para continuar...")


#submenu siata

def _elegir_siata():
    """Retorna el objeto SiataCSV activo elegido por el usuario."""
    if not objetos_siata:
        print("No hay archivos SIATA cargados. Cargue uno primero.")
        return None
    if len(objetos_siata) == 1:
        return objetos_siata[0]
    print("\n  Archivos SIATA cargados:")
    for i, obj in enumerate(objetos_siata):
        print(f"    [{i}] {obj.nombre}")
    idx = pedir_entero("  Elija el índice: ", 0, len(objetos_siata) - 1)
    return objetos_siata[idx]


def submenu_siata():
    while True:
        separador("MÓDULO SIATA – Calidad del Aire (CSV)")
        print("  [1] Cargar nuevo archivo CSV")
        print("  [2] Ver información del archivo (info + describe)")
        print("  [3] Gráficos: plot / boxplot / histograma")
        print("  [4] Operaciones: apply / map / suma-resta")
        print("  [5] Remuestreo: diario / mensual / trimestral")
        print("  [0] Volver al menú principal")

        op = pedir_opcion("\n  Elija una opción: ", ["0","1","2","3","4","5"])

        if op == "0":
            break

        elif op == "1":
            ruta = seleccionar_archivo("csv")
            if ruta:
                try:
                    obj = SiataCSV(ruta)
                    objetos_siata.append(obj)
                    registro.agregar(obj)
                except (FileNotFoundError, ValueError) as e:
                    print(f"Error: {e}")

        elif op == "2":
            obj = _elegir_siata()
            if obj:
                obj.mostrar_info()

        elif op == "3":
            obj = _elegir_siata()
            if obj:
                obj.graficar_columna()

        elif op == "4":
            obj = _elegir_siata()
            if obj:
                obj.operaciones()

        elif op == "5":
            obj = _elegir_siata()
            if obj:
                obj.graficar_remuestreo()

        pausar()


#submenu eeg

def _elegir_eeg():
    """Retorna el objeto EEGMat activo elegido por el usuario."""
    if not objetos_eeg:
        print("No hay archivos EEG cargados. Cargue uno primero.")
        return None
    if len(objetos_eeg) == 1:
        return objetos_eeg[0]
    print("\n  Archivos EEG cargados:")
    for i, obj in enumerate(objetos_eeg):
        print(f"    [{i}] {obj.nombre}")
    idx = pedir_entero("  Elija el índice: ", 0, len(objetos_eeg) - 1)
    return objetos_eeg[idx]


def submenu_eeg():
    while True:
        separador("MÓDULO EEG – Electroencefalografía (MAT)")
        print("  [1] Cargar nuevo archivo MAT")
        print("  [2] Suma de 3 canales (matriz 2D)")
        print("  [3] Promedio y desviación estándar (matriz 3D, stem)")
        print("  [0] Volver al menú principal")

        op = pedir_opcion("\n  Elija una opción: ", ["0","1","2","3"])

        if op == "0":
            break

        elif op == "1":
            ruta = seleccionar_archivo("mat")
            if ruta:
                try:
                    obj = EEGMat(ruta)
                    objetos_eeg.append(obj)
                    registro.agregar(obj)
                except (FileNotFoundError, ValueError, KeyError) as e:
                    print(f"Error: {e}")

        elif op == "2":
            obj = _elegir_eeg()
            if obj:
                obj.sumar_canales()

        elif op == "3":
            obj = _elegir_eeg()
            if obj:
                obj.estadisticos_3d()

        pausar()