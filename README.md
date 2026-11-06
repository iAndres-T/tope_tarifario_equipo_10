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
