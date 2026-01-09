#!/usr/bin/env python3
"""
Interfaz interactiva para el chatbot con manejo de confirmaciones.
Permite al usuario confirmar consultas que requieren procesar muchos hashes.
"""

from chatbot import orquestador_bot

def chat_interactive():
    """
    Ejecuta el chatbot en modo interactivo con manejo de confirmaciones.
    """
    print("="*80)
    print("🤖 CHATBOT DE TRAZABILIDAD TEXTIL v2.0.1")
    print("="*80)
    print("\nBienvenido! Puedes hacer preguntas sobre trazabilidad de prendas.")
    print("Escribe 'salir' para terminar la sesión.\n")

    # Estado de la última consulta pendiente de confirmación
    pending_query = None
    pending_validation = None

    while True:
        try:
            # Obtener pregunta del usuario
            user_input = input("\n👤 Tu pregunta: ").strip()

            if not user_input:
                continue

            # Comando de salida
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("\n👋 ¡Hasta luego!")
                break

            # Verificar si es una confirmación de consulta pendiente
            if pending_query and user_input.lower() in ['si', 'sí', 's', 'yes', 'y', 'ok', 'continuar']:
                print("\n✅ Confirmación recibida. Procesando consulta...\n")
                # Ejecutar con auto_confirm=True para evitar doble confirmación
                respuesta = orquestador_bot(pending_query, auto_confirm=True)
                print(f"\n🤖 Respuesta:\n{respuesta}\n")

                # Limpiar estado pendiente
                pending_query = None
                pending_validation = None
                continue

            # Si hay consulta pendiente pero usuario no confirmó, cancelar
            if pending_query:
                print("\n❌ Consulta anterior cancelada. Procesando nueva pregunta...\n")
                pending_query = None
                pending_validation = None

            # Procesar nueva consulta
            print("\n🔍 Analizando tu consulta...\n")
            respuesta = orquestador_bot(user_input)

            # Verificar si la respuesta es una solicitud de confirmación
            if "¿Deseas continuar?" in respuesta or "Responde 'sí' para proceder" in respuesta:
                # Guardar estado pendiente
                pending_query = user_input
                print(f"\n🤖 {respuesta}\n")
            else:
                # Respuesta normal
                print(f"\n🤖 Respuesta:\n{respuesta}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Sesión interrumpida. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            print("Por favor, intenta reformular tu pregunta.\n")
            pending_query = None
            pending_validation = None

def chat_single_query(question, auto_confirm=False):
    """
    Ejecuta una sola consulta sin modo interactivo.

    Args:
        question: Pregunta del usuario
        auto_confirm: Si es True, procesa automáticamente sin pedir confirmación

    Returns:
        str: Respuesta del chatbot
    """
    return orquestador_bot(question, auto_confirm=auto_confirm)


if __name__ == "__main__":
    import sys

    # Si se pasa una pregunta como argumento, ejecutar en modo single-query
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"\n🤖 Procesando: {question}\n")
        respuesta = chat_single_query(question)
        print(f"\n🤖 Respuesta:\n{respuesta}\n")
    else:
        # Modo interactivo
        chat_interactive()
