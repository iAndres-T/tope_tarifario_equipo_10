# Laboratorio #4 Primera parte

**Curso:** Análisis de Algoritmos  
**Caso asignado:** Caso de estudio 1 — Conciliación nocturna del recaudo del Sistema Integrado de Transporte  
**Equipo #10:**
- Sara López Cardona
- Kevin Daniel Mendoza Castillo
- Pablo Andrés Tabares Cardona

---

## 1. Análisis del problema

### 1.1 Contexto organizacional y descripción general
El Sistema Integrado de Transporte del Valle Metropolitano (SITVM) presta servicio de metro, dos líneas de cable aéreo y rutas de buses alimentadores a cerca de 4.000.000 de habitantes. Todas las noches, con las estaciones cerradas, un único servidor dedicado procesa por lotes las validaciones del día y, al cierre de cada mes, ejecuta la **Operación 4: liquidación del tope tarifario** de las tarjetas personalizadas.

Desde la entrada en operación de las rutas alimentadoras y la segunda línea de cable, el proceso nocturno supera las 8 horas e incumple la ventana operativa de 4 horas (00:00 a 04:00). En la liquidación del tope tarifario, el programa actual intenta explorar todas las combinaciones posibles de pases y, como no termina para las tarjetas con muchos días de viaje, recurre a una regla simplificada que ocasiona reclamos en Atención al Usuario por cobrar más que el mínimo en determinados meses y retrasa semanas el abono de saldos.

### 1.2 Entradas, salida, unidades y límites de la operación
Al cierre mensual, el sistema debe garantizar que ningún usuario con tarjeta personalizada haya pagado más que la combinación más económica de pasajes y pases capaz de cubrir todos sus viajes del mes.

| Elemento | Descripción técnica | Unidades y límites informados por el caso |
| :--- | :--- | :--- |
| **Entrada principal** (`viajes_por_dia`) | Lista de enteros `list[int]` de longitud $d$, donde el índice `0` corresponde al día 1 del periodo y cada posición contiene los viajes validados ese día (`0` si no viajó). | `viajes` $\in \mathbb{Z}_{\ge 0}$ (viajes/día); periodo mensual real $d \in \{28, 29, 30, 31\}$ días calendario. |
| **Entrada de conciliación** (`cobrado`) | Monto total descontado a la tarjeta a lo largo del mes antes de aplicar la devolución. | Entero no negativo en pesos colombianos (COP). |
| **Catálogo tarifario (perfil general)** | Cuatro productos vigentes:<br>1. Pasaje sencillo: **3.900 pesos** (1 viaje).<br>2. Pase diario: **9.500 pesos** (viajes ilimitados en 1 día calendario).<br>3. Pase semanal: **36.000 pesos** (viajes ilimitados en 7 días consecutivos).<br>4. Pase mensual: **135.000 pesos** (viajes ilimitados en 30 días consecutivos). | Precios enteros en pesos (COP); duraciones de cobertura en días calendario consecutivos ($1$, $7$ y $30$ días). |
| **Volumen operativo real** | Tarjetas personalizadas con al menos un viaje en el mes que deben liquidarse la noche de cierre. | Cerca de **950.000 tarjetas activas/mes** (sobre 3.200.000 tarjetas emitidas y ~1.400.000 validaciones en un día hábil típico). |
| **Salida** (`costo_minimo` / `liquidar_tope`) | `costo_minimo`: menor desembolso posible que cubre todos los viajes del periodo.<br>`liquidar_tope`: saldo a favor a abonar en la tarjeta ($\max(0, \text{cobrado} - \text{costo\_minimo})$). | Enteros no negativos en pesos (COP). |

### 1.3 Restricciones del negocio y de infraestructura
1. **Exactitud financiera estricta:** la devolución acreditada debe ser exactamente la diferencia frente a la combinación más barata posible; ni un peso de menos para el usuario ni un peso de más para el sistema, y nunca un valor negativo.
2. **Ventana operativa nocturna:** en la noche de cierre de mes, la operación cuenta con la ventana de **4 horas (00:00 a 04:00, es decir, 14.400 s)** compartida con las operaciones nocturnas diarias antes del cargue de listas a las 04:30.
3. **Infraestructura fija:** un único servidor dedicado con consumo aproximado de **500 W (0,5 kW)** bajo carga sostenida, ejecutándose en memoria principal y en un solo hilo (sin procesamiento distribuido ni paralelo).
4. **Trazabilidad:** las secuencias y registros originales de validaciones no deben alterarse durante el cálculo para respaldar eventuales reclamaciones ante Atención al Usuario.

### 1.4 Supuestos realizados por el equipo
1. **Meses de 28, 29, 30 y 31 días y bordes del periodo:** de acuerdo con la tabla tarifaria del SITVM, el pase mensual cubre **exactamente 30 días consecutivos** (no el mes calendario completo cuando $d = 31$). En un mes de 31 días con viajes diarios, un pase mensual cubre un tramo de 30 días (por ejemplo, días 1 al 30 o días 2 al 31) y el día restante se cubre con el producto adicional que resulte más económico. Asimismo, como cada cierre mensual se concilia de manera independiente, si un pase semanal o mensual adquirido hacia el final del mes rebasa el día $d$, su cobertura dentro de la liquidación se trunca en $d$ sin trasladar días sobrantes al mes siguiente.
2. **Interpretación de la regla simplificada actual (`costo_regla_actual`):** el enunciado establece que *«cada día se cobra lo más barato entre los pasajes sencillos y el pase diario, y se aplica el pase semanal o mensual si la suma ya lo supera»*. Modelamos esta regla agrupando el periodo en bloques consecutivos de hasta 30 días y, dentro de cada bloque mensual, en cortes semanales fijos de hasta 7 días consecutivos (días 1–7, 8–14, 15–21, 22–28 y días restantes): cada día se valora con $\min(v_t \times 3.900,\; 9.500)$; si el acumulado de un corte de 7 días supera 36.000 pesos se reemplaza por 36.000 pesos, y si la suma de cortes semanales dentro del bloque de 30 días supera 135.000 pesos se reemplaza por 135.000 pesos. De esta manera, todo cobro producido por la regla corresponde a una combinación legal de productos del SITVM.
3. **Perfil tarifario evaluado:** se modela el perfil general vigente, dado que el caso indica que los perfiles diferenciales (estudiante, adulto mayor, discapacidad) mantienen la misma estructura de productos con valores menores; el algoritmo solo recibe constantes tarifarias distintas sin cambiar su lógica ni su complejidad.
4. **Supuestos generales permitidos:** la serie diaria de viajes por tarjeta ya llega íntegra y validada en memoria principal, sin cambios concurrentes durante la corrida nocturna.
