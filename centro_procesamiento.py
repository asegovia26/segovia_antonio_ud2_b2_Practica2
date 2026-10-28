import threading
import time
from queue import Queue
from time import perf_counter


# ---------------------------------------------------------
# DATOS INICIALES
# ---------------------------------------------------------

trabajos = [
    ("Informe de ventas", 2),
    ("Copia de seguridad", 3),
    ("Consulta de clientes", 1),
    ("Actualización de productos", 2),
    ("Generación de facturas", 3),
    ("Exportación de datos", 1),
    ("Comprobación del inventario", 2),
    ("Envío de notificaciones", 1)
]


# ---------------------------------------------------------
# RECURSOS COMPARTIDOS
# ---------------------------------------------------------

cola_trabajos = Queue()

evento_inicio = threading.Event()

semaforo_recurso = threading.Semaphore(2)

lock_contador = threading.Lock()

trabajos_terminados = 0


# ---------------------------------------------------------
# FUNCIÓN DE PROCESAMIENTO
# ---------------------------------------------------------

def procesar_trabajo(nombre, duracion):
    """
    Simula el acceso a un recurso externo limitado.
    """

    with semaforo_recurso:
        hilo_actual = threading.current_thread().name

        print(
            f"[{hilo_actual}] "
            f"Accede al recurso: {nombre}"
        )

        time.sleep(duracion)

        print(
            f"[{hilo_actual}] "
            f"Finaliza el recurso: {nombre}"
        )


# ---------------------------------------------------------
# FUNCIÓN CONSUMIDORA
# ---------------------------------------------------------

def consumidor():
    global trabajos_terminados

    hilo_actual = threading.current_thread().name

    print(
        f"[{hilo_actual}] Esperando señal de inicio"
    )

    # Esperar a que el hilo principal active el evento
    evento_inicio.wait()

    print(
        f"[{hilo_actual}] Comienza a trabajar"
    )

    while True:
        # Recuperar el siguiente elemento
        trabajo = cola_trabajos.get()

        # Comprobar la señal de finalización
        if trabajo is None:
            cola_trabajos.task_done()

            print(
                f"[{hilo_actual}] "
                f"Finaliza su ejecución"
            )

            break

        nombre, duracion = trabajo

        procesar_trabajo(
            nombre,
            duracion
        )

        # Actualizar el contador compartido
        with lock_contador:
            trabajos_terminados += 1

            print(
                f"[{hilo_actual}] "
                f"Trabajos terminados: "
                f"{trabajos_terminados}"
            )

        # Indicar que el trabajo ha terminado
        cola_trabajos.task_done()


# ---------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------

if __name__ == "__main__":
    inicio_medicion = perf_counter()

    consumidores = []

    numero_consumidores = 3

    # Crear los consumidores
    for numero in range(
        1,
        numero_consumidores + 1
    ):
        hilo = threading.Thread(
            target=consumidor,
            name=f"Consumidor-{numero}"
        )

        consumidores.append(hilo)

    # Iniciar los consumidores
    for hilo in consumidores:
        hilo.start()

    # Introducir los trabajos en la cola
    for trabajo in trabajos:
        cola_trabajos.put(trabajo)

    print(
        "\nEl centro está preparando "
        "el inicio del procesamiento..."
    )

    time.sleep(2)

    print(
        "\nEl centro autoriza el inicio.\n"
    )

    # Activar la señal de inicio
    evento_inicio.set()

    # Introducir una señal de finalización
    # para cada consumidor
    for _ in consumidores:
        cola_trabajos.put(None)

    # Esperar a que todos los elementos
    # de la cola hayan sido procesados
    cola_trabajos.join()

    # Esperar la terminación de los hilos
    for hilo in consumidores:
        hilo.join()

    tiempo_total = (
        perf_counter() - inicio_medicion
    )

    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)

    print(
        f"Trabajos previstos: "
        f"{len(trabajos)}"
    )

    print(
        f"Trabajos terminados: "
        f"{trabajos_terminados}"
    )

    print(
        f"Tiempo total: "
        f"{tiempo_total:.2f} segundos"
    )
