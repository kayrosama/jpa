import requests
from utils.logger import log
from utils.data_config import cargar_endpoints


class VerificadorReserva:
    def __init__(self):
        self.endpoints = cargar_endpoints()
        log("utils.verificador.VerificadorReserva - Endpoints cargados correctamente en VerificadorReserva.")

    def existe_reserva(self, token: str, workerid: int, fecha_verify: str) -> str:
        log("utils.verificador.VerificadorReserva - Ejecutando existe_reserva.")
        step_verify = next((ep for ep in self.endpoints if "getVerification" in ep), None)

        if not step_verify:
            log("utils.verificador.VerificadorReserva - No se encontró configuración para el paso Verification.")
            return ""

        if not token or not workerid:
            log("utils.verificador.VerificadorReserva - Token o workerId no disponible para verificación de reserva.")
            return ""

        url_get = step_verify["getVerification"][0]["url"].replace("{workerid}", str(workerid)).replace("{fecha}", fecha_verify)
        headers = {"token": token}

        try:
            response = requests.get(url_get, headers=headers, timeout=10)
            data = response.json()
            status = data.get("status")
            vcode = data.get("code")
            reply = data.get("reply", []) if status == "OK" else []

            log(f"Data completa: {data}")
            log(f"Status: {status}, Code: {vcode}, Reply: {reply}")

            # Validación combinada de status y code
            if status == "OK":
                if vcode == 10000:
                    if isinstance(reply, list) and len(reply) == 1:
                        registro = reply[0]
                        reservationid = registro.get("reservationid", "")
                        log(f"Reserva válida encontrada: {reservationid}")
                        return reservationid
                    else:
                        log("Reply vacío o con más de un registro para code 10000.")
                        return ""
                elif vcode == 40009:
                    log("Code 40009 detectado, devolviendo reservationid = 0.")
                    return "0"
                else:
                    log("Code distinto a 10000 y 40009, devolviendo vacío.")
                    return ""
            else:
                log(f"Status distinto de OK ({status}), devolviendo vacío.")
                return ""

        except Exception as e:
            log(f"Error al verificar reserva: {str(e)}")
            return ""

