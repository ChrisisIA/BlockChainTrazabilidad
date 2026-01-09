# Sistema de Chatbot de Trazabilidad - Mejoras Implementadas

## Resumen de Mejoras

Se ha mejorado significativamente el sistema de chatbot para consultas de trazabilidad de prendas, enfocándose en robustez, inteligencia de decisión y manejo de errores.

---

## 1. **Orquestador Bot Mejorado** (`orquestador_bot`)

### Contexto Inteligente

El orquestador ahora tiene un contexto mucho más detallado que le permite:

- **Entender la arquitectura del sistema completo**:
  - Qué datos están en la base de datos MariaDB
  - Qué datos requieren consultar JSONs de Swarm
  - Cómo optimizar el flujo de consultas

- **Tomar decisiones inteligentes**:
  - Determinar si una consulta necesita solo DB o también JSONs
  - Calcular el número óptimo de hashes a procesar
  - Decidir cuándo aplicar límites para eficiencia

### Ejemplo de Decisión del Orquestador

**Consulta**: "¿Cuántas prendas de LACOSTE hay?"

**Decisión del Orquestador**:
```json
{
    "razonamiento": "Consulta simple de conteo por cliente. TDESCCLIE está en DB. No necesita JSONs ni hashes.",
    "query_for_query_bot": "¿Cuántas prendas de LACOSTE hay en total?",
    "needs_json_fetch": false,
    "limit_hashes": 0,
    "final_call": true
}
```

**Consulta**: "¿Cuántas prendas de LACOSTE para hombres y mujeres hay y por qué máquinas pasaron?"

**Decisión del Orquestador**:
```json
{
    "razonamiento": "Consulta mixta: conteo por género (DB) + máquinas (JSON). Filtrar por LACOSTE en DB, luego fetch JSONs para extraer info de máquinas. Limitar a 100 hashes para no sobrecargar.",
    "query_for_query_bot": "Dame todas las prendas de LACOSTE con sus hashes, agrupadas por género",
    "needs_json_fetch": true,
    "limit_hashes": 100,
    "final_call": true
}
```

### Flujo de Ejecución Robusto

El orquestador ahora ejecuta un flujo estructurado con logging detallado:

1. **Generación de Plan** - IA analiza la consulta y decide el flujo óptimo
2. **Validación de Plan** - Verifica que el plan sea un JSON válido
3. **Ejecución de DB** - Genera SQL, ejecuta y valida resultados
4. **Manejo de Vacíos** - Si no hay resultados, intenta consultas alternativas
5. **Extracción de Hashes** - Identifica hashes relevantes con límites inteligentes
6. **Recuperación de JSONs** - (Preparado para cuando lo implementes)
7. **Respuesta Final** - Genera respuesta coherente al usuario

---

## 2. **Query Bot Mejorado** (`query_bot`)

### Contexto Enriquecido

- **Documentación completa de columnas** con tipos y ejemplos
- **Ejemplos múltiples** de queries SQL para diferentes casos
- **Reglas críticas** para generar SQL seguro y eficiente
- **Limpieza automática** de formato markdown en respuestas

### Mejoras de Seguridad

- Solo genera queries SELECT (nunca operaciones peligrosas)
- Usa LIKE para comparaciones tolerantes a mayúsculas/minúsculas
- Siempre incluye TTICKHASH cuando necesita recuperar hashes

### Ejemplos en el Contexto

```sql
-- Conteo simple
"¿Cuántas prendas para hombre hay?"
→ SELECT COUNT(*) FROM apdobloctrazhash WHERE TTIPOGENE = 'Hombres'

-- Listado con filtros
"Dame todas las prendas de LACOSTE para hombres"
→ SELECT * FROM apdobloctrazhash WHERE TDESCCLIE LIKE '%LACOSTE%' AND TTIPOGENE = 'Hombres'

-- Agregación
"¿Cuántas prendas de LACOSTE hay por género?"
→ SELECT TTIPOGENE, COUNT(*) as cantidad FROM apdobloctrazhash WHERE TDESCCLIE LIKE '%LACOSTE%' GROUP BY TTIPOGENE
```

---

## 3. **Sistema de Validación de Lógica** (`validate_response_logic`)

Nueva función que valida la coherencia de respuestas antes de aceptarlas:

### Validación de SQL
- Verifica que empiece con SELECT
- Detecta operaciones peligrosas (DROP, DELETE, UPDATE, etc.)
- Verifica presencia de cláusula FROM
- Rechaza queries inválidas

### Validación de JSON
- Verifica que sea parseable
- Valida estructura de objeto
- Detecta errores de formato

### Validación de Texto
- Detecta mensajes de error comunes
- Verifica longitud mínima
- Identifica respuestas vacías o inválidas

---

## 4. **Sistema de Reintentos Inteligente** (`retry_operation`)

Reescrito completamente para ser mucho más robusto:

### Características

1. **Validación por Tipo**:
   - `sql`: Valida queries SQL
   - `json`: Valida objetos JSON
   - `text`: Valida respuestas de texto
   - `dataframe`: Valida DataFrames de pandas

2. **Corrección con IA**:
   - Cuando falla una operación, usa IA para generar corrección
   - Aplica la corrección y reintenta automáticamente
   - Máximo de reintentos configurable (default: 3)

3. **Logging Detallado**:
   - Muestra cada intento con número
   - Indica si la validación pasó o falló
   - Explica el motivo del error

### Ejemplo de Retry en Acción

```
[Retry 1/3] Ejecutando: query_bot
✗ Error en intento 1: SQL no contiene cláusula FROM
[IA] Generando corrección para el error...
[IA] Corrección sugerida: SELECT COUNT(*) FROM apdobloctrazhash WHERE...
[Retry 2/3] Ejecutando: query_bot
✓ SQL válido generado
```

---

## 5. **Final Response Bot Mejorado** (`final_response_bot`)

### Contexto Profesional

- **Reglas claras** sobre cómo estructurar respuestas
- **Ejemplos específicos** para diferentes tipos de consultas
- **Instrucciones de formato** para conteos, listas y análisis

### Características

- Respuestas en español natural (sin jerga técnica)
- Usa números exactos de los datos proporcionados
- Estructura clara (bullets, enumeraciones)
- Menciona limitaciones cuando aplican
- NO inventa datos - solo usa lo disponible

### Ejemplos de Respuestas

**Input**: `{"db_results": [{"count": 1523}]}`
**Output**: "Hay un total de 1,523 prendas de la marca LACOSTE en el sistema."

**Input**: `{"db_results": [{"TTIPOGENE": "Hombres", "cantidad": 850}, {"TTIPOGENE": "Mujeres", "cantidad": 673}]}`
**Output**:
```
Las prendas de LACOSTE se distribuyen de la siguiente manera:
• Hombres: 850 prendas
• Mujeres: 673 prendas
Total: 1,523 prendas
```

---

## 6. **Mejoras en `execute_query`**

- Normaliza nombres de columnas a minúsculas para consistencia
- Cierra conexiones correctamente
- Logging detallado de errores
- Manejo robusto de excepciones

---

## Flujo Completo de una Consulta

```
Usuario: "¿Cuántas prendas de LACOSTE para hombres y mujeres hay?"

PASO 1: Orquestador analiza la consulta
  → Decisión: Necesita DB, no necesita JSONs
  → Genera instrucción para query_bot

PASO 2: Query Bot genera SQL
  → Retry con validación de SQL
  → Output: SELECT TTIPOGENE, COUNT(*) as cantidad FROM apdobloctrazhash WHERE TDESCCLIE LIKE '%LACOSTE%' GROUP BY TTIPOGENE

PASO 3: Ejecutar Query
  → Retry con validación de DataFrame
  → Output: [{"ttipogene": "Hombres", "cantidad": 850}, {"ttipogene": "Mujeres", "cantidad": 673}]

PASO 4: Generar Respuesta Final
  → Retry con validación de texto
  → Output: "Las prendas de LACOSTE se distribuyen de la siguiente manera:
             • Hombres: 850 prendas
             • Mujeres: 673 prendas
             Total: 1,523 prendas"

RESULTADO: Usuario recibe respuesta coherente y precisa
```

---

## Parámetros Configurables

El `orquestador_bot` acepta parámetros que TÚ controlas (no el usuario):

```python
orquestador_bot(
    user_question,           # Pregunta del usuario
    max_hashes=100,          # Límite de hashes a procesar (el orquestador puede ajustarlo)
    max_tokens=10000,        # Límite de tokens antes de llamar al bot final
    max_retries=3            # Número de reintentos por operación fallida
)
```

---

## Próximos Pasos (Cuando Implementes JSONs)

El sistema está **preparado** para integrar la recuperación de JSONs. Solo necesitas:

1. **Implementar `fetch_jsons(hashes, json_storage_path)`**:
   - Recibe lista de hashes
   - Recupera JSONs desde Swarm
   - Retorna diccionario `{hash: json_data}`

2. **Implementar `summarize_jsons(jsons, user_question)`**:
   - Recibe JSONs recuperados
   - Usa IA para extraer info relevante a la pregunta
   - Retorna resumen enfocado

3. **Descomentar el código en `orquestador_bot`** (líneas 604-618):
   ```python
   # TODO: Cuando implementes fetch_jsons, descomentar esto:
   # print(f"\n[PASO 5] Recuperando JSONs de Swarm para {len(hashes)} hashes...")
   # jsons = retry_operation(fetch_jsons, hashes, json_storage_path)
   # ...
   ```

---

## Cómo Usar

### Instalación de Dependencias

```bash
cd Swarm
pip install openai python-dotenv pymysql pandas
```

### Configurar Variables de Entorno

Asegúrate de tener en tu `.env`:
```
DEEPSEEK_API_KEY=tu_api_key_aqui
DB_PRENDAS_USER=...
DB_PRENDAS_PASSWORD=...
DB_PRENDAS_HOST=...
DB_PRENDAS_PORT=...
DB_PRENDAS_NAME=...
```

### Ejecutar el Bot

```bash
python chatbot.py
```

O desde otro script:
```python
from chatbot import orquestador_bot

respuesta = orquestador_bot("¿Cuántas prendas de LACOSTE hay?")
print(respuesta)
```

---

## Logs de Debugging

El sistema ahora proporciona logging detallado en consola:

```
================================================================================
NUEVA CONSULTA: ¿Cuántas prendas de LACOSTE para hombres y mujeres hay?
================================================================================

[PASO 1] Generando plan de ejecución con IA...
[Retry 1/3] Ejecutando: generate_plan
✓ JSON válido generado

[PLAN GENERADO]
  Razonamiento: Consulta mixta: conteo por género (DB)...
  Necesita DB: True
  Necesita JSONs: False
  Límite de hashes: 0

[PASO 2] Generando SQL desde instrucción: 'Dame el conteo de prendas LACOSTE por género'
[Retry 1/3] Ejecutando: query_bot
✓ SQL válido generado

Query generada por el bot de querys:
SELECT TTIPOGENE, COUNT(*) as cantidad FROM apdobloctrazhash WHERE TDESCCLIE LIKE '%LACOSTE%' GROUP BY TTIPOGENE

[PASO 3] Ejecutando query SQL en la base de datos...
[Retry 1/3] Ejecutando: execute_query
✓ DataFrame válido con 2 filas
✓ Recuperados 2 registros de la base de datos

[PASO FINAL] Generando respuesta final para el usuario...
[Retry 1/3] Ejecutando: final_response_bot
✓ Respuesta de texto válida

=== RESPUESTA FINAL GENERADA ===
Las prendas de LACOSTE se distribuyen de la siguiente manera:
• Hombres: 850 prendas
• Mujeres: 673 prendas
Total: 1,523 prendas
================================

================================================================================
RESPUESTA ENVIADA AL USUARIO
================================================================================
```

---

## Beneficios Clave

✅ **Robustez**: Sistema de reintentos asegura que el usuario nunca vea errores raros
✅ **Inteligencia**: Orquestador decide flujo óptimo automáticamente
✅ **Validación**: Todas las respuestas se validan antes de aceptarse
✅ **Eficiencia**: Límites inteligentes evitan sobrecargas innecesarias
✅ **Mantenibilidad**: Código bien documentado y modular
✅ **Extensibilidad**: Preparado para agregar recuperación de JSONs fácilmente
✅ **UX**: Respuestas en español natural, claras y precisas

---

## Notas Importantes

1. **No límites tú los hashes/tokens**: El orquestador lo hace inteligentemente
2. **El retry_operation es crítico**: Asegura que las respuestas tengan lógica
3. **Los contextos son detallados**: No los simplifiques - la IA los necesita completos
4. **Logging es tu amigo**: Te ayudará a debuggear cuando algo falle
5. **Temperatura baja en bots técnicos**: query_bot (0.1), orquestador (0.2) para determinismo

---

## Contacto

Para dudas o mejoras adicionales, consulta el archivo principal: `chatbot.py`
