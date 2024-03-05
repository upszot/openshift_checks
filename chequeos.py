import os 
import sys
import concurrent.futures
import json

def obtener_url_cluster(CLUSTER_NAME, ENTORNO):
    LISTA_CLUSTER = f"config/Cluster/Entorno_{ENTORNO}/Lista_Cluster_{ENTORNO}.txt"
    URL_CLUSTER = None
    #print(f"LISTA_CLUSTER: {LISTA_CLUSTER}")

    with open(LISTA_CLUSTER, 'r') as file:
        for line in file:
            if not line.startswith('#') and line.strip():
                columns = line.strip().split()
                if columns[0] == CLUSTER_NAME:
                    URL_CLUSTER = columns[1]
                    #print(f"URL_CLUSTER: {URL_CLUSTER}")
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
    with open("config/config_script.json", "r") as file:
        configuracion = json.load(file)
    return configuracion.get("scripts", [])


def ejecutar_script_bash(namespace, cluster, url, script, clave):
    comando_bash = f"{script} {namespace} {cluster} {url} {clave}"
    #subprocess.run(comando_bash, shell=True)
    print(f"comando_bash: {comando_bash}")
    
    resultado = subprocess.run(comando_bash, shell=True, capture_output=True)
    #resultado = subprocess.run(['C:/Program Files/Git/usr/bin/bash.exe', '-c', comando_bash], capture_output=True)
    #resultado = subprocess.run(['bash.exe', '-c', comando_bash], capture_output=True, text=True)

    #print(f"Salida estándar del script: {resultado.stdout}")
    
    #if resultado.stderr:
    #    print(f"Error al ejecutar el script: {resultado.stderr}")

    print("\n")

def main(DOMINIO):
    print(f"Dominio: {DOMINIO}")
    # Solicitar al usuario que ingrese una clave
    clave = input("Ingrese la clave: ")

    matriz_namespaces = obtener_matriz_namespace(DOMINIO)
    print(f"Matriz Namespaces: {matriz_namespaces}")
    configuracion_scripts = cargar_configuracion()
    scripts_activos = [script["script"] for script in configuracion_scripts if script.get("enabled", False)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Utilizar concurrent.futures para ejecutar las llamadas en paralelo
        futures = [
            executor.submit(ejecutar_script_bash, *fila, script,clave)
            for fila in matriz_namespaces
            for script in scripts_activos
        ]

        # Esperar a que todas las llamadas se completen
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py <DOMINIO>")
        sys.exit(1)

    DOMINIO = sys.argv[1]
    main(DOMINIO)