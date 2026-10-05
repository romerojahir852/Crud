"""Módulo de Modelos del Dominio (models.py) para el Sistema de Estudiantes.

Este módulo implementa el concepto fundamental de POO y demuestra la aplicación
estratégica de las cuatro colecciones nativas de Python:
- list  : Secuencia mutable para almacenar el historial de calificaciones por materia.
- tuple : Estructura inmutable que define los campos obligatorios y retornos de métodos.
- set   : Conjunto sin duplicados para el control de materias inscritas y operaciones algebraicas (intersección).
- dict  : Estructura asociativa clave-valor que modela el kardex de materias y notas {'Materia': [calificaciones]}.
"""

import json

# TUPLA inmutable: define los atributos identificadores y obligatorios de un estudiante.
CAMPOS_ESTUDIANTE = ("nombre", "apellido", "email", "carnet")


class Estudiante:
    """MODELO: Entidad de dominio que representa a un estudiante universitario.

    Atributos:
        id (int): Identificador numérico primario único.
        nombre (str): Nombre(s) del estudiante.
        apellido (str): Apellido(s) del estudiante.
        email (str): Correo institucional o personal validado.
        carnet (str): Código alfanumérico único de matrícula (ej. 'EST2026001').
        notas (dict[str, list[float]]): Diccionario que asocia cada materia con su lista de notas.
        materias (set[str]): Conjunto matemático de materias cursadas por el estudiante.
    """

    def __init__(self, id_estudiante, nombre, apellido, email, carnet, notas=None, materias=None):
        self.id = id_estudiante
        self.nombre = nombre.strip().title()
        self.apellido = apellido.strip().title()
        self.email = email.strip().lower()
        self.carnet = carnet.strip().upper()

        # DICCIONARIO DE LISTAS: Mapeo de asignaturas a listas de calificaciones numéricas
        self.notas = notas if notas is not None else {}

        # CONJUNTO (set): Evita asignaturas repetidas y provee operaciones algebraicas rápidas
        self.materias = set(materias) if materias is not None else set()

        # Sincronización defensiva: si hay materias en las notas, asegurar que estén en materias
        for materia in self.notas.keys():
            self.materias.add(materia)

    def obtener_nombre_completo(self):
        """Retorna la representación formal completa del nombre y apellido."""
        return f"{self.nombre} {self.apellido}"

    def inscribir_materia(self, materia):
        """Inscribe una asignatura en el conjunto self.materias.

        Aprovecha la propiedad del set: si la materia ya existe, la inserción es idempotente.
        """
        nombre_materia = materia.strip().title()
        self.materias.add(nombre_materia)
        self.notas.setdefault(nombre_materia, [])
        return nombre_materia

    def agregar_nota(self, materia, nota):
        """Registra una calificación numérica en la asignatura indicada.

        Inscribe automáticamente la asignatura y añade el float a la lista de notas.
        """
        materia_normalizada = self.inscribir_materia(materia)
        self.notas[materia_normalizada].append(float(nota))

    def obtener_promedio_materia(self, materia):
        """Calcula la media aritmética de las notas de una asignatura específica."""
        materia_normalizada = materia.strip().title()
        calificaciones = self.notas.get(materia_normalizada, [])
        if not calificaciones:
            return 0.0
        return round(sum(calificaciones) / len(calificaciones), 2)

    def obtener_promedio(self):
        """Calcula el promedio general aritmético de todas las notas del estudiante."""
        todas = []
        for lista_notas in self.notas.values():
            todas.extend(lista_notas)
        if not todas:
            return 0.0
        return round(sum(todas) / len(todas), 2)

    def materias_en_comun(self, otro_estudiante):
        """Aplica la operación matemática de INTERSECCIÓN (&) entre dos conjuntos de materias.

        Costo computacional: O(min(len(A), len(B))) gracias a la tabla hash del set.
        """
        if not isinstance(otro_estudiante, Estudiante):
            return set()
        return self.materias & otro_estudiante.materias

    def a_diccionario(self):
        """Serializa el objeto a un diccionario nativo compatible con JSON.

        IMPORTANTE: JSON no soporta 'set'. Convertimos 'self.materias' a una 'list' ordenada.
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "carnet": self.carnet,
            "notas": self.notas,
            "materias": sorted(self.materias),  # set -> list para serialización JSON
        }

    @classmethod
    def desde_diccionario(cls, datos):
        """Patrón Factory: reconstruye la instancia y rehidrata la lista de materias a 'set'."""
        return cls(
            datos["id"],
            datos["nombre"],
            datos["apellido"],
            datos["email"],
            datos["carnet"],
            notas=datos.get("notas", {}),
            materias=set(datos.get("materias", [])),  # list -> set para restauración de dominio
        )

    def a_json(self):
        """Retorna la cadena serializada en formato JSON con soporte Unicode."""
        return json.dumps(self.a_diccionario(), ensure_ascii=False)

    def __str__(self):
        return f"[{self.carnet}] {self.obtener_nombre_completo()} - Materias: {len(self.materias)} | Promedio: {self.obtener_promedio()}"
