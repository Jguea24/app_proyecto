from django.core.cache import cache


def _location_key(empresa_id, repartidor_id):
    return f"tracking:{empresa_id}:{repartidor_id}"


def _drivers_key(empresa_id):
    return f"tracking:{empresa_id}:drivers"


def set_location(empresa_id, repartidor_id, payload):
    key = _location_key(empresa_id, repartidor_id)
    cache.set(key, payload, timeout=60 * 60)

    drivers_key = _drivers_key(empresa_id)
    drivers = cache.get(drivers_key, [])
    if repartidor_id not in drivers:
        drivers.append(repartidor_id)
        cache.set(drivers_key, drivers, timeout=60 * 60)


def get_location(empresa_id, repartidor_id):
    return cache.get(_location_key(empresa_id, repartidor_id))


def list_locations(empresa_id):
    drivers = cache.get(_drivers_key(empresa_id), [])
    results = []
    for driver_id in drivers:
        location = cache.get(_location_key(empresa_id, driver_id))
        if location:
            results.append(location)
    return results
