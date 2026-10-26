# firmware/net/http_client.py
import ujson
import urequests

def send_measurement(url: str, token: str, payload: dict) -> bool:
    """Envía el paquete de medición al endpoint de ingesta de FastAPI."""
    headers = {
        "Content-Type": "application/json",
        "X-Device-Token": token
    }
    
    data_str = ujson.dumps(payload)
    response = None
    try:
        response = urequests.post(url, data=data_str, headers=headers)
        if response.status_code == 201:
            print(f"[HTTP] Ingesta exitosa (201 Created). Packet ID: {payload.get('packet_id')}")
            return True
        elif response.status_code == 409:
            print(f"[HTTP] Paquete duplicado omitido (409 Conflict). Packet ID: {payload.get('packet_id')}")
            return True
        else:
            print(f"[HTTP] Error en ingesta ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[HTTP] Excepción al comunicar con el backend: {e}")
        return False
    finally:
        if response:
            response.close()
