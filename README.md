# Apuesta24/7 - Sistema de Apuestas Deportivas

Proyecto web desarrollado con **Django**, **Django REST Framework**, **PostgreSQL**, **Redis**, **Celery** y **Django Channels**.

El sistema simula una plataforma de apuestas deportivas usando **moneda virtual**, 

> Plataforma con moneda virtual.

---

## Objetivo del proyecto

Construir un simulador de apuestas deportivas con enfoque en:

- Registro de usuarios y KYC simulado.
- Wallet con contabilidad de partida doble.
- Eventos deportivos y mercados de apuestas.
- Cuotas en formato decimal europeo.
- Apuestas simples y combinadas.
- Controles de juego responsable.
- Auditoría inmutable.
- Reglas básicas antifraude.
- Dashboard del operador.
- Vista de auditoria en el panel interno para revisar registros y verificaciones.

---

## Stack tecnológico

- Python 3.11
- Django 5.x
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Django Channels
- Docker
- Pytest
- Hypothesis

---

## Arquitectura del proyecto

```txt
apuestas/
│
├── config/                 # Configuración principal de Django
├── api/                    # Rutas generales de API
├── usuarios/               # Usuarios, perfiles y KYC
├── billetera/              # Wallet y contabilidad de partida doble
├── eventos/                # Eventos deportivos
├── mercados/               # Mercados de apuestas
├── cuotas/                 # Odds y recotización
├── apuestas_core/          # Apuestas, liquidación, cash-out y combinadas
├── juego_responsable/      # Límites y autoexclusión
├── auditoria/              # Auditoría inmutable
├── antifraude/             # Alertas y reglas antifraude
├── panel/                  # Dashboard operador
├── tiempo_real/            # WebSockets con Django Channels
├── utilidades/             # Helpers generales
├── docs/                   # ADRs, bocetos y documentación
├── templates/              # Templates HTML
└── static/                 # Archivos estáticos
