#!/usr/bin/env python3
"""
Script de prueba para el sistema de corrección automática de errores de escritura.
"""

from chatbot import correct_user_input_with_ai, fuzzy_match_value, get_unique_values

def test_fuzzy_matching():
    """Prueba fuzzy matching con diferentes errores"""
    print("\n" + "="*80)
    print("PRUEBA 1: Fuzzy Matching Directo")
    print("="*80)
    
    # Simular lista de clientes
    test_clients = ["LACOSTE", "NIKE", "ADIDAS", "PUMA", "REEBOK"]
    
    test_cases = [
        ("LASCOSTE", test_clients),  # Error de ortografía
        ("NIQUE", test_clients),      # Error de ortografía
        ("ADDIDAS", test_clients),    # Doble D
        ("LACOSTE", test_clients),    # Correcto
        ("puma", test_clients),       # Minúsculas
    ]
    
    for input_val, valid_vals in test_cases:
        matched, confidence = fuzzy_match_value(input_val, valid_vals)
        if matched:
            print(f"'{input_val}' → '{matched}' (confianza: {confidence:.2%})")
        else:
            print(f"'{input_val}' → No match encontrado")

def test_ai_correction():
    """Prueba corrección con IA usando valores reales de la DB"""
    print("\n" + "="*80)
    print("PRUEBA 2: Corrección Automática con IA")
    print("="*80)
    
    test_questions = [
        "¿Cuántas prendas de LASCOSTE para honbres hay?",
        "¿Cuántas prendas de NIQUE tengo?",
        "Dame las prendas de LACOSTE para mujeres",  # Correcto
        "¿Qué tipos de T-Shirth existen?",
    ]
    
    for question in test_questions:
        print(f"\nPregunta original: {question}")
        corrected, corrections = correct_user_input_with_ai(question)
        
        if corrections:
            print(f"✓ Corregida a: {corrected}")
            print(f"  Correcciones: {corrections}")
        else:
            print("✓ Sin errores detectados")

def test_unique_values():
    """Prueba recuperación de valores únicos con caché"""
    print("\n" + "="*80)
    print("PRUEBA 3: Valores Únicos de la DB (con caché)")
    print("="*80)
    
    print("\nObteniendo clientes (primera vez)...")
    clients = get_unique_values('TDESCCLIE', use_cache=False)
    print(f"✓ {len(clients)} clientes únicos")
    print(f"Primeros 10: {clients[:10]}")
    
    print("\nObteniendo clientes (segunda vez - desde caché)...")
    clients_cached = get_unique_values('TDESCCLIE', use_cache=True)
    print(f"✓ {len(clients_cached)} clientes (cacheados)")
    
    print("\nObteniendo géneros...")
    genders = get_unique_values('TTIPOGENE')
    print(f"✓ Géneros: {genders}")

if __name__ == "__main__":
    print("\n🧪 INICIANDO PRUEBAS DEL SISTEMA DE CORRECCIÓN\n")
    
    try:
        test_fuzzy_matching()
        test_unique_values()
        test_ai_correction()
        
        print("\n" + "="*80)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
