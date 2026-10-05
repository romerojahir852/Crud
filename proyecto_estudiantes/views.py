"""Módulo Controlador (views.py) para el Sistema de Estudiantes.

Implementa la capa de lógica de negocio y orquestación de operaciones CRUD,
cálculo de notas, validaciones estrictas y álgebra de conjuntos.

REGLA DE ORO DE MVC:
- Este módulo NUNCA invoca print() ni input().
- Todas las respuestas que reportan estado retornan una tupla inmutable (exito: bool, mensaje: str).
- El acceso y mutación de persistencia se delega al GestorJSON.
"""

from models import Estudiante, CAMPOS_ESTUDIANTE
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido

# Instancia del gestor de persistencia apuntando a la base de datos JSON de estudiantes
gestor = GestorJSON("data/estudiantes.json")

# TUPLAS DE CONFIGURACIÓN INMUTABLES:
# Evitan modificaciones involuntarias durante el ciclo de vida del proceso
CAMPOS_OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")


# ===================== MÉTODOS DE SOPORTE E INDEXACIÓN =====================

def emails_registrados(excepto_id=None):
    """CONJUNTO (set) con los correos electrónicos registrados normalizados.

    Proporciona consultas de pertenencia en tiempo O(1) constante mediante hashing.
    """
    return {
        registro["email"].strip().lower()
        for registro in gestor.leer()
        if registro.get("id") != excepto_id
    }


def carnets_registrados(excepto_id=None):
    """CONJUNTO (set) con los códigos de carnet ya emitidos en el sistema.

    Garantiza la regla de unicidad del código de carnet en tiempo O(1).
    """
    return {
        registro["carnet"].strip().upper()
        for registro in gestor.leer()
        if registro.get("id") != excepto_id
    }


def siguiente_id():
    """Genera el identificador autoincremental garantizando una clave primaria única."""
    ids = [registro["id"] for registro in gestor.leer()]
    return max(ids) + 1 if ids else 1


# ===================== C · CREATE =====================

def crear_estudiante(datos):
    """Registra y persiste a un nuevo estudiante previa validación exhaustiva.

    Parámetros:
        datos (dict): Diccionario con las llaves de CAMPOS_ESTUDIANTE.
    Retorna:
        tuple (bool, str): Tupla con el indicador de éxito y mensaje descriptivo.
    """
    try:
        # 1. Normalización de entradas mediante comprensión de diccionario
        valores = {
            "nombre": str(datos.get("nombre", "")).strip(),
            "apellido": str(datos.get("apellido", "")).strip(),
            "email": str(datos.get("email", "")).strip().lower(),
            "carnet": str(datos.get("carnet", "")).strip().upper(),
        }

        # 2. Validación de campos requeridos recorriendo la TUPLA de obligatorios
        faltantes = [campo for campo in CAMPOS_OBLIGATORIOS if not valores[campo]]
        if faltantes:
            return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"

        # 3. Validación sintáctica de correo
        if not es_email_valido(valores["email"]):
            return False, f"El correo '{valores['email']}' no tiene un formato válido."

        # 4. Verificación de unicidad de email mediante pertenencia en CONJUNTO (set)
        if valores["email"] in emails_registrados():
            return False, f"El correo '{valores['email']}' ya pertenece a otro estudiante."

        # 5. Verificación de unicidad de carnet mediante pertenencia en CONJUNTO (set)
        if valores["carnet"] in carnets_registrados():
            return False, f"El carnet '{valores['carnet']}' ya se encuentra registrado."

        # 6. Creación de instancia del Modelo con listas y conjuntos vacíos iniciales
        nuevo_id = siguiente_id()
        estudiante = Estudiante(
            id_estudiante=nuevo_id,
            nombre=valores["nombre"],
            apellido=valores["apellido"],
            email=valores["email"],
            carnet=valores["carnet"],
            notas={},
            materias=set(),
        )

        # 7. Persistencia atómica en la colección JSON
        registros = gestor.leer()
        registros.append(estudiante.a_diccionario())
        if not gestor.guardar(registros):
            return False, "Error de E/S al escribir en el archivo de almacenamiento."

        return (
            True,
            f"Estudiante '{estudiante.obtener_nombre_completo()}' creado con ID {estudiante.id} y Carnet {estudiante.carnet}.",
        )

    except Exception as error:
        return False, f"Error inesperado en crear_estudiante: {error}"


# ===================== R · READ =====================

def obtener_todos():
    """Retorna una LISTA con todos los objetos Estudiante deserializados."""
    return [Estudiante.desde_diccionario(registro) for registro in gestor.leer()]


def obtener_por_id(id_estudiante):
    """Busca un estudiante por su ID numérico y retorna el objeto o None."""
    for estudiante in obtener_todos():
        if estudiante.id == id_estudiante:
            return estudiante
    return None


def obtener_por_carnet(carnet):
    """Busca un estudiante por su carnet único normalizado."""
    carnet_buscado = str(carnet).strip().upper()
    for estudiante in obtener_todos():
        if estudiante.carnet == carnet_buscado:
            return estudiante
    return None


# ===================== S · SEARCH =====================

def buscar_estudiantes(termino):
    """Búsqueda lineal que filtra sobre nombre, apellido, correo, carnet y materias inscritas."""
    termino = str(termino).strip().lower()
    if not termino:
        return []

    coincidencias = []
    for registro in gestor.leer():
        estudiante = Estudiante.desde_diccionario(registro)

        # Comparar con los atributos elementales
        coincide_campo = any(
            termino in str(registro.get(campo, "")).lower()
            for campo in CAMPOS_BUSCABLES
        )

        # Comparar también si el término coincide con alguna de sus materias (recorriendo el set)
        coincide_materia = any(termino in materia.lower() for materia in estudiante.materias)

        if coincide_campo or coincide_materia:
            coincidencias.append(estudiante)

    return coincidencias


# ===================== U · UPDATE =====================

def actualizar_estudiante(id_estudiante, cambios):
    """Actualiza datos básicos de un estudiante existente validando integridad referencial.

    Parámetros:
        id_estudiante (int): ID del estudiante a modificar.
        cambios (dict): Diccionario con los campos a alterar.
    """
    try:
        # Validación de atributos con DIFERENCIA DE CONJUNTOS (set difference)
        desconocidos = set(cambios.keys()) - set(CAMPOS_ESTUDIANTE)
        if desconocidos:
            return False, f"Atributos no permitidos: {', '.join(sorted(desconocidos))}"

        if not cambios:
            return False, "No se suministraron modificaciones."

        # Validaciones específicas de atributos sensibles
        if "email" in cambios:
            email_nuevo = str(cambios["email"]).strip().lower()
            if not es_email_valido(email_nuevo):
                return False, f"El correo '{email_nuevo}' tiene formato inválido."
            if email_nuevo in emails_registrados(excepto_id=id_estudiante):
                return False, f"El correo '{email_nuevo}' ya está en uso."
            cambios["email"] = email_nuevo

        if "carnet" in cambios:
            carnet_nuevo = str(cambios["carnet"]).strip().upper()
            if not carnet_nuevo:
                return False, "El carnet no puede estar vacío."
            if carnet_nuevo in carnets_registrados(excepto_id=id_estudiante):
                return False, f"El carnet '{carnet_nuevo}' ya pertenece a otro estudiante."
            cambios["carnet"] = carnet_nuevo

        if "nombre" in cambios:
            cambios["nombre"] = str(cambios["nombre"]).strip().title()

        if "apellido" in cambios:
            cambios["apellido"] = str(cambios["apellido"]).strip().title()

        registros = gestor.leer()
        posicion = None
        for indice, registro in enumerate(registros):
            if registro["id"] == id_estudiante:
                posicion = indice
                break

        if posicion is None:
            return False, f"No existe ningún estudiante con ID {id_estudiante}."

        registros[posicion].update(cambios)
        if not gestor.guardar(registros):
            return False, "Error al persistir la actualización en disco."

        return True, f"Estudiante con ID {id_estudiante} actualizado exitosamente."

    except Exception as error:
        return False, f"Error inesperado al actualizar: {error}"


# ===================== D · DELETE =====================

def eliminar_estudiante(id_estudiante):
    """Elimina permanentemente a un estudiante generando una nueva lista filtrada."""
    registros = gestor.leer()
    filtrados = [reg for reg in registros if reg["id"] != id_estudiante]

    if len(filtrados) == len(registros):
        return False, f"No se encontró un estudiante con ID {id_estudiante}."

    if not gestor.guardar(filtrados):
        return False, "Error de escritura al eliminar el registro."

    return True, f"Estudiante con ID {id_estudiante} eliminado satisfactoriamente."


# ===================== GESTIÓN DE NOTAS Y MATERIAS =====================

def agregar_nota(id_estudiante, materia, nota):
    """Registra una calificación en una materia para el estudiante especificado.

    Reglas de negocio:
        - La nota debe ser un valor numérico en el rango [0.0, 20.0].
        - Si la materia no existe, se inscribe automáticamente en el conjunto.
    Retorna:
        tuple: (exito: bool, mensaje: str)
    """
    # 1. Validar existencia del estudiante
    registros = gestor.leer()
    posicion = None
    for indice, reg in enumerate(registros):
        if reg["id"] == id_estudiante:
            posicion = indice
            break

    if posicion is None:
        return False, f"No se encontró ningún estudiante con ID {id_estudiante}."

    # 2. Validar nombre de la materia
    nombre_materia = str(materia).strip().title()
    if not nombre_materia:
        return False, "El nombre de la materia no puede estar vacío."

    # 3. Validar valor numérico y rango de la nota [0, 20]
    try:
        valor_nota = float(nota)
    except (ValueError, TypeError):
        return False, f"La nota ingresada '{nota}' no es un número válido."

    if valor_nota < 0.0 or valor_nota > 20.0:
        return False, f"Calificación inválida ({valor_nota}). Debe encontrarse en el rango de 0 a 20 puntos."

    # 4. Rehidratar a objeto del dominio y agregar la nota
    estudiante = Estudiante.desde_diccionario(registros[posicion])
    estudiante.agregar_nota(nombre_materia, round(valor_nota, 2))

    # 5. Persistir el objeto actualizado
    registros[posicion] = estudiante.a_diccionario()
    if not gestor.guardar(registros):
        return False, "Error al guardar la calificación en el disco."

    return (
        True,
        f"Calificación {round(valor_nota, 2)} asignada a '{estudiante.obtener_nombre_completo()}' en '{nombre_materia}'. Promedio actual: {estudiante.obtener_promedio()}",
    )


# ===================== ÁLGEBRA DE CONJUNTOS (MATERIAS) =====================

def materias_ofertadas():
    """CONJUNTO (set) global con la totalidad de materias inscritas por todos los estudiantes.

    Aplica la operación matemática de UNIÓN sobre los conjuntos individuales.
    """
    materias_globales = set()
    for estudiante in obtener_todos():
        # Operador |= realiza la unión in-place de conjuntos
        materias_globales |= estudiante.materias
    return materias_globales


def estudiantes_en_comun(id_a, id_b):
    """Calcula las materias compartidas entre dos estudiantes usando INTERSECCIÓN (&) de conjuntos.

    Retorna:
        tuple (bool, str, set):
            - bool: éxito de la operación.
            - str: mensaje explicativo.
            - set: conjunto de materias en común.
    """
    est_a = obtener_por_id(id_a)
    est_b = obtener_por_id(id_b)

    if not est_a:
        return False, f"No existe el primer estudiante con ID {id_a}.", set()
    if not est_b:
        return False, f"No existe el segundo estudiante con ID {id_b}.", set()

    materias_compartidas = est_a.materias_en_comun(est_b)
    total = len(materias_compartidas)

    mensaje = (
        f"{est_a.obtener_nombre_completo()} y {est_b.obtener_nombre_completo()} "
        f"comparten {total} materia(s)."
    )
    return True, mensaje, materias_compartidas


# ===================== ANALÍTICA Y ESTADÍSTICAS =====================

def estadisticas_estudiantes():
    """Calcula métricas consolidadas del rendimiento académico general."""
    estudiantes = obtener_todos()
    if not estudiantes:
        return {
            "total": 0,
            "promedio_global": 0.0,
            "materias_totales": [],
            "mejor_estudiante": None,
            "sin_notas": [],
        }

    promedios = [e.obtener_promedio() for e in estudiantes if e.obtener_promedio() > 0]
    promedio_global = round(sum(promedios) / len(promedios), 2) if promedios else 0.0

    mejor = max(estudiantes, key=lambda e: e.obtener_promedio(), default=None)
    sin_notas = [e.obtener_nombre_completo() for e in estudiantes if e.obtener_promedio() == 0]

    return {
        "total": len(estudiantes),
        "promedio_global": promedio_global,
        "materias_totales": sorted(materias_ofertadas()),
        "mejor_estudiante": mejor,
        "sin_notas": sin_notas,
    }
