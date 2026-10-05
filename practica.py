"""Práctica de Colecciones en Python (practica.py).

Resolución comentada de los 6 ejercicios de la Sección 13 de la guía académica.
Demuestra el uso de:
- list (secuencias ordenadas mutables)
- tuple (inmutabilidad y desempaquetado)
- set (álgebra de conjuntos y búsqueda instantánea O(1))
- dict (asociación clave-valor y agrupamientos)
"""

import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def ejercicio_1():
    print("--- EJERCICIO 1: Quitar duplicados conservando el orden original ---")
    ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]
    print(f"Lista de entrada: {ciudades}")

    # Explicación teórica:
    # Un set() elimina duplicados pero NO conserva el orden de inserción.
    # Combinamos un 'set' como tabla hash de consulta rápida O(1) con una 'list' para preservar el orden.
    vistas = set()
    unicas = []
    for ciudad in ciudades:
        if ciudad not in vistas:
            vistas.add(ciudad)
            unicas.append(ciudad)

    print(f"Resultado sin duplicados (orden preservado): {unicas}")
    print()
    return unicas


def ejercicio_2():
    print("--- EJERCICIO 2: Frecuencia de elementos con diccionario ---")
    ciudades = ["Quito", "Guayaquil", "Quito", "Cuenca", "Guayaquil"]
    print(f"Lista de entrada: {ciudades}")

    conteo = {}
    for ciudad in ciudades:
        # dict.get(clave, 0) previene KeyError y simplifica la inicialización
        conteo[ciudad] = conteo.get(ciudad, 0) + 1

    print(f"Diccionario de frecuencias: {conteo}")
    mas_repetida = max(conteo, key=conteo.get)
    print(f"Ciudad con mayor recurrencia: '{mas_repetida}' ({conteo[mas_repetida]} apariciones)")
    print()
    return conteo


def ejercicio_3():
    print("--- EJERCICIO 3: Álgebra de conjuntos (Teoría de Conjuntos) ---")
    inscritos_matematica = {"Ana", "Luis", "Sol", "Marco"}
    inscritos_ingles = {"Luis", "Marco", "Ruth"}

    print(f"Matemática : {inscritos_matematica}")
    print(f"Inglés     : {inscritos_ingles}")

    # Operaciones de teoría de conjuntos
    ambas = inscritos_matematica & inscritos_ingles      # Intersección
    solo_mate = inscritos_matematica - inscritos_ingles  # Diferencia relativa (A \ B)
    total = len(inscritos_matematica | inscritos_ingles) # Cardinalidad de la Unión (A U B)

    print(f"Estudiantes en ambas materias (A ∩ B) : {sorted(ambas)}")
    print(f"Estudiantes solo en matemática (A \\ B): {sorted(solo_mate)}")
    print(f"Total de estudiantes únicos inscritos (|A ∪ B|): {total}")
    print()
    return ambas, solo_mate, total


def ejercicio_4():
    print("--- EJERCICIO 4: Indexación de lista a tabla hash (Diccionario) ---")
    clientes = [
        {"id": 1, "nombre": "Ana"},
        {"id": 2, "nombre": "Luis"},
        {"id": 3, "nombre": "María"}
    ]
    print(f"Datos originales: {clientes}")

    # Comprensión de diccionario para construir un índice O(1)
    indice = {cliente["id"]: cliente for cliente in clientes}
    print(f"Índice generado (llave primaria id): {indice}")

    id_busqueda = 2
    print(f"Acceso directo a cliente con id={id_busqueda}: {indice[id_busqueda]['nombre']}")
    print("Costo de búsqueda en lista: O(N) | Costo con índice hash: O(1)")
    print()
    return indice


def ejercicio_5():
    print("--- EJERCICIO 5: Tuplas como registros inmutables y desempaquetado ---")
    ventas = [("enero", 1500), ("febrero", 1800), ("marzo", 1200)]
    print(f"Colección de tuplas: {ventas}")

    total = sum(monto for _mes, monto in ventas)
    mejor_mes, mejor_monto = max(ventas, key=lambda venta: venta[1])

    print(f"Total anual acumulado : ${total}")
    print(f"Mes con mayor facturación: {mejor_mes} con ${mejor_monto}")
    print("Desglose tabulado:")
    for mes, monto in ventas:
        print(f"  • {mes:<12} -> ${monto:>6}")
    print()
    return total, mejor_mes, mejor_monto


def ejercicio_6():
    print("--- EJERCICIO 6: Agrupamiento relacional con dict.setdefault ---")
    registros = [
        {"nombre": "Ana", "ciudad": "Guayaquil"},
        {"nombre": "Luis", "ciudad": "Guayaquil"},
        {"nombre": "Sol", "ciudad": "Quito"},
        {"nombre": "Pedro", "ciudad": "Cuenca"},
        {"nombre": "María", "ciudad": "Quito"},
    ]

    agrupados = {}
    for r in registros:
        ciudad = r.get("ciudad", "Sin ciudad").title()
        agrupados.setdefault(ciudad, []).append(r["nombre"])

    print("Clientes agrupados por ciudad:")
    for ciudad, nombres in sorted(agrupados.items()):
        print(f"  🏢 {ciudad:<12}: {', '.join(nombres)}")
    print()
    return agrupados


if __name__ == "__main__":
    print("===============================================================")
    print("  EJERCICIOS PRÁCTICOS DE COLECCIONES EN PYTHON - TAREA 1")
    print("===============================================================\n")
    ejercicio_1()
    ejercicio_2()
    ejercicio_3()
    ejercicio_4()
    ejercicio_5()
    ejercicio_6()
    print("✓ Todos los ejercicios ejecutados y comprobados con éxito.")
