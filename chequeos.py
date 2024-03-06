import os 
import sys
import concurrent.futures
import json
import subprocess
import threading

# Agrega un bloqueo global para imprimir de manera segura
lock_imprimir = threading.Lock()


def obtener_url_cluster(CLUSTER_NAME, ENTORNO):
    LISTA_CLUSTER = f"config/Cluster/Entorno_{ENTORNO}/Lista_Cluster_{ENTORNO}.txt"
    URL_CLUSTER = None

    with open(LISTA_CLUSTER, 'r') as file:
        for line in file:
            if not line.startswith('#') and line.strip():
                columns = line.strip().split()
                if columns[0] == CLUSTER_NAME:
                    URL_CLUSTER = columns[1]
                    break

    return URL_CLUSTER

def obtener_matriz_namespace(DOMINIO):
    matriz_namespaces = []
    directorio_namespaces = f'config/Namespaces/Dominio_{DOMINIO}/'

    for archivo in os.listdir(directorio_namespaces):
        if archivo.endswith('.txt'):
            path_archivo = os.path.join(directorio_namespaces, archivo)

            with open(path_archivo, 'r') as file:
                for linea in file:
                    if not linea.startswith('#') and linea.strip():
                        columnas = linea.strip().split()
                        entorno = columnas[0].split('-')[-1]

                        for nombre_cluster in columnas[1:]:
                            url_cluster = obtener_url_cluster(nombre_cluster, entorno)
                            matriz_namespaces.append([columnas[0], nombre_cluster, url_cluster])

    return matriz_namespaces

def cargar_configuracion():
    try:
        with open("config/config_script.json", "r") as file:
            configuracion = json.load(file)
        return configuracion.get("scripts", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error al cargar configuraciones: {e}")
        return []

def ejecutar_script_bash(namespace, cluster, url, script, clave):
    # Utiliza la ruta completa al ejecutable de Bash
    ruta_bash = r"C:\Program Files\Git\usr\bin\bash.exe"
    comando_bash = f'"{ruta_bash}" {script} {namespace} {cluster} {url} {clave}'

    try:
        resultado = subprocess.run(comando_bash, shell=True, capture_output=True)
        salida_stdout = resultado.stdout.decode().rstrip()
        salida_stderr = resultado.stderr.decode().rstrip()

        with lock_imprimir:
            print(salida_stdout)
            if salida_stderr:
                print(f"Error al ejecutar el script:\n{salida_stderr}")

            # Agrega una línea en blanco después de cada ejecución
            print()

    except Exception as e:
        with lock_imprimir:
            print(f"Error al ejecutar el script: {e}")



def main(DOMINIO):
    print(f"Dominio: {DOMINIO}")
    clave = input("Ingrese la clave: ")

    matriz_namespaces = obtener_matriz_namespace(DOMINIO)
    print(f"\nMatriz Namespaces: {matriz_namespaces}")
    print("\n")
    configuracion_scripts = cargar_configuracion()
    scripts_activos = [script["script"] for script in configuracion_scripts if script.get("enabled", False)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(ejecutar_script_bash, *fila, script, clave)
            for fila in matriz_namespaces
            for script in scripts_activos
        ]

        concurrent.futures.wait(futures)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py <DOMINIO>")
        sys.exit(1)

    DOMINIO = sys.argv[1]
    main(DOMINIO)
