from datetime import date


def validar_mayoria_edad(fecha_nacimiento):
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )
    return edad >= 18


def validar_dni_basico(dni):
    if not dni:
        return False

    if not dni.isdigit():
        return False

    if len(dni) != 8:
        return False

    return True