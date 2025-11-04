import requests

def geocode_address(address):
    """
    Geocodifica una dirección utilizando la API de Nominatim de OpenStreetMap.
    :param address: Dirección a geocodificar (cadena de texto).
    :return: Una tupla (latitud, longitud) si se encuentra la dirección; de lo contrario, (None, None).
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,        # Dirección a buscar
        "format": "json",    # Formato de la respuesta (JSON)
        "addressdetails": 1, # Incluir detalles de la dirección
    }
    
    # Realizar la solicitud HTTP a la API
    try:
        response = requests.get(url, params=params, headers={"User-Agent": "django-app"})
        if response.status_code == 200:
            results = response.json()
            if results:
                # Extraer latitud y longitud del primer resultado
                location = results[0]
                return float(location["lat"]), float(location["lon"])
    except Exception as e:
        print(f"Error al geocodificar la dirección '{address}': {e}")
    
    return None, None
