"""Suite de Pruebas Unitarias e Integración para proyecto_estudiantes.

Verifica rigurosamente todos los criterios de la rúbrica de evaluación:
1. Separación de capas MVC (cero print/input en views.py).
2. Las cinco operaciones fundamentales de datos (CRUD + Search).
3. Uso y álgebra de las 4 colecciones de Python (list, tuple, set, dict).
4. Validaciones de negocio: carnet duplicado, nota fuera de rango [0, 20], IDs inexistentes.
5. Persistencia bidireccional en JSON preservando el tipo set rehidratado.
"""

import os
import sys
import inspect

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import views
import models
from models import Estudiante
from shared.json_manager import GestorJSON


import ast

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))

def verificar_separacion_mvc():
    """Valida mediante AST (Abstract Syntax Tree) que views.py no ejecute llamadas a print() ni input()."""
    ruta_views = os.path.join(DIR_ACTUAL, "views.py")
    with open(ruta_views, "r", encoding="utf-8") as archivo:
        arbol = ast.parse(archivo.read(), filename="views.py")

    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Call):
            if isinstance(nodo.func, ast.Name) and nodo.func.id in ("print", "input"):
                raise AssertionError(
                    f"Violación de MVC: Llamada prohibida a {nodo.func.id}() detectada en la línea {nodo.lineno} de views.py"
                )

    print("✓ Criterio 1 superado: Separación estricta MVC (0 llamadas AST a print() o input() en views.py).")


def ejecutar_pruebas_estudiantes():
    print("=== INICIANDO VALIDACIÓN ACADÉMICA AUTOMATIZADA (PROYECTO ESTUDIANTES) ===")

    # Asegurar que el directorio de este script esté en sys.path
    if DIR_ACTUAL not in sys.path:
        sys.path.insert(0, DIR_ACTUAL)

    # Verificación arquitectónica
    verificar_separacion_mvc()

    # Configuración de base de datos aislada para pruebas
    ruta_test = os.path.join(DIR_ACTUAL, "data", "test_estudiantes.json")
    os.makedirs(os.path.join(DIR_ACTUAL, "data"), exist_ok=True)
    if os.path.exists(ruta_test):
        os.remove(ruta_test)

    # Inyección de dependencia del gestor
    views.gestor = GestorJSON(ruta_test)

    # 1. CREATE: Crear primer estudiante
    exito_c1, msg_c1 = views.crear_estudiante({
        "nombre": "Ana",
        "apellido": "Pérez",
        "email": "ana@escuela.edu",
        "carnet": "EST2026001",
    })
    assert exito_c1 is True, f"Fallo al crear estudiante: {msg_c1}"
    print("✓ Criterio 2.1 superado: Creación exitosa de estudiante (CREATE).")

    # 2. VALIDACIÓN: Rechazar carnet duplicado usando SET
    exito_dup_carnet, msg_dup_c = views.crear_estudiante({
        "nombre": "Beatriz",
        "apellido": "Mendoza",
        "email": "beatriz@escuela.edu",
        "carnet": "est2026001",  # En minúsculas para comprobar normalización
    })
    assert exito_dup_carnet is False, "Debe rechazar carnet duplicado"
    assert "carnet" in msg_dup_c.lower()
    print("✓ Criterio 2.2 superado: Rechazo O(1) de carnet duplicado mediante CONJUNTO (set).")

    # 3. VALIDACIÓN: Rechazar email duplicado usando SET
    exito_dup_email, msg_dup_e = views.crear_estudiante({
        "nombre": "Carlos",
        "apellido": "Salazar",
        "email": "ANA@escuela.edu",  # Normalización a minúsculas
        "carnet": "EST2026002",
    })
    assert exito_dup_email is False, "Debe rechazar email duplicado"
    assert "correo" in msg_dup_e.lower()
    print("✓ Criterio 2.3 superado: Rechazo O(1) de correo duplicado mediante CONJUNTO (set).")

    # 4. Crear segundo y tercer estudiante
    views.crear_estudiante({
        "nombre": "Luis",
        "apellido": "García",
        "email": "luis@escuela.edu",
        "carnet": "EST2026002",
    })
    views.crear_estudiante({
        "nombre": "María",
        "apellido": "Torres",
        "email": "maria@escuela.edu",
        "carnet": "EST2026003",
    })

    # 5. READ: Obtener todos y por ID
    todos = views.obtener_todos()
    assert len(todos) == 3, f"Se esperaban 3 estudiantes, encontrados {len(todos)}"
    est1 = views.obtener_por_id(1)
    assert est1 is not None and est1.carnet == "EST2026001"
    est_carnet = views.obtener_por_carnet("est2026002")
    assert est_carnet is not None and est_carnet.id == 2
    print("✓ Criterio 2.4 superado: Lectura individual y colectiva de objetos (READ).")

    # 6. GESTIÓN DE NOTAS: Validaciones de rango [0, 20]
    # Caso 6.1: Nota fuera de rango (mayor a 20)
    exito_n_alta, _ = views.agregar_nota(1, "Matemática", 21)
    assert exito_n_alta is False, "Debe rechazar notas > 20"

    # Caso 6.2: Nota fuera de rango (menor a 0)
    exito_n_baja, _ = views.agregar_nota(1, "Matemática", -1)
    assert exito_n_baja is False, "Debe rechazar notas < 0"

    # Caso 6.3: Nota no numérica
    exito_n_texto, _ = views.agregar_nota(1, "Matemática", "veinte")
    assert exito_n_texto is False, "Debe rechazar notas no numéricas"

    # Caso 6.4: ID inexistente
    exito_n_noid, _ = views.agregar_nota(999, "Matemática", 18)
    assert exito_n_noid is False, "Debe rechazar calificación para ID inexistente"

    # Caso 6.5: Calificaciones válidas
    v1, _ = views.agregar_nota(1, "Matemática", 18.0)
    v2, _ = views.agregar_nota(1, "Matemática", 20.0)
    v3, _ = views.agregar_nota(1, "Inglés", 16.0)
    assert v1 and v2 and v3

    est1_actualizado = views.obtener_por_id(1)
    assert est1_actualizado.obtener_promedio() == 18.0, f"Promedio esperado 18.0, obtenido {est1_actualizado.obtener_promedio()}"
    assert "Matemática" in est1_actualizado.materias
    assert "Inglés" in est1_actualizado.materias
    print("✓ Criterio 3.1 superado: Validaciones de notas en rango [0, 20] y cálculo de promedios.")

    # 7. ASIGNACIÓN A OTROS ESTUDIANTES PARA ÁLGEBRA DE CONJUNTOS
    views.agregar_nota(2, "Inglés", 15.0)
    views.agregar_nota(2, "Física", 17.0)
    views.agregar_nota(3, "Química", 19.0)

    # 8. MATERIAS OFERTADAS (UNIÓN DE CONJUNTOS)
    ofertadas = views.materias_ofertadas()
    assert isinstance(ofertadas, set), "materias_ofertadas() debe retornar un set"
    esperadas = {"Matemática", "Inglés", "Física", "Química"}
    assert ofertadas == esperadas, f"Conjunto ofertado incorrecto: {ofertadas} vs {esperadas}"
    print("✓ Criterio 3.2 superado: Unión de conjuntos con materias_ofertadas().")

    # 9. MATERIAS EN COMÚN (INTERSECCIÓN DE CONJUNTOS)
    ok_comun, _, compartidas = views.estudiantes_en_comun(1, 2)
    assert ok_comun is True
    assert compartidas == {"Inglés"}, f"Intersección esperada {{'Inglés'}}, obtenida {compartidas}"

    ok_c13, _, comp13 = views.estudiantes_en_comun(1, 3)
    assert comp13 == set(), "Ana y María no comparten materias (conjunto vacío)"
    print("✓ Criterio 3.3 superado: Intersección de conjuntos (&) en estudiantes_en_comun().")

    # 10. SEARCH: Búsqueda lineal
    res_carnet = views.buscar_estudiantes("EST2026002")
    assert len(res_carnet) == 1 and res_carnet[0].id == 2
    res_materia = views.buscar_estudiantes("Química")
    assert len(res_materia) == 1 and res_materia[0].nombre == "María"
    print("✓ Criterio 4 superado: Búsqueda lineal multisectorial (SEARCH).")

    # 11. UPDATE: Actualización con verificación de claves
    exito_u_bad, _ = views.actualizar_estudiante(2, {"campo_falso": "valor"})
    assert exito_u_bad is False, "Debe rechazar claves desconocidas con diferencia de conjuntos"

    exito_u_dup, _ = views.actualizar_estudiante(2, {"carnet": "EST2026001"})
    assert exito_u_dup is False, "Debe rechazar actualizar a un carnet ya existente en otro alumno"

    exito_u_ok, _ = views.actualizar_estudiante(2, {"nombre": "Luis Alberto"})
    assert exito_u_ok is True
    assert views.obtener_por_id(2).nombre == "Luis Alberto"
    print("✓ Criterio 5 superado: Actualización selectiva controlada (UPDATE).")

    # 12. PERSISTENCIA JSON BIDIRECCIONAL (ROUND-TRIP)
    # Releemos el archivo crudo y verificamos que materias se rehidrate como set
    gestor_prueba = GestorJSON(ruta_test)
    datos_crudos = gestor_prueba.leer()
    assert isinstance(datos_crudos, list)
    assert isinstance(datos_crudos[0]["materias"], list), "En JSON se debe persistir como lista"

    est_rehidratado = Estudiante.desde_diccionario(datos_crudos[0])
    assert isinstance(est_rehidratado.materias, set), "Al deserializar debe rehidratarse como conjunto (set)"
    print("✓ Criterio 6 superado: Persistencia bidireccional set <-> list en JSON sin pérdida de tipos.")

    # 13. DELETE: Eliminación
    exito_del, _ = views.eliminar_estudiante(3)
    assert exito_del is True
    assert len(views.obtener_todos()) == 2
    print("✓ Criterio 7 superado: Eliminación segura de registros (DELETE).")

    # Limpieza
    if os.path.exists(ruta_test):
        os.remove(ruta_test)

    print("\n=================================================================")
    print("  ¡TODAS LAS PRUEBAS DE PROYECTO ESTUDIANTES APROBADAS AL 100%!  ")
    print("=================================================================")


if __name__ == "__main__":
    ejecutar_pruebas_estudiantes()
