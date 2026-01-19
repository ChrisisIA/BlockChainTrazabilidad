import pandas as pd
import os
import pymysql
import warnings
import requests
from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_cors import CORS
from datetime import timedelta
import cx_Oracle
from dotenv import load_dotenv
from flask_jwt_extended import get_jwt
from chatbot import orquestador_bot, set_ai_model, AIModel, correct_user_input_with_ai, extract_filters_from_question

# ------------------- Configuraciones y env ----------------------------

# Cargar las variables de entorno
load_dotenv()
warnings.filterwarnings('ignore')

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")

DB_PRENDAS_USER = os.getenv("DB_PRENDAS_USER")
DB_PRENDAS_PASSWORD = os.getenv("DB_PRENDAS_PASSWORD")
DB_PRENDAS_HOST = os.getenv("DB_PRENDAS_HOST")
DB_PRENDAS_PORT = int(os.getenv("DB_PRENDAS_PORT"))
DB_PRENDAS_NAME = os.getenv("DB_PRENDAS_NAME")

db_config = {
    'host': DB_PRENDAS_HOST,
    'port': DB_PRENDAS_PORT,
    'user': DB_PRENDAS_USER,
    'password': DB_PRENDAS_PASSWORD,
    'database': DB_PRENDAS_NAME,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

# Configuración del DSN de Oracle (solo configuración, no conexión)
ORACLE_DSN = cx_Oracle.makedsn(DB_HOST, DB_PORT, sid=DB_NAME)

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")

# Configuración de CORS - Permite peticiones desde cualquier origen
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False,
        "max_age": 3600
    }
})

# Configuración del JWT
app.config["JWT_SECRET_KEY"] = "supersecretkey"  # Cambia esto por una clave segura
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=48)  # El token expira en 2 días

jwt = JWTManager(app)


# ------------------------------ Funciones -----------------------------

def connect_to_my_db():
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except Exception as e:
        print("falló al conectarse a la base de datos de MariaDB")
        return None

def get_oracle_connection():
    try:
        conn = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=ORACLE_DSN)
        return conn
    except Exception as e:
        print(f"Error al conectarse a Oracle: {e}")
        return None

def verify_user(user: str, pwd: str):
    connection = None
    cursor = None
    try:
        connection = get_oracle_connection()
        if not connection:
            return "Error de conexión a la base de datos"

        cursor = connection.cursor()
        username = cursor.var(cx_Oracle.STRING)
        p_menserro = cursor.var(cx_Oracle.STRING)
        cursor.callproc("prc_login", [user, pwd, username, p_menserro])

        if p_menserro.getvalue():
            return p_menserro.getvalue()
        else:
            return username.getvalue(), "Verificacion Correcta"

    except Exception as e:
        print(f"Error en verify_user: {e}")
        return f"Error: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# ----------------------------------------------------------------------

# -------------------------------- Flask -------------------------------


# Ruta para autenticación
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    print("data login:", data)
    usercode = data.get("username")
    password = data.get("password")

    username, verify = verify_user(usercode, password)

    if verify == "Verificacion Correcta":
        additional_claims = {"username": username}
        access_token = create_access_token(identity=usercode, additional_claims=additional_claims)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Usuario o contraseña incorrecta"}), 401

# Ruta protegida con autenticación
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    username = get_jwt()["username"]
    return jsonify({"usercode": current_user, "username": username}), 200

@app.route('/get_hash', methods=['POST'])
def get_hash():
    """
    Obtiene el hash más reciente (versión más alta) de un tickbarr desde la base de datos.
    """
    conn = None
    cursor = None
    try:
        data = request.json
        tickbarr = data.get("tickbarr")

        if not tickbarr:
            return jsonify({"error": "Falta el parámetro tickbarr"}), 400

        # Conectar a la base de datos usando la función existente
        conn = connect_to_my_db()
        if not conn:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500

        cursor = conn.cursor()

        # Consultar el hash más reciente del tickbarr
        query = """
        SELECT TTICKHASH FROM apdobloctrazhash
        WHERE TTICKBARR = %s
        ORDER BY TNUMEVERS DESC
        LIMIT 1
        """
        cursor.execute(query, (tickbarr,))
        result = cursor.fetchone()

        if result:
            hash_value = result[0]
            print(f"Hash encontrado para tickbarr {tickbarr}: {hash_value}")
            return jsonify({
                "tickbarr": tickbarr,
                "hash": hash_value,
                "mensaje": "Hash encontrado exitosamente"
            }), 200
        else:
            return jsonify({
                "error": "No se encontró hash para el tickbarr proporcionado"
            }), 404

    except Exception as e:
        print(f"Error en get_hash: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/filter_data', methods=['POST'])
def filter_data():
    """
    Filtra datos de apdobloctrazhash según parámetros opcionales.
    Acepta 1 o más filtros: numecaja, esticlie, etiqclie, coditall
    """
    conn = None
    cursor = None
    try:
        data = request.json
        numecaja = data.get("numecaja")
        esticlie = data.get("esticlie")
        etiqclie = data.get("etiqclie")
        coditall = data.get("coditall")

        # Construir query dinámicamente según los filtros proporcionados
        where_clauses = []
        params = []

        if numecaja:
            where_clauses.append("TNUMECAJA = %s")
            params.append(numecaja)

        if esticlie:
            where_clauses.append("TESTICLIE = %s")
            params.append(esticlie)

        if etiqclie:
            where_clauses.append("TETIQCLIE = %s")
            params.append(etiqclie)

        if coditall:
            where_clauses.append("TCODITALL = %s")
            params.append(coditall)

        # Validar que al menos un filtro fue proporcionado
        if not where_clauses:
            return jsonify({
                "error": "Debe proporcionar al menos un filtro (numecaja, esticlie, etiqclie o coditall)"
            }), 400

        # Conectar a la base de datos
        conn = connect_to_my_db()
        if not conn:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500

        cursor = conn.cursor(pymysql.cursors.DictCursor)  # Usar DictCursor para obtener resultados como diccionarios

        # Construir query completo
        where_sql = " AND ".join(where_clauses)
        query = f"""
        SELECT
            TTICKBARR,
            TNUMEVERS,
            TNUMECAJA,
            TESTICLIE,
            TETIQCLIE,
            TCODITALL,
            TTICKHASH,
            TFECHGUAR
        FROM apdobloctrazhash
        WHERE {where_sql}
        ORDER BY TFECHGUAR DESC
        """

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        if results:
            # Convertir datetime a string para JSON serialization
            for row in results:
                if 'TFECHGUAR' in row and row['TFECHGUAR']:
                    row['TFECHGUAR'] = row['TFECHGUAR'].strftime('%Y-%m-%d %H:%M:%S')

            return jsonify({
                "success": True,
                "count": len(results),
                "filters_applied": {
                    "numecaja": numecaja,
                    "esticlie": esticlie,
                    "etiqclie": etiqclie,
                    "coditall": coditall
                },
                "data": results
            }), 200
        else:
            return jsonify({
                "success": True,
                "count": 0,
                "message": "No se encontraron resultados con los filtros proporcionados",
                "filters_applied": {
                    "numecaja": numecaja,
                    "esticlie": esticlie,
                    "etiqclie": etiqclie,
                    "coditall": coditall
                },
                "data": []
            }), 200

    except Exception as e:
        print(f"Error en filter_data: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint del chatbot de trazabilidad.
    Recibe una pregunta del usuario y retorna la respuesta del bot orquestador.

    Body JSON:
        - question: Pregunta del usuario (requerido)
        - model: Modelo de IA a usar (opcional, default: "deepseek")
        - filters: Filtros opcionales para incluir en la consulta (opcional)

    Returns:
        - response: Respuesta del chatbot
        - model_used: Modelo de IA utilizado
        - corrections: Correcciones realizadas en la pregunta
        - extracted_filters: Filtros extraídos de la pregunta para sincronizar con UI
        - corrected_question: Pregunta corregida (si hubo correcciones)
    """
    try:
        data = request.json
        question = data.get("question")
        model = data.get("model", "deepseek").lower()
        filters = data.get("filters", {})

        if not question:
            return jsonify({"error": "Falta el parámetro 'question'"}), 400

        # Configurar el modelo de IA según el parámetro
        if model == "gemini":
            set_ai_model(AIModel.GEMINI)
        else:
            set_ai_model(AIModel.DEEPSEEK)

        print(f"[CHAT API] Pregunta original: {question}")
        print(f"[CHAT API] Modelo: {model}")
        print(f"[CHAT API] Filtros recibidos: {filters}")

        # PASO 1: Corregir errores tipográficos en la pregunta
        corrected_question, corrections = correct_user_input_with_ai(question)

        if corrections:
            print(f"[CHAT API] Correcciones aplicadas: {corrections}")
            print(f"[CHAT API] Pregunta corregida: {corrected_question}")

        # PASO 2: Extraer filtros de la pregunta corregida
        extracted_filters = extract_filters_from_question(corrected_question, corrections)
        print(f"[CHAT API] Filtros extraídos: {extracted_filters}")

        # PASO 3: Combinar filtros del UI con los extraídos de la pregunta
        # Los filtros del UI tienen prioridad (no se sobrescriben)
        final_filters = extracted_filters.copy()
        for key, value in filters.items():
            if value and str(value).strip():
                final_filters[key] = value  # UI filters override extracted

        # PASO 4: Agregar filtros al contexto de la pregunta para el orquestador
        question_with_context = corrected_question
        if final_filters and any(final_filters.values()):
            filter_context = []
            filter_mappings = {
                "client": ("cliente", "TDESCCLIE"),
                "clientStyle": ("estilo cliente", "TESTICLIE"),
                "boxNumber": ("número de caja", "TNUMECAJA"),
                "label": ("etiqueta", "TETIQCLIE"),
                "size": ("talla", "TCODITALL"),
                "gender": ("género", "TTIPOGENE"),
                "age": ("edad", "TTIPOEDAD"),
                "garmentType": ("tipo de prenda", "TTIPOPREN"),
            }

            for key, value in final_filters.items():
                if value and key in filter_mappings:
                    filter_name, _ = filter_mappings[key]
                    filter_context.append(f"{filter_name}: {value}")

            if filter_context:
                question_with_context = f"{corrected_question} (Filtrar por: {', '.join(filter_context)})"

        print(f"[CHAT API] Pregunta final con contexto: {question_with_context}")

        # PASO 5: Llamar al orquestador del chatbot
        response = orquestador_bot(question_with_context, auto_confirm=True)

        return jsonify({
            "success": True,
            "response": response,
            "model_used": model,
            "filters_applied": final_filters if any(final_filters.values()) else None,
            # Nuevos campos para sincronización bidireccional
            "corrections": corrections if corrections else None,
            "extracted_filters": extracted_filters,
            "corrected_question": corrected_question if corrections else None
        }), 200

    except Exception as e:
        print(f"Error en /chat: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Error al procesar la consulta: {str(e)}"
        }), 500

@app.route('/get_swarm_data', methods=['POST'])
def get_swarm_data():
    """
    Proxy endpoint para obtener datos JSON desde Ethereum Swarm.
    Recibe un hash y retorna el JSON almacenado en Swarm.
    """
    try:
        data = request.json
        hash_value = data.get("hash")

        if not hash_value:
            return jsonify({"error": "Falta el parámetro hash"}), 400

        # Llamar al gateway de Swarm
        swarm_url = f"https://api.gateway.ethswarm.org/bzz/{hash_value}"
        response = requests.get(swarm_url, timeout=30)

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "error": f"Error al obtener datos de Swarm: {response.status_code}"
            }), response.status_code

    except requests.exceptions.Timeout:
        return jsonify({"error": "Timeout al conectar con Swarm gateway"}), 504
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con Swarm: {e}")
        return jsonify({"error": "Error de conexión con Swarm gateway"}), 502
    except Exception as e:
        print(f"Error en get_swarm_data: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)