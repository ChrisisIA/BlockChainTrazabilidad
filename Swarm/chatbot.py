from openai import OpenAI
from google import genai
from enum import Enum
import os
import warnings
import pymysql
import pandas as pd
import json
import requests
from difflib import get_close_matches
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

load_dotenv()
warnings.filterwarnings('ignore')

# ============================================================================
# SISTEMA MULTI-MODELO DE IA
# ============================================================================

class AIModel(Enum):
    """Modelos de IA disponibles"""
    DEEPSEEK = "deepseek"
    GEMINI = "gemini"
    # Agregar nuevos modelos aquí en el futuro:
    # OPENAI = "openai"
    # CLAUDE = "claude"

# Configuración global del modelo activo
_current_model = AIModel.DEEPSEEK  # Modelo por defecto

def set_ai_model(model: AIModel):
    """
    Establece el modelo de IA a usar globalmente.

    Args:
        model: AIModel enum (DEEPSEEK, GEMINI, etc.)

    Ejemplo:
        set_ai_model(AIModel.GEMINI)
    """
    global _current_model
    _current_model = model
    print(f"✓ Modelo de IA configurado: {model.value.upper()}")

def get_current_model() -> AIModel:
    """Retorna el modelo de IA actualmente configurado"""
    return _current_model

class AIProvider:
    """
    Proveedor unificado de IA que abstrae las diferencias entre modelos.
    Soporta: DeepSeek, Gemini (y extensible a otros).
    """

    def __init__(self, model: AIModel = None):
        """
        Inicializa el proveedor con el modelo especificado o el global.

        Args:
            model: AIModel a usar (opcional, usa el global si no se especifica)
        """
        self.model = model or _current_model
        self._init_client()

    def _init_client(self):
        """Inicializa el cliente según el modelo seleccionado"""
        if self.model == AIModel.DEEPSEEK:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY no encontrada en variables de entorno")
            self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            self.model_name = "deepseek-chat"

        elif self.model == AIModel.GEMINI:
            api_key = os.getenv("GEMINI_API_KEY", "AIzaSyAM2HEOC4HD0fgsJqbChCU_WoWk7F-Riq4")
            self.client = genai.Client(api_key=api_key)
            self.model_name = "gemini-2.5-flash"

        # Agregar más modelos aquí en el futuro:
        # elif self.model == AIModel.OPENAI:
        #     api_key = os.getenv("OPENAI_API_KEY")
        #     self.client = OpenAI(api_key=api_key)
        #     self.model_name = "gpt-4"

        else:
            raise ValueError(f"Modelo no soportado: {self.model}")

    def chat(self, system_prompt: str, user_message: str, temperature: float = 0.3) -> str:
        """
        Genera una respuesta de chat unificada para cualquier modelo.

        Args:
            system_prompt: Contexto/instrucciones del sistema
            user_message: Mensaje del usuario
            temperature: Temperatura para generación (0.0-1.0)

        Returns:
            str: Respuesta generada por el modelo
        """
        try:
            if self.model == AIModel.DEEPSEEK:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()

            elif self.model == AIModel.GEMINI:
                # Gemini usa un formato diferente - combinamos system + user
                full_prompt = f"{system_prompt}\n\n---\n\nUsuario: {user_message}"
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=temperature
                    ) if hasattr(genai.types, 'GenerateContentConfig') else None
                )
                return response.text.strip()

            # Agregar más modelos aquí
            else:
                raise ValueError(f"Modelo no implementado: {self.model}")

        except Exception as e:
            print(f"[ERROR] Error en {self.model.value}: {str(e)}")
            raise

    def __repr__(self):
        return f"AIProvider(model={self.model.value}, model_name={self.model_name})"


def get_ai_provider(model: AIModel = None) -> AIProvider:
    """
    Factory function para obtener un proveedor de IA.

    Args:
        model: Modelo específico (opcional, usa el global si no se especifica)

    Returns:
        AIProvider configurado

    Ejemplo:
        provider = get_ai_provider()  # Usa el modelo global
        provider = get_ai_provider(AIModel.GEMINI)  # Usa Gemini específicamente
    """
    return AIProvider(model)

# Caché global para valores únicos de la DB
_db_values_cache = {}

DB_USER = os.getenv("DB_PRENDAS_USER")
DB_PASSWORD = os.getenv("DB_PRENDAS_PASSWORD")
DB_HOST = os.getenv("DB_PRENDAS_HOST")
DB_PORT = int(os.getenv("DB_PRENDAS_PORT"))
DB_NAME = os.getenv("DB_PRENDAS_NAME")

db_config = {
    'host': DB_HOST,
    'port': DB_PORT,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

def connect_to_my_db():
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except Exception as e:
        print("falló al conectarse a la base de datos de MariaDB")
        return None

def execute_query(query):
    """
    Ejecuta una query SQL en la base de datos MariaDB.
    Args:
        query: String con la consulta SQL (debe ser SELECT)
    Returns:
        pandas.DataFrame con los resultados o DataFrame vacío si falla
    """
    conn = connect_to_my_db()
    if conn:
        try:
            df = pd.read_sql(query, conn)
            conn.close()

            # Normalizar nombres de columnas a minúsculas para consistencia
            df.columns = df.columns.str.lower()

            if df.empty:
                print("[WARN] Query ejecutada correctamente pero no retornó resultados")
                return pd.DataFrame()
            else:
                return df
        except Exception as e:
            print(f"[ERROR] Error al ejecutar query: {e}")
            if conn:
                conn.close()
            return pd.DataFrame()
    else:
        print("[ERROR] No se pudo conectar a la base de datos")
        return pd.DataFrame()

def get_unique_values(column_name, use_cache=True, limit=1000):
    """
    Obtiene valores únicos de una columna específica de la DB.
    Usa caché para evitar consultas repetidas.

    Args:
        column_name: Nombre de la columna (ej: 'TDESCCLIE', 'TTIPOGENE')
        use_cache: Si usar caché o forzar consulta nueva
        limit: Límite de valores únicos a retornar

    Returns:
        list: Lista de valores únicos o [] si falla
    """
    global _db_values_cache

    # Normalizar nombre de columna a mayúsculas
    column_name = column_name.upper()

    # Verificar caché
    if use_cache and column_name in _db_values_cache:
        print(f"[CACHE] Usando valores cacheados para {column_name}")
        return _db_values_cache[column_name]

    # Columnas válidas para consultar
    valid_columns = [
        'TDESCCLIE', 'TCODICLIE', 'TTIPOGENE', 'TTIPOEDAD',
        'TTIPOPREN', 'TTIPOTEJI', 'TCODITALL', 'TLUGADEST'
    ]

    if column_name not in valid_columns:
        print(f"[WARN] Columna '{column_name}' no está en la lista de columnas válidas")
        return []

    try:
        query = f"SELECT DISTINCT {column_name} FROM apdobloctrazhash WHERE {column_name} IS NOT NULL LIMIT {limit}"
        df = execute_query(query)

        if df.empty:
            return []

        # Convertir a lista y limpiar
        values = df[column_name.lower()].dropna().astype(str).str.strip().tolist()
        values = [v for v in values if v]  # Filtrar vacíos

        # Guardar en caché
        _db_values_cache[column_name] = values

        print(f"✓ Recuperados {len(values)} valores únicos para {column_name}")
        return values

    except Exception as e:
        print(f"[ERROR] Error al obtener valores únicos de {column_name}: {e}")
        return []

def fuzzy_match_value(input_value, valid_values, threshold=0.6):
    """
    Encuentra el valor más cercano usando fuzzy matching.

    Args:
        input_value: Valor ingresado por el usuario (puede tener errores)
        valid_values: Lista de valores válidos de la DB
        threshold: Umbral de similitud (0.0 a 1.0)

    Returns:
        tuple: (matched_value, confidence) o (None, 0.0) si no hay match
    """
    if not input_value or not valid_values:
        return None, 0.0

    # Limpiar input
    input_clean = str(input_value).strip().upper()

    # Convertir valid_values a mayúsculas para comparación
    valid_upper = [str(v).strip().upper() for v in valid_values]

    # Match exacto (caso insensitive)
    if input_clean in valid_upper:
        idx = valid_upper.index(input_clean)
        return valid_values[idx], 1.0

    # Fuzzy matching con difflib
    matches = get_close_matches(input_clean, valid_upper, n=1, cutoff=threshold)

    if matches:
        matched_upper = matches[0]
        idx = valid_upper.index(matched_upper)
        original_value = valid_values[idx]

        # Calcular confianza aproximada (similitud de caracteres)
        from difflib import SequenceMatcher
        confidence = SequenceMatcher(None, input_clean, matched_upper).ratio()

        return original_value, confidence

    return None, 0.0

def correct_user_input_with_ai(user_question):
    """
    Usa IA para detectar y corregir nombres mal escritos en la pregunta del usuario,
    consultando valores reales de la DB.

    Args:
        user_question: Pregunta original del usuario

    Returns:
        tuple: (corrected_question, corrections_made: dict)
    """
    # Usar el sistema multi-modelo
    provider = get_ai_provider()

    # Obtener valores válidos de columnas clave
    valid_clients = get_unique_values('TDESCCLIE')
    valid_genders = get_unique_values('TTIPOGENE')
    valid_garment_types = get_unique_values('TTIPOPREN')
    valid_fabric_types = get_unique_values('TTIPOTEJI')

    # Preparar contexto con valores válidos
    context = f"""
Eres un experto en corregir errores de escritura en consultas sobre trazabilidad de prendas.

**TU TAREA**:
Analiza la pregunta del usuario y detecta nombres de clientes, tipos de prenda, géneros, etc. que puedan estar mal escritos.
Compara con los valores válidos de la base de datos y sugiere correcciones.

**VALORES VÁLIDOS DE LA BASE DE DATOS**:

Clientes (TDESCCLIE):
{', '.join(valid_clients[:50])}  # Primeros 50

Géneros (TTIPOGENE):
{', '.join(valid_genders)}

Tipos de Prenda (TTIPOPREN):
{', '.join(valid_garment_types[:30])}

Tipos de Tejido (TTIPOTEJI):
{', '.join(valid_fabric_types)}

**REGLAS**:
1. Si detectas un nombre que NO está en la lista pero es similar, sugiérelo corregido
2. Usa fuzzy matching mental: "LASCOSTE" → "LACOSTE", "NIQUE" → "NIKE"
3. NO corrijas si el nombre existe exactamente en la lista
4. Retorna JSON con: {{"corrected_question": "...", "corrections": {{"original": "corrected"}}}}

**EJEMPLO**:

Input: "¿Cuántas prendas de LASCOSTE para honbres hay?"
Output: {{"corrected_question": "¿Cuántas prendas de LACOSTE para hombres hay?", "corrections": {{"LASCOSTE": "LACOSTE", "honbres": "hombres"}}}}

Input: "¿Cuántas prendas de LACOSTE hay?"
Output: {{"corrected_question": "¿Cuántas prendas de LACOSTE hay?", "corrections": {{}}}}
"""

    try:
        response_text = provider.chat(context, user_question, temperature=0.1)

        # Limpiar formato markdown
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()

        result = json.loads(response_text)

        corrected_q = result.get("corrected_question", user_question)
        corrections = result.get("corrections", {})

        if corrections:
            print(f"\n[CORRECCIÓN AUTOMÁTICA]")
            for orig, corr in corrections.items():
                print(f"  '{orig}' → '{corr}'")
            print(f"Pregunta corregida: {corrected_q}\n")

        return corrected_q, corrections

    except Exception as e:
        print(f"[WARN] Error en corrección automática: {e}")
        return user_question, {}

def extract_filters_from_question(question, corrections=None):
    """
    Extrae valores de filtro estructurados de la pregunta del usuario.
    Usa IA para identificar entidades mencionadas y las valida contra la DB.

    Args:
        question: Pregunta del usuario (preferiblemente ya corregida)
        corrections: Dict de correcciones realizadas {original: corregido}

    Returns:
        dict: Filtros extraídos con estructura compatible con FilterState del frontend
              {client, clientStyle, boxNumber, label, size, gender, age, garmentType}
    """
    provider = get_ai_provider()

    # Estructura de filtros vacía
    empty_filters = {
        "client": "",
        "clientStyle": "",
        "boxNumber": "",
        "label": "",
        "size": "",
        "gender": "",
        "age": "",
        "garmentType": ""
    }

    # Obtener valores válidos de la DB para validación
    valid_clients = get_unique_values('TDESCCLIE')
    valid_genders = get_unique_values('TTIPOGENE')
    valid_garment_types = get_unique_values('TTIPOPREN')
    valid_sizes = get_unique_values('TCODITALL')
    valid_ages = get_unique_values('TTIPOEDAD')

    context = f"""
Eres un extractor de entidades especializado en consultas sobre trazabilidad de prendas.

**TU TAREA**:
Analiza la pregunta del usuario y extrae cualquier valor que corresponda a los filtros disponibles.
SOLO extrae valores que estén EXPLÍCITAMENTE mencionados en la pregunta.

**FILTROS DISPONIBLES Y VALORES VÁLIDOS**:

1. client (Cliente) - Valores válidos:
{', '.join(valid_clients[:30]) if valid_clients else 'No disponible'}

2. gender (Género) - Valores válidos:
{', '.join(valid_genders) if valid_genders else 'No disponible'}

3. garmentType (Tipo de Prenda) - Valores válidos:
{', '.join(valid_garment_types[:20]) if valid_garment_types else 'No disponible'}

4. size (Talla) - Valores válidos:
{', '.join(valid_sizes[:20]) if valid_sizes else 'No disponible'}

5. age (Edad) - Valores válidos:
{', '.join(valid_ages) if valid_ages else 'No disponible'}

6. clientStyle (Estilo Cliente) - Código alfanumérico del estilo
7. boxNumber (Número de Caja) - Número de caja
8. label (Etiqueta) - Código de etiqueta

**REGLAS ESTRICTAS**:
1. SOLO incluye valores que estén CLARAMENTE mencionados en la pregunta
2. Si un valor mencionado coincide con un valor válido de la lista, usa el valor EXACTO de la lista
3. Si no hay mención de un filtro, déjalo como string vacío ""
4. NO inventes valores ni supongas filtros no mencionados
5. Retorna SOLO JSON válido, sin explicaciones

**FORMATO DE RESPUESTA** (JSON puro):
{{"client": "", "clientStyle": "", "boxNumber": "", "label": "", "size": "", "gender": "", "age": "", "garmentType": ""}}

**EJEMPLOS**:

Pregunta: "¿Cuántas prendas de LACOSTE hay?"
Respuesta: {{"client": "LACOSTE", "clientStyle": "", "boxNumber": "", "label": "", "size": "", "gender": "", "age": "", "garmentType": ""}}

Pregunta: "¿Cuántas camisetas de hombre talla M hay?"
Respuesta: {{"client": "", "clientStyle": "", "boxNumber": "", "label": "", "size": "M", "gender": "HOMBRE", "age": "", "garmentType": "CAMISETA"}}

Pregunta: "¿Cuántos registros hay en total?"
Respuesta: {{"client": "", "clientStyle": "", "boxNumber": "", "label": "", "size": "", "gender": "", "age": "", "garmentType": ""}}
"""

    try:
        response_text = provider.chat(context, f"Pregunta: {question}", temperature=0.1)

        # Limpiar formato markdown si existe
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()

        result = json.loads(response_text)

        # Validar y normalizar los valores extraídos contra la DB
        validated_filters = empty_filters.copy()

        # Mapeo de campos a valores válidos y función de validación
        field_validators = {
            "client": valid_clients,
            "gender": valid_genders,
            "garmentType": valid_garment_types,
            "size": valid_sizes,
            "age": valid_ages
        }

        for field, value in result.items():
            if field in validated_filters and value and str(value).strip():
                value_str = str(value).strip()

                # Si el campo tiene validación contra DB
                if field in field_validators and field_validators[field]:
                    # Usar fuzzy matching para encontrar el valor correcto
                    matched_value, confidence = fuzzy_match_value(value_str, field_validators[field])
                    if matched_value and confidence >= 0.7:
                        validated_filters[field] = matched_value
                        print(f"[FILTER EXTRACT] {field}: '{value_str}' → '{matched_value}' (conf: {confidence:.2f})")
                    else:
                        # Si no hay match bueno, usar el valor original
                        validated_filters[field] = value_str
                        print(f"[FILTER EXTRACT] {field}: '{value_str}' (sin match DB)")
                else:
                    # Campos sin validación (clientStyle, boxNumber, label)
                    validated_filters[field] = value_str
                    print(f"[FILTER EXTRACT] {field}: '{value_str}'")

        # Contar filtros extraídos
        extracted_count = sum(1 for v in validated_filters.values() if v)
        if extracted_count > 0:
            print(f"[FILTER EXTRACT] Total filtros extraídos: {extracted_count}")

        return validated_filters

    except json.JSONDecodeError as e:
        print(f"[WARN] Error parseando JSON de filtros: {e}")
        print(f"[WARN] Respuesta recibida: {response_text[:200] if 'response_text' in locals() else 'N/A'}")
        return empty_filters
    except Exception as e:
        print(f"[WARN] Error extrayendo filtros: {e}")
        return empty_filters

def query_bot(question):
    """
    Bot generador de SQL: Convierte preguntas en español a queries SQL válidas.
    - question: Pregunta del usuario o instrucción del orquestador.
    """
    # Usar el sistema multi-modelo
    provider = get_ai_provider()

    context = """
Eres un experto en generar queries SQL a partir de preguntas en español sobre trazabilidad de prendas.

**TABLA**: apdobloctrazhash

**COLUMNAS**:
- TTICKBARR: Tickbar único de la prenda (VARCHAR)
- TNUMEVERS: Versión del registro (INT)
- TNUMECAJA: Número de caja del lote (VARCHAR)
- TESTICLIE: Estilo del cliente (VARCHAR)
- TETIQCLIE: Etiqueta del cliente (VARCHAR)
- TCODITALL: Talla de la prenda (VARCHAR, ejemplos: '10', 'M', 'XL', '8', '12')
- TTICKHASH: Hash Swarm del tickbarr (VARCHAR) - úsalo cuando necesites recuperar hashes
- TCODICLIE: Código del cliente (VARCHAR, ejemplos: 'LAC', 'NKE')
- TDESCCLIE: Nombre/descripción del cliente (VARCHAR, ejemplos: 'LACOSTE', 'NIKE', 'ADIDAS')
- TTIPOPREN: Tipo de prenda (VARCHAR, ejemplos: 'T-Shirt', 'Turtle Neck', 'Camisa', 'Batas')
- TTIPOEDAD: Grupo de edad (VARCHAR, valores: 'Adulto', 'Niño')
- TTIPOGENE: Género (VARCHAR, valores: 'Hombres', 'Mujeres', 'Unisex')
- TLUGADEST: Lugar de destino (VARCHAR)
- TTIPOTEJI: Tipo de tejido (VARCHAR, ejemplos: 'Interlock', 'Jersey', 'Rib', 'Rectilineos', 'Pique', 'Twill')

**REGLAS CRÍTICAS**:
1. Solo genera queries SELECT - NUNCA INSERT, UPDATE, DELETE, DROP, ALTER
2. Usa UPPER() o LIKE para comparaciones de texto que puedan tener variaciones
3. Cuando cuentes registros, usa COUNT(*) o COUNT(DISTINCT columna) según corresponda
4. Si necesitas hashes, SIEMPRE incluye TTICKHASH en el SELECT
5. Para consultas de clientes, usa TDESCCLIE (nombre completo) no TCODICLIE
6. Responde SOLO con la query SQL limpia - SIN ```sql, SIN explicaciones, SIN saltos de línea extra

**EJEMPLOS**:

Pregunta: "¿Cuántas prendas para hombre hay?"
SELECT COUNT(*) FROM apdobloctrazhash WHERE TTIPOGENE = 'Hombres'

Pregunta: "¿Qué clientes tienen talla 10?"
SELECT DISTINCT TCODICLIE, TDESCCLIE FROM apdobloctrazhash WHERE TCODITALL = '10'

Pregunta: "Dame todas las prendas de LACOSTE para hombres"
SELECT * FROM apdobloctrazhash WHERE TDESCCLIE LIKE '%LACOSTE%' AND TTIPOGENE = 'Hombres'

Pregunta: "Lista los hashes de prendas tipo T-Shirt de NIKE"
SELECT TTICKBARR, TTICKHASH FROM apdobloctrazhash WHERE TDESCCLIE LIKE '%NIKE%' AND TTIPOPREN LIKE '%T-Shirt%'

Pregunta: "¿Cuántas prendas de LACOSTE hay por género?"
SELECT TTIPOGENE, COUNT(*) as cantidad FROM apdobloctrazhash WHERE TDESCCLIE LIKE '%LACOSTE%' GROUP BY TTIPOGENE

Pregunta: "Tipos de tejido usados en prendas para niños"
SELECT DISTINCT TTIPOTEJI FROM apdobloctrazhash WHERE TTIPOEDAD = 'Niño'

**IMPORTANTE**:
- Retorna SOLO la query SQL sin formato markdown
- Si la pregunta menciona información que NO está en la DB (ej: máquinas, fechas de producción, procesos),
  genera una query que filtre por los campos disponibles y retorna los TTICKHASH para consultar JSONs después
"""

    respuesta_texto = provider.chat(context, question, temperature=0.1)

    # Limpieza de formato markdown si aparece
    if respuesta_texto.startswith("```sql"):
        respuesta_texto = respuesta_texto.replace("```sql", "").replace("```", "").strip()

    print("Query generada por el bot de querys:")
    print(respuesta_texto)
    return respuesta_texto

def fetch_json_from_swarm(hash_value, timeout=10, verbose=True):
    """
    Recupera un JSON individual desde Ethereum Swarm gateway.

    Args:
        hash_value: Hash Swarm del tickbarr
        timeout: Timeout en segundos para la petición HTTP
        verbose: Si mostrar logs detallados (False para procesamiento paralelo)

    Returns:
        dict: JSON parseado del tickbarr o None si falla
    """
    swarm_gateway_url = f"https://api.gateway.ethswarm.org/bzz/{hash_value}"

    try:
        if verbose:
            print(f"  → Descargando JSON para hash: {hash_value[:16]}...")

        response = requests.get(swarm_gateway_url, timeout=timeout)

        if response.status_code == 200:
            json_data = response.json()
            if verbose:
                print(f"  ✓ JSON recuperado exitosamente ({len(str(json_data))} chars)")
            return json_data
        else:
            if verbose:
                print(f"  ✗ Error HTTP {response.status_code} para hash {hash_value[:16]}")
            return None

    except requests.exceptions.Timeout:
        if verbose:
            print(f"  ✗ Timeout al recuperar hash {hash_value[:16]}")
        return None
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"  ✗ Error de red: {str(e)[:100]}")
        return None
    except json.JSONDecodeError:
        if verbose:
            print(f"  ✗ Respuesta no es un JSON válido")
        return None
    except Exception as e:
        if verbose:
            print(f"  ✗ Error inesperado: {str(e)[:100]}")
        return None

# ============================================================================
# FUNCIÓN DE TRANSFORMACIÓN DE JSON PARA ANÁLISIS DE IA
# ============================================================================

# Mapeo de secciones a nombres legibles
SECTION_NAMES = {
    "tztotrazwebinfo": "INFORMACION_GENERAL",
    "tztotrazwebalma": "ALMACEN",
    "tztotrazwebacab": "ACABADO",
    "tztotrazwebacabmedi": "MEDICIONES_ACABADO",
    "tztotrazwebcost": "COSTURA",
    "tztotrazwebcostoper": "OPERACIONES_COSTURA",
    "tztotrazwebcort": "CORTE",
    "tztotrazwebcortoper": "OPERACIONES_CORTE",
    "tztotrazwebtint": "TINTORERIA",
    "tztotrazwebteje": "TEJEDURIA",
    "tztotrazwebhilo": "HILOS",
    "tztotrazwebhilolote": "LOTES_HILO",
    "tztotrazwebhiloloteprin": "PROVEEDORES_HILO"
}

# Mapeo de campos importantes a nombres legibles
FIELD_NAMES = {
    # Información general
    "TCODICLIE": "codigo_cliente",
    "TNOMBCLIE": "nombre_cliente",
    "TCODIESTICLIE": "estilo_cliente",
    "TCODITALL": "talla",
    "TDESCPREN": "descripcion_prenda",
    "TTIPOPREN": "tipo_prenda",
    "TDESCTIPOPREN": "descripcion_tipo_prenda",
    "TDESCEDAD": "edad",
    "TDESCGENE": "genero",
    "TGENDER": "gender",
    # Almacén
    "TNUMECAJA": "numero_caja",
    "TCODIDEST": "codigo_destino",
    "TDESCDEST": "destino",
    "TFECHRECEALMA": "fecha_recepcion_almacen",
    "TNOMBPERSRECEALMA": "persona_recepcion",
    # Acabado
    "TFECHPESA": "fecha_pesado",
    "TNOMBPERSPESA": "persona_pesado",
    "TFECHEMPA": "fecha_empaque",
    "TNOMBPERSEMPA": "persona_empaque",
    "TFECHAUDI": "fecha_auditoria",
    "TNOMBPERSAUDI": "persona_auditoria",
    # Costura
    "TORDECOST": "orden_costura",
    "TNUMELINECOST": "linea_costura",
    "TDESCPLANCOST": "planta_costura",
    "TNOMBPERSSUPE": "supervisor_costura",
    # Operaciones costura
    "TDESCOPERESPE": "operacion_costura",
    "TNOMBPERS": "operario",
    "TFECHLECT": "fecha_lectura",
    # Corte
    "TNUMEORDECORT": "orden_corte",
    "TNUMETEND": "numero_tendido",
    "TFECHDESPCORT": "fecha_despacho_corte",
    # Operaciones corte
    "TDESCOPER": "operacion_corte",
    # Tintorería - MÁQUINAS IMPORTANTES
    "TNUMEOB": "numero_OB",
    "TNUMEUD": "numero_UD",
    "TTIPOARTI": "tipo_articulo",
    "TDESCTIPOARTI": "descripcion_tipo_articulo",
    "TDESCTELA": "descripcion_tela",
    "TDESCCOLN": "descripcion_color",
    "TMAQUTENI": "codigo_maquina_tenido",
    "TNOMBMAQUTENI": "maquina_tenido",
    "TFABRMAQUTENI": "fabricante_maquina_tenido",
    "TMAQUCORT": "codigo_maquina_cortadora",
    "TNOMBMAQUCORT": "maquina_cortadora",
    "TFABRMAQUCORT": "fabricante_maquina_cortadora",
    "TMAQUSECA": "codigo_maquina_secado",
    "TNOMBMAQUSECA": "maquina_secado",
    "TFABRMAQUSECA": "fabricante_maquina_secado",
    "TMAQUACAB": "codigo_rama",
    "TNOMBMAQUACAB": "RAMA_ACABADO",  # MUY IMPORTANTE - Rama
    "TFABRMAQUACAB": "fabricante_rama",
    "TPARTTINT": "partida_tintoreria",
    "TFECHTENIINIC": "fecha_inicio_tenido",
    "TFECHTENIFINA": "fecha_fin_tenido",
    "TFECHSECAINIC": "fecha_inicio_secado",
    "TFECHSECAFINA": "fecha_fin_secado",
    "TFECHACABINIC": "fecha_inicio_acabado",
    "TFECHACABFINA": "fecha_fin_acabado",
    "TNOMBOPERACABINIC": "operario_acabado",
    # Tejeduría
    "TORDETEJE": "orden_tejeduria",
    "TCODITELA": "codigo_tela",
    "TTIPOTEJI": "tipo_tejido",
    "TDESCTIPOTEJI": "descripcion_tipo_tejido",
    "TCODIMAQU": "codigo_maquina_tejeduria",
    "TNOMBMAQU": "maquina_tejeduria",
    "TFABRMAQU": "fabricante_maquina_tejeduria",
    "TFECHTEJE": "fecha_tejido",
    "TKILOPIEZ": "kilos_pieza",
    # Hilos
    "TCODICOLOHILO": "codigo_color_hilo",
    "TDESCCOLOHILO": "color_hilo",
    "TTITUHILO": "titulo_hilo",
    "TCOMPHILO": "composicion_hilo",
    "TNOMBPROV": "proveedor_hilo",
    "TNUMELOTE": "numero_lote"
}


def transform_json_for_ai(json_data, max_items_per_array=3):
    """
    Transforma un JSON de trazabilidad textil en un formato LEGIBLE para el bot de IA.

    Esta función:
    1. Renombra las secciones a nombres descriptivos (ej: tztotrazwebtint -> TINTORERIA)
    2. Renombra los campos importantes a nombres legibles (ej: TNOMBMAQUACAB -> RAMA_ACABADO)
    3. Agrupa valores únicos de arrays para evitar repetición
    4. Mantiene la estructura clara: SECCION.campo = valor(es)

    Args:
        json_data: JSON original de trazabilidad
        max_items_per_array: Máximo de items a procesar por array (para limitar tamaño)

    Returns:
        dict: JSON transformado con estructura legible:
        {
            "TINTORERIA": {
                "RAMA_ACABADO": ["Rama 3"],
                "maquina_tenido": ["Saturno 30.600"],
                "numero_OB": [4343462, 4343463, ...]
            },
            ...
        }
    """
    if not isinstance(json_data, dict):
        return {"_error": "Input no es un diccionario válido"}

    transformed = {}

    for section_key, section_data in json_data.items():
        # Ignorar metadata interna
        if section_key.startswith("_"):
            continue

        # Obtener nombre legible de la sección
        section_name = SECTION_NAMES.get(section_key, section_key)

        if isinstance(section_data, list) and len(section_data) > 0:
            # Procesar arrays - agrupar valores únicos por campo
            section_result = {}
            items_to_process = section_data[:max_items_per_array]

            # Recolectar todos los campos y sus valores únicos
            field_values = {}
            for item in items_to_process:
                if isinstance(item, dict):
                    for field_key, field_value in item.items():
                        # Obtener nombre legible del campo
                        field_name = FIELD_NAMES.get(field_key, field_key)

                        if field_name not in field_values:
                            field_values[field_name] = set()

                        # Agregar valor si no es None ni vacío
                        if field_value is not None:
                            str_val = str(field_value).strip()
                            if str_val and str_val != "None":
                                field_values[field_name].add(str_val)

            # Convertir sets a listas o valores únicos
            for field_name, values_set in field_values.items():
                if len(values_set) == 1:
                    section_result[field_name] = list(values_set)[0]
                elif len(values_set) > 1:
                    # Limitar a 5 valores únicos máximo
                    section_result[field_name] = list(values_set)[:5]

            # Agregar nota si hay más items de los procesados
            if len(section_data) > max_items_per_array:
                section_result["_total_registros"] = len(section_data)

            if section_result:
                transformed[section_name] = section_result

        elif isinstance(section_data, dict):
            # Para diccionarios directos
            section_result = {}
            for field_key, field_value in section_data.items():
                field_name = FIELD_NAMES.get(field_key, field_key)
                if field_value is not None:
                    section_result[field_name] = field_value
            if section_result:
                transformed[section_name] = section_result

    return transformed


def flatten_json_for_analysis(json_data, include_section_context=True):
    """
    Aplana un JSON de trazabilidad en pares clave=valor simples.
    Ideal para que el bot vea TODOS los campos disponibles de un vistazo.

    Formato de salida:
        SECCION.campo = valor

    Ejemplo:
        TINTORERIA.RAMA_ACABADO = Rama 3
        TINTORERIA.maquina_tenido = Saturno 30.600
        COSTURA.operacion = Unir Hombros Con Cinta
    """
    if not isinstance(json_data, dict):
        return {"_error": "Input no es un diccionario válido"}

    # Primero transformar a formato legible
    transformed = transform_json_for_ai(json_data, max_items_per_array=5)

    # Luego aplanar completamente
    flattened = {}
    for section_name, section_data in transformed.items():
        if isinstance(section_data, dict):
            for field_name, field_value in section_data.items():
                if field_name.startswith("_"):
                    continue
                key = f"{section_name}.{field_name}"
                flattened[key] = field_value

    return flattened


def flatten_json_compact(json_data, max_items_per_section=5):
    """
    Versión compacta: Usa transform_json_for_ai internamente.
    Mantiene compatibilidad con código existente.
    """
    return transform_json_for_ai(json_data, max_items_per_array=max_items_per_section)


def prepare_json_for_ai_analysis(json_data, mode="compact"):
    """
    Prepara un JSON de trazabilidad para ser analizado por el bot de IA.
    Esta es la función principal que debe usarse antes de enviar datos al bot.

    IMPORTANTE: Transforma el JSON a un formato legible con:
    - Secciones renombradas (ej: tztotrazwebtint -> TINTORERIA)
    - Campos renombrados (ej: TNOMBMAQUACAB -> RAMA_ACABADO)
    - Valores agrupados y sin duplicados

    Args:
        json_data: JSON original de trazabilidad (puede ser dict o list de dicts)
        mode: Modo de preparación:
            - "compact": Estructura jerárquica legible (recomendado)
            - "flat": Pares clave=valor aplanados

    Returns:
        dict: JSON transformado y legible para el bot

    Ejemplo de salida (mode="compact"):
        {
            "TINTORERIA": {
                "RAMA_ACABADO": "Rama 3",
                "maquina_tenido": "Saturno 30.600",
                "numero_OB": ["4343462", "4343463"]
            },
            "COSTURA": {
                "operacion_costura": ["Unir Hombros", "Pegar Cuello"]
            }
        }
    """
    # Si es una lista de JSONs, combinarlos
    if isinstance(json_data, list):
        if len(json_data) == 0:
            return {"_error": "Lista vacía de JSONs"}

        # Transformar y combinar múltiples JSONs
        combined = {}
        for single_json in json_data:
            transformed = transform_json_for_ai(single_json, max_items_per_array=5)

            # Combinar resultados por sección
            for section_name, section_data in transformed.items():
                if section_name.startswith("_"):
                    continue

                if section_name not in combined:
                    combined[section_name] = {}

                if isinstance(section_data, dict):
                    for field_name, field_value in section_data.items():
                        if field_name.startswith("_"):
                            continue

                        if field_name not in combined[section_name]:
                            combined[section_name][field_name] = set()

                        # Agregar valores
                        if isinstance(field_value, list):
                            for v in field_value:
                                combined[section_name][field_name].add(str(v))
                        else:
                            combined[section_name][field_name].add(str(field_value))

        # Convertir sets a listas
        for section_name in combined:
            for field_name in combined[section_name]:
                values = list(combined[section_name][field_name])
                if len(values) == 1:
                    combined[section_name][field_name] = values[0]
                else:
                    combined[section_name][field_name] = values[:10]  # Máximo 10 valores

        combined["_metadata"] = {"jsons_combined": len(json_data)}

        # Si modo flat, aplanar el resultado
        if mode == "flat":
            flattened = {}
            for section_name, section_data in combined.items():
                if section_name.startswith("_"):
                    continue
                if isinstance(section_data, dict):
                    for field_name, field_value in section_data.items():
                        flattened[f"{section_name}.{field_name}"] = field_value
            return flattened

        return combined

    # Para un solo JSON
    if mode == "flat":
        return flatten_json_for_analysis(json_data)
    else:
        return transform_json_for_ai(json_data, max_items_per_array=5)


def extract_values_from_flattened(flattened_json, field_patterns):
    """
    Extrae valores específicos de un JSON aplanado usando patrones de campo.

    Args:
        flattened_json: JSON previamente aplanado con prepare_json_for_ai_analysis
        field_patterns: Lista de patrones de campo a extraer
            Ej: ["TNOMBMAQUACAB", "tztotrazwebtint.TNOMBMAQUACAB", "TNUMEOB"]

    Returns:
        dict: Diccionario con los valores extraídos
            {
                "TNOMBMAQUACAB": ["Rama 3", "Rama 2"],
                "TNUMEOB": ["12345"]
            }
    """
    extracted = {}

    for pattern in field_patterns:
        pattern_lower = pattern.lower()
        pattern_upper = pattern.upper()

        for key, value in flattened_json.items():
            if key.startswith("_"):
                continue

            # Buscar coincidencias (case insensitive)
            key_lower = key.lower()

            # Coincidencia exacta del campo (al final del path)
            field_name = key.split(".")[-1].upper() if "." in key else key.upper()

            if (pattern_upper in key.upper() or
                pattern_lower in key_lower or
                field_name == pattern_upper):

                # Usar el nombre del campo como key del resultado
                result_key = field_name if field_name != key.upper() else pattern_upper

                if result_key not in extracted:
                    extracted[result_key] = []

                if isinstance(value, list):
                    extracted[result_key].extend(value)
                else:
                    extracted[result_key].append(value)

    # Eliminar duplicados
    for key in extracted:
        seen = set()
        unique = []
        for v in extracted[key]:
            v_str = str(v)
            if v_str not in seen:
                seen.add(v_str)
                unique.append(v)
        extracted[key] = unique

    return extracted


def extract_relevant_keys_with_ai(sample_jsons, user_question):
    """
    Usa IA para analizar JSONs de muestra TRANSFORMADOS y determinar qué campos son relevantes.

    ESTRATEGIA MEJORADA:
    - Usa solo 3 JSONs de muestra para análisis
    - Transforma los JSONs a formato legible (secciones y campos renombrados)
    - Muestra un print del JSON transformado para debugging

    Args:
        sample_jsons: Lista de JSONs de muestra - se usarán máximo 3
        user_question: Pregunta original del usuario

    Returns:
        dict: {
            "keys": lista de nombres de campos relevantes,
            "has_relevant_data": bool indicando si hay datos útiles,
            "explanation": str explicando por qué no hay datos (si aplica)
        }
    """
    # Usar el sistema multi-modelo
    provider = get_ai_provider()

    # Asegurar que sample_jsons sea una lista
    if not isinstance(sample_jsons, list):
        sample_jsons = [sample_jsons]

    # LIMITAR A 3 JSONs MÁXIMO
    sample_jsons = sample_jsons[:3]

    print(f"\n{'='*60}")
    print(f"[IA] Analizando {len(sample_jsons)} JSON(s) para identificar campos relevantes...")
    print(f"{'='*60}")

    # Transformar los JSONs a formato legible
    print(f"\n[PASO 1] Transformando JSONs a formato legible...")
    transformed_jsons = []
    for i, j in enumerate(sample_jsons):
        transformed = transform_json_for_ai(j, max_items_per_array=5)
        transformed_jsons.append(transformed)

    # PRINT DEL PRIMER JSON TRANSFORMADO PARA DEBUGGING
    print(f"\n{'='*60}")
    print(f"[DEBUG] JSON #1 TRANSFORMADO (de {len(sample_jsons)} analizados):")
    print(f"{'='*60}")
    print(json.dumps(transformed_jsons[0], indent=2, ensure_ascii=False, default=str))
    print(f"{'='*60}\n")

    # Combinar todos los JSONs transformados en uno solo
    print(f"[PASO 2] Combinando {len(transformed_jsons)} JSONs transformados...")
    combined = {}
    for transformed in transformed_jsons:
        for section_name, section_data in transformed.items():
            if section_name.startswith("_"):
                continue

            if section_name not in combined:
                combined[section_name] = {}

            if isinstance(section_data, dict):
                for field_name, field_value in section_data.items():
                    if field_name.startswith("_"):
                        continue

                    if field_name not in combined[section_name]:
                        combined[section_name][field_name] = set()

                    # Agregar valores
                    if isinstance(field_value, list):
                        for v in field_value:
                            combined[section_name][field_name].add(str(v))
                    else:
                        combined[section_name][field_name].add(str(field_value))

    # Convertir sets a listas
    for section_name in combined:
        for field_name in list(combined[section_name].keys()):
            values = list(combined[section_name][field_name])
            if len(values) == 1:
                combined[section_name][field_name] = values[0]
            elif len(values) > 1:
                combined[section_name][field_name] = values[:5]  # Máximo 5 valores
            else:
                del combined[section_name][field_name]

    # Convertir a string JSON legible para el prompt
    jsons_str = json.dumps(combined, indent=2, ensure_ascii=False, default=str)

    # Contar campos totales
    total_fields = sum(len(section_data) for section_data in combined.values() if isinstance(section_data, dict))
    print(f"[IA] JSON combinado tiene {len(combined)} secciones y {total_fields} campos únicos")

    context = """
Eres un experto en análisis de datos de trazabilidad textil. Tu tarea es analizar el JSON proporcionado
y determinar qué campos contienen información relevante para responder la pregunta del usuario.

**IMPORTANTE - FORMATO DEL JSON**:
El JSON está TRANSFORMADO a un formato legible:
- Las SECCIONES tienen nombres descriptivos: INFORMACION_GENERAL, TINTORERIA, COSTURA, TEJEDURIA, etc.
- Los CAMPOS tienen nombres legibles: RAMA_ACABADO, maquina_tenido, operacion_costura, etc.
- Los valores pueden ser strings únicos o listas de valores

**SECCIONES Y QUÉ CONTIENEN**:
- INFORMACION_GENERAL: Cliente, estilo, talla, género, descripción de prenda
- ALMACEN: Número de caja, destino, fecha recepción
- ACABADO: Fechas de pesado, empaque, auditoría, personas responsables
- MEDICIONES_ACABADO: Mediciones de control de calidad (talla, dimensiones)
- COSTURA: Orden de costura, línea, planta, supervisor
- OPERACIONES_COSTURA: Operaciones específicas (Unir hombros, Pegar cuello, etc.) y operarios
- CORTE: Orden de corte, número de tendido
- OPERACIONES_CORTE: Operaciones de corte (Tendido, Corte, Numeración) y operarios
- TINTORERIA: Máquinas (RAMA_ACABADO, maquina_tenido, maquina_secado), OB, UD, colores, telas
- TEJEDURIA: Máquinas tejedoras, operarios, fechas de tejido
- HILOS, LOTES_HILO, PROVEEDORES_HILO: Información de hilos y proveedores

**CAMPOS MUY IMPORTANTES**:
- RAMA_ACABADO: Las "Ramas" son máquinas de acabado (Rama 1, Rama 2, Rama 3)
- maquina_tenido: Máquinas de teñido (ej: Saturno 30.600)
- maquina_secado: Máquinas de secado
- operacion_costura: Descripción de operaciones de costura
- operacion_corte: Descripción de operaciones de corte
- numero_OB: Número de orden de producción
- numero_UD: Número de unidad de producción
- operario: Nombre del operario que realizó una operación

**INSTRUCCIONES**:
1. Lee la pregunta del usuario cuidadosamente
2. Busca en el JSON los campos que contengan información relevante
**FORMATO DE RESPUESTA** (JSON estricto, sin markdown):
{
    "has_relevant_data": true/false,
    "keys": ["SECCION.campo", "SECCION.otro_campo", ...],
    "explanation": "Explicación si has_relevant_data es false, null si es true",
    "reasoning": "Breve explicación de por qué estos campos son relevantes"
}

**REGLAS**:
- has_relevant_data: true si encontraste CUALQUIER campo que pueda ayudar a responder
- has_relevant_data: false SOLO si definitivamente NO hay información relacionada
- En "keys", usa el formato SECCION.campo (ej: "TINTORERIA.RAMA_ACABADO")
- Si hay duda, marca has_relevant_data: true para no perder información
- Retorna SOLO el JSON, sin texto adicional ni formato markdown

**EJEMPLOS DE RESPUESTA**:

Usuario pregunta: "¿Qué ramas procesaron las prendas?"
{
    "has_relevant_data": true,
    "keys": ["TINTORERIA.RAMA_ACABADO"],
    "explanation": null,
    "reasoning": "RAMA_ACABADO en TINTORERIA contiene los nombres de las Ramas de acabado"
}

Usuario pregunta: "¿Qué operaciones de costura se hicieron?"
{
    "has_relevant_data": true,
    "keys": ["OPERACIONES_COSTURA.operacion_costura", "OPERACIONES_COSTURA.operario"],
    "explanation": null,
    "reasoning": "operacion_costura contiene las descripciones de las operaciones realizadas"
}

Usuario pregunta: "¿Qué máquinas se usaron en tejeduría?"
{
    "has_relevant_data": true,
    "keys": ["TEJEDURIA.maquina_tejeduria", "TEJEDURIA.fabricante_maquina_tejeduria"],
    "explanation": null,
    "reasoning": "maquina_tejeduria contiene los nombres de las máquinas de tejeduría"
}
"""

    prompt = f"""
**PREGUNTA DEL USUARIO**: {user_question}

**JSON TRANSFORMADO PARA ANALIZAR**:
{jsons_str}

Analiza este JSON y determina qué campos contienen información relevante para responder la pregunta.
Recuerda:
- Las SECCIONES son: INFORMACION_GENERAL, TINTORERIA, COSTURA, OPERACIONES_COSTURA, TEJEDURIA, etc.
- Los CAMPOS tienen nombres legibles: RAMA_ACABADO, maquina_tenido, operacion_costura, operario, etc.
- Los valores ya están visibles (pueden ser strings o listas)
- Retorna los campos en formato SECCION.campo
"""

    try:
        response_text = provider.chat(context, prompt, temperature=0.1)

        # Limpiar formato markdown si existe
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        if response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()

        result = json.loads(response_text)

        # Validar estructura de respuesta
        if not isinstance(result, dict):
            print(f"[WARN] IA retornó formato inválido, asumiendo datos relevantes por seguridad")
            return {
                "keys": [],
                "has_relevant_data": True,
                "explanation": None
            }

        has_relevant = result.get("has_relevant_data", True)
        keys = result.get("keys", [])
        explanation = result.get("explanation")
        reasoning = result.get("reasoning", "")

        # Log del resultado
        if has_relevant:
            print(f"[IA] ✓ Datos relevantes encontrados.")
            print(f"[IA] Campos identificados: {keys}")
            if reasoning:
                print(f"[IA] Razonamiento: {reasoning}")
        else:
            print(f"[IA] ✗ NO hay datos relevantes en el JSON")
            print(f"[IA] Explicación: {explanation}")

        return {
            "keys": keys,
            "has_relevant_data": has_relevant,
            "explanation": explanation
        }

    except Exception as e:
        print(f"[WARN] Error al identificar campos relevantes: {e}")
        # En caso de error, asumir que SÍ hay datos para no bloquear consultas válidas
        print(f"[FALLBACK] Error en análisis - asumiendo datos relevantes por seguridad")
        return {
            "keys": [],
            "has_relevant_data": True,
            "explanation": None
        }

def fetch_and_filter_jsons(hashes, user_question, max_workers=10):
    """
    Recupera múltiples JSONs de Swarm en paralelo.

    ESTRATEGIA ADAPTATIVA:
    - Si hay ≤10 hashes: Retornar JSONs COMPLETOS (sin filtrado)
    - Si hay >10 hashes: Analizar primeros 5 JSONs completos para identificar campos,
                         luego filtrar el resto

    Args:
        hashes: Lista de hashes Swarm
        user_question: Pregunta del usuario para identificar campos relevantes
        max_workers: Número de threads paralelos para descarga (default: 10)

    Returns:
        dict: Diccionario con estructura:
            - Si hay datos: {hash: data, ...}
            - Si NO hay datos relevantes: {"__NO_RELEVANT_DATA__": True, ...}
    """
    if not hashes or len(hashes) == 0:
        print("[WARN] No hay hashes para procesar")
        return {}

    num_hashes = len(hashes)
    print(f"\n[PASO 5] Procesando {num_hashes} JSONs de Swarm...")
    start_time = time.time()

    # ============================================================================
    # ESTRATEGIA ADAPTATIVA: Decidir según cantidad de hashes
    # ============================================================================

    USE_FULL_JSONS = num_hashes <= 10  # Umbral: 10 hashes o menos = JSONs completos
    SAMPLE_SIZE = 3  # CAMBIADO: Usar solo 3 JSONs de muestra para análisis

    if USE_FULL_JSONS:
        print(f"\n[ESTRATEGIA] ≤10 hashes detectados → Usando JSONs COMPLETOS (sin filtrado)")
        print(f"  → Se retornarán los {num_hashes} JSONs completos para máxima precisión")
        relevant_keys = []  # No filtrar, usar JSONs completos
        sample_jsons = []  # No necesitamos muestras
    else:
        print(f"\n[ESTRATEGIA] >10 hashes detectados → Analizando {SAMPLE_SIZE} JSONs de muestra")
        print(f"  → Se identificarán campos relevantes y se filtrarán los {num_hashes} JSONs")

        # PASO 1: Descargar los primeros 3 JSONs como muestra
        print(f"\n[Paso 5.1] Descargando {SAMPLE_SIZE} JSONs de muestra para análisis...")

        sample_hashes = hashes[:SAMPLE_SIZE]
        sample_jsons = []

        for i, hash_val in enumerate(sample_hashes):
            print(f"  → Descargando muestra {i+1}/{SAMPLE_SIZE} (hash: {hash_val[:20]}...)")
            json_data = fetch_json_from_swarm(hash_val)
            if json_data:
                sample_jsons.append(json_data)
            else:
                print(f"  [WARN] No se pudo descargar muestra {i+1}")

        if len(sample_jsons) == 0:
            print("[ERROR] No se pudo recuperar ningún JSON de muestra")
            return {}

        print(f"  ✓ {len(sample_jsons)} JSONs de muestra descargados")

        # PASO 2: Usar IA para identificar campos relevantes
        # NOTA: extract_relevant_keys_with_ai ahora transforma los JSONs internamente
        print(f"\n[Paso 5.2] Analizando JSONs con IA (se transformarán a formato legible)...")
        relevance_analysis = extract_relevant_keys_with_ai(sample_jsons, user_question)

        # VALIDACIÓN TEMPRANA - Si no hay datos relevantes, ABORTAR
        if not relevance_analysis.get("has_relevant_data", True):
            print(f"\n{'='*60}")
            print(f"[ABORTO TEMPRANO] Los JSONs NO contienen datos relevantes")
            print(f"{'='*60}")
            print(f"Explicación: {relevance_analysis.get('explanation', 'No especificada')}")

            available_sections = list(sample_jsons[0].keys()) if sample_jsons else []

            elapsed_time = time.time() - start_time
            print(f"\n✓ Análisis completado en {elapsed_time:.1f} segundos")
            print(f"✓ Se analizaron {len(sample_jsons)} JSONs (evitando procesar {num_hashes} innecesariamente)")

            return {
                "__NO_RELEVANT_DATA__": True,
                "explanation": relevance_analysis.get("explanation", "El JSON no contiene la información solicitada."),
                "sample_sections": available_sections[:10],
                "total_hashes_skipped": num_hashes,
                "samples_analyzed": len(sample_jsons)
            }

        relevant_keys = relevance_analysis.get("keys", [])

    # PASO 3: Función para extraer solo los campos relevantes de un JSON
    def extract_fields(json_data, field_patterns):
        """
        Extrae campos específicos de un JSON usando el nuevo formato de transformación.

        ESTRATEGIA:
        1. Transforma el JSON a formato legible con transform_json_for_ai
        2. Busca los campos especificados (formato: SECCION.campo o solo campo)

        Args:
            json_data: JSON original de trazabilidad
            field_patterns: Lista de patrones (ej: ["TINTORERIA.RAMA_ACABADO", "RAMA_ACABADO"])

        Returns:
            dict: Campos extraídos con sus valores únicos
        """
        # Si no hay paths específicos, retornar JSON transformado compacto
        if not field_patterns or len(field_patterns) == 0:
            transformed = transform_json_for_ai(json_data, max_items_per_array=3)

            # Aplanar para resultado más simple
            compact_result = {}
            for section_name, section_data in transformed.items():
                if section_name.startswith("_"):
                    continue
                if isinstance(section_data, dict):
                    for field_name, field_value in section_data.items():
                        if field_name.startswith("_"):
                            continue
                        key = f"{section_name}.{field_name}"
                        compact_result[key] = field_value
                        if len(compact_result) >= 20:
                            break
                if len(compact_result) >= 20:
                    compact_result["_nota"] = "Resumen limitado a 20 campos"
                    break

            return compact_result

        # Transformar el JSON a formato legible
        transformed = transform_json_for_ai(json_data, max_items_per_array=10)

        # Extraer los campos especificados
        extracted = {}

        for pattern in field_patterns:
            pattern_parts = pattern.split(".")
            if len(pattern_parts) == 2:
                # Formato: SECCION.campo
                section_name = pattern_parts[0]
                field_name = pattern_parts[1]

                if section_name in transformed:
                    section_data = transformed[section_name]
                    if isinstance(section_data, dict) and field_name in section_data:
                        extracted[field_name] = section_data[field_name]
            else:
                # Solo campo - buscar en todas las secciones
                field_name = pattern
                for section_name, section_data in transformed.items():
                    if section_name.startswith("_"):
                        continue
                    if isinstance(section_data, dict):
                        # Buscar coincidencia exacta o parcial
                        for key, value in section_data.items():
                            if key.lower() == field_name.lower() or field_name.lower() in key.lower():
                                extracted[key] = value

        # Si no se encontró nada, intentar búsqueda más amplia
        if not extracted:
            for pattern in field_patterns:
                pattern_lower = pattern.lower().replace(".", " ").strip()
                for section_name, section_data in transformed.items():
                    if section_name.startswith("_"):
                        continue
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            if pattern_lower in key.lower() or pattern_lower in section_name.lower():
                                extracted[f"{section_name}.{key}"] = value

        # Eliminar duplicados y limitar valores
        for key in list(extracted.keys()):
            if isinstance(extracted[key], list):
                # Eliminar duplicados manteniendo orden
                seen = set()
                unique = []
                for v in extracted[key]:
                    v_str = str(v)
                    if v_str not in seen and v_str:
                        seen.add(v_str)
                        unique.append(v)
                extracted[key] = unique[:10]  # Máximo 10 valores únicos

        return extracted if extracted else {"nota": "Campos solicitados no encontrados en JSON"}

    # ============================================================================
    # PASO 4: Procesar todos los hashes EN PARALELO
    # ============================================================================

    if USE_FULL_JSONS:
        print(f"\n[Paso 5.3] Descargando {num_hashes} JSONs COMPLETOS en paralelo...")
    else:
        print(f"\n[Paso 5.3] Descargando y filtrando {num_hashes} JSONs en paralelo...")
        print(f"  → Campos a extraer: {relevant_keys[:5]}{'...' if len(relevant_keys) > 5 else ''}")

    result_jsons = {}
    successful = 0
    failed = 0
    total_size = 0

    # Límites adaptativos según estrategia
    if USE_FULL_JSONS:
        MAX_TOTAL_SIZE = 500000   # 500KB para JSONs completos (pocos hashes)
        MAX_INDIVIDUAL_SIZE = 60000  # 60KB por JSON completo
    else:
        MAX_TOTAL_SIZE = 200000   # 200KB para JSONs filtrados (muchos hashes)
        MAX_INDIVIDUAL_SIZE = 5000   # 5KB por JSON filtrado

    # Función para procesar un hash individual
    def process_single_hash(hash_val, use_full):
        """Procesa un hash individual: descarga y opcionalmente filtra"""
        try:
            # Descargar sin logs verbosos (modo paralelo)
            json_data = fetch_json_from_swarm(hash_val, timeout=15, verbose=False)

            if not json_data:
                return hash_val, None, 0, "download_failed"

            if use_full:
                # Retornar JSON completo (sin filtrar)
                result_data = json_data
            else:
                # Extraer campos relevantes
                result_data = extract_fields(json_data, relevant_keys)

            # Calcular tamaño
            result_str = json.dumps(result_data, ensure_ascii=False, default=str)
            result_size = len(result_str)

            # Truncar si es muy grande
            if result_size > MAX_INDIVIDUAL_SIZE:
                if use_full:
                    # Para JSONs completos, limitar arrays internos
                    truncated_data = {}
                    for key, value in result_data.items():
                        if isinstance(value, list) and len(value) > 3:
                            truncated_data[key] = value[:3]
                            truncated_data[f"__{key}_total__"] = len(value)
                        else:
                            truncated_data[key] = value
                    truncated_data["_nota"] = "JSON truncado por tamaño"
                    result_data = truncated_data
                else:
                    # Para JSONs filtrados, mostrar solo primeros campos
                    keys_list = list(result_data.keys())
                    truncated_data = {k: result_data[k] for k in keys_list[:10]}
                    truncated_data["_truncated"] = f"Mostrando 10 de {len(keys_list)} campos"
                    result_data = truncated_data

                result_str = json.dumps(result_data, ensure_ascii=False, default=str)
                result_size = len(result_str)
                return hash_val, result_data, result_size, "success_truncated"

            return hash_val, result_data, result_size, "success"

        except Exception as e:
            return hash_val, None, 0, f"error: {str(e)[:100]}"

    # Usar ThreadPoolExecutor para procesamiento paralelo
    print(f"  → Iniciando descarga paralela con {max_workers} workers...")
    print(f"  → Límite total: {MAX_TOTAL_SIZE//1000}KB | Límite por JSON: {MAX_INDIVIDUAL_SIZE//1000}KB")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Enviar todos los hashes para procesamiento paralelo
        future_to_hash = {
            executor.submit(process_single_hash, hash_val, USE_FULL_JSONS): hash_val
            for hash_val in hashes
        }

        # Procesar resultados a medida que se completan
        completed = 0
        for future in as_completed(future_to_hash):
            hash_val, result_data, result_size, status = future.result()
            completed += 1

            # Verificar si excedimos el límite total
            if total_size + result_size > MAX_TOTAL_SIZE:
                print(f"\n[LIMIT] Límite de tamaño alcanzado ({total_size:,} bytes)")
                print(f"[INFO] Procesados {completed}/{num_hashes} JSONs antes de alcanzar límite")
                # Cancelar tareas pendientes
                for pending_future in future_to_hash:
                    pending_future.cancel()
                break

            # Procesar según el estado
            if status.startswith("success"):
                result_jsons[hash_val] = result_data
                total_size += result_size
                successful += 1

                # Mostrar progreso cada 5 JSONs o al final
                if completed % 5 == 0 or completed == num_hashes:
                    mode = "completos" if USE_FULL_JSONS else "filtrados"
                    print(f"  [{completed}/{num_hashes}] ✓ {successful} {mode} | "
                          f"Tamaño: {total_size:,} bytes (~{total_size//1000}KB)")
            else:
                failed += 1
                if "download_failed" in status:
                    print(f"  [WARN] Fallo descarga: {hash_val[:16]}...")
                elif "error" in status:
                    print(f"  [ERROR] {status}")

    elapsed_time = time.time() - start_time

    mode_str = "COMPLETOS" if USE_FULL_JSONS else "FILTRADOS"
    print(f"\n✓ Procesamiento completado en {elapsed_time:.1f} segundos")
    print(f"✓ Modo: JSONs {mode_str}")
    print(f"✓ Velocidad: {num_hashes/elapsed_time:.1f} JSONs/segundo")
    print(f"✓ Resultados: {successful} éxitos, {failed} fallos")
    print(f"✓ JSONs procesados: {len(result_jsons)}")
    print(f"✓ Tamaño total: {total_size:,} bytes (~{total_size//1000}KB)\n")

    return result_jsons

def final_response_bot(all_data_str, user_question, max_data_size=80000):
    """
    Bot final: Sintetiza una respuesta coherente y precisa basada en toda la información recabada.

    IMPORTANTE: all_data ahora tiene esta estructura optimizada:
    - user_question: Pregunta del usuario
    - razonamiento: Análisis del orquestador
    - db_summary: Resumen de datos de DB (NO datos crudos completos)
    - jsons: Datos FILTRADOS de JSONs (solo campos relevantes)
    - metadata: Estadísticas básicas

    Args:
        all_data_str: String JSON con datos recolectados
        user_question: Pregunta original del usuario
        max_data_size: Tamaño máximo en caracteres (default: 80KB - aumentado porque ya filtramos)
    """
    # Usar el sistema multi-modelo
    provider = get_ai_provider()

    # VALIDACIÓN CRÍTICA: Verificar tamaño de datos antes de enviar
    data_size = len(all_data_str)
    print(f"[VALIDACIÓN] Tamaño de datos: {data_size:,} caracteres")

    if data_size > max_data_size:
        print(f"[WARN] Datos exceden el límite ({data_size:,} > {max_data_size:,})")
        print(f"[TRUNCATE] Aplicando truncamiento inteligente...")

        try:
            all_data = json.loads(all_data_str)

            # Estrategia de truncamiento: Mantener estructura, reducir JSONs
            truncated_data = {
                "user_question": all_data.get("user_question"),
                "razonamiento": all_data.get("razonamiento"),
                "metadata": all_data.get("metadata"),
                "db_summary": all_data.get("db_summary"),  # Ya es un resumen, mantenerlo
                "jsons": {},
                "truncated_warning": f"Datos truncados: {data_size:,} caracteres originales"
            }

            # Incluir solo una muestra de JSONs (primeros 30)
            jsons_dict = all_data.get("jsons", {})
            if jsons_dict:
                sample_jsons = dict(list(jsons_dict.items())[:30])
                truncated_data["jsons"] = sample_jsons
                truncated_data["jsons_note"] = f"Mostrando 30 de {len(jsons_dict)} JSONs"

            all_data_str = json.dumps(truncated_data, ensure_ascii=False)
            new_size = len(all_data_str)
            print(f"✓ Datos truncados: {data_size:,} → {new_size:,} caracteres ({100*new_size//data_size}%)")

        except Exception as e:
            print(f"[ERROR] Fallo al truncar datos: {e}")
            # Si falla el truncamiento, usar solo metadata
            all_data_str = json.dumps({
                "error": "Datos demasiado grandes para procesar",
                "user_question": user_question,
                "size": data_size
            }, ensure_ascii=False)

    context = """
Eres un experto asistente de trazabilidad de prendas textiles. Tu objetivo es responder consultas de usuarios de manera clara, precisa y profesional.

**TU TAREA**:
Analiza los datos proporcionados y genera una respuesta coherente que:
1. Responda directamente la pregunta del usuario
2. Use números y estadísticas concretas cuando estén disponibles
3. Estructure la información de forma clara (usa listas, bullets si es necesario)
4. Mencione limitaciones si las hay (ej: "Se analizaron los primeros 100 registros de X total")

**CONTEXTO DEL DOMINIO - TRAZABILIDAD TEXTIL DE PRENDAS**:
Estos datos provienen de un sistema de trazabilidad textil que rastrea prendas desde la materia prima hasta el acabado final.

**CONVENCIÓN DE NOMBRES DE COLUMNAS**:
Los nombres de columnas siguen un patrón: comienzan con 'T' seguido de abreviaturas de 4 caracteres.
Para entender el significado, quita la 'T' inicial y lee de 4 en 4 caracteres:
- TCODICLIE → CODI + CLIE = Código de Cliente
- TFABRMAQUTENI → FABR + MAQU + TENI = Fabricación de Máquina de Teñido
- TNOMBMAQUACAB → NOMB + MAQU + ACAB = Nombre de Máquina de Acabado (conocidas como "Ramas")
- TDESCOPERESPE → DESC + OPER + ESPE = Descripción de Operación Específica
- TNUMELINECOST → NUME + LINE + COST = Número de Línea de Costura

**SECCIONES DE DATOS Y SUS SIGNIFICADOS**:
- tztotrazwebinfo → Información general de la prenda (cliente, estilo, talla, género)
- tztotrazwebalma → Información de almacén
- tztotrazwebacab → Acabado final (incluye Ramas de acabado, secado)
- tztotrazwebacabmedi → Mediciones y control de calidad
- tztotrazwebcost → Costura/confección
- tztotrazwebcostoper → Operaciones específicas de costura
- tztotrazwebcort → Corte de tela
- tztotrazwebcortoper → Operaciones de corte
- tztotrazwebtint → Tintorería (teñido, máquinas de teñido, ramas, secado)
- tztotrazwebteje → Tejeduría (máquinas tejedoras)
- tztotrazwebhilo → Hilos utilizados
- tztotrazwebhilolote → Lotes de hilos
- tztotrazwebhiloloteprin → Facturación y proveedores

**KEYS IMPORTANTES QUE DEBES CONOCER**:
- TNOMBMAQUACAB → Máquinas de acabado llamadas "Ramas" (ej: Rama 1, Rama 2, Rama 3)
- TNOMBMAQUSECA → Máquina de secado
- TNOMBMAQUCORT → Máquina cortadora
- TFABRMAQUTENI → Máquina de teñido
- TNUMEOB → Número de OB (Orden de Bordado/Producción)
- TNUMEUD → Número de UD (Unidad de Producción)
- TTIPOARTI → Tipo de artículo
- TDESCOPERESPE → Descripción de operación de costura
- TNOMBPERS → Nombre del operario
- TNUMELINECOST → Número de línea de costura

**ESTRUCTURA DE DATOS QUE RECIBIRÁS**:
- user_question: La pregunta original del usuario
- razonamiento: Análisis previo del sistema
- db_summary: Resumen de datos de la base de datos (conteos, agregaciones)
- jsons: Diccionario con datos FILTRADOS de trazabilidad extraídos de JSONs
  - Cada entrada contiene solo los campos relevantes para la pregunta
- metadata: Estadísticas (total_records, jsons_analyzed)

**REGLAS DE RESPUESTA**:
1. NO inventes datos - solo usa lo que está en los datos proporcionados
2. Si falta información, indícalo claramente (ej: "Los datos de máquinas aún no están disponibles")
3. Para conteos, usa los números de db_summary o metadata.total_records
4. Sé conversacional pero preciso - habla en español natural
5. NO menciones detalles técnicos como "JSON", "hash", "DataFrame" al usuario final
6. Si la respuesta es un conteo simple, responde directamente: "Hay X prendas..."
7. Para listas, limita a los más relevantes (máximo 10 items) e indica si hay más
8. Cuando veas TNOMBMAQUACAB, tradúcelo como "Rama" en tu respuesta
9. Interpreta los nombres de columnas usando la convención de 4 caracteres

**FORMATO DE RESPUESTA**:
- Para conteos simples: "Hay [número] prendas [descripción]."
- Para listas: Usa bullets o enumeración clara
- Para análisis complejos: Divide en secciones con subtítulos claros

**EJEMPLOS**:

Consulta: "¿Cuántas prendas de LACOSTE hay?"
Datos: {"db_summary": [{"count(*)": 1523}], "metadata": {"total_records": 1523}}
Respuesta: "Hay un total de 1,523 prendas de la marca LACOSTE en el sistema."

Consulta: "¿Qué ramas procesaron las prendas de LACOSTE?"
Datos: {
  "db_summary": {"total_registros": 80},
  "jsons": {
    "hash1": {"TNOMBMAQUACAB": ["Rama 2"]},
    "hash2": {"TNOMBMAQUACAB": ["Rama 2"]},
    "hash3": {"TNOMBMAQUACAB": ["Rama 3"]}
  },
  "metadata": {"jsons_analyzed": 80}
}
Respuesta: "Las prendas de LACOSTE fueron procesadas en las siguientes Ramas de acabado:

• Rama 2
• Rama 3

Se analizaron 80 prendas en total."

Consulta: "¿Qué máquinas se usaron en tejeduría?"
Datos: {
  "jsons": {
    "hash1": {"TNOMBMAQU": ["Matsuya 21 G16 F40", "Matsuya 31 G16 F40"]},
    "hash2": {"TNOMBMAQU": ["Matsuya 21 G16 F40", "Semel 5- 20 Agujas"]}
  }
}
Respuesta: "Las máquinas utilizadas en tejeduría fueron:
• Matsuya 21 G16 F40
• Matsuya 31 G16 F40
• Semel 5- 20 Agujas"

Consulta: "¿Qué operaciones de costura se realizaron?"
Datos: {
  "jsons": {
    "hash1": {"TDESCOPERESPE": ["Cerrado de costados", "Pegado de cuello"]},
    "hash2": {"TDESCOPERESPE": ["Cerrado de costados", "Dobladillo"]}
  }
}
Respuesta: "Las operaciones de costura realizadas fueron:
• Cerrado de costados
• Pegado de cuello
• Dobladillo"

**IMPORTANTE**:
- Responde SOLO con la respuesta final al usuario - sin explicaciones de proceso, sin código, sin jerga técnica
- Los datos en 'jsons' ya están filtrados y contienen SOLO los campos relevantes
- Agrupa y resume datos repetidos (ej: contar valores únicos, listar valores distintos)
- Usa nombres amigables: "Rama" en vez de "TNOMBMAQUACAB", "línea de costura" en vez de "TNUMELINECOST"
"""

    try:
        all_data = json.loads(all_data_str)
    except json.JSONDecodeError:
        return "Lo siento, hubo un error al procesar la información. Por favor, intenta reformular tu consulta."

    # Preparar prompt con datos estructurados
    prompt = f"Consulta del usuario: {user_question}\n\nDatos disponibles:\n{json.dumps(all_data, indent=2, ensure_ascii=False)}"

    respuesta_texto = provider.chat(context, prompt, temperature=0.3)
    print("\n=== RESPUESTA FINAL GENERADA ===")
    print(respuesta_texto)
    print("================================\n")
    return respuesta_texto

def validate_response_logic(response_text, expected_type="text"):
    """
    Valida que una respuesta tenga sentido lógico y no sea un error o contenido vacío.
    - response_text: Texto de la respuesta a validar.
    - expected_type: Tipo esperado ('sql', 'json', 'text').

    Returns: (is_valid: bool, error_message: str)
    """
    if not response_text or len(response_text.strip()) == 0:
        return False, "Respuesta vacía"

    response_lower = response_text.lower().strip()

    # Detectar errores comunes en respuestas de IA
    error_indicators = [
        "lo siento", "no puedo", "error", "disculpa", "no entiendo",
        "no sé", "unable to", "cannot", "failed", "invalid"
    ]

    if expected_type == "sql":
        # Validar que sea un SQL válido
        if not response_text.strip().upper().startswith('SELECT'):
            return False, "SQL no comienza con SELECT"

        # Detectar SQL peligroso
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in response_text.upper():
                return False, f"SQL contiene operación peligrosa: {keyword}"

        # Verificar que tenga FROM
        if 'FROM' not in response_text.upper():
            return False, "SQL no contiene cláusula FROM"

    elif expected_type == "json":
        # Validar que sea un JSON parseable
        try:
            parsed = json.loads(response_text)
            if not isinstance(parsed, dict):
                return False, "JSON no es un objeto"
        except json.JSONDecodeError as e:
            return False, f"JSON inválido: {str(e)}"

    elif expected_type == "text":
        # Para texto general, verificar que no sea un mensaje de error
        for indicator in error_indicators:
            if indicator in response_lower and len(response_text) < 100:
                return False, f"Respuesta parece un error: contiene '{indicator}'"

    # Verificar que no sea solo espacios o caracteres especiales
    if len(response_text.strip()) < 5:
        return False, "Respuesta demasiado corta"

    return True, ""

def validate_query_feasibility(user_question, total_hashes_available):
    """
    Valida si una consulta es factible y coherente antes de procesarla.

    Args:
        user_question: Pregunta del usuario
        total_hashes_available: Número total de hashes que se procesarían

    Returns:
        dict: {
            "is_valid": bool,
            "requires_confirmation": bool,
            "message": str (mensaje para el usuario),
            "recommended_limit": int (hashes recomendados a procesar)
        }
    """
    # Usar el sistema multi-modelo
    provider = get_ai_provider()

    validation_context = """
Eres un experto en validar consultas sobre trazabilidad de prendas textiles.

**TU TAREA**:
Analizar si una pregunta del usuario es factible, coherente y completa.

**CRITERIOS DE VALIDACIÓN**:

1. **Pregunta NO VÁLIDA** (is_valid: false):
   - Pregunta sin sentido o incoherente
   - Solicita información que NUNCA estaría en el sistema (ej: "color del cielo", "clima")
   - Demasiado ambigua para entender qué se pide
   - Falta información crítica imposible de inferir

2. **Pregunta VÁLIDA pero necesita CONFIRMACIÓN** (requires_confirmation: true):
   - Procesaría >100 hashes (podría tardar mucho)
   - Pregunta muy amplia que podría ser más específica
   - Usuario debería saber que se usará muestra limitada

3. **Pregunta VÁLIDA y DIRECTA** (requires_confirmation: false):
   - Clara, específica, con filtros adecuados
   - Procesaría ≤100 hashes
   - Puede responderse directamente

**FORMATO DE RESPUESTA**:
Responde SOLO con un JSON válido:
{
    "is_valid": true/false,
    "requires_confirmation": true/false,
    "message": "Mensaje claro y amigable para el usuario (en español)",
    "recommended_limit": número_de_hashes_a_procesar,
    "suggestion": "Sugerencia opcional para mejorar la pregunta (null si no aplica)"
}

**EJEMPLOS**:

Input: "¿Cuántas prendas de LACOSTE hay?"
Total hashes: 450
Output:
{
    "is_valid": true,
    "requires_confirmation": true,
    "message": "Tu consulta procesaría 450 prendas. Para un análisis más rápido, ¿podrías ser más específico? (ej: tipo de prenda, género, talla). O puedo analizar una muestra de 100 prendas.",
    "recommended_limit": 100,
    "suggestion": "Prueba: '¿Cuántas prendas de LACOSTE para hombres hay?' o '¿Cuántas T-Shirts de LACOSTE hay?'"
}

Input: "¿Qué color tiene el cielo?"
Total hashes: 0
Output:
{
    "is_valid": false,
    "requires_confirmation": false,
    "message": "Lo siento, tu pregunta no está relacionada con trazabilidad de prendas. Solo puedo responder consultas sobre producción, clientes, tipos de prenda, máquinas, etc.",
    "recommended_limit": 0,
    "suggestion": "Intenta preguntas como: '¿Cuántas prendas hay de X cliente?' o '¿Qué máquinas procesaron las prendas de Y?'"
}

Input: "Lista las prendas"
Total hashes: 15000
Output:
{
    "is_valid": true,
    "requires_confirmation": true,
    "message": "Tu consulta es muy amplia (15,000 prendas en total). Por favor, especifica: ¿qué cliente, tipo de prenda, género o talla te interesa? O puedo analizar una muestra de 100 prendas.",
    "recommended_limit": 100,
    "suggestion": "Prueba: 'Lista prendas de [CLIENTE]' o 'Lista prendas de tipo [T-Shirt/Camisa/etc]'"
}

Input: "¿Qué máquinas procesaron las prendas de NIKE talla 10?"
Total hashes: 45
Output:
{
    "is_valid": true,
    "requires_confirmation": false,
    "message": null,
    "recommended_limit": 45,
    "suggestion": null
}

Input: "prendas"
Total hashes: 15000
Output:
{
    "is_valid": false,
    "requires_confirmation": false,
    "message": "Tu pregunta es demasiado ambigua. ¿Qué quieres saber sobre las prendas? (cantidad, clientes, tipos, máquinas, etc.)",
    "recommended_limit": 0,
    "suggestion": "Intenta: '¿Cuántas prendas hay de X?' o '¿Qué tipos de prendas existen?'"
}
"""

    prompt = f"""
Pregunta del usuario: "{user_question}"
Total de hashes/prendas que procesaría: {total_hashes_available}

¿Es una consulta válida y factible? ¿Necesita confirmación del usuario?
"""

    try:
        response_text = provider.chat(validation_context, prompt, temperature=0.2)

        # Limpiar formato markdown
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        if response_text.endswith("```"):
            response_text = response_text.replace("```", "").strip()

        validation_result = json.loads(response_text)

        return validation_result

    except Exception as e:
        print(f"[WARN] Error en validación de consulta: {e}")
        # Fallback: Si hay muchos hashes, pedir confirmación
        if total_hashes_available > 100:
            return {
                "is_valid": True,
                "requires_confirmation": True,
                "message": f"Tu consulta procesaría {total_hashes_available} registros. ¿Deseas continuar con los primeros 100 o prefieres ser más específico?",
                "recommended_limit": 100,
                "suggestion": None
            }
        else:
            return {
                "is_valid": True,
                "requires_confirmation": False,
                "message": None,
                "recommended_limit": total_hashes_available,
                "suggestion": None
            }

def orquestador_bot(user_question, max_hashes=100, max_tokens=10000, max_retries=3, auto_confirm=False):
    """
    Bot orquestador impulsado por IA: Analiza la consulta del usuario, decide el flujo dinámico,
    y coordina llamadas a funciones para responder de manera óptima.

    Args:
        user_question: Pregunta del usuario en español
        max_hashes: Límite de hashes a procesar (el orquestador puede ajustarlo según necesidad)
        max_tokens: Límite de tokens antes de llamar al bot final (el orquestador puede ajustarlo)
        max_retries: Número máximo de reintentos por operación fallida
        auto_confirm: Si es True, procesa automáticamente sin pedir confirmación (para testing)

    Returns:
        str: Respuesta final al usuario
    """
    # Usar el sistema multi-modelo
    provider = get_ai_provider()

    print(f"\n{'='*80}")
    print(f"NUEVA CONSULTA: {user_question}")
    print(f"{'='*80}\n")

    # PASO 0: Corrección automática de errores de escritura
    print("[PASO 0] Verificando y corrigiendo posibles errores de escritura...")
    corrected_question, corrections = correct_user_input_with_ai(user_question)

    # Si hubo correcciones, usar la pregunta corregida
    if corrections:
        print(f"✓ Pregunta original corregida automáticamente")
        user_question = corrected_question
    else:
        print("✓ No se detectaron errores de escritura")

    # Contexto mejorado para el orquestador IA
    orchestrator_context = """
Eres un orquestador inteligente especializado en consultas de trazabilidad de prendas textiles.

**ARQUITECTURA DEL SISTEMA**:
1. **Base de Datos (MariaDB)** - Tabla: apdobloctrazhash
   Contiene metadatos de prendas y hashes Swarm:
   - TTICKBARR: ID único de prenda (tickbar)
   - TTICKHASH: Hash Swarm para recuperar trazabilidad completa
   - TCODICLIE: Código del cliente (ej: '0001', '0024')
   - TDESCCLIE: Nombre del cliente (ej: 'LACOSTE', 'NIKE')
   - TTIPOGENE: Género (Hombres, Mujeres, Unisex)
   - TTIPOEDAD: Edad (Adulto, Niño)
   - TTIPOPREN: Tipo de prenda (T-Shirt, Camisa, Batas, etc.)
   - TTIPOTEJI: Tipo de tejido (Interlock, Jersey, Rib, etc.)
   - TCODITALL: Talla (10, M, XL, etc.)
   - TNUMECAJA: Número de caja
   - TESTICLIE: Estilo del cliente
   - TETIQCLIE: Etiqueta del cliente
   - TLUGADEST: Lugar de destino
   - TNUMEVERS: Versión del registro

2. **JSONs en Swarm** (accesibles via TTICKHASH)
   Contienen trazabilidad detallada NO disponible en DB:
   - Máquinas específicas que procesaron la prenda
   - Fechas exactas de cada proceso
   - Operarios y turnos
   - Eventos de producción (corte, costura, teñido, etc.)
   - Información de hilos, lotes, proveedores
   - Detalles de calidad y auditorías

**TU MISIÓN**:
Analizar la pregunta del usuario y diseñar el flujo óptimo para responderla. Debes decidir:
1. ¿Se puede responder SOLO con datos de la DB? (ej: conteos, filtros por cliente/género/talla)
2. ¿Necesito filtrar en DB y luego consultar JSONs? (ej: "prendas de LACOSTE que pasaron por máquina 31")
3. ¿Qué filtros aplicar en la DB para reducir el conjunto de datos?
4. ¿Cuántos hashes son razonables procesar? (ej: para conteos simples: 0, para análisis detallado: 50-100)

**REGLAS DE DECISIÓN**:

A) **Consultas que NO necesitan JSONs** (needs_json_fetch: false):
   - Conteos simples: "¿Cuántas prendas de X hay?"
   - Listados de clientes/tipos: "¿Qué clientes tienen talla 10?"
   - Agregaciones por campos de DB: "Prendas por género"
   - Consultas que solo usan columnas de apdobloctrazhash

B) **Consultas que SÍ necesitan JSONs** (needs_json_fetch: true):
   - Menciona máquinas, operarios, fechas específicas, procesos
   - Pide detalles de trazabilidad: "¿Por dónde pasó la prenda X?"
   - Requiere información de hilos, lotes, proveedores
   - Combina filtros de DB con datos de JSON: "Prendas de LACOSTE por máquina"

C) **Límite de hashes**:
   - Consultas de conteo/listado simple: 0 hashes (solo DB)
   - Consultas con análisis moderado: 50-100 hashes
   - Consultas muy específicas (ej: un tickbar): todos los hashes relevantes
   - Si la query podría retornar >1000 registros, limita a 100 para análisis JSON

**FORMATO DE RESPUESTA**:
Responde SOLO con un JSON válido (sin ```json ni explicaciones extra):
{
    "razonamiento": "Análisis detallado: ¿Qué necesita el usuario? ¿Qué datos están en DB vs JSON? ¿Cómo filtrar eficientemente?",
    "query_for_query_bot": "Instrucción precisa para query_bot en español (o null si no necesita DB)",
    "needs_json_fetch": true/false,
    "limit_hashes": número (0 si no necesita JSONs, 50-100 si sí),
    "final_call": true
}

**EJEMPLOS**:

Usuario: "¿Cuántas prendas de LACOSTE hay?"
{
    "razonamiento": "Consulta simple de conteo por cliente. TDESCCLIE está en DB. No necesita JSONs ni hashes.",
    "query_for_query_bot": "¿Cuántas prendas de LACOSTE hay en total?",
    "needs_json_fetch": false,
    "limit_hashes": 0,
    "final_call": true
}

Usuario: "¿Cuántas prendas de LACOSTE para hombres y mujeres hay y por qué máquinas pasaron?"
{
    "razonamiento": "Consulta mixta: conteo por género (DB) + máquinas (JSON). Filtrar por LACOSTE en DB, luego fetch JSONs para extraer info de máquinas. Limitar a 100 hashes para no sobrecargar.",
    "query_for_query_bot": "Dame todas las prendas de LACOSTE con sus hashes, agrupadas por género",
    "needs_json_fetch": true,
    "limit_hashes": 100,
    "final_call": true
}

Usuario: "Lista los tipos de tejido disponibles"
{
    "razonamiento": "Consulta de catálogo. TTIPOTEJI está en DB. Solo necesito un SELECT DISTINCT.",
    "query_for_query_bot": "¿Qué tipos de tejido existen en la base de datos?",
    "needs_json_fetch": false,
    "limit_hashes": 0,
    "final_call": true
}

IMPORTANTE:
- Sé conservador con needs_json_fetch - solo actívalo si REALMENTE necesitas datos que NO están en DB
- El usuario NO maneja límites - tú decides basado en eficiencia
- Siempre devuelve JSON válido sin formato markdown
"""

    # Función helper mejorada para retries con validación de lógica
    def retry_operation(operation, *args, validation_type="text", **kwargs):
        """
        Ejecuta una operación con reintentos inteligentes si falla o retorna datos inválidos.

        Args:
            operation: Función a ejecutar
            *args: Argumentos posicionales para la función
            validation_type: Tipo de validación ('sql', 'json', 'text', 'dataframe')
            **kwargs: Argumentos con nombre para la función

        Returns:
            Resultado de la operación si es válido, None si falla después de todos los reintentos
        """
        retries = 0
        last_error = ""

        while retries < max_retries:
            try:
                print(f"[Retry {retries + 1}/{max_retries}] Ejecutando: {operation.__name__}")

                result = operation(*args, **kwargs)

                # Validación según el tipo de operación
                if validation_type == "dataframe":
                    # Para execute_query, verificar que el DataFrame no esté vacío
                    if result is None or (hasattr(result, 'empty') and result.empty):
                        raise ValueError("DataFrame vacío - posible query sin resultados")
                    print(f"✓ DataFrame válido con {len(result)} filas")
                    return result

                elif validation_type == "sql":
                    # Validar SQL generado
                    is_valid, error_msg = validate_response_logic(result, "sql")
                    if not is_valid:
                        raise ValueError(f"SQL inválido: {error_msg}")
                    print(f"✓ SQL válido generado")
                    return result

                elif validation_type == "json":
                    # Validar JSON (ej: plan del orquestador)
                    is_valid, error_msg = validate_response_logic(result, "json")
                    if not is_valid:
                        raise ValueError(f"JSON inválido: {error_msg}")
                    print(f"✓ JSON válido generado")
                    return result

                elif validation_type == "text":
                    # Validar texto general (respuestas finales)
                    is_valid, error_msg = validate_response_logic(result, "text")
                    if not is_valid:
                        raise ValueError(f"Respuesta inválida: {error_msg}")
                    print(f"✓ Respuesta de texto válida")
                    return result

                else:
                    # Sin validación específica, solo verificar que no sea None o vacío
                    if result is None or (isinstance(result, str) and len(result.strip()) == 0):
                        raise ValueError("Resultado vacío o nulo")
                    return result

            except Exception as e:
                retries += 1
                last_error = str(e)
                print(f"✗ Error en intento {retries}: {last_error}")

                if retries >= max_retries:
                    print(f"✗ Falló después de {max_retries} intentos")
                    return None

                # Generar corrección usando IA
                print(f"[IA] Generando corrección para el error...")

                correction_context = f"""
Error encontrado: {last_error}
Operación: {operation.__name__}
Consulta original del usuario: {user_question}

Analiza el error y sugiere una corrección específica:
- Si es un error de SQL: Proporciona un query corregido
- Si es un error de validación: Ajusta la respuesta para que sea válida
- Si es un error de datos vacíos: Sugiere una consulta alternativa

Responde SOLO con la corrección (sin explicaciones adicionales).
"""

                try:
                    correction = provider.chat(
                        "Eres un experto en corregir errores en sistemas de consulta de bases de datos.",
                        correction_context,
                        temperature=0.2
                    )
                    print(f"[IA] Corrección sugerida: {correction[:100]}...")

                    # Aplicar corrección según el tipo de operación
                    if operation.__name__ == 'query_bot':
                        # Para query_bot, usar la corrección como nueva pregunta
                        args = (correction,)
                    elif operation.__name__ == '<lambda>':
                        # Para lambdas del orquestador (plan JSON), regenerar con feedback
                        # Esto se maneja en el retry automático
                        pass

                except Exception as correction_error:
                    print(f"✗ Error al generar corrección: {correction_error}")

        print(f"✗ Operación '{operation.__name__}' falló después de {max_retries} reintentos")
        return None

    # PASO 0.5: Validación rápida de coherencia de la pregunta (NUEVO)
    print("\n[PASO 0.5] Validando coherencia de la pregunta...")

    # Validación básica: detectar preguntas totalmente fuera de contexto
    if len(user_question.strip()) < 5:
        return "❌ Tu pregunta es demasiado corta. Por favor, proporciona más detalles sobre lo que deseas saber."

    # PASO 1: Generar plan dinámico usando IA
    print("\n[PASO 1] Generando plan de ejecución con IA...")

    def generate_plan():
        plan_text = provider.chat(orchestrator_context, user_question, temperature=0.2)

        # Limpiar formato markdown si existe
        if plan_text.startswith("```json"):
            plan_text = plan_text.replace("```json", "").replace("```", "").strip()

        return plan_text

    plan_json = retry_operation(generate_plan, validation_type="json")

    if not plan_json:
        return "Lo siento, no pude analizar tu consulta correctamente. ¿Puedes reformularla?"

    try:
        plan = json.loads(plan_json)
        print(f"\n[PLAN GENERADO]")
        print(f"  Razonamiento: {plan.get('razonamiento', 'N/A')[:150]}...")
        print(f"  Necesita DB: {plan.get('query_for_query_bot') is not None}")
        print(f"  Necesita JSONs: {plan.get('needs_json_fetch', False)}")
        print(f"  Límite de hashes: {plan.get('limit_hashes', 0)}")
    except json.JSONDecodeError:
        return "Error al procesar el plan de ejecución. Por favor, intenta de nuevo."

    # PASO 2: Inicializar estructuras de datos
    # =========================================================================
    # IMPORTANTE: Separamos los datos en dos estructuras:
    # 1. reference_data: Para mostrar al usuario (tickbarrs, hashes) - NO se envía al LLM
    # 2. all_data: Solo información relevante para generar la respuesta - SÍ se envía al LLM
    # =========================================================================

    # Datos de referencia (para mostrar al usuario, NO para el LLM)
    reference_data = {
        "tickbarrs_procesados": [],  # Lista de tickbarrs analizados
        "total_en_db": 0,            # Total de registros encontrados en DB
        "total_procesados": 0        # Total de JSONs procesados
    }

    # Datos para el LLM final (SOLO información relevante, sin hashes ni datos crudos de DB)
    all_data = {
        "user_question": user_question,
        "razonamiento": plan.get("razonamiento", ""),
        "db_summary": None,          # Resumen de DB (conteos, agregaciones), NO datos crudos
        "jsons": {},                 # Datos filtrados de JSONs (campos relevantes)
        "metadata": {
            "total_records": 0,
            "jsons_analyzed": 0
        }
    }

    # PASO 3: Ejecutar consulta a DB si es necesaria
    if plan.get("query_for_query_bot"):
        print(f"\n[PASO 2] Generando SQL desde instrucción: '{plan['query_for_query_bot']}'")

        sql_query = retry_operation(query_bot, plan["query_for_query_bot"], validation_type="sql")

        if not sql_query:
            return "No pude generar una consulta SQL válida. Por favor, reformula tu pregunta."

        print(f"\n[PASO 3] Ejecutando query SQL en la base de datos...")

        db_results_df = retry_operation(execute_query, sql_query, validation_type="dataframe")

        if db_results_df is None:
            # Si no hay resultados, intentar con consulta alternativa
            print("[INFO] No se encontraron resultados. Intentando consulta más amplia...")
            alternative_prompt = f"No hubo resultados para: '{plan['query_for_query_bot']}'. Sugiere una consulta SQL más amplia que pueda retornar datos relacionados."

            alt_sql = retry_operation(query_bot, alternative_prompt, validation_type="sql")
            if alt_sql:
                db_results_df = execute_query(alt_sql)

            if db_results_df is None or db_results_df.empty:
                return f"No se encontraron registros que coincidan con tu consulta: '{user_question}'. Intenta con términos más generales."

        # =========================================================================
        # IMPORTANTE: NO enviar todos los datos crudos de DB al LLM
        # Solo enviamos un RESUMEN útil para la respuesta
        # =========================================================================

        # Guardar total en reference_data
        reference_data["total_en_db"] = len(db_results_df)
        all_data["metadata"]["total_records"] = len(db_results_df)

        # Crear resumen de DB (sin incluir hashes ni datos repetitivos)
        # Solo incluimos columnas que NO sean hashes y que sean útiles para la respuesta
        columns_to_exclude = ['ttickhash', 'ttickbarr', 'tnumevers']
        useful_columns = [col for col in db_results_df.columns if col.lower() not in columns_to_exclude]

        if useful_columns:
            # Si hay columnas útiles (no son solo hashes), crear resumen
            db_summary = {}

            # Para consultas de conteo, el resultado ya es un resumen
            if len(db_results_df.columns) <= 3 and any('count' in str(col).lower() for col in db_results_df.columns):
                # Es un resultado de COUNT - enviarlo directamente
                db_summary = db_results_df.to_dict('records')
            else:
                # Para otros casos, solo enviar estadísticas básicas
                db_summary = {
                    "total_registros": len(db_results_df),
                    "columnas_disponibles": useful_columns[:10]  # Máximo 10 columnas
                }

                # Si hay agrupaciones (GROUP BY), incluir esos resultados
                if len(db_results_df) <= 20:  # Solo si son pocos registros (resultado de agregación)
                    summary_df = db_results_df[useful_columns] if useful_columns else db_results_df
                    db_summary["datos"] = summary_df.head(20).to_dict('records')

            all_data["db_summary"] = db_summary
        else:
            # Si solo hay hashes, no enviamos nada de DB al LLM (los datos vendrán de JSONs)
            all_data["db_summary"] = {"nota": "Datos de DB son solo identificadores, información detallada en JSONs"}

        print(f"✓ Recuperados {len(db_results_df)} registros de la base de datos")

        # PASO 3.5: VALIDACIÓN DE FACTIBILIDAD (NUEVO)
        if plan.get("needs_json_fetch", False) and 'ttickhash' in db_results_df.columns:
            # Contar hashes antes de procesar
            total_hashes = db_results_df['ttickhash'].dropna().nunique()

            print(f"\n[PASO 3.5] Validando factibilidad de la consulta...")
            print(f"  → Total de hashes a procesar: {total_hashes}")

            # Validar si la consulta es factible y coherente
            validation = validate_query_feasibility(user_question, total_hashes)

            print(f"  → Consulta válida: {validation['is_valid']}")
            print(f"  → Requiere confirmación: {validation['requires_confirmation']}")

            # Si la consulta NO es válida, retornar mensaje al usuario
            if not validation['is_valid']:
                print(f"\n[VALIDACIÓN FALLIDA] Consulta no válida")
                response_msg = f"❌ {validation['message']}"
                if validation.get('suggestion'):
                    response_msg += f"\n\n💡 Sugerencia: {validation['suggestion']}"
                return response_msg

            # Si requiere confirmación y no está en modo auto, informar al usuario
            if validation['requires_confirmation'] and not auto_confirm:
                print(f"\n[CONFIRMACIÓN REQUERIDA] Consulta necesita confirmación del usuario")

                confirmation_msg = f"⚠️ {validation['message']}"

                if validation.get('suggestion'):
                    confirmation_msg += f"\n\n💡 Sugerencia: {validation['suggestion']}"

                confirmation_msg += f"\n\n📊 Estadísticas:"
                confirmation_msg += f"\n  • Total de registros: {total_hashes}"
                confirmation_msg += f"\n  • Se procesarán: {validation['recommended_limit']} (primeros)"
                confirmation_msg += f"\n  • Tiempo estimado: ~{validation['recommended_limit'] * 0.3:.0f} segundos"

                confirmation_msg += f"\n\n¿Deseas continuar? Responde 'sí' para proceder o reformula tu pregunta para ser más específico."

                return confirmation_msg

            # Si todo está bien, continuar con el límite recomendado
            recommended_limit = validation.get('recommended_limit', max_hashes)
            print(f"✓ Consulta validada - se procesarán {recommended_limit} hashes")

        # PASO 4: Extraer hashes si es necesario
        if plan.get("needs_json_fetch", False) and 'ttickhash' in db_results_df.columns:
            hashes = db_results_df['ttickhash'].dropna().unique().tolist()

            # Usar el límite recomendado por la validación (si existe)
            if 'recommended_limit' in locals():
                limit = recommended_limit
            else:
                limit = plan.get("limit_hashes", max_hashes)

            if len(hashes) > limit and limit > 0:
                print(f"[INFO] Limitando {len(hashes)} hashes a primeros {limit}")
                hashes = hashes[:limit]

            # =========================================================================
            # IMPORTANTE: Los hashes van a reference_data, NO a all_data
            # El LLM no necesita ver la lista de hashes para generar la respuesta
            # =========================================================================
            reference_data["tickbarrs_procesados"] = hashes  # Para referencia del usuario
            reference_data["total_procesados"] = len(hashes)

            print(f"✓ Se identificaron {len(hashes)} hashes para análisis detallado")

            # PASO 5: Recuperar y filtrar JSONs de Swarm
            try:
                filtered_jsons = fetch_and_filter_jsons(hashes, user_question)

                # NUEVO: Verificar si se detectó que NO hay datos relevantes en los JSONs
                if filtered_jsons and filtered_jsons.get("__NO_RELEVANT_DATA__"):
                    print(f"\n[ABORTO TEMPRANO] Los JSONs no contienen la información solicitada")

                    # Generar respuesta informativa al usuario SIN enviar datos al LLM final
                    explanation = filtered_jsons.get("explanation", "La información solicitada no está disponible en los datos de trazabilidad.")
                    sample_sections = filtered_jsons.get("sample_sections", [])
                    skipped_count = filtered_jsons.get("total_hashes_skipped", len(hashes))

                    # Construir respuesta amigable
                    response_msg = f"❌ **No se encontró la información solicitada**\n\n"
                    response_msg += f"{explanation}\n\n"

                    if sample_sections:
                        response_msg += f"📋 **Información disponible en los datos de trazabilidad:**\n"
                        for section in sample_sections[:8]:
                            response_msg += f"  • {section}\n"

                    response_msg += f"\n💡 **Sugerencia:** Intenta preguntar sobre alguno de los campos disponibles, "
                    response_msg += f"como información del cliente, procesos de costura, corte, teñido, hilos, etc."

                    response_msg += f"\n\n📊 **Nota técnica:** Se analizó 1 JSON de muestra para evitar procesar {skipped_count} registros innecesariamente."

                    return response_msg

                # Caso normal: hay datos relevantes
                if filtered_jsons and len(filtered_jsons) > 0:
                    # =========================================================================
                    # Solo enviamos los datos FILTRADOS de JSONs al LLM
                    # Estos ya fueron procesados por extract_fields y contienen solo campos relevantes
                    # =========================================================================
                    all_data["jsons"] = filtered_jsons
                    all_data["metadata"]["jsons_analyzed"] = len(filtered_jsons)
                    reference_data["total_procesados"] = len(filtered_jsons)
                    print(f"✓ Análisis de JSONs completado: {len(filtered_jsons)} tickbarrs procesados")
                else:
                    all_data["note"] = "No se pudieron recuperar JSONs de Swarm en este momento."
                    print(f"[WARN] No se recuperaron JSONs - continuando con datos de DB")

            except Exception as e:
                print(f"[ERROR] Error al procesar JSONs: {str(e)}")
                all_data["note"] = f"Error al recuperar trazabilidad detallada: {str(e)[:100]}"

    else:
        print("\n[INFO] Consulta no requiere acceso a base de datos - respondiendo directamente")

    # PASO FINAL: Generar respuesta al usuario
    print(f"\n[PASO FINAL] Generando respuesta final para el usuario...")

    # =========================================================================
    # Verificar tamaño de all_data antes de enviarlo al LLM
    # =========================================================================
    all_data_str = json.dumps(all_data, ensure_ascii=False)
    data_size = len(all_data_str)

    print(f"[DEBUG] Tamaño de datos para LLM: {data_size:,} caracteres")
    print(f"[DEBUG] Registros en DB: {reference_data['total_en_db']}")
    print(f"[DEBUG] JSONs procesados: {reference_data['total_procesados']}")

    # Si los datos son muy grandes, mostrar advertencia
    if data_size > 100000:
        print(f"[WARN] Datos muy grandes ({data_size:,} chars). Puede haber truncamiento.")

    print(all_data_str)
    
    final_response = retry_operation(
        final_response_bot,
        all_data_str,
        user_question,
        validation_type="text"
    )

    if final_response:
        print(f"\n{'='*80}")
        print("RESPUESTA ENVIADA AL USUARIO")
        print(f"{'='*80}\n")

        # Agregar nota de referencia si se procesaron JSONs
        if reference_data["total_procesados"] > 0:
            final_response += f"\n\n---\n📊 *Se analizaron {reference_data['total_procesados']} registros de {reference_data['total_en_db']} encontrados en la base de datos.*"

        return final_response
    else:
        return "Lo siento, no pude generar una respuesta coherente. Por favor, intenta reformular tu pregunta."

# Ejemplo de uso del chatbot
if __name__ == "__main__":

    # Opción 2: Usar Gemini
    set_ai_model(AIModel.DEEPSEEK)

    # Mostrar el modelo actual
    print(f"\n🤖 Modelo de IA activo: {get_current_model().value.upper()}\n")

    respuesta = orquestador_bot("¿Hay prendas Lascoste que se trabajaron en la rama 3? de haber cuantas prendas se trabajaron?, procesa los primeros 200 hashes que encuentres no me preguntes si quiero o no procesar los primeros 200, solo hazlo!")
    print(respuesta)

    