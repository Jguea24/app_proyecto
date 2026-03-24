from rest_framework import status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    details = response.data
    message = "Error en la solicitud."

    if isinstance(details, dict) and "detail" in details:
        message = str(details.get("detail"))
    elif response.status_code == status.HTTP_400_BAD_REQUEST:
        message = "Datos de entrada invalidos."
    elif response.status_code == status.HTTP_401_UNAUTHORIZED:
        message = "No autenticado."
    elif response.status_code == status.HTTP_403_FORBIDDEN:
        message = "No autorizado para ejecutar esta accion."
    elif response.status_code == status.HTTP_404_NOT_FOUND:
        message = "Recurso no encontrado."

    response.data = {
        "ok": False,
        "error": message,
        "details": details,
    }
    return response
