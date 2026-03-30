try:
    from .celery import app as celery_app
except Exception:  # pragma: no cover - permite ejecutar sin Celery instalado
    celery_app = None

__all__ = ("celery_app",)
