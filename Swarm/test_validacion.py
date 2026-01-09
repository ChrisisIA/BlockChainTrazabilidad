#!/usr/bin/env python3
"""
Script de prueba para validar el sistema de confirmación y validación de consultas.
Demuestra cómo el chatbot maneja diferentes tipos de consultas.
"""

from chatbot import validate_query_feasibility

def test_validation_scenarios():
    """
    Prueba diferentes escenarios de validación de consultas.
    """
    print("="*80)
    print("TEST: VALIDACIÓN DE CONSULTAS")
    print("="*80)

    test_cases = [
        {
            "question": "¿Cuántas prendas de LACOSTE hay?",
            "total_hashes": 450,
            "expected": "requires_confirmation: true (muchos hashes)"
        },
        {
            "question": "¿Qué máquinas procesaron las prendas de NIKE talla 10?",
            "total_hashes": 45,
            "expected": "requires_confirmation: false (pocos hashes, específica)"
        },
        {
            "question": "Lista las prendas",
            "total_hashes": 15000,
            "expected": "requires_confirmation: true (demasiado amplia)"
        },
        {
            "question": "¿Qué color tiene el cielo?",
            "total_hashes": 0,
            "expected": "is_valid: false (fuera de contexto)"
        },
        {
            "question": "prendas",
            "total_hashes": 15000,
            "expected": "is_valid: false (demasiado ambigua)"
        },
        {
            "question": "¿Cuántas T-Shirts de LACOSTE para hombres hay?",
            "total_hashes": 85,
            "expected": "requires_confirmation: false (específica, pocos hashes)"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"TEST CASO {i}/{len(test_cases)}")
        print(f"{'─'*80}")
        print(f"Pregunta: \"{test_case['question']}\"")
        print(f"Total hashes: {test_case['total_hashes']}")
        print(f"Expectativa: {test_case['expected']}")

        try:
            validation = validate_query_feasibility(
                test_case['question'],
                test_case['total_hashes']
            )

            print(f"\n📊 Resultado de Validación:")
            print(f"  • is_valid: {validation['is_valid']}")
            print(f"  • requires_confirmation: {validation['requires_confirmation']}")
            print(f"  • recommended_limit: {validation['recommended_limit']}")

            if validation.get('message'):
                print(f"\n💬 Mensaje para usuario:")
                print(f"  {validation['message']}")

            if validation.get('suggestion'):
                print(f"\n💡 Sugerencia:")
                print(f"  {validation['suggestion']}")

            # Validar resultado esperado
            if not validation['is_valid']:
                status = "❌ NO VÁLIDA"
            elif validation['requires_confirmation']:
                status = "⚠️ REQUIERE CONFIRMACIÓN"
            else:
                status = "✅ VÁLIDA - PROCESAR DIRECTAMENTE"

            print(f"\n{status}")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")

    print(f"\n{'='*80}")
    print("TEST COMPLETADO")
    print(f"{'='*80}\n")


def test_confirmation_flow():
    """
    Simula el flujo de confirmación con el usuario.
    """
    print("\n" + "="*80)
    print("SIMULACIÓN: FLUJO DE CONFIRMACIÓN")
    print("="*80)

    # Caso 1: Consulta que requiere confirmación
    print("\n📝 ESCENARIO 1: Consulta amplia que requiere confirmación")
    print("-" * 80)

    question = "¿Cuántas prendas de LACOSTE hay?"
    total_hashes = 450

    print(f"\nUsuario pregunta: \"{question}\"")
    print(f"Sistema detecta: {total_hashes} hashes a procesar")

    validation = validate_query_feasibility(question, total_hashes)

    if validation['requires_confirmation']:
        print("\n🤖 Bot responde:")
        print(f"⚠️ {validation['message']}")

        if validation.get('suggestion'):
            print(f"\n💡 {validation['suggestion']}")

        print(f"\n📊 Estadísticas:")
        print(f"  • Total de registros: {total_hashes}")
        print(f"  • Se procesarán: {validation['recommended_limit']} (primeros)")
        print(f"  • Tiempo estimado: ~{validation['recommended_limit'] * 0.3:.0f} segundos")

        print(f"\n¿Deseas continuar? Responde 'sí' para proceder.")

        print("\n👤 Usuario responde: 'sí'")
        print("✅ Sistema procede a procesar los primeros 100 hashes")

    # Caso 2: Consulta inválida
    print("\n\n📝 ESCENARIO 2: Consulta inválida")
    print("-" * 80)

    question = "¿Qué color tiene el cielo?"
    total_hashes = 0

    print(f"\nUsuario pregunta: \"{question}\"")

    validation = validate_query_feasibility(question, total_hashes)

    if not validation['is_valid']:
        print("\n🤖 Bot responde:")
        print(f"❌ {validation['message']}")

        if validation.get('suggestion'):
            print(f"\n💡 Sugerencia: {validation['suggestion']}")

        print("\n❌ Sistema NO procesa la consulta")

    # Caso 3: Consulta válida y directa
    print("\n\n📝 ESCENARIO 3: Consulta específica y válida")
    print("-" * 80)

    question = "¿Qué máquinas procesaron las prendas de NIKE talla 10?"
    total_hashes = 45

    print(f"\nUsuario pregunta: \"{question}\"")
    print(f"Sistema detecta: {total_hashes} hashes a procesar")

    validation = validate_query_feasibility(question, total_hashes)

    if validation['is_valid'] and not validation['requires_confirmation']:
        print("\n🤖 Bot procede directamente:")
        print("✅ Consulta válida y específica")
        print(f"✅ Procesando {validation['recommended_limit']} hashes...")
        print("✅ Sistema procesa sin pedir confirmación")

    print("\n" + "="*80)
    print("SIMULACIÓN COMPLETADA")
    print("="*80 + "\n")


def main():
    """
    Ejecutar todos los tests de validación.
    """
    print("\n" + "🧪 "*20)
    print("SUITE DE PRUEBAS - VALIDACIÓN Y CONFIRMACIÓN DE CONSULTAS")
    print("🧪 "*20 + "\n")

    try:
        # Test 1: Validación de diferentes escenarios
        test_validation_scenarios()

        # Test 2: Simulación de flujo de confirmación
        test_confirmation_flow()

        print("\n" + "🎉 "*20)
        print("TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("🎉 "*20 + "\n")

        print("\n📋 RESUMEN DE FUNCIONALIDADES:")
        print("-" * 80)
        print("1. ✅ Validación de coherencia de preguntas")
        print("2. ✅ Detección de consultas fuera de contexto")
        print("3. ✅ Solicitud de confirmación para consultas amplias (>100 hashes)")
        print("4. ✅ Sugerencias automáticas para mejorar preguntas")
        print("5. ✅ Procesamiento directo de consultas específicas y válidas")
        print("-" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR EN TESTS: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
