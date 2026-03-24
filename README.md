# PYMES - En Ruta (Backend)

Backend SaaS para gestion de rutas y entregas con Django REST Framework, JWT y PostgreSQL.

## Stack
- Python 3.12
- Django 6
- Django REST Framework
- PostgreSQL
- SimpleJWT

## Apps
- `users`: autenticacion, registro, usuarios y roles (`ADMIN`, `DRIVER`).
- `routes`: rutas y puntos de entrega.
- `deliveries`: evidencias de entrega (`DeliveryProof`) con soporte offline.
- `tracking`: ubicaciones en tiempo real e historial con soporte offline.

## Autenticacion
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`

Compatibilidad SimpleJWT:
- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `POST /api/auth/token/verify/`

### Payload de registro
```json
{
  "email": "driver@empresa.com",
  "first_name": "Dina",
  "last_name": "Tanguila",
  "address": "Quito",
  "birth_date": "2001-06-13",
  "password": "Driver1234!",
  "confirm_password": "Driver1234!"
}
```

Campo opcional `photo`:
- Envia `photo` con `multipart/form-data` para subir foto de perfil.

## Endpoints principales
- `GET/POST /api/users/` (admin)
- `GET/PATCH /api/users/me/`
- `GET/POST /api/routes/`
- `POST /api/routes/{id}/assign_driver/` (admin)
- `POST /api/routes/{id}/start/`
- `POST /api/routes/{id}/complete/`
- `GET /api/routes/{id}/delivery_points/`
- `GET/POST /api/delivery-points/`
- `GET /api/delivery-points/by_route/?route=<route_id>`
- `POST /api/delivery-points/{id}/update_status/`
- `GET/POST /api/delivery-proofs/`
- `POST /api/delivery-proofs/{id}/upload_evidence/`
- `POST /api/delivery-proofs/{id}/change_status/`
- `GET/POST /api/tracking/`

## Soporte offline
`DeliveryProof` y `Tracking` aceptan:
- `offline_id` (id unico del dispositivo para idempotencia)
- `synced_from_offline`
- `device_recorded_at`

Si reenvias un `offline_id` ya registrado, el API devuelve el registro existente (`200`) en lugar de crear duplicado.

## Permisos
- `ADMIN`: acceso total.
- `DRIVER`: acceso solo a sus rutas, puntos, evidencias y tracking.

## Variables de entorno
Usa `.env.example` como base.

Base de datos:
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

JWT:
- `JWT_ACCESS_MINUTES`
- `JWT_REFRESH_DAYS`

## Ejecucion local
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Notas
- `AUTH_USER_MODEL = users.User`.
- API protegida por JWT por defecto (`REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`).
