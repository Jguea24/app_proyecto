import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ParadaRuta, Ruta

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Ruta)
def notify_route_assignment(sender, instance, created, **kwargs):
    if created:
        logger.info("Ruta creada: %s", instance.id)
    if instance.estado == Ruta.Estado.ASIGNADA:
        logger.info("Ruta asignada: %s", instance.id)


@receiver(post_save, sender=ParadaRuta)
def notify_parada_update(sender, instance, created, **kwargs):
    if created:
        logger.info("Parada creada: %s", instance.id)
    if instance.estado == ParadaRuta.Estado.ENTREGADO:
        logger.info("Parada entregada: %s", instance.id)
