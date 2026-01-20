import pandas as pd
import os
import pymysql
import warnings

from dotenv import load_dotenv


# Cargar las variables de entorno
load_dotenv()

DB_USER = os.getenv("DB_PRENDAS_USER")
warnings.filterwarnings('ignore')

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
    
def get_complete_history_bot():
    """Obtiene todo el historial del bot."""
    conn = connect_to_my_db()
    if conn:
        try:
            query = "SELECT * FROM apdoblochistbott"
            df = pd.read_sql(query, conn)
            conn.close()
            if df.empty:
                return pd.DataFrame()
            else:
                return df
        except Exception as e:
            print(e)
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()


def get_next_conversation_group(user_code: str) -> int:
    """
    Obtiene el siguiente numero de grupo de conversacion para un usuario.
    Si el usuario no tiene conversaciones previas, retorna 1.
    """
    conn = connect_to_my_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT COALESCE(MAX(tgrupconv), 0) + 1
                FROM apdoblochistbott
                WHERE tcodiusua = %s
            """
            cursor.execute(query, (user_code,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] if result else 1
        except Exception as e:
            print(f"Error en get_next_conversation_group: {e}")
            conn.close()
            return 1
    return 1


def get_current_conversation_group(user_code: str) -> int:
    """
    Obtiene el grupo de conversacion actual (el mas reciente) para un usuario.
    Si no existe ninguna conversacion, retorna None.
    """
    conn = connect_to_my_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT MAX(tgrupconv)
                FROM apdoblochistbott
                WHERE tcodiusua = %s
            """
            cursor.execute(query, (user_code,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] if result and result[0] else None
        except Exception as e:
            print(f"Error en get_current_conversation_group: {e}")
            conn.close()
            return None
    return None


def get_conversation_history(user_code: str, conversation_group: int) -> list:
    """
    Obtiene el historial de una conversacion especifica para un usuario.
    Retorna lista de diccionarios con pregunta, respuesta y fecha.
    """
    conn = connect_to_my_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT tpregusua, trespbott, tfechconv
                FROM apdoblochistbott
                WHERE tcodiusua = %s AND tgrupconv = %s
                ORDER BY tfechconv ASC
            """
            cursor.execute(query, (user_code, conversation_group))
            results = cursor.fetchall()
            cursor.close()
            conn.close()

            history = []
            for row in results:
                history.append({
                    "question": row[0],
                    "answer": row[1],
                    "timestamp": row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else None
                })
            return history
        except Exception as e:
            print(f"Error en get_conversation_history: {e}")
            conn.close()
            return []
    return []


def get_all_conversations_for_user(user_code: str) -> list:
    """
    Obtiene todos los grupos de conversacion de un usuario con su primera pregunta
    para mostrar en la lista de chats anteriores.
    """
    conn = connect_to_my_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                SELECT tgrupconv, MIN(tpregusua) as first_question, MIN(tfechconv) as start_date
                FROM apdoblochistbott
                WHERE tcodiusua = %s
                GROUP BY tgrupconv
                ORDER BY start_date DESC
            """
            cursor.execute(query, (user_code,))
            results = cursor.fetchall()
            cursor.close()
            conn.close()

            conversations = []
            for row in results:
                conversations.append({
                    "group_id": row[0],
                    "first_question": row[1][:50] + "..." if row[1] and len(row[1]) > 50 else row[1],
                    "start_date": row[2].strftime('%Y-%m-%d %H:%M') if row[2] else None
                })
            return conversations
        except Exception as e:
            print(f"Error en get_all_conversations_for_user: {e}")
            conn.close()
            return []
    return []


def save_chat_message(user_code: str, user_name: str, conversation_group: int,
                      question: str, answer: str) -> bool:
    """
    Guarda un mensaje del chat (pregunta y respuesta) en el historial.
    """
    conn = connect_to_my_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO apdoblochistbott
                (tcodiusua, tnombusua, tgrupconv, tpregusua, trespbott, tfechconv)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (user_code, user_name, conversation_group, question, answer))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error en save_chat_message: {e}")
            conn.rollback()
            conn.close()
            return False
    return False


def get_conversation_context_for_ai(user_code: str, conversation_group: int, limit: int = 10) -> str:
    """
    Obtiene el historial de conversacion formateado para enviar como contexto a la IA.
    Limita a las ultimas N interacciones para no sobrecargar el contexto.
    """
    history = get_conversation_history(user_code, conversation_group)

    if not history:
        return ""

    # Tomar solo las ultimas 'limit' interacciones
    recent_history = history[-limit:] if len(history) > limit else history

    context_parts = ["Historial de conversacion anterior:"]
    for entry in recent_history:
        context_parts.append(f"Usuario: {entry['question']}")
        context_parts.append(f"Asistente: {entry['answer']}")

    return "\n".join(context_parts)


def delete_conversation(user_code: str, conversation_group: int) -> bool:
    """
    Elimina una conversacion completa del historial.
    """
    conn = connect_to_my_db()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                DELETE FROM apdoblochistbott
                WHERE tcodiusua = %s AND tgrupconv = %s
            """
            cursor.execute(query, (user_code, conversation_group))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error en delete_conversation: {e}")
            conn.rollback()
            conn.close()
            return False
    return False


#print(get_complete_history_bot())