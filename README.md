# Apuesta24/7

Simulador educativo de apuestas deportivas con moneda virtual.

El proyecto no integra pasarelas de pago reales, no convierte fichas a dinero y no representa una casa de apuestas real. Todo el flujo financiero usa fichas virtuales para practicar reglas de wallet, auditoria y juego responsable.

## Que cubre

- Registro de usuarios con KYC simulado.
- Wallet con contabilidad de partida doble.
- Eventos deportivos, mercados y cuotas decimales.
- Apuestas simples y combinadas.
- Validaciones de saldo, estado de cuenta y autoexclusion.
- Limites de deposito y controles de juego responsable.
- Auditoria inmutable por cadena de hashes.
- Reglas basicas antifraude.
- Panel de operador para revisar eventos y apuestas.

## Stack

- Python 3.11
- Django 5.x
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Django Channels
- Pytest

## Estructura principal

```txt
config/              Configuracion de Django, ASGI y Celery
api/                 Rutas generales de API
usuarios/            Registro, perfiles y KYC
billetera/           Wallet, ledger y movimientos de saldo
eventos/             Deportes, ligas, equipos y eventos
mercados/            Mercados y selecciones
cuotas/              Odds y recotizacion
apuestas_core/       Apuestas, liquidacion, combinadas y cash-out
juego_responsable/   Limites y autoexclusion
auditoria/           Cadena de auditoria
antifraude/          Alertas y reglas de riesgo
panel/               Vistas web del cliente y operador
templates/           HTML
static/              CSS, JS e imagenes
docs/                ADRs y notas del proyecto
```

## Instalacion local

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Si se trabaja con Docker, levantar primero PostgreSQL y Redis:

```bash
docker compose up -d
```

## Validacion

```bash
python manage.py check
pytest -q
```

Estado actual verificado:

- `python manage.py check`: sin errores.
- `pytest -q`: 13 pruebas pasando.

## Notas para commits

Conviene hacer commits pequenos y por tema. Un orden razonable para este reto:

1. Configurar lectura robusta de `DEBUG`.
2. Activar configuracion base de pytest.
3. Agregar pruebas de normalizacion decimal.
4. Cubrir validacion de partida doble.
5. Agregar pruebas de limites de monto de apuesta.
6. Validar montos positivos en operaciones de billetera.
7. Evitar operaciones de wallet sobre usuarios ajenos.
8. Corregir creacion de KYC cuando no existe verificacion previa.
9. Agregar pruebas de DNI y mayoria de edad.
10. Limpiar README y documentar alcance de moneda virtual.
