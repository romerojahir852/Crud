"""Suite de Pruebas Automatizadas para proyecto_clientes.

Valida el cumplimiento estricto de las 5 operaciones CRUD,
las reglas de negocio y la separación MVC.
"""

import os
import sys
import shutil

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIR_ACTUAL not in sys.path:
    sys.path.insert(0, DIR_ACTUAL)

import views
from models import Cliente
from shared.json_manager import GestorJSON

def ejecutar_pruebas():
    print("=== INICIANDO BATERÍA DE PRUEBAS AUTOMATIZADAS (CLIENTES) ===")
    
    # 1. Configurar un archivo de pruebas aislado
    ruta_test = os.path.join(DIR_ACTUAL, "data", "test_clientes.json")
    os.makedirs(os.path.join(DIR_ACTUAL, "data"), exist_ok=True)
    if os.path.exists(ruta_test):
        os.remove(ruta_test)

    # Inyectar gestor de pruebas
    views.gestor = GestorJSON(ruta_test)

    # Prueba 1: Crear cliente válido
    exito, msg = views.crear_cliente({
        "nombre": "Ana",
        "apellido": "Pérez",
        "email": "ana@ejemplo.com",
        "telefono": "0987654321",
        "ciudad": "Guayaquil",
        "direccion": "Av. Principal 123"
    })
    assert exito is True, f"Fallo al crear cliente válido: {msg}"
    print("✓ Prueba 1 superada: Creación de cliente válido.")

    # Prueba 2: Rechazar duplicación de email
    exito_dup, msg_dup = views.crear_cliente({
        "nombre": "Anita",
        "apellido": "Gómez",
        "email": "ANA@ejemplo.com",  # Mayúsculas intencionales para probar normalización
        "telefono": "0999999999",
        "ciudad": "Quito",
        "direccion": "Calle 1"
    })
    assert exito_dup is False, "Debe rechazar email duplicado"
    print("✓ Prueba 2 superada: Detección O(1) de email duplicado.")

    # Prueba 3: Rechazar formato de email inválido
    exito_mal, msg_mal = views.crear_cliente({
        "nombre": "Carlos",
        "apellido": "López",
        "email": "carlos_sin_arroba",
        "telefono": "",
        "ciudad": "",
        "direccion": ""
    })
    assert exito_mal is False, "Debe rechazar email sintácticamente inválido"
    print("✓ Prueba 3 superada: Validación de formato de email.")

    # Prueba 4: Crear segundo cliente y listar
    views.crear_cliente({
        "nombre": "Luis",
        "apellido": "García",
        "email": "luis@ejemplo.com",
        "telefono": "0911111111",
        "ciudad": "Guayaquil",
        "direccion": "Calle 5"
    })
    todos = views.obtener_todos()
    assert len(todos) == 2, f"Se esperaban 2 clientes, se obtuvieron {len(todos)}"
    print("✓ Prueba 4 superada: Lectura y deserialización completa (READ).")

    # Prueba 5: Búsqueda lineal
    resultados = views.buscar_clientes("guayaquil")
    assert len(resultados) == 2, "La búsqueda por ciudad debe arrojar 2 resultados"
    resultados_nombre = views.buscar_clientes("Luis")
    assert len(resultados_nombre) == 1 and resultados_nombre[0].id == 2, "Búsqueda por nombre fallida"
    print("✓ Prueba 5 superada: Búsqueda lineal multisectorial (SEARCH).")

    # Prueba 6: Actualización y rechazo de claves desconocidas
    exito_act_bad, _ = views.actualizar_cliente(1, {"campo_inventado": "valor"})
    assert exito_act_bad is False, "Debe rechazar atributos fuera de CAMPOS_CLIENTE"

    exito_act, msg_act = views.actualizar_cliente(1, {"telefono": "0998887777"})
    assert exito_act is True, f"Fallo al actualizar: {msg_act}"
    c1 = views.obtener_por_id(1)
    assert c1.telefono == "0998887777", "El teléfono no fue persistido correctamente"
    print("✓ Prueba 6 superada: Actualización selectiva y validación por conjuntos (UPDATE).")

    # Prueba 7: Estadísticas con conjuntos y comprensiones
    stats = views.estadisticas()
    assert stats["total"] == 2
    assert "Guayaquil" in stats["ciudades"]
    assert "ejemplo.com" in stats["dominios"]
    print("✓ Prueba 7 superada: Métricas y analítica con dicts y sets (estadisticas).")

    # Prueba 8: Eliminación
    exito_del, msg_del = views.eliminar_cliente(2)
    assert exito_del is True, f"Fallo al eliminar: {msg_del}"
    assert len(views.obtener_todos()) == 1, "Debe quedar 1 cliente tras eliminar"
    print("✓ Prueba 8 superada: Eliminación sin mutación en bucle (DELETE).")

    # Limpieza de archivo de test
    if os.path.exists(ruta_test):
        os.remove(ruta_test)

    print("\nTODAS LAS PRUEBAS DE CLIENTES FINALIZARON CON ÉXITO (100% PASS).")

if __name__ == "__main__":
    ejecutar_pruebas()
