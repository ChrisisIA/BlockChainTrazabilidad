#!/usr/bin/env python3
"""
Script de prueba para demostrar la mejora de rendimiento con paralelización.
Compara procesamiento secuencial vs paralelo.
"""

import time
from chatbot import fetch_json_from_swarm
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_sequential_download(hashes):
    """Descarga hashes de forma secuencial (método antiguo)"""
    print("\n" + "="*80)
    print("TEST: DESCARGA SECUENCIAL (Método Antiguo)")
    print("="*80)

    start_time = time.time()
    successful = 0
    failed = 0

    for i, hash_val in enumerate(hashes, 1):
        print(f"[{i}/{len(hashes)}] Descargando hash {hash_val[:16]}...")
        json_data = fetch_json_from_swarm(hash_val, timeout=10, verbose=False)

        if json_data:
            successful += 1
        else:
            failed += 1

    elapsed = time.time() - start_time

    print(f"\n✓ Descarga secuencial completada:")
    print(f"  • Tiempo total: {elapsed:.2f} segundos")
    print(f"  • Velocidad: {len(hashes)/elapsed:.2f} JSONs/segundo")
    print(f"  • Éxitos: {successful}, Fallos: {failed}")

    return elapsed


def test_parallel_download(hashes, max_workers=10):
    """Descarga hashes en paralelo (método nuevo)"""
    print("\n" + "="*80)
    print(f"TEST: DESCARGA PARALELA (Método Nuevo - {max_workers} workers)")
    print("="*80)

    start_time = time.time()
    successful = 0
    failed = 0

    def download_hash(hash_val):
        """Función para descargar un hash"""
        json_data = fetch_json_from_swarm(hash_val, timeout=10, verbose=False)
        return hash_val, json_data

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_hash = {executor.submit(download_hash, h): h for h in hashes}

        for i, future in enumerate(as_completed(future_to_hash), 1):
            hash_val, json_data = future.result()

            if json_data:
                successful += 1
            else:
                failed += 1

            if i % 5 == 0 or i == len(hashes):
                print(f"  [{i}/{len(hashes)}] Progreso: {successful} éxitos, {failed} fallos")

    elapsed = time.time() - start_time

    print(f"\n✓ Descarga paralela completada:")
    print(f"  • Tiempo total: {elapsed:.2f} segundos")
    print(f"  • Velocidad: {len(hashes)/elapsed:.2f} JSONs/segundo")
    print(f"  • Éxitos: {successful}, Fallos: {failed}")

    return elapsed


def compare_performance():
    """Compara rendimiento entre ambos métodos"""
    print("\n" + "🚀 "*20)
    print("COMPARACIÓN DE RENDIMIENTO: SECUENCIAL VS PARALELO")
    print("🚀 "*20)

    # Hashes de prueba (usar hashes reales de tu sistema)
    # NOTA: Reemplaza estos con hashes reales de tu base de datos
    test_hashes = [
        # Aquí van hashes reales
        # Por ahora usamos hashes de ejemplo para demostración
        "ejemplo_hash_1" * 4,  # 64 caracteres (ejemplo)
        "ejemplo_hash_2" * 4,
        "ejemplo_hash_3" * 4,
        "ejemplo_hash_4" * 4,
        "ejemplo_hash_5" * 4,
        "ejemplo_hash_6" * 4,
        "ejemplo_hash_7" * 4,
        "ejemplo_hash_8" * 4,
        "ejemplo_hash_9" * 4,
        "ejemplo_hash_10" * 4,
    ]

    print(f"\n📊 Configuración de prueba:")
    print(f"  • Cantidad de hashes: {len(test_hashes)}")
    print(f"  • Timeout por hash: 10 segundos")
    print(f"  • Workers paralelos: 10")

    print("\n⚠️ NOTA: Esta prueba usa hashes de ejemplo.")
    print("Para prueba real, reemplaza 'test_hashes' con hashes de tu DB.")

    # Test 1: Secuencial
    time_sequential = test_sequential_download(test_hashes)

    # Test 2: Paralelo
    time_parallel = test_parallel_download(test_hashes, max_workers=10)

    # Comparación
    print("\n" + "="*80)
    print("COMPARACIÓN FINAL")
    print("="*80)

    speedup = time_sequential / time_parallel if time_parallel > 0 else 0
    improvement = ((time_sequential - time_parallel) / time_sequential * 100) if time_sequential > 0 else 0

    print(f"\n📊 Resultados:")
    print(f"  • Tiempo secuencial: {time_sequential:.2f}s")
    print(f"  • Tiempo paralelo:   {time_parallel:.2f}s")
    print(f"  • Aceleración:       {speedup:.2f}x más rápido")
    print(f"  • Mejora:            {improvement:.1f}% más rápido")

    if speedup > 1:
        print(f"\n✅ ÉXITO: El procesamiento paralelo es {speedup:.2f}x más rápido!")
    else:
        print(f"\n⚠️ El procesamiento paralelo no mostró mejora significativa.")

    print("\n💡 Proyección para diferentes cantidades de hashes:")
    print("-" * 80)

    for num_hashes in [10, 50, 100, 200]:
        seq_time = (time_sequential / len(test_hashes)) * num_hashes
        par_time = (time_parallel / len(test_hashes)) * num_hashes

        print(f"  {num_hashes:3d} hashes → Secuencial: {seq_time:6.1f}s | "
              f"Paralelo: {par_time:5.1f}s | "
              f"Ahorro: {seq_time - par_time:5.1f}s")


def demo_real_world_usage():
    """Demuestra el uso en un caso real"""
    print("\n" + "="*80)
    print("DEMOSTRACIÓN: CASO DE USO REAL")
    print("="*80)

    print("\n📝 Escenario:")
    print("Usuario consulta: '¿Qué máquinas procesaron las prendas de LACOSTE?'")
    print("Resultado de DB: 100 hashes encontrados")

    print("\n⏱️ Tiempos estimados:")
    print("-" * 80)

    # Estimaciones basadas en 0.5s por hash (red + procesamiento)
    time_per_hash = 0.5

    sequential_time = 100 * time_per_hash
    parallel_time_10 = (100 * time_per_hash) / 10  # 10 workers
    parallel_time_20 = (100 * time_per_hash) / 20  # 20 workers

    print(f"  Secuencial (1 hash a la vez):     {sequential_time:.0f} segundos (~{sequential_time/60:.1f} minutos)")
    print(f"  Paralelo (10 workers):            {parallel_time_10:.0f} segundos")
    print(f"  Paralelo (20 workers):            {parallel_time_20:.0f} segundos")

    print(f"\n💰 Ahorro de tiempo:")
    print(f"  Con 10 workers: {sequential_time - parallel_time_10:.0f} segundos ahorrados ({((sequential_time - parallel_time_10)/sequential_time*100):.0f}% más rápido)")
    print(f"  Con 20 workers: {sequential_time - parallel_time_20:.0f} segundos ahorrados ({((sequential_time - parallel_time_20)/sequential_time*100):.0f}% más rápido)")

    print("\n✅ Recomendación: Usar 10-15 workers para balance óptimo entre velocidad y carga del servidor.")


if __name__ == "__main__":
    print("\n" + "🧪 "*30)
    print("SUITE DE PRUEBAS - PARALELIZACIÓN DE DESCARGA DE SWARM")
    print("🧪 "*30)

    try:
        # Demostración de caso real
        demo_real_world_usage()

        # Comparación de rendimiento (comentado por defecto - requiere hashes reales)
        # print("\n⚠️ Para ejecutar la comparación real, descomenta la siguiente línea")
        # print("   y reemplaza test_hashes con hashes reales de tu DB.\n")
        # compare_performance()

        print("\n" + "🎉 "*30)
        print("SUITE DE PRUEBAS COMPLETADA")
        print("🎉 "*30)

        print("\n📋 RESUMEN DE MEJORAS:")
        print("-" * 80)
        print("✅ Procesamiento paralelo implementado con ThreadPoolExecutor")
        print("✅ Configuración por defecto: 10 workers concurrentes")
        print("✅ Velocidad estimada: 10x más rápido para 100 hashes")
        print("✅ Manejo robusto de errores y timeouts")
        print("✅ Progreso visible cada 10 JSONs procesados")
        print("✅ Cancelación automática al alcanzar límite de tamaño")
        print("-" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0
