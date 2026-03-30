# En Ruta (Backend)

Backend SaaS multitenant para gestion de rutas y entregas con Django, DRF, PostGIS, Channels y Celery.

## Stack
- Django 5 + Django REST Framework
- PostgreSQL 18 + PostGIS
- Channels + Redis (WebSockets)
- Celery + Redis (tareas asincronas)
- JWT (djangorestframework-simplejwt)
- Storage: Cloudinary o AWS S3
- OpenRouteService para optimizacion de rutas

## Apps
- `apps.empresas`: modelo Empresa (tenant)
- `apps.usuarios`: modelo Usuario personalizado + autenticacion
- `apps.pedidos`: pedidos con PointField (PostGIS)
- `apps.rutas`: rutas y paradas
- `apps.tracking`: WebSocket consumers y tracking en Redis

## Respuesta estandar
Todas las respuestas usan:
```json
{ "status": "success|error", "data": {}, "message": "" }
```

## Autenticacion
- `POST /api/auth/register/` (crea empresa + admin)
- `POST /api/auth/login/` (JWT)
- `POST /api/auth/refresh/`
- `POST /api/auth/verify/`

## Endpoints principales
- `GET/POST /api/empresas/` (solo superuser)
- `GET /api/empresas/me/`
- `GET/POST /api/usuarios/` (admin)
- `GET/PATCH /api/usuarios/me/`
- `GET/POST /api/pedidos/` (admin crea)
- `GET/POST /api/rutas/` (admin crea)
- `POST /api/rutas/{id}/asignar_repartidor/`
- `POST /api/rutas/{id}/iniciar/`
- `POST /api/rutas/{id}/completar/`
- `POST /api/rutas/{id}/optimizar/`
- `GET/POST /api/paradas/`
- `GET /api/paradas/por_ruta/?ruta=<ruta_id>`
- `GET /api/tracking/` (admin)
- `GET /api/tracking/{repartidor_id}/`

WebSocket:
- `ws://<host>/ws/tracking/?token=<JWT>`

## Variables de entorno
Revisa `.env.example`.

## Ejecucion local
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Notas
- `AUTH_USER_MODEL = usuarios.Usuario`
- Multitenancy por FK `empresa` en todos los modelos.
- Tracking en Redis (no se persiste en BD).
