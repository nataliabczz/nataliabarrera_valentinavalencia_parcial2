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