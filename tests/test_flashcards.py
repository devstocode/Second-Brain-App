# tests/test_flashcards.py
import sys
import os
from datetime import datetime, timedelta

# Permitir importar desde la raíz del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.flashcard_service import FlashcardService

def test_flashcards_flow():
    print("🧪 Iniciando pruebas del sistema de Flashcards...")
    service = FlashcardService()

    # 1. Crear Mazo
    nombre_mazo = "Neurotest Mazo"
    
    # Limpieza previa en caso de una prueba interrumpida
    mazos = service.obtener_todos_los_mazos()
    pre_existente = next((m for m in mazos if m['nombre'] == nombre_mazo), None)
    if pre_existente:
        service.eliminar_mazo(pre_existente['id'])
        
    exito, msg = service.crear_mazo(nombre_mazo)
    print(f"   - Crear mazo '{nombre_mazo}': {exito} ({msg})")
    assert exito, "Error al crear mazo"

    # Obtener todos los mazos y encontrar el ID del nuestro
    mazos = service.obtener_todos_los_mazos()
    mazo = next((m for m in mazos if m['nombre'] == nombre_mazo), None)
    assert mazo is not None, "Mazo creado no encontrado en la lista"
    mazo_id = mazo['id']
    print(f"   - Mazo encontrado con ID: {mazo_id}")

    # 2. Crear Tarjeta
    pregunta = "¿Cuál es el neurotransmisor principal de la unión neuromuscular?"
    respuesta = "Acetilcolina"
    tags = "sinapsis, neuro"
    exito_card, msg_card = service.crear_tarjeta(mazo_id, pregunta, respuesta, tags)
    print(f"   - Crear tarjeta: {exito_card} ({msg_card})")
    assert exito_card, "Error al crear tarjeta"

    # Verificar que el conteo en el mazo es correcto
    mazos_actualizados = service.obtener_todos_los_mazos()
    mazo_act = next((m for m in mazos_actualizados if m['id'] == mazo_id), None)
    print(f"   - Conteo de tarjetas: {mazo_act['total_cartas']} total, {mazo_act['cartas_pendientes']} pendientes")
    assert mazo_act['total_cartas'] == 1, "El conteo de tarjetas no coincide"

    # 3. Obtener tarjetas del mazo
    tarjetas = service.obtener_tarjetas_por_mazo(mazo_id)
    assert len(tarjetas) == 1, "No se recuperó la tarjeta creada"
    tarjeta = tarjetas[0]
    print(f"   - Tarjeta recuperada: P='{tarjeta['pregunta']}' R='{tarjeta['respuesta']}'")
    
    # 4. Probar Algoritmo SM-2 (Calificación: Bien -> 2)
    tarjeta_id = tarjeta['id']
    exito_resp, msg_resp = service.responder_tarjeta(tarjeta_id, calificacion=2) # Bien (Good)
    print(f"   - Responder tarjeta (Bien): {exito_resp} ({msg_resp})")
    assert exito_resp, "Error al calificar tarjeta"

    # Verificar que los datos se actualizaron en la base de datos
    tarjetas_actualizadas = service.obtener_tarjetas_por_mazo(mazo_id)
    tarjeta_act = tarjetas_actualizadas[0]
    print(f"   - Datos SM-2 actualizados: Reps={tarjeta_act['repetitions']}, Intervalo={tarjeta_act['interval']} días, Ease={tarjeta_act['ease_factor']:.2f}")
    assert tarjeta_act['repetitions'] == 1, "Las repeticiones no aumentaron"
    assert tarjeta_act['interval'] == 1, "El intervalo inicial para la primera repetición exitosa debería ser 1 día"

    # 5. Limpieza (Eliminar mazo)
    service.eliminar_mazo(mazo_id)
    print("   - Mazo de prueba eliminado con éxito.")
    
    # Verificar que ya no exista el mazo ni la tarjeta
    mazos_finales = service.obtener_todos_los_mazos()
    assert not any(m['id'] == mazo_id for m in mazos_finales), "El mazo no fue eliminado"
    
    print("✅ ¡Todas las pruebas del flujo de Flashcards pasaron correctamente!")

if __name__ == "__main__":
    test_flashcards_flow()
