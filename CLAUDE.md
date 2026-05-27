# CLAUDE.md

## Proyecto

Nombre visual del sistema:

Apuesta24/7

Sistema web de apuestas deportivas con fichas virtuales, usuarios, billetera, eventos, mercados, cuotas, apuestas, auditoría, juego responsable y panel administrativo.

## Modo de trabajo

Trabaja de forma autónoma.

No pidas permiso para cambios normales si el cambio es necesario para completar la tarea del usuario.

Puedes modificar cualquier archivo del proyecto cuando sea necesario, incluyendo:

- templates/
- static/
- usuarios/
- panel/
- billetera/
- apuestas_core/
- eventos/
- mercados/
- cuotas/
- auditoria/
- juego_responsable/
- antifraude/
- tiempo_real/
- api/
- config/

Antes de tocar lógica crítica, revisa el contexto del proyecto y mantén la arquitectura existente.

## Regla principal

No rompas funcionalidades existentes.

Mantén funcionando:

- login cliente
- login admin
- registro
- redirección por roles
- eventos
- billetera
- mis apuestas
- creación de apuestas
- liquidación ganada/perdida/anulada
- auditoría
- juego responsable
- panel admin
- APIs DRF

## Identidad visual

Usar el nombre:

Apuesta24/7

Estilo visual:

- deportivo
- moderno
- profesional
- oscuro elegante
- naranja, rojo, azul oscuro y negro grafito
- verde para éxito
- rojo solo para errores
- cards modernas
- bordes redondeados
- sombras suaves
- responsive

## Roles del sistema

Usar estos roles:

- Cliente
- Administrador
- Operador
- Superadmin

No usar:

- trabajador
- empleado

## Redirecciones

Mantener esta matriz:

| Escenario | Destino |
|---|---|
| Cliente login | /eventos/ |
| Admin/staff login | /admin/ |
| Registro exitoso | /eventos/ |
| Admin login page con cliente autenticado | /eventos/ |
| Admin login page con admin autenticado | /admin/ |
| Página protegida sin sesión | /login/ |

## Rutas principales

Mantener:

- /login/
- /registro/
- /admin/login/
- /
- /eventos/
- /billetera/
- /mis-apuestas/
- /admin/
- /api/

## Billetera

La página Billetera sirve para administrar fichas virtuales.

Debe tener:

- saldo disponible
- botón Cargar fichas
- botón Retirar fichas
- ver movimientos
- límites de juego responsable
- estado de cuenta

No debe tener:

- botón Apostar ahora
- cuotas
- eventos deportivos
- formulario de apuesta

Flujo correcto:

Billetera = cargar fichas  
Eventos = apostar  
Mis apuestas = historial

## Modal de carga de fichas

En Billetera, el botón “Cargar fichas” debe abrir un modal.

El modal debe tener:

- Yape
- Plin
- monto
- código promocional opcional
- botón APLICAR
- botón GENERAR QR
- QR visual
- botón Simular recarga exitosa

Yape, Plin y QR son solo flujo visual del sistema.  
No conectar con servicios externos.

Endpoint interno para cargar fichas:

POST /api/billetera/operaciones/recargar/

JSON:

{
  "usuario_id": 1,
  "amount": "100.0000",
  "idempotency_key": "recarga-web-" + Date.now()
}

Usar CSRF token correctamente.

## Eventos

La página Eventos sí permite apostar.

Debe tener:

- evento deportivo
- mercado 1X2
- cuotas
- monto a apostar
- botón Apostar ahora

Endpoint para crear apuesta:

POST /api/apuestas/operaciones/crear_simple/

JSON:

{
  "usuario_id": 1,
  "odd_id": 1,
  "stake": "10.0000",
  "idempotency_key": "apuesta-web-" + Date.now(),
  "ip_origen": "127.0.0.1"
}

Usar CSRF token correctamente.

## Mis apuestas

La página Mis apuestas solo muestra historial.

Debe mostrar:

- apuestas activas
- ganadas
- perdidas
- anuladas
- estado accepted / won / lost / void
- pago potencial
- fecha
- selección
- evento

## Login cliente

Debe mantener:

- diseño deportivo
- portada visual
- acceso cliente
- registro
- recuperación visual si existe
- redirección a /eventos/

## Login admin

Debe mantener:

- diseño profesional
- portada visual para operador/admin
- acceso administrador
- redirección a /admin/

## Panel admin

Mantener Django admin funcional.

El admin debe poder:

- gestionar usuarios
- revisar KYC
- gestionar eventos
- gestionar mercados
- cambiar cuotas
- liquidar apuestas
- revisar billetera
- revisar auditoría
- revisar juego responsable
- revisar antifraude

## Backend

Puedes modificar backend si es necesario, pero con cuidado.

Cuando toques backend crítico:

- usar Decimal, nunca float
- usar transaction.atomic
- usar select_for_update en movimientos financieros
- respetar idempotency_key
- no romper serializers
- no romper endpoints existentes
- mantener tests si existen

## Wallet

Toda operación debe mantener partida doble:

- débito
- crédito
- balance

Saldo se calcula por movimientos, no debe guardarse manualmente.

## Apuestas

Flujo:

1. Usuario selecciona cuota
2. Ingresa monto
3. Sistema valida saldo, cuenta y restricciones
4. Bloquea fondos
5. Crea apuesta accepted
6. Admin/sistema liquida como won/lost/void

## Auditoría

Mantener auditoría para:

- creación de apuesta
- liquidación
- movimiento de wallet
- cambio de cuota

## Textos que se deben evitar como principales

Evitar usar en títulos grandes:

- recarga simulada
- retiro simulado
- dinero real
- depósito real
- retiro real

Usar mejor:

- cargar fichas
- retirar fichas
- saldo disponible
- fichas virtuales
- FV

## Footer obligatorio

Mantener en footer, pequeño y discreto:

“Plataforma educativa con moneda virtual. No constituye una casa de apuestas.”

No quitar este texto porque forma parte del enunciado del reto.

## Forma de respuesta

Cuando realices cambios, responde con:

1. Archivos modificados
2. Qué cambiaste
3. Cómo probar
4. Comandos sugeridos

## Comandos de validación

Después de cambios importantes:

```powershell
docker compose exec web python manage.py check