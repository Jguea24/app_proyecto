# Notas de migracion

1. Este refactor crea nuevas apps bajo `apps/` y deja las apps anteriores fuera de `INSTALLED_APPS`.
2. Crea una base de datos nueva o limpia el esquema anterior antes de migrar.
3. Habilita PostGIS en tu base:
   - `CREATE EXTENSION IF NOT EXISTS postgis;`
4. Ejecuta:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
5. Carga variables de entorno desde `.env`.
6. Verifica Redis para Channels/Celery.
7. Instala GDAL/GEOS en Windows y configura GDAL_LIBRARY_PATH y GEOS_LIBRARY_PATH en .env.
