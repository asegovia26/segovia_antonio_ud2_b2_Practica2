# UD2. Bloque 2. Práctica 2: Centro de procesamiento coordinado

**Alumno:** Antonio Segovia Santos

---

## 1. Interpretación inicial

1. **¿Cuántos trabajos se introducen en la cola?**
   Se introducen **8 trabajos reales** (definidos en la lista `trabajos`) y posteriormente **3 marcas centinela (`None`)**, haciendo un total de 11 elementos introducidos en `cola_trabajos`.

2. **¿Cuántos hilos consumidores se crean?**
   Se crean **3 hilos consumidores** (`Consumidor-1`, `Consumidor-2` y `Consumidor-3`), según la variable `numero_consumidores = 3`.

3. **¿Cuántos consumidores pueden acceder simultáneamente al recurso externo?**
   Solamente **2 consumidores** pueden acceder de forma simultánea, ya que el semáforo está configurado con capacidad 2 (`threading.Semaphore(2)`).

4. **¿Qué instrucción mantiene inicialmente detenidos a los consumidores?**
   La instrucción `evento_inicio.wait()` dentro de la función `consumidor()`.

5. **¿Qué instrucción permite que comiencen todos los consumidores?**
   La instrucción `evento_inicio.set()` ejecutada por el programa principal tras la pausa de preparación de 2 segundos.

---

## 2. Primera ejecución

> **[INSERTAR AQUÍ CAPTURA COMPLETA DE LA CONSOLA DE LA PRIMERA EJECUCIÓN]**

### Datos anotados de la ejecución:
- **Número de trabajos previstos:** 8
- **Número de trabajos terminados:** 8
- **Tiempo total:** ~10.01 segundos (2 segundos de preparación inicial + 8 segundos de procesamiento con 2 recursos simultáneos).
- **Orden aproximado de los consumidores:** Al activarse el evento, los 3 consumidores despiertan e intentan procesar los primeros 3 trabajos de la cola (`Informe de ventas`, `Copia de seguridad` y `Consulta de clientes`), pero solo 2 logran entrar al semáforo de inmediato, mientras el tercero espera a que uno libere el recurso.

### Respuestas:
1. **¿Los trabajos se procesan en el mismo orden en todas las ejecuciones?**
   Los trabajos se extraen de la cola en orden FIFO (primero en entrar, primero en salir), pero **el orden exacto en que los hilos acceden al semáforo y terminan cada trabajo puede variar** entre ejecuciones debido a la planificación de hilos del sistema operativo y a las distintas duraciones de cada tarea.

2. **¿El resultado final debe seguir siendo correcto aunque cambie el orden?**
   **Sí.** Gracias a la sincronización mediante `Queue`, `Semaphore` y `Lock`, siempre se procesarán los 8 trabajos sin pérdidas ni condiciones de carrera, y el contador final `trabajos_terminados` siempre será 8.

3. **¿Qué consumidor procesa cada trabajo?**
   No está prefijado; cada trabajo es procesado de manera dinámica por el primer consumidor que quede libre y extraiga el siguiente elemento de `cola_trabajos` mediante `get()`.

---

## 3. Funcionamiento de `queue.Queue`

1. **¿Qué instrucción introduce un trabajo en la cola?**
   `cola_trabajos.put(trabajo)` (y `cola_trabajos.put(None)` para los centinelas).

2. **¿Qué instrucción recupera un trabajo?**
   `trabajo = cola_trabajos.get()`

3. **¿Qué ocurre si un consumidor ejecuta `get()` y la cola está vacía?**
   El hilo consumidor **se bloquea (queda en espera)** automáticamente hasta que haya algún elemento disponible en la cola, sin consumir CPU innecesariamente.

4. **¿Por qué es preferible utilizar `Queue` en lugar de compartir una lista normal?**
   Porque `queue.Queue` es **thread-safe** (segura para hilos): gestiona internamente los bloqueos necesarios para insertar y extraer elementos sin condiciones de carrera, evita que dos hilos tomen el mismo trabajo por error y ofrece métodos de sincronización integrados como `get()` bloqueante, `task_done()` y `join()`.

5. **¿Qué diferencia existe entre la cola y el contador `trabajos_terminados`?**
   La **cola (`Queue`)** es una estructura de datos sincronizada que almacena y distribuye las tareas pendientes entre los hilos (vaciándose a medida que se consumen), mientras que **`trabajos_terminados`** es una variable entera simple compartida en memoria que lleva el recuento acumulado de tareas completadas y necesita protegerse explícitamente con un `Lock`.

---

## 4. Señal de inicio mediante `Event`

Instrucciones analizadas:
```python
evento_inicio.wait()
evento_inicio.set()
```

1. **¿Qué hace `wait()`?**
   Bloquea la ejecución del hilo que la llama mientras la bandera interna del evento sea `False`. Si la bandera ya es `True` (o cuando pasa a `True`), el hilo continúa inmediatamente.

2. **¿Qué hace `set()`?**
   Cambia el estado interno del evento a `True` y despierta simultáneamente a todos los hilos que estaban esperando en `wait()`.

3. **¿Cuántos consumidores se desbloquean al ejecutar `set()`?**
   Se desbloquean **todos los consumidores** que estaban esperando (**los 3 consumidores**).

4. **¿Por qué se ejecuta primero `start()` y después `evento_inicio.set()`?**
   Para que los 3 hilos consumidores ya estén creados, iniciados y listos esperando en el punto de sincronización (`evento_inicio.wait()`) antes de que el centro autorice el comienzo simultáneo del procesamiento.

5. **¿Qué ocurriría si se eliminara la llamada a `set()`?**
   La bandera del evento nunca pasaría a `True`, por lo que los 3 hilos consumidores quedarían bloqueados indefinidamente en `evento_inicio.wait()` y el programa principal también quedaría bloqueado esperando en `cola_trabajos.join()` (**interbloqueo / bloqueo indefinido**).

---

## 5. Límite de acceso mediante `Semaphore`

Instrucción analizada:
```python
semaforo_recurso = threading.Semaphore(2)
```

1. **¿Qué representa el valor 2?**
   Representa el número máximo de permisos o accesos simultáneos disponibles para entrar en la sección protegida por el semáforo (la capacidad del recurso externo).

2. **¿Cuántos consumidores pueden ejecutar simultáneamente `procesar_trabajo()` dentro del semáforo?**
   Como máximo **2 consumidores** al mismo tiempo dentro del bloque `with semaforo_recurso:`.

3. **¿Qué ocurre con un tercer consumidor que intenta acceder?**
   Queda **bloqueado en espera** a la entrada del bloque `with semaforo_recurso:` hasta que uno de los dos consumidores que están dentro finalice su trabajo y libere un permiso del semáforo.

4. **¿Qué diferencia existe entre `Semaphore(2)` y `Lock`?**
   Un `Lock` garantiza **exclusión mutua estricta** (solo **1 hilo** puede acceder a la vez), mientras que `Semaphore(2)` cuenta con un contador interno que permite que hasta **2 hilos** accedan de manera concurrente al recurso antes de bloquear al resto.

5. **¿Cuántos accesos permitiría `Semaphore(1)`?**
   Permitiría **1 único acceso simultáneo** (comportándose en la práctica de forma equivalente a una exclusión mutua en cuanto a capacidad de acceso concurrente).

---

## 6. Modificación del semáforo

> **[INSERTAR AQUÍ CAPTURA DE CONSOLA CON `threading.Semaphore(1)`]**
>
> **[INSERTAR AQUÍ CAPTURA DE CONSOLA CON `threading.Semaphore(2)`]**
>
> **[INSERTAR AQUÍ CAPTURA DE CONSOLA CON `threading.Semaphore(3)`]**

### Tabla de tiempos y accesos observados

| Capacidad | Tiempo total | Máximo de accesos simultáneos observado |
| :---: | :---: | :---: |
| **1** | ~17.01 segundos | 1 consumidor a la vez |
| **2** | ~10.01 segundos | 2 consumidores a la vez |
| **3** | ~8.01 segundos | 3 consumidores a la vez |

*(Nota: Los tiempos incluyen los 2 segundos iniciales de preparación del centro más el tiempo de procesamiento de los 8 trabajos cuya suma total de duraciones es 15 segundos).*

### Respuestas:
1. **¿Qué configuración ha tardado más?**
   La configuración con **`Semaphore(1)`** (~17.01 s), porque serializa por completo el acceso al recurso externo: los trabajos se ejecutan uno tras otro sin paralelismo en el recurso (2 s de espera inicial + 15 s de suma de duraciones).

2. **¿Qué configuración permite mayor concurrencia?**
   La configuración con **`Semaphore(3)`**, ya que permite que los 3 hilos consumidores existentes accedan al recurso simultáneamente sin tener que esperarse entre sí.

3. **¿Aumentar la capacidad garantiza siempre reducir el tiempo?**
   **No siempre.** Si aumentamos la capacidad del semáforo por encima del número de hilos consumidores (por ejemplo, `Semaphore(10)` habiendo solo 3 consumidores) o por encima del número de trabajos disponibles, no habrá más mejora de tiempo porque el límite pasará a estar en la cantidad de hilos trabajadores o en la duración individual de las tareas más largas.

4. **¿Qué valor representa mejor un recurso con dos conexiones disponibles?**
   El valor **`2` (`threading.Semaphore(2)`)**, pues modela exactamente dos permisos de acceso concurrente.

---

## 7. Contador compartido y `Lock`

Bloque analizado:
```python
with lock_contador:
    trabajos_terminados += 1
```

1. **¿Por qué `trabajos_terminados` es un dato compartido?**
   Porque es una variable global que es leída y modificada por los 3 hilos consumidores y posteriormente leída por el hilo principal para mostrar el resumen final.

2. **¿Qué parte del código constituye la sección crítica?**
   El bloque donde se modifica y consulta la variable global `trabajos_terminados`:
   ```python
   trabajos_terminados += 1
   print(
       f"[{hilo_actual}] "
       f"Trabajos terminados: "
       f"{trabajos_terminados}"
   )
   ```

3. **¿Qué riesgo existiría sin el `Lock`?**
   Existiría una **condición de carrera (*race condition*)**: dos o más hilos podrían leer el mismo valor de `trabajos_terminados` al mismo tiempo, incrementarlo por separado y sobrescribir el resultado, perdiéndose incrementos y mostrando conteos incoherentes o un total final menor de 8.

4. **¿Por qué todos los consumidores deben utilizar el mismo `Lock`?**
   Porque la exclusión mutua solo funciona si todos los hilos compiten por adquirir **el mismo candado (`lock_contador`)**. Si cada consumidor usara un `Lock` distinto, ningún hilo bloquearía a los demás y entrarían simultáneamente en la sección crítica.

5. **¿Debe incluirse `time.sleep(duracion)` dentro del `Lock`?**
   **No.** `time.sleep(duracion)` simula el trabajo sobre el recurso externo (que ya está regulado por el semáforo). Si se metiera dentro del `Lock`, ningún otro consumidor podría actualizar el contador ni avanzar mientras otro duerme, reduciendo innecesariamente la concurrencia. Las secciones críticas protegidas por `Lock` deben ser lo más breves posible.

---

## 8. `task_done()` y `cola.join()`

1. **¿Qué indica `cola_trabajos.task_done()`?**
   Notifica a la cola que un elemento previamente extraído con `get()` ya ha terminado de ser procesado por completo, decrementando el contador interno de tareas pendientes de la cola.

2. **¿Cuántas veces debe llamarse por cada elemento recuperado mediante `get()`?**
   Exactamente **una vez (`1`)** por cada elemento extraído con `get()`.

3. **¿Por qué también se llama a `task_done()` cuando el elemento es `None`?**
   Porque cada `None` fue introducido en la cola mediante `put(None)`, lo cual incrementó el contador interno de tareas pendientes de la cola. Si no se llamara a `task_done()` al recibir `None`, el contador de la cola nunca llegaría a cero y `cola_trabajos.join()` se quedaría bloqueado para siempre.

4. **¿Qué espera exactamente `cola_trabajos.join()`?**
   Espera hasta que **todos los elementos que han sido introducidos en la cola hayan sido extraídos y marcados como completados** mediante `task_done()` (es decir, hasta que el contador de tareas pendientes de la cola llegue a 0).

5. **¿Qué podría suceder si olvidamos un `task_done()`?**
   El contador interno de tareas pendientes de la cola nunca llegaría a cero y el programa principal se quedaría **bloqueado indefinidamente** en la línea `cola_trabajos.join()`.

---

## 9. Finalización mediante centinelas

Bloque analizado:
```python
for _ in consumidores:
    cola_trabajos.put(None)
```

1. **¿Qué representa `None`?**
   Representa un **valor centinela** (marca especial de finalización) que indica al consumidor que ya no quedan más trabajos por procesar y que debe terminar su ejecución.

2. **¿Por qué se introduce un `None` por cada consumidor?**
   Porque cuando un consumidor extrae un `None` de la cola con `get()`, ese elemento desaparece de la cola. Como hay 3 consumidores ejecutando un bucle infinito `while True:`, se necesitan **3 valores `None`** para que cada uno de los 3 hilos reciba su propia señal de parada.

3. **¿Qué ocurriría si solo se introdujera un `None`?**
   Solo **uno** de los consumidores finalizaría, mientras que los otros **dos consumidores quedarían bloqueados indefinidamente** en `cola_trabajos.get()` esperando más elementos, impidiendo que `hilo.join()` y el programa principal terminen.

4. **¿Por qué el consumidor ejecuta `break`?**
   Para salir del bucle infinito `while True:` una vez detectado el centinela `None`, permitiendo que la función `consumidor()` termine y el hilo finalice limpiamente.

5. **¿Es `None` un trabajo real?**
   **No.** No tiene nombre ni duración, no pasa por `procesar_trabajo()` ni incrementa el contador `trabajos_terminados`; es únicamente un mensaje de control para detener a los hilos consumidores.

---

## 10. Diferencia entre los dos `join()`

- **`cola_trabajos.join()`**:
  - **Selección correcta:** *Espera a que todos los elementos introducidos en la cola se marquen como completados.*
  - **Explicación:** Bloquea al hilo principal hasta que por cada `put()` realizado en la cola se haya ejecutado su correspondiente `task_done()`.

- **`hilo.join()`**:
  - **Selección correcta:** *Espera a que termine un hilo.*
  - **Explicación:** Bloquea al hilo principal hasta que el objeto `Thread` (`Consumidor-1`, `Consumidor-2` o `Consumidor-3`) haya finalizado completamente la ejecución de su función `consumidor()`.

---

## 11. Resumen de herramientas y sección crítica

### Identificación de la sección crítica
La sección crítica del programa se encuentra en la función `consumidor()`, en las líneas donde se incrementa y muestra la variable global compartida `trabajos_terminados`:
```python
with lock_contador:
    trabajos_terminados += 1
    print(f"[{hilo_actual}] Trabajos terminados: {trabajos_terminados}")
```

### Explicación de cada herramienta utilizada
- **`queue.Queue`**: Cola sincronizada (*thread-safe*) que permite comunicar al hilo productor (programa principal) con los hilos consumidores, repartiendo los trabajos de forma segura y coordinando su finalización con `get()`, `put()`, `task_done()` y `join()`.
- **`threading.Event`**: Mecanismo de señalización entre hilos mediante una bandera booleana interna que permite mantener a todos los consumidores en espera (`wait()`) hasta que el programa principal autoriza el arranque simultáneo (`set()`).
- **`threading.Semaphore`**: Primitiva de sincronización con contador interno que limita la cantidad máxima de hilos que pueden acceder al mismo tiempo a un recurso compartido de capacidad limitada (en este caso, 2 accesos simultáneos al recurso externo).
- **`threading.Lock`**: Candado de exclusión mutua que garantiza que un único hilo a la vez pueda entrar en la sección crítica para modificar el contador compartido `trabajos_terminados`, evitando condiciones de carrera.
- **Centinela (`None`)**: Valor especial introducido al final de la cola (uno por cada hilo consumidor) para indicarles de forma ordenada que no llegarán más trabajos y que deben salir del bucle `while True`.

---

## 12. Conclusión final

En esta práctica se ha comprobado cómo coordinar múltiples hilos de forma segura combinando distintas primitivas de sincronización en Python. La estructura `Queue` permite distribuir los trabajos entre los consumidores sin colisiones, mientras que el uso de valores centinela (`None`) garantiza que cada hilo salga limpiamente de su bucle cuando ya no quedan tareas. Mediante `Event`, todos los consumidores esperan una señal común antes de iniciar su ejecución, y con `Semaphore` se limita el número de accesos simultáneos al recurso externo, observándose que ampliar su capacidad de 1 a 3 reduce el tiempo total al incrementar la concurrencia. Por su parte, `Lock` protege la sección crítica del contador compartido `trabajos_terminados` para evitar condiciones de carrera al actualizar el progreso. Finalmente, combinar `cola.join()` —que espera a que todas las tareas de la cola se marquen con `task_done()`— y `hilo.join()` —que espera a que los hilos consumidores finalicen su ejecución— asegura un cierre ordenado y resultados exactos.
