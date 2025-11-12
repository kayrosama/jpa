import requests
from utils.logger import log
from utils.data_config import cargar_endpoints


class VerificadorReserva:
    def __init__(self):
        self.endpoints = cargar_endpoints()
        log("Endpoints cargados correctamente en VerificadorReserva.")

    def existe_reserva(self, token: str, workerid: int, fecha_verify: str) -> str:
        log("Ejecutando existe_reserva.")
        step_verify = next((ep for ep in self.endpoints if ep.get("step") == "Verification"), None)

        if not step_verify:
            log("No se encontró configuración para el paso Verification.")
            return ""

        if not token or not workerid:
            log("Token o workerId no disponible para verificación de reserva.")
            return ""

        url_get = step_verify["url"].replace("{workerid}", str(workerid)).replace("{fecha}", fecha_verify)
        headers = {"token": token}

        try:
            response = requests.get(url_get, headers=headers, timeout=10)
            data = response.json()
            status = data.get("status")
            reply = data.get("reply", []) if status == "OK" else []

            if status == "OK" and isinstance(reply, list) and reply:
                reservationid = reply[0].get("reservationid", "")
                log(f"Reserva encontrada: {reservationid}")
                return reservationid
            else:
                log(f"No se encontró reserva. Respuesta GET: {data}")
                return ""
        except Exception as e:
            log(f"Error al verificar reserva: {str(e)}")
            return ""
