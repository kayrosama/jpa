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
            log("utils.verificador.VerificadorReserva - No se encontro configuracion para el paso Verification.")
            return ""

        if not token or not workerid:
            log("utils.verificador.VerificadorReserva - Token o workerId no disponible para verificacion de reserva.")
            return ""

        url_get = step_verify["getVerification"][0]["url"].replace("{workerid}", str(workerid)).replace("{fecha}", fecha_verify)
        headers = {"token": token}

        try:
            response = requests.get(url_get, headers=headers, timeout=10)
            data = response.json()
            status = data.get("status")
            reply = data.get("reply", []) if status == "OK" else []
            
            if status == "OK" and isinstance(reply, list) and len(reply) <= 1:
                if len(reply) == 1:
                    registro = reply[0]
                    reservationid = registro.get("reservationid", "")
                    checkoutdate = registro.get("checkoutdate")
                    
                    # Validar que reservationid sea numérico y checkoutdate sea None
                    if reservationid.isdigit() and (checkoutdate is None or checkoutdate == ""):
                        log(f"utils.verificador.VerificadorReserva - Reserva válida encontrada: {reservationid}")
                        return reservationid
                    else:
                        log(f"utils.verificador.VerificadorReserva - Reserva inválida. Datos: {registro}")
                        return ""
                else:
                    # reply vacío
                    log("utils.verificador.VerificadorReserva - No se encontró reserva.")
                    return ""
            else:
                log(f"utils.verificador.VerificadorReserva - Respuesta inválida o más de un registro. Respuesta GET: {data}")
                return ""
        except Exception as e:
            log(f"utils.verificador.VerificadorReserva - Error al verificar reserva: {str(e)}")
            return ""

