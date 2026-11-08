# Laboratorio #4 Primera parte

**Curso:** Análisis de Algoritmos  
**Caso asignado:** Caso de estudio 1 — Conciliación nocturna del recaudo del Sistema Integrado de Transporte  
**Equipo #10:**
- Sara López Cardona
- Kevin Daniel Mendoza Castillo
- Pablo Andrés Tabares Cardona
- Andres Mauricio Agudelo Elorza

---

## 1. Análisis del problema

### 1.1 Contexto organizacional y descripción general
El Sistema Integrado de Transporte del Valle Metropolitano (SITVM) presta servicio de metro, dos líneas de cable aéreo y rutas de buses alimentadores a cerca de 4.000.000 de habitantes. Todas las noches, con las estaciones cerradas, un único servidor dedicado procesa por lotes las validaciones del día y, al cierre de cada mes, ejecuta la **Operación 4: liquidación del tope tarifario** de las tarjetas personalizadas.

Desde la entrada en operación de las rutas alimentadoras y la segunda línea de cable, el proceso nocturno supera las 8 horas e incumple la ventana operativa de 4 horas (00:00 a 04:00). En la liquidación del tope tarifario, el programa actual intenta explorar todas las combinaciones posibles de pases y, como no termina para las tarjetas con muchos días de viaje, recurre a una regla simplificada que ocasiona reclamos en Atención al Usuario por cobrar más que el mínimo en determinados meses y retrasa semanas el abono de saldos.

### 1.2 Entradas, salida, unidades y límites de la operación
Al cierre mensual, el sistema debe garantizar que ningún usuario con tarjeta personalizada haya pagado más que la combinación más económica de pasajes y pases capaz de cubrir todos sus viajes del mes.

| Elemento | Descripción técnica | Unidades y límites informados por el caso |
| :--- | :--- | :--- |
| **Entrada principal** (`viajes_por_dia`) | Lista de enteros `list[int]` de longitud $d$, donde el índice `0` corresponde al día 1 del periodo y cada posición contiene los viajes validados ese día (`0` si no viajó). | `viajes` $\in \mathbb{Z}_{\ge 0}$ (viajes/día); periodo mensual real $d \in \lbrace 28, 29, 30, 31 \rbrace$ días calendario. |
| **Entrada de conciliación** (`cobrado`) | Monto total descontado a la tarjeta a lo largo del mes antes de aplicar la devolución. | Entero no negativo en pesos colombianos (COP). |
| **Catálogo tarifario (perfil general)** | Cuatro productos vigentes:<br>1. Pasaje sencillo: **3.900 pesos** (1 viaje).<br>2. Pase diario: **9.500 pesos** (viajes ilimitados en 1 día calendario).<br>3. Pase semanal: **36.000 pesos** (viajes ilimitados en 7 días consecutivos).<br>4. Pase mensual: **135.000 pesos** (viajes ilimitados en 30 días consecutivos). | Precios enteros en pesos (COP); duraciones de cobertura en días calendario consecutivos ($1$, $7$ y $30$ días). |
| **Volumen operativo real** | Tarjetas personalizadas con al menos un viaje en el mes que deben liquidarse la noche de cierre. | Cerca de **950.000 tarjetas activas/mes** (sobre 3.200.000 tarjetas emitidas y ~1.400.000 validaciones en un día hábil típico). |
| **Salida** (`costo_minimo` / `liquidar_tope`) | `costo_minimo`: menor desembolso posible que cubre todos los viajes del periodo.<br>`liquidar_tope`: saldo a favor a abonar en la tarjeta ($\max(0, \text{cobrado} - \text{costo mínimo})$). | Enteros no negativos en pesos (COP). |

### 1.3 Restricciones del negocio y de infraestructura
1. **Exactitud financiera estricta:** la devolución acreditada debe ser exactamente la diferencia frente a la combinación más barata posible; ni un peso de menos para el usuario ni un peso de más para el sistema, y nunca un valor negativo.
2. **Ventana operativa nocturna:** en la noche de cierre de mes, la operación cuenta con la ventana de **4 horas (00:00 a 04:00, es decir, 14.400 s)** compartida con las operaciones nocturnas diarias antes del cargue de listas a las 04:30.
3. **Infraestructura fija:** un único servidor dedicado con consumo aproximado de **500 W (0,5 kW)** bajo carga sostenida, ejecutándose en memoria principal y en un solo hilo (sin procesamiento distribuido ni paralelo).
4. **Trazabilidad:** las secuencias y registros originales de validaciones no deben alterarse durante el cálculo para respaldar eventuales reclamaciones ante Atención al Usuario.

### 1.4 Supuestos realizados por el equipo
1. **Meses de 28, 29, 30 y 31 días y bordes del periodo:** de acuerdo con la tabla tarifaria del SITVM, el pase mensual cubre **exactamente 30 días consecutivos** (no el mes calendario completo cuando $d = 31$). En un mes de 31 días con viajes diarios, un pase mensual cubre un tramo de 30 días (por ejemplo, días 1 al 30 o días 2 al 31) y el día restante se cubre con el producto adicional que resulte más económico. Asimismo, como cada cierre mensual se concilia de manera independiente, si un pase semanal o mensual adquirido hacia el final del mes rebasa el día $d$, su cobertura dentro de la liquidación se trunca en $d$ sin trasladar días sobrantes al mes siguiente.
2. **Interpretación de la regla simplificada actual (`costo_regla_actual`):** el enunciado establece que *«cada día se cobra lo más barato entre los pasajes sencillos y el pase diario, y se aplica el pase semanal o mensual si la suma ya lo supera»*. Modelamos esta regla agrupando el periodo en bloques consecutivos de hasta 30 días y, dentro de cada bloque mensual, en cortes semanales fijos de hasta 7 días consecutivos (días 1–7, 8–14, 15–21, 22–28 y días restantes): cada día se valora con $\min(v_t \times 3.900, 9.500)$; si el acumulado de un corte de 7 días supera 36.000 pesos se reemplaza por 36.000 pesos, y si la suma de cortes semanales dentro del bloque de 30 días supera 135.000 pesos se reemplaza por 135.000 pesos. De esta manera, todo cobro producido por la regla corresponde a una combinación legal de productos del SITVM.
3. **Perfil tarifario evaluado:** se modela el perfil general vigente, dado que el caso indica que los perfiles diferenciales (estudiante, adulto mayor, discapacidad) mantienen la misma estructura de productos con valores menores; el algoritmo solo recibe constantes tarifarias distintas sin cambiar su lógica ni su complejidad.
4. **Supuestos generales permitidos:** la serie diaria de viajes por tarjeta ya llega íntegra y validada en memoria principal, sin cambios concurrentes durante la corrida nocturna.

---

## 2. Diseño de la solución

### 2.1 Estructuras de datos seleccionadas
Se emplean listas contiguas indexadas por día (`list[int]` en Python). Tanto la serie de entrada `viajes_por_dia` (longitud $d$) como la tabla de programación dinámica `costo` (longitud $d + 2$, indexada de $1$ a $d+1$) requieren acceso posicional directo en tiempo $O(1)$ hacia los estados $t+1$, $t+7$ y $t+30$, sin necesidad de estructuras enlazadas ni tablas hash.

### 2.2 Estrategia elegida: programación dinámica sobre los días del periodo

#### Por qué el problema admite programación dinámica
Cubrir los viajes del mes con el menor gasto exhibe las dos propiedades estructurales que hacen aplicable la programación dinámica:

1. **Subestructura óptima:** sea $C(t)$ el costo mínimo para cubrir todos los viajes desde el día $t$ hasta el día $d$, suponiendo que los días $1, \dots, t-1$ ya quedaron cubiertos. Si en el día $t$ hay viajes ($v_t > 0$), cualquier solución óptima para $[t, d]$ debe adquirir algún producto que empiece en $t$ y cubra hasta cierto día $t + L - 1$ (con $L \in \lbrace 1, 7, 30 \rbrace$), dejando sin cubrir el sufijo $[t + L, d]$. Por el argumento de cortar y pegar, la forma en que dicha solución cubre $[t + L, d]$ tiene que costar exactamente el mínimo $C(t + L)$: si existiera otra combinación válida más barata para $[t + L, d]$, bastaría sustituirla y el costo total en $[t, d]$ disminuiría, contradiciendo la optimalidad supuesta.
2. **Subproblemas traslapados:** múltiples combinaciones de compras en los primeros días desembocan exactamente en el mismo día futuro por cubrir. Por ejemplo, llegar al día 8 habiendo pagado siete días individuales (mezclando pasajes sencillos y pases diarios) o habiendo comprado un pase semanal el día 1 conduce al mismo subproblema restante $C(8)$. Una exploración exhaustiva recalcula $C(8)$ repetidamente en cada rama que aterriza en el día 8, mientras que la programación dinámica calcula y almacena cada $C(t)$ una única vez.

#### Estado, caso base, recurrencia y orden de llenado
Definimos el estado mediante un único entero $t \in \lbrace 1, 2, \dots, d + 1 \rbrace$:
- **Estado $C(t)$:** costo mínimo en pesos para cubrir todos los viajes comprendidos entre el día $t$ y el día $d$ inclusive. El costo óptimo de todo el periodo es $C(1)$.
- **Caso base:** cuando ya no restan días por cubrir, el desembolso es nulo:

$$
C(d + 1) = 0
$$

Si un pase semanal ($t + 7$) o mensual ($t + 30$) rebasa el final del periodo, el primer día sin cubrir se trunca al caso base mediante $\min(t + L, d + 1)$.
- **Ecuación de recurrencia:** para cada día $t \in \lbrace 1, \dots, d \rbrace$ con $v_t =$ `viajes_por_dia[t - 1]` viajes:
  - Si $v_t = 0$ (día sin viajes), no es necesario comprar producto alguno en $t$, pues iniciar un pase en un día vacío nunca cubre más viajes que iniciarlo en el siguiente día activo:

$$
C(t) = C(t + 1) \quad (\text{si } v_t = 0)
$$

  - Si $v_t > 0$, se toma la alternativa de menor costo entre cubrir únicamente el día $t$ (eligiendo entre $v_t$ pasajes sencillos o un pase diario), adquirir un pase semanal de 7 días o adquirir un pase mensual de 30 días:

$$
C(t) = \min \begin{cases}
\min(3.900 \cdot v_t, 9.500) + C(t + 1) & \text{(cubrir solo el día } t\text{)} \\
36.000 + C(\min(t + 7, d + 1)) & \text{(pase semanal: 7 días)} \\
135.000 + C(\min(t + 30, d + 1)) & \text{(pase mensual: 30 días)}
\end{cases}
$$

- **Orden de llenado (tabulación):** dado que $C(t)$ depende exclusivamente de estados posteriores ($t+1$, $t+7$ y $t+30$), la tabla se llena **de atrás hacia adelante**, empezando en $C(d+1) = 0$ y recorriendo $t = d, d-1, \dots, 1$. Al terminar el ciclo, todas las dependencias han sido resueltas en $O(1)$ cada una y la solución óptima se lee en $C(1)$.

### 2.3 Ejemplo resuelto a mano paso a paso ($d = 8$ días)
Consideremos una instancia de 8 días con `viajes_por_dia = [1, 3, 2, 0, 3, 2, 3, 2]`. Partimos del caso base $C(9) = 0$ y llenamos la tabla desde el día 8 hasta el día 1:

| Día $t$ | Viajes $v_t$ | Cubrir solo hoy: $\min(3.900 v_t, 9.500) + C(t+1)$ | Pase semanal: $36.000 + C(\min(t+7, 9))$ | Pase mensual: $135.000 + C(9)$ | $C(t)$ óptimo | Elección en $t$ |
| :---: | :---: | :--- | :--- | :--- | :---: | :---: |
| **9** | — | — | — | — | **0** | Caso base |
| **8** | 2 | $\min(7.800, 9.500) + C(9) = 7.800 + 0 = 7.800$ | $36.000 + C(9) = 36.000$ | $135.000$ | **7.800** | 2 pasajes |
| **7** | 3 | $\min(11.700, 9.500) + C(8) = 9.500 + 7.800 = 17.300$ | $36.000 + C(9) = 36.000$ | $135.000$ | **17.300** | Pase diario |
| **6** | 2 | $7.800 + C(7) = 7.800 + 17.300 = 25.100$ | $36.000 + C(9) = 36.000$ | $135.000$ | **25.100** | 2 pasajes |
| **5** | 3 | $9.500 + C(6) = 9.500 + 25.100 = 34.600$ | $36.000 + C(9) = 36.000$ | $135.000$ | **34.600** | Pase diario |
| **4** | 0 | Día sin viajes: $C(4) = C(5) = 34.600$ | — | — | **34.600** | Nada (saltar) |
| **3** | 2 | $7.800 + C(4) = 7.800 + 34.600 = 42.400$ | $36.000 + C(9) = 36.000$ | $135.000$ | **36.000** | Pase semanal |
| **2** | 3 | $9.500 + C(3) = 9.500 + 36.000 = 45.500$ | $36.000 + C(9) = 36.000$ | $135.000$ | **36.000** | Pase semanal |
| **1** | 1 | $3.900 + C(2) = 3.900 + 36.000 = 39.900$ | $36.000 + C(8) = 36.000 + 7.800 = 43.800$ | $135.000$ | **39.900** | 1 pasaje |

- **Reconstrucción de la compra óptima:** iniciando en $t = 1$, la elección es **1 pasaje sencillo** (3.900 pesos) y se avanza a $t = 2$; en $t = 2$, la elección es **pase semanal** (36.000 pesos), que cubre los 7 días consecutivos del día 2 al día 8 y salta directamente a $t = 9$ (fin). Las elecciones intermedias de los días 3 a 8 no se ejecutan porque quedaron cubiertas por el pase del día 2. El costo mínimo total es $C(1) =$ **39.900 pesos** (nótese que comprar el semanal en el día 1 habría dejado descubierto el día 8, costando 43.800 pesos).

---

## 3. Implementación

### 3.1 Módulos desarrollados
Todo el código de la operación se encuentra modularizado dentro de `src/tope_tarifario/`:

- [`src/tope_tarifario/estrategia.py`](src/tope_tarifario/estrategia.py): implementa `costo_minimo` y `liquidar_tope` mediante programación dinámica iterativa por tabulación, además de `calcular_tabla_y_elecciones`, `reconstruir_compras` y `costo_minimo_conteo`.
- [`src/tope_tarifario/exhaustivo.py`](src/tope_tarifario/exhaustivo.py): implementa `costo_exhaustivo` (y `costo_exhaustivo_conteo`), explorando recursivamente las cuatro alternativas de productos en cada día con viajes sin almacenar resultados previos.
- [`src/tope_tarifario/regla_actual.py`](src/tope_tarifario/regla_actual.py): implementa `costo_regla_actual` (y `costo_regla_actual_conteo`), que reproduce la regla simplificada vigente por topes diarios, semanales y mensuales en bloques consecutivos.
- [`src/tope_tarifario/pruebas.py`](src/tope_tarifario/pruebas.py): suite reproducible de verificaciones con `assert` sobre casos límite, traza manual, instancias aleatorias, restricción exacta de devolución y contraejemplos.
- [`src/tope_tarifario/datos.py`](src/tope_tarifario/datos.py) y [`src/tope_tarifario/medicion.py`](src/tope_tarifario/medicion.py): generación sintética con semilla fija, banco de cronometraje, conteo de operaciones y creación automatizada de gráficas con `matplotlib`.

### 3.2 Decisiones de implementación relevantes
1. **Tabulación iterativa en lugar de memoización recursiva:** implementar `costo_minimo` con un ciclo `for t in range(d, 0, -1)` evita el sobrecosto de llamadas recursivas en Python y elimina por completo el límite de profundidad de recursión (`RecursionError`) al escalar a $d = 20\,000$ días durante las pruebas de extrapolación.
2. **Desacoplamiento entre cronometraje y conteo de operaciones:** en lugar de incrementar un contador global dentro de `costo_minimo`, `costo_regla_actual` y `costo_exhaustivo`, se implementaron funciones gemelas sufijadas con `_conteo`. Así, la medición con `time.perf_counter()` refleja el tiempo real del algoritmo puro sin contaminación por instrumentación adicional, y en `pruebas.py` se verifica con `assert` que ambas variantes devuelvan siempre el mismo costo.
3. **Exploración fiel de los 4 productos en la búsqueda exhaustiva:** en cada día con viajes, `costo_exhaustivo` ramifica explícitamente sobre los cuatro productos del SITVM (pasajes sencillos del día, pase diario, pase semanal y pase mensual) sin precolapsar decisiones locales. Esto verifica de forma independiente el modelo tarifario completo y refleja por qué la solución actual del cliente colapsa cuando una tarjeta acumula muchos días de viaje en el mes.
4. **Inmutabilidad de las entradas:** ninguna función modifica la lista `viajes_por_dia` recibida, preservando la trazabilidad exigida por el negocio.

---

## 4. Evaluación del desempeño

### 4.1 Complejidad temporal y espacial
Sea $d$ el número total de días del periodo evaluado, $m \le d$ la cantidad de días con al menos un viaje ($v_t > 0$) y $k = 4$ el número constante de productos en la tabla tarifaria:

| Solución | Complejidad temporal | Complejidad espacial auxiliar | Justificación analítica |
| :--- | :---: | :---: | :--- |
| **Programación dinámica (`costo_minimo`)** | $\Theta(d)$ | $\Theta(d)$ | Recorre exactamente $d$ estados una vez; en cada día evalúa a lo sumo $k = 4$ opciones en $O(1)$, luego $\Theta(d \cdot k) = \Theta(d)$ sin importar cuántos días tengan viajes. Reserva un arreglo `costo` de longitud $d + 2$, es decir $\Theta(d)$ enteros (nota: si no se requiere reconstruir compras, bastaría incluso una ventana circular de 31 posiciones en $\Theta(1)$ espacio). |
| **Regla simplificada actual (`costo_regla_actual`)** | $\Theta(d)$ | $\Theta(1)$ | Recorre una sola vez los $d$ días agrupados en tramos de 7 y 30 posiciones, efectuando una cantidad constante de sumas y comparaciones por día y un puñado de acumuladores escalares en memoria. |
| **Búsqueda exhaustiva (`costo_exhaustivo`)** | $\Theta(d + r^m)$ con $r \approx 2,0066$ | $\Theta(d)$ | En los $d - m$ días sin viaje avanza sin ramificar, pero en cada día con viaje abre 4 llamadas recursivas: dos de salto 1 (pasajes sencillos y pase diario), una de salto 7 y una de salto 30. En el peor caso ($m = d$), $T(m) = 2T(m-1) + T(m-7) + T(m-30) + \Theta(1)$, cuya raíz característica es $r \approx 2,0066$ ($\Omega(2^m)$, crecimiento exponencial en los días con viaje). La pila de recursión alcanza profundidad máxima $d$, ocupando $\Theta(d)$ marcos de activación. |

**Contraste teórico:** mientras el enfoque exhaustivo duplica con creces su trabajo por cada nuevo día activo del usuario (pasando de ~1.000 combinaciones con 10 días activos a más de $10^9$ con 30 días activos), la programación dinámica reutiliza los estados ya tabulados y reduce el tiempo a crecimiento estrictamente lineal $\Theta(d)$, empatando el orden asintótico de la regla simplificada actual pero garantizando optimalidad exacta.

### 4.2 Verificación de las implementaciones
El script [`src/tope_tarifario/pruebas.py`](src/tope_tarifario/pruebas.py) verifica automáticamente mediante `assert`:
- **Casos límite:** lista vacía (`[]`), un solo día con 0, 1, 2, 3 y 10 viajes, meses de 30 días sin viajes (`[0]*30`), semanas intensivas (`[4]*7`), pases semanales que convienen aunque sobren días (`[5]*5`), meses intensivos de 30 días (`[4]*30`), meses de 31 días (`[4]*31` y `[1] + [4]*30`) e inmutabilidad de la lista de entrada.
- **Traza manual:** coincidencia exacta en `viajes_por_dia = [1, 3, 2, 0, 3, 2, 3, 2]` tanto en el valor óptimo (`39.900` pesos) como en cada casilla $C(1) \dots C(9)$ y en la secuencia reconstruida `[(1, 'pasajes'), (2, 'semanal')]`.
- **100 instancias aleatorias pequeñas (`semilla = 2026`, $0 \le d \le 14$):** igualdad estricta `costo_minimo(v) == costo_exhaustivo(v)`, validación independiente de que las compras reconstruidas cubren todos los días con viajes y suman exactamente el óptimo, y verificación de que `costo_regla_actual(v) >= costo_minimo(v)`.
- **Restricción del negocio y contraejemplo:** exactitud al peso y no negatividad de `liquidar_tope`, más el sobrecobro de `costo_regla_actual` en los contraejemplos de 10, 30 y 31 días.

### 4.3 Diseño experimental, mediciones y gráficas
Los experimentos se implementaron en [`src/tope_tarifario/datos.py`](src/tope_tarifario/datos.py) y [`src/tope_tarifario/medicion.py`](src/tope_tarifario/medicion.py) bajo las siguientes condiciones reproducibles:
- **Semilla e instancias:** semilla base fija `2026`; para cada tamaño $d$ se pregeneran **15 instancias sintéticas** con probabilidad diaria de viaje del $90\,\%$ (entre 1 y 5 viajes por día activo), de modo que los días con viaje $m$ crecen proporcionalmente con $d$. Las tres soluciones se evalúan exactamente sobre los mismos lotes.
- **Cronometraje:** se mide exclusivamente la llamada a cada función con `time.perf_counter()` (nunca la generación de datos ni el conteo de operaciones). Para amortiguar el ruido del reloj en microsegundos se promedian 400 repeticiones por lote en $d \le 100$, 80 en $500 \le d \le 2.500$ y 25 en $d \ge 5.000$; para la solución exhaustiva se usan 20 repeticiones en $d \le 12$, 5 en $d = 16$ y 2 en $d = 20$, verificando previamente con `assert` que `costo_minimo` y `costo_exhaustivo` coinciden en todas las instancias.

#### Resultados en periodos cortos ($d = 4$ a $20$ días)

| Tamaño $d$ (días) | Días con viaje medios ($m$) | Tiempo PD (µs) | Tiempo Regla (µs) | Tiempo Exhaustivo (ms) | Operaciones PD | Operaciones Regla | Operaciones Exhaustivo |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **4** | 3,8 | 0,00223 | 0,00140 | 0,0092 | 15,4 | 9,8 | 54,7 |
| **6** | 5,4 | 0,00299 | 0,00162 | 0,0329 | 22,2 | 13,4 | 196,3 |
| **8** | 7,3 | 0,00393 | 0,00241 | 0,1232 | 29,8 | 19,3 | 759,6 |
| **10** | 9,0 | 0,00465 | 0,00251 | 0,4217 | 37,0 | 23,0 | 2.616,3 |
| **12** | 10,9 | 0,00548 | 0,00280 | 1,7647 | 44,8 | 26,9 | 10.856,1 |
| **16** | 14,7 | 0,00736 | 0,00366 | 20,7425 | 60,0 | 36,7 | 129.402,0 |
| **20** | 17,6 | 0,00861 | 0,00414 | 235,9748 | 72,8 | 43,6 | 1.447.321,9 |

#### Resultados en tamaños grandes para sostener la extrapolación ($d = 30$ a $20.000$ días)

| Tamaño $d$ (días) | Tiempo PD (ms) | Tiempo Regla actual (ms) | Operaciones PD | Operaciones Regla actual |
| :---: | :---: | :---: | :---: | :---: |
| **30** | 0,0128 | 0,0067 | 109,4 | 66,5 |
| **100** | 0,0437 | 0,0205 | 366,8 | 222,9 |
| **500** | 0,2479 | 0,1041 | 1.852,6 | 1.116,9 |
| **1.000** | 0,5133 | 0,2289 | 3.697,0 | 2.233,0 |
| **2.500** | 1,3569 | 0,5458 | 9.246,8 | 5.582,9 |
| **5.000** | 2,6743 | 1,0728 | 18.521,4 | 11.173,1 |
| **10.000** | 5,5641 | 2,1759 | 37.016,2 | 22.339,4 |
| **20.000** | 10,8823 | 4,2381 | 74.013,4 | 44.670,5 |

![Tiempo medio frente al tamaño d](graficas/tope_tarifario/tiempo_vs_n.png)

![Operaciones elementales frente al tamaño d](graficas/tope_tarifario/operaciones_vs_n.png)

#### Medición sintética de mejora en la liquidación para los usuarios
Al evaluar 5.000 tarjetas sintéticas mensuales representativas de cuatro perfiles de movilidad urbana en [`medicion.py`](src/tope_tarifario/medicion.py):
- **En meses de 30 días:** la regla simplificada actual cobra de más al **31,40 %** de las tarjetas, con un sobrecobro medio de **8.885 pesos** por tarjeta afectada (hasta un máximo observado de **28.500 pesos**). Extrapolado a las 950.000 tarjetas del SITVM, equivale a cerca de **2.650 millones de pesos** mensuales que la programación dinámica liquida de forma justa.
- **En meses de 31 días:** el porcentaje de tarjetas afectadas sube al **37,68 %** (sobrecobro medio de **8.553 pesos** por afectada), dado que los cortes fijos tampoco pueden desplazar el inicio del pase de 30 días hacia los días de mayor demanda.

### 4.4 Contraste entre lo medido y la complejidad teórica esperada
Tomando las parejas donde el segundo tamaño duplica al primero ($d = 10 \to 20$ en la zona con exhaustiva y $d = 10.000 \to 20.000$ en la zona asintótica):

| Pareja $(d \to 2d)$ | Solución | Multiplicador de operaciones | Multiplicador de tiempo | Esperado por la teoría |
| :---: | :--- | :---: | :---: | :--- |
| **$10 \to 20$** | Programación dinámica | **1,97x** ($37,0 \to 72,8$) | **1,85x** ($4,65 \to 8,61\ \mu\text{s}$) | $\Theta(d) \implies 2,00\text{x}$ |
| **$10 \to 20$** | Regla actual | **1,90x** ($23,0 \to 43,6$) | **1,65x** ($2,51 \to 4,14\ \mu\text{s}$) | $\Theta(d) \implies 2,00\text{x}$ |
| **$10 \to 20$** | Búsqueda exhaustiva | **553,20x** ($2.616 \to 1.447.322$) | **559,52x** ($0,4217 \to 235,9748\text{ ms}$) | $\Theta(r^m) \implies r^{\Delta m}$ |
| **$10.000 \to 20.000$** | Programación dinámica | **2,00x** ($37.016 \to 74.013$) | **1,96x** ($5,56 \to 10,88\text{ ms}$) | $\Theta(d) \implies 2,00\text{x}$ |
| **$10.000 \to 20.000$** | Regla actual | **2,00x** ($22.339 \to 44.671$) | **1,95x** ($2,18 \to 4,24\text{ ms}$) | $\Theta(d) \implies 2,00\text{x}$ |

**Explicación de coincidencias y diferencias:**
1. En $d = 10 \to 20$, el conteo de operaciones de PD ($1,97\text{x}$) y de la regla actual ($1,90\text{x}$) prácticamente clava el factor teórico $2\text{x}$ (la leve variación proviene de que el lote de $d=20$ promedió $17,6$ días activos frente a $9,0$ en $d=10$, y los días en cero ejecutan 1 operación en vez de 4). En tiempo ($1,86\text{x}$ y $1,63\text{x}$), el multiplicador es ligeramente menor que $2$ porque a escala de $2\text{ a }5\ \mu\text{s}$ el costo fijo $b_0$ de invocar la función y reservar la lista en Python pesa una fracción apreciable de $T(d) = c \cdot d + b_0$. Cuando pasamos a $d = 10.000 \to 20.000$ (panel derecho de ambas gráficas), $b_0$ se vuelve despreciable y la recta teórica aparece con nitidez: **2,00x** en operaciones y **2,04x** (PD) / **2,07x** (regla actual) en tiempo.
2. En la búsqueda exhaustiva, pasar de $d = 10$ ($m = 9,0$ días con viaje) a $d = 20$ ($m = 17,6$ días con viaje) incrementa $\Delta m = 8,6$ días activos. Si todos los días tuvieran viaje ($\Delta m = 10$), esperaríamos $\approx 2,0066^{10} \approx 1.058\text{x}$; con $\Delta m = 8,6$ días activos, la teoría predice $\approx 2^{8,6} \text{ a } 2,08^{8,6} \approx 388\text{x a } 550\text{x}$ (considerando la dispersión exponencial entre instancias del lote donde aquellas con $m = 19$ o $20$ dominan la media). Además, la razón de tiempos (**558,33x**) calca la razón de operaciones (**553,20x**) con menos de $1\,\%$ de diferencia, confirmando que el tiempo está gobernado directamente por la explosión combinatoria del árbol recursivo.

### 4.5 Extrapolación al volumen real y cumplimiento de la ventana operativa
Las cifras siguientes son **estimaciones por extrapolación** a partir de las curvas medidas en este equipo para el volumen real del cierre mensual del SITVM: $N = 950.000$ tarjetas activas con periodos mensuales de $d = 30$ días, frente a la ventana nocturna disponible de **4 horas (14.400 s)**:

1. **Programación dinámica (`estrategia`):** como la gráfica derecha demuestra crecimiento lineal en $d$ y las $N$ tarjetas se liquidan secuencialmente de forma independiente, el tiempo total escala linealmente con $N$: $T_{\text{total}} = N \times T_{\text{PD}}(30)$. Con $T_{\text{PD}}(30) = 12,76\ \mu\text{s}$/tarjeta medido directamente (pendiente asintótica: $0,5441\ \mu\text{s}$/día):

$$T_{\text{PD}}(950.000) \approx 950.000 \times 12,76 \times 10^{-6}\text{ s} \approx \mathbf{12,12\text{ segundos}} \quad (0,00337\text{ h})$$

   **¿Cabe en la ventana?** Sí: consume el **0,0842 %** de las 4 horas. (El cálculo solo contempla el tiempo de CPU de la función medida).
2. **Regla simplificada actual (`regla_actual` ejecutada de forma aislada):** también es lineal en $d$ y en $N$. Con $T_{\text{regla}}(30) = 6,70\ \mu\text{s}$/tarjeta:

$$T_{\text{regla}}(950.000) \approx 950.000 \times 6,70 \times 10^{-6}\text{ s} \approx \mathbf{6,37\text{ segundos}} \quad (0,00177\text{ h})$$

   Cabe en la ventana en tiempo de cómputo, pero **incumple la restricción obligatoria de negocio** al devolver menos saldo del debido en más de tres de cada diez tarjetas.
3. **Solución exhaustiva (`exhaustivo`):** aquí **no puede aplicarse una regla de tres**, porque el tiempo crece exponencialmente con los días con viaje $m$ según $T_{\text{exh}}(m) \approx T_{\text{exh}}(17,6) \cdot r^{\,m - 17,6}$, donde la tasa empírica medida entre $d=10$ y $d=20$ es $r = (171,38 / 0,3070)^{1/8,6} \approx 2,086$.
   - Para **una sola tarjeta** de un usuario frecuente que viaja $m = 27$ días en el mes ($90\,\%$ de 30 días), el tiempo estimado sube a $0,17138\text{ s} \times 2,086^{9,4} \approx \mathbf{172,3\text{ segundos}}$ ($\approx 2,9\text{ minutos}$ por tarjeta; y si viajó los $m = 30$ días, supera los **26 minutos para esa única tarjeta**).
   - Si tan solo el $15\,\%$ de los usuarios del SITVM ($142.500$ tarjetas intensivas con $m \approx 27$) se procesara con la solución exhaustiva, la corrida tomaría $\approx \mathbf{6.822\text{ horas}}$ ($\approx \mathbf{284\text{ días}}$ ininterrumpidos de servidor). Para tarjetas que viajan más de ~22 días al mes, el volumen real **sencillamente no termina** dentro de la ventana nocturna ni antes del cierre del mes siguiente, explicando por qué el programa actual del SITVM colapsa y debe abortar hacia la regla simplificada.

---

## 5. Análisis comparativo

### 5.1 Limitación de la regla actual: contraejemplo calculado
La regla simplificada falla porque toma decisiones locales y cierra bloques sin anticipar los viajes de los días siguientes. Considere la siguiente instancia de **10 días** (cuyo resultado es idéntico si se completa con 20 días sin viajes hasta cerrar un mes de 30 días):

$$\text{viajes por dia} = [1,\; 1,\; 1,\; 3,\; 3,\; 3,\; 3,\; 3,\; 3,\; 3]$$

- **Cálculo con la regla actual (`costo_regla_actual`):**
  1. Costo diario individual $\min(3.900 \cdot v_t,\; 9.500)$: días 1, 2 y 3 cuestan $3.900$ pesos cada uno; días 4 al 10 tienen 3 viajes ($11.700 > 9.500$), por lo que aplican pase diario a $9.500$ pesos cada uno.
  2. Primer bloque semanal (días 1 al 7): suma $3 \times 3.900 + 4 \times 9.500 = 11.700 + 38.000 = 49.700$ pesos. Como supera $36.000$, la regla aplica el pase semanal en los días 1 al 7 y cobra **36.000 pesos**, desperdiciando tres días del pase semanal en días baratos de un solo viaje.
  3. Segundo bloque semanal (días 8 al 10): suma $3 \times 9.500 = 28.500$ pesos. Como no supera $36.000$, cobra **28.500 pesos**.
  4. Total mensual: $36.000 + 28.500 =$ **64.500 pesos** (no supera el mensual de $135.000$).
- **Cálculo óptimo (`costo_minimo` y `costo_exhaustivo`):**
  1. Días 1, 2 y 3: se cubren con 3 pasajes sencillos = $3 \times 3.900 =$ **11.700 pesos**.
  2. Día 4: se adquiere un único **pase semanal** que cubre los 7 días consecutivos de alta demanda (días 4 al 10) = **36.000 pesos**.
  3. Total óptimo: $11.700 + 36.000 =$ **47.700 pesos**.
- **Diferencia (sobrecobro al usuario):** $64.500 - 47.700 =$ **16.800 pesos cobrados de más** (es decir, 16.800 pesos de devolución que el usuario pierde injustamente). Nótese además que incluso si una regla voraz activara el pase semanal apenas el acumulado corrido superara 36.000 pesos (lo cual ocurre el día 7), cometería exactamente el mismo error y cobraría los mismos 64.500 pesos. En meses de 31 días ocurre un desfase análogo con el pase mensual: en `[1] + [4]*30`, la regla cobra $135.000 + 9.500 = 144.500$ pesos frente al óptimo de $3.900 + 135.000 = 138.900$ pesos (**5.600 pesos de más**).

### 5.2 La condición contraria: ¿qué tendría que cambiar para que una estrategia voraz fuera óptima?
Una estrategia voraz sería óptima y no haría falta programación dinámica si cambiara cualquiera de estas dos reglas del negocio:
1. **Ausencia de pases multidiarios:** si el catálogo tarifario solo ofreciera pasaje sencillo (3.900 pesos) y pase diario (9.500 pesos), eliminando los pases semanal y mensual, la compra de un día no cubriría ningún día posterior. Las decisiones diarias serían independientes entre sí y elegir cada día $\min(3.900 \cdot v_t,\; 9.500)$ cumpliría la propiedad de elección voraz sin necesidad de reconsiderar días pasados.
2. **Pases restringidos a bloques calendario fijos y disjuntos:** si las condiciones comerciales definieran el pase semanal exclusivamente para semanas fijas del calendario (días 1–7, 8–14, 15–21, 22–28) y el pase mensual para la totalidad fija del mes (días 1 al $d$), ningún pase podría desplazarse ni solapar fronteras entre semanas; entonces aplicar vorazmente el mínimo por día, luego por semana fija y luego por el mes completo produciría siempre el óptimo exacto. Precisamente porque los pases reales cubren *cualquier* ventana de 7 o 30 días consecutivos es indispensable la programación dinámica.

### 5.3 Recomendación técnica para el SITVM
Recomendamos a la Gerencia de Tecnología **adoptar la estrategia de programación dinámica por tabulación (`costo_minimo` y `liquidar_tope`)** para reemplazar tanto la exploración exhaustiva como la regla simplificada de respaldo:
- **Ganancias frente al esquema actual:**
  1. **Cumplimiento estricto del negocio y fin de las quejas:** garantiza devoluciones exactas al peso para el 100 % de las tarjetas personalizadas (eliminando sobrecobros que en datos sintéticos perjudican a más del 31 % de los usuarios).
  2. **Velocidad equivalente a la regla simplificada:** liquida las 950.000 tarjetas del mes en ~7,7 segundos (frente a ~4,6 segundos de la regla errónea y frente al colapso de horas/meses de la búsqueda exhaustiva), eliminando las semanas de retraso en la acreditación de saldos.
- **Riesgos y límites que la organización debe conocer:**
  1. **Crecimiento del volumen de tarjetas:** ante una expansión del 30 % en tarjetas activas (~1.235.000 tarjetas), el tiempo de `costo_minimo` subiría linealmente de ~7,7 s a ~10,0 s, manteniendo intacta la viabilidad dentro de las 4 horas; sin embargo, esta función recibe `viajes_por_dia` ya consolidado por tarjeta, de modo que la preparación previa de los conteos diarios desde el archivo crudo de validaciones debe escalar igualmente en tiempo lineal o casi lineal para no trasladar allí el cuello de botella.
  2. **Cambios en la estructura tarifaria:** como la complejidad exacta es $\Theta(d \cdot k)$, si en el futuro se introdujeran decenas de pases nuevos ($k$ grande) la constante crecería proporcionalmente a $k$; y si se crearan pases que no cubran días calendario completos sino bolsas de horas, zonas o transbordos acumulados, el estado ya no sería solo el día $t$ y habría que ampliar la dimensión de la tabla.
  3. **Definición comercial entre meses consecutivos:** tecnología y recaudo deben dejar estipulado contractualmente que el tope se liquida por mes calendario cerrado (o, si algún día se permitiera que un pase de 30 días comprado el día 20 cubra hasta el día 19 del mes siguiente, persistir como estado inicial del nuevo mes los días ya cubiertos por cada tarjeta).

---

## 6. Implicaciones éticas, sociales y ambientales

### 6.1 Consumo energético
Con la potencia informada por el cliente para el servidor dedicado bajo carga sostenida ($P = 500\text{ W} = 0,5\text{ kW}$) y la relación $E\text{ (kWh)} = P\text{ (kW)} \times t\text{ (h)}$, presentamos las **estimaciones** de consumo eléctrico para liquidar las 950.000 tarjetas mensuales y su proyección a un año de operación (12 cierres de mes):

| Escenario evaluado (950.000 tarjetas/mes) | Tiempo estimado por cierre | Energía por cierre mensual (kWh) | Proyección anual — 12 cierres (kWh/año) | Viabilidad operativa y financiera |
| :--- | :---: | :---: | :---: | :--- |
| **Estrategia propuesta (Programación dinámica)** | 7,73 s (0,00215 h) | **0,00107 kWh** (1,07 Wh) | **0,01289 kWh/año** (12,9 Wh/año) | Viable y óptima (100 % exacta). |
| **Regla simplificada aislada (`regla_actual`)** | 4,58 s (0,00127 h) | **0,00064 kWh** (0,64 Wh) | **0,00763 kWh/año** (7,6 Wh/año) | Inviable por negocio (sobrecobra a >31 % de tarjetas). |
| **Proceso híbrido actual del SITVM** *(exhaustiva hasta agotar ventana >4 h de desborde + regla simplificada)* | > 4,0 h de desborde nocturno | **> 2,00 kWh** | **> 24,00 kWh/año** | Desborda la ventana nocturna y genera sobrecobros. |
| **Búsqueda exhaustiva pura** *(estimada solo sobre el 15 % de tarjetas intensivas, $m \approx 27$)* | ~6.821,7 h (~284 días) | **~3.410,9 kWh** | **~40.930,8 kWh/año** | Computacionalmente inviable (no termina). |

**Análisis de la diferencia anual:**
1. **Regla simplificada frente a programación dinámica:** comparar directamente las dos rutinas $\Theta(d)$ arroja una diferencia de apenas $0,01289 - 0,00763 =$ **+0,00526 kWh al año** (5,26 Wh anuales, equivalente a mantener encendido el servidor apenas **38 segundos adicionales en todo el año**). Esto demuestra empíricamente que devolverle hasta el último peso exacto a los pasajeros no conlleva penalización energética relevante frente a la heurística actual.
2. **Proceso actual real del SITVM frente a programación dinámica:** dado que hoy la organización sí intenta correr la exploración exhaustiva antes de caer en la regla simplificada —contribuyendo a que el lote nocturno supere las 8 horas (al menos 4 horas por encima de la ventana en el cierre de mes)—, sustituir ese esquema por programación dinámica reduce el consumo anual desde más de **24 kWh/año** (e incluso miles de kWh si se intentara completar la exhaustiva sin corte) a **0,013 kWh/año**, logrando un **ahorro superior al 99,9 %** de la energía consumida hoy en el cierre mensual.

---

## 7. Conclusiones

1. La liquidación del tope tarifario del SITVM posee subestructura óptima y subproblemas traslapados sobre los días del periodo, lo que permite sustituir un árbol recursivo exponencial $\Theta(d + r^m)$ ($r \approx 2,0066$) por tabulación en tiempo $\Theta(d)$ sin sacrificar exactitud.
2. La regla simplificada vigente falla siempre que convenga desplazar el inicio de un pase semanal o mensual fuera de cortes fijos (como se demostró con el sobrecobro de 16.800 pesos en `[1, 1, 1, 3, 3, 3, 3, 3, 3, 3]` y con el 31,4 % a 37,7 % de tarjetas afectadas en pruebas sintéticas).
3. En el volumen real de 950.000 tarjetas mensuales, la programación dinámica resuelve el cierre en ~7,73 segundos (0,054 % de la ventana de 4 horas) con un gasto energético estimado de apenas 0,0129 kWh al año en el servidor de 500 W, frente a la inviabilidad operativa y energética de la búsqueda exhaustiva.

---

## 8. Reproducción de pruebas y experimentos

Siga estos pasos desde la raíz del repositorio para configurar el entorno virtual, ejecutar la verificación completa con `assert` y regenerar las mediciones junto con las gráficas en `graficas/tope_tarifario/`:

### En Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 1. Ejecutar suite de pruebas
python src/tope_tarifario/pruebas.py

# 2. Ejecutar experimentos y generar graficas
python src/tope_tarifario/medicion.py
```

### En Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1. Ejecutar suite de pruebas
python3 src/tope_tarifario/pruebas.py

# 2. Ejecutar experimentos y generar graficas
python3 src/tope_tarifario/medicion.py
```
