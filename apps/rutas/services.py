import json

import requests
from django.conf import settings


def optimize_route(coordinates):
    """Solicita optimizacion de ruta a OpenRouteService."""

    api_key = getattr(settings, "ORS_API_KEY", None)
    if not api_key:
        raise RuntimeError("ORS_API_KEY no configurada.")

    url = "https://api.openrouteservice.org/v2/optimization"  # noqa: S105
    payload = {
        "jobs": [
            {
                "id": idx + 1,
                "location": [coord[1], coord[0]],
            }
            for idx, coord in enumerate(coordinates)
        ],
        "vehicles": [
            {
                "id": 1,
                "profile": "driving-car",
                "start": [coordinates[0][1], coordinates[0][0]] if coordinates else [0, 0],
            }
        ],
    }

    headers = {"Authorization": api_key, "Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
