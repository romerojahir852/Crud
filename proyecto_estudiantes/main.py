"""Módulo Vista (main.py) del Sistema de Gestión de Estudiantes.

Implementa la capa de presentación (interfaz de usuario en consola).
Cumple con la separación de responsabilidades de MVC:
- Gestiona la interacción con el usuario (input() y print()).
- No contiene lógica del negocio ni acceso a disco.
- Despacha las opciones del menú mediante una tabla de despacho (diccionario).
"""

from models import CAMPOS_ESTUDIANTE
from shared.herramientas import (
    imprimir_titulo,
    imprimir_exito,
    imprimir_error,
    imprimir_info,
    imprimir_alerta,
    confirmar,
)
from views import (
    crear_estudiante,
    obtener_todos,
    obtener_por_id,
    obtener_por_carnet,
    buscar_estudiantes,
    actualizar_estudiante,
    eliminar_estudiante,
    agregar_nota,
    materias_ofertadas,
    estudiantes_en_comun,
    estadisticas_estudiantes,
)


def pausa():
    """Detiene la pantalla para permitir la lectura de resultados por el usuario."""
    input("\nPresione [Enter] para continuar...")


def mostrar_tabla_estudiantes(estudiantes):
    """Presenta una lista de estudiantes en formato tabular profesional."""
    encabezado = f"{'ID':<4} {'CARNET':<12} {'NOMBRE COMPLETO':<26} {'EMAIL':<26} {'MATERIAS':<10} {'PROMEDIO':<8}"
    print(encabezado)
    print("=" * len(encabezado))
    for est in estudiantes:
        num_materias = len(est.materias)
        print(
            f"{est.id:<4} {est.carnet:<12} {est.obtener_nombre_completo():<26} "
            f"{est.email:<26} {num_materias:<10} {est.obtener_promedio():<8.2f}"
        )
    print("=" * len(encabezado))
    imprimir_info(f"Total desplegado: {len(estudiantes)} estudiante(s)")


# ===================== OPCIÓN 1: CREAR =====================
def opcion_crear():
    imprimir_titulo("REGISTRO DE NUEVO ESTUDIANTE")
    print("Ingrese la información requerida:\n")

    datos = {}
    for campo in CAMPOS_ESTUDIANTE:
        etiqueta = campo.replace("_", " ").capitalize()
        datos[campo] = input(f"• {etiqueta}: ")

    exito, mensaje = crear_estudiante(datos)  # Desempaquetado de tupla
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)
    pausa()


# ===================== OPCIÓN 2: LEER TODOS =====================
def opcion_ver_todos():
    imprimir_titulo("LISTADO GENERAL DE ESTUDIANTES")
    estudiantes = obtener_todos()
    if not estudiantes:
        imprimir_alerta("No existen estudiantes registrados aún en el sistema.")
    else:
        mostrar_tabla_estudiantes(estudiantes)
    pausa()


# ===================== OPCIÓN 3: BUSCAR =====================
def opcion_buscar():
    imprimir_titulo("BÚSQUEDA MULTISECTORIAL DE ESTUDIANTES")
    termino = input("Ingrese criterio de búsqueda (nombre, carnet, materia o correo): ")
    coincidencias = buscar_estudiantes(termino)

    if not coincidencias:
        imprimir_info(f"No se hallaron coincidencias para el criterio '{termino}'.")
    else:
        mostrar_tabla_estudiantes(coincidencias)
    pausa()


# ===================== OPCIÓN 4: VER DETALLE / KARDEX =====================
def opcion_ver_detalle():
    imprimir_titulo("EXPEDIENTE ACADÉMICO / KARDEX POR ID")
    try:
        id_est = int(input("Ingrese el ID del estudiante: "))
    except ValueError:
        imprimir_error("El ID debe ser un número entero.")
        return pausa()

    estudiante = obtener_por_id(id_est)
    if not estudiante:
        imprimir_error(f"No existe ningún estudiante con ID {id_est}.")
        return pausa()

    print(f"  ID               : {estudiante.id}")
    print(f"  Carnet           : {estudiante.carnet}")
    print(f"  Nombre Completo  : {estudiante.obtener_nombre_completo()}")
    print(f"  Correo Electrónico: {estudiante.email}")
    print(f"  Materias Inscritas: {', '.join(sorted(estudiante.materias)) if estudiante.materias else 'Ninguna'}")
    print(f"  Promedio General : {estudiante.obtener_promedio():.2f}")
    print("\n--- Desglose de Calificaciones por Materia ---")

    if not estudiante.notas:
        imprimir_info("El estudiante no registra calificaciones todavía.")
    else:
        for materia, lista_notas in sorted(estudiante.notas.items()):
            prom = estudiante.obtener_promedio_materia(materia)
            notas_str = ", ".join(f"{n:.1f}" for n in lista_notas) if lista_notas else "Sin notas"
            print(f"  📚 {materia:<20}: [{notas_str}] -> Promedio: {prom:.2f}")

    pausa()


# ===================== OPCIÓN 5: ACTUALIZAR =====================
def opcion_actualizar():
    imprimir_titulo("ACTUALIZAR DATOS DE ESTUDIANTE")
    try:
        id_est = int(input("Ingrese el ID del estudiante a editar: "))
    except ValueError:
        imprimir_error("El ID debe ser un número entero.")
        return pausa()

    estudiante = obtener_por_id(id_est)
    if not estudiante:
        imprimir_error(f"No existe ningún estudiante con ID {id_est}.")
        return pausa()

    imprimir_info(f"Modificando a: {estudiante.obtener_nombre_completo()} (Carnet: {estudiante.carnet})")
    print("Presione [Enter] sin escribir para conservar el valor actual entre corchetes:\n")

    cambios = {}
    for campo in CAMPOS_ESTUDIANTE:
        actual = getattr(estudiante, campo)
        etiqueta = campo.capitalize()
        nuevo = input(f"• {etiqueta} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    exito, mensaje = actualizar_estudiante(id_est, cambios)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)
    pausa()


# ===================== OPCIÓN 6: ELIMINAR =====================
def opcion_eliminar():
    imprimir_titulo("ELIMINACIÓN DE ESTUDIANTE")
    try:
        id_est = int(input("Ingrese el ID del estudiante a eliminar: "))
    except ValueError:
        imprimir_error("El ID debe ser un valor numérico entero.")
        return pausa()

    estudiante = obtener_por_id(id_est)
    if not estudiante:
        imprimir_error(f"No existe ningún estudiante con ID {id_est}.")
        return pausa()

    imprimir_alerta(f"Se procederá a dar de baja a: {estudiante}")
    if confirmar("¿Está completamente seguro de eliminar este registro?"):
        exito, mensaje = eliminar_estudiante(id_est)
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)
    else:
        imprimir_info("Operación cancelada por el usuario.")
    pausa()


# ===================== OPCIÓN 7: AGREGAR NOTA (0 - 20) =====================
def opcion_agregar_nota():
    imprimir_titulo("REGISTRAR CALIFICACIÓN (ESCALA 0 A 20)")
    try:
        id_est = int(input("Ingrese el ID del estudiante: "))
    except ValueError:
        imprimir_error("El ID debe ser un número entero.")
        return pausa()

    estudiante = obtener_por_id(id_est)
    if not estudiante:
        imprimir_error(f"No existe ningún estudiante con ID {id_est}.")
        return pausa()

    imprimir_info(f"Estudiante seleccionado: {estudiante.obtener_nombre_completo()} (Carnet: {estudiante.carnet})")
    if estudiante.materias:
        materias_actuales = ", ".join(sorted(estudiante.materias))
        print(f"Materias actualmente inscritas: {materias_actuales}")

    materia = input("Nombre de la asignatura: ").strip()
    nota_input = input("Calificación a asignar (0.00 - 20.00): ").strip()

    exito, mensaje = agregar_nota(id_est, materia, nota_input)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)
    pausa()


# ===================== OPCIÓN 8: VER PROMEDIO =====================
def opcion_ver_promedio():
    imprimir_titulo("CONSULTA RÁPIDA DE PROMEDIO")
    criterio = input("Ingrese ID o Carnet del estudiante: ").strip()
    estudiante = None
    if criterio.isdigit():
        estudiante = obtener_por_id(int(criterio))
    if not estudiante:
        estudiante = obtener_por_carnet(criterio)

    if not estudiante:
        imprimir_error(f"No se encontró estudiante con el identificador '{criterio}'.")
        return pausa()

    imprimir_info(f"Estudiante: {estudiante.obtener_nombre_completo()} ({estudiante.carnet})")
    print(f"  • Total de materias inscritas : {len(estudiante.materias)}")
    print(f"  • Promedio general acumulado   : {estudiante.obtener_promedio():.2f} / 20.00")
    if estudiante.notas:
        print("\n  Promedios por asignatura:")
        for mat in sorted(estudiante.materias):
            print(f"    - {mat:<20}: {estudiante.obtener_promedio_materia(mat):.2f}")
    pausa()


# ===================== OPCIÓN 9: MATERIAS OFERTADAS (CONJUNTO GLOBAL) =====================
def opcion_materias_ofertadas():
    imprimir_titulo("CATÁLOGO DE MATERIAS OFERTADAS / INSCRITAS")
    materias = materias_ofertadas()  # Retorna un set
    if not materias:
        imprimir_info("No existen materias registradas en ningún expediente actualmente.")
    else:
        print(f"Total de materias distintas detectadas: {len(materias)}\n")
        for i, mat in enumerate(sorted(materias), start=1):
            print(f"  {i:>2}. 📘 {mat}")
    pausa()


# ===================== OPCIÓN 10: MATERIAS EN COMÚN (INTERSECCIÓN DE CONJUNTOS) =====================
def opcion_materias_en_comun():
    imprimir_titulo("COMPARATIVA DE ASIGNATURAS EN COMÚN (INTERSECCIÓN DE CONJUNTOS)")
    try:
        id_a = int(input("Ingrese el ID del primer estudiante : "))
        id_b = int(input("Ingrese el ID del segundo estudiante: "))
    except ValueError:
        imprimir_error("Ambos IDs deben ser números enteros válidos.")
        return pausa()

    if id_a == id_b:
        imprimir_alerta("Ingresó el mismo ID para ambos estudiantes.")
        return pausa()

    exito, mensaje, comunes = estudiantes_en_comun(id_a, id_b)
    if not exito:
        imprimir_error(mensaje)
    else:
        imprimir_exito(mensaje)
        if comunes:
            print("\nMaterias que cursan en común (A ∩ B):")
            for mat in sorted(comunes):
                print(f"  ★ {mat}")
        else:
            imprimir_info("Los estudiantes no comparten ninguna asignatura actualmente.")
    pausa()


# ===================== OPCIÓN 11: ESTADÍSTICAS GENERALES =====================
def opcion_estadisticas():
    imprimir_titulo("PANEL DE RENDIMIENTO Y ESTADÍSTICAS GENERALES")
    stats = estadisticas_estudiantes()

    print(f"  • Total de estudiantes registrados : {stats['total']}")
    print(f"  • Promedio general de la institución: {stats['promedio_global']:.2f} / 20.00")
    print(f"  • Total de asignaturas ofertadas    : {len(stats['materias_totales'])}")

    if stats["mejor_estudiante"]:
        mejor = stats["mejor_estudiante"]
        print(
            f"  • Cuadro de Honor (Mejor Promedio)  : {mejor.obtener_nombre_completo()} "
            f"({mejor.carnet}) con {mejor.obtener_promedio():.2f} pts."
        )

    if stats["sin_notas"]:
        print(f"  • Estudiantes pendientes de notas   : {len(stats['sin_notas'])} ({', '.join(stats['sin_notas'])})")

    pausa()


def salir():
    imprimir_info("¡Sesión finalizada exitosamente! Éxitos en el ciclo académico.")
    return "salir"


# DICCIONARIO DE OPCIONES: Tabla de despacho en tiempo constante O(1)
OPCIONES = {
    "1": ("Crear estudiante", opcion_crear),
    "2": ("Listar todos los estudiantes", opcion_ver_todos),
    "3": ("Buscar estudiantes", opcion_buscar),
    "4": ("Ver kardex / detalle por ID", opcion_ver_detalle),
    "5": ("Actualizar estudiante", opcion_actualizar),
    "6": ("Eliminar estudiante", opcion_eliminar),
    "7": ("Agregar nota (Escala 0-20)", opcion_agregar_nota),
    "8": ("Ver promedio académico", opcion_ver_promedio),
    "9": ("Materias ofertadas (Conjunto global)", opcion_materias_ofertadas),
    "10": ("Materias en común (Intersección)", opcion_materias_en_comun),
    "11": ("Estadísticas institucionales", opcion_estadisticas),
    "0": ("Cerrar sistema", salir),
}


def mostrar_menu():
    imprimir_titulo("SISTEMA DE GESTIÓN ACADÉMICA DE ESTUDIANTES (MVC)")
    for tecla, (texto, _func) in OPCIONES.items():
        print(f"  [{tecla:>2}] {texto}")
    print()


def main():
    while True:
        mostrar_menu()
        tecla = input("Seleccione una opción: ").strip()

        if tecla not in OPCIONES:
            imprimir_error("Opción inválida. Seleccione un número del menú.")
            pausa()
            continue

        _texto, funcion = OPCIONES[tecla]
        if funcion() == "salir":
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nEjecución cancelada por el usuario. Saliendo de forma segura...")
