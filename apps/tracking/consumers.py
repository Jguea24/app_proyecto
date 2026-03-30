from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework.exceptions import ValidationError

from .serializers import TrackingPayloadSerializer
from .services import set_location


class TrackingConsumer(AsyncJsonWebsocketConsumer):
    """Consumer WebSocket para enviar ubicacion en tiempo real."""

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated or user.rol != "REPARTIDOR":
            await self.close()
            return

        self.empresa_id = str(user.empresa_id)
        self.repartidor_id = str(user.id)
        self.group_name = f"tracking_empresa_{self.empresa_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        serializer = TrackingPayloadSerializer(data=content)
        if not serializer.is_valid():
            await self.send_json({"error": serializer.errors})
            return

        payload = serializer.validated_data
        data = {
            "repartidor_id": self.repartidor_id,
            "empresa_id": self.empresa_id,
            "latitud": payload["latitud"],
            "longitud": payload["longitud"],
            "timestamp": payload["timestamp"].isoformat(),
        }

        await sync_to_async(set_location)(self.empresa_id, self.repartidor_id, data)
        await self.channel_layer.group_send(self.group_name, {"type": "broadcast_tracking", "data": data})

    async def broadcast_tracking(self, event):
        await self.send_json(event["data"])
