"""Módulo de utilidades para consola y validaciones en proyecto_estudiantes.

Proporciona soporte ANSI, limpieza de pantalla, validación de correo y mensajes con estilo.
"""

import os
import sys

# Soporte de caracteres UTF-8 en terminales de Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.system("")

# DICCIONARIO: códigos ANSI asociados a colores semánticos
COLORES = {
    "ROJO": "\033[91m",
    "VERDE": "\033[92m",
    "AZUL": "\033[94m",
    "AMARILLO": "\033[93m",
    "CYAN": "\033[96m",
    "MORADO": "\033[95m",
    "BLANCO": "\033[97m",
    "RESET": "\033[0m",
}

# TUPLA inmutable de respuestas afirmativas
RESPUESTAS_SI = ("si", "sí", "s", "yes", "y")


def limpiar_pantalla():
    """Limpia la pantalla de forma multiplataforma."""
    os.system("cls" if os.name == "nt" else "clear")


def imprimir_color(texto, color):
    """Imprime texto con el color correspondiente y restablece el estilo estándar."""
    codigo = COLORES.get(color, COLORES["BLANCO"])
    print(f"{codigo}{texto}{COLORES['RESET']}")


def imprimir_titulo(texto):
    """Limpia la consola y presenta un encabezado estilizado."""
    limpiar_pantalla()
    imprimir_color("=" * 70, "AZUL")
    print(f"  {texto}".center(70))
    imprimir_color("=" * 70, "AZUL")
    print()


def imprimir_exito(mensaje):
    """Muestra un mensaje de éxito en verde."""
    imprimir_color(f"✓ {mensaje}", "VERDE")


def imprimir_error(mensaje):
    """Muestra un mensaje de error en rojo."""
    imprimir_color(f"✗ {mensaje}", "ROJO")


def imprimir_info(mensaje):
    """Muestra un mensaje informativo en cian."""
    imprimir_color(f"ℹ {mensaje}", "CYAN")


def imprimir_alerta(mensaje):
    """Muestra un mensaje de atención en amarillo."""
    imprimir_color(f"⚠ {mensaje}", "AMARILLO")


def confirmar(pregunta):
    """Solicita una confirmación binaria al usuario."""
    respuesta = input(f"{pregunta} (si/no): ").strip().lower()
    return respuesta in RESPUESTAS_SI


def es_email_valido(texto):
    """Verifica si una cadena posee formato de correo electrónico estándar."""
    texto = texto.strip()
    if texto.count("@") != 1:
        return False
    usuario, dominio = texto.split("@")
    return len(usuario) > 0 and "." in dominio and not dominio.endswith(".")
