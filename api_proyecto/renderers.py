from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    """Envuelve todas las respuestas en un formato estandar."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None

        if isinstance(data, dict) and {"status", "data", "message"}.issubset(data.keys()):
            return super().render(data, accepted_media_type, renderer_context)

        status_code = getattr(response, "status_code", 200)

        if status_code >= 400:
            message = "Error"
            if isinstance(data, dict) and "detail" in data:
                message = str(data.get("detail"))
            payload = {"status": "error", "data": data, "message": message}
        else:
            payload = {"status": "success", "data": data, "message": ""}

        return super().render(payload, accepted_media_type, renderer_context)
