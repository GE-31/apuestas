from datetime import date, timedelta

from usuarios.validators import validar_dni_basico, validar_mayoria_edad


def test_validar_dni_basico_acepta_ocho_digitos():
    assert validar_dni_basico("12345678") is True


def test_validar_dni_basico_rechaza_texto_y_longitud_incorrecta():
    assert validar_dni_basico("1234abcd") is False
    assert validar_dni_basico("1234567") is False


def test_validar_mayoria_edad_acepta_usuario_mayor_de_edad():
    fecha_nacimiento = date.today().replace(year=date.today().year - 18)

    assert validar_mayoria_edad(fecha_nacimiento) is True


def test_validar_mayoria_edad_rechaza_menor_de_edad():
    fecha_nacimiento = date.today() - timedelta(days=(18 * 365) - 2)

    assert validar_mayoria_edad(fecha_nacimiento) is False
