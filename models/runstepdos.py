import requests
import random 
import datetime
import time 
from copy import deepcopy
from utils.data_config import cargar_endpoints , cargar_usuario , save_user_config 
from utils.data_feriados import es_feriado_avanzado
from utils.verificador import VerificadorReserva
from utils.logger import log


class RunTwo:
    def __init__(self):
        log("RunTwo - Cargando de endpoints.")
        self.endpoints = cargar_endpoints()
        log("RunTwo - Cargando datos de usuario.")
        self.data_user = cargar_usuario()

    def getReserva(self) -> dict:
        log("RunTwo.getReserva - Mapeando datos a utilizar en el proceso.")
        token = self.data_user.get("token_trx")
        workerid = self.data_user.get("workerid")
        workplaceid = self.data_user.get("workplaceid")
        floorid = self.data_user.get("floorid")
        typeid = self.data_user.get("typeid")

        try:
            log("RunTwo.getReserva - Ejecutando proceso para obtener Reservation.")
            step_reserva = next((ep for ep in self.endpoints if "getReservation" in ep), None)
            if not step_reserva:
                return {"status": "ERROR", "message": "RunTwo.getReserva - No se encontro configuracion para getReservation."}

            if not token:
                log("RunTwo.getReserva - Token no disponible, omitiendo en getReserva.")
                return {"status": "ERROR", "message": "RunTwo.getReserva - Omitiendo en getReserva porque el token transaction no esta disponible."}

            fecha_objetivo = datetime.date.today() + datetime.timedelta(days=30)
            fecha_str = fecha_objetivo.strftime("%d-%m-%Y")
            log(f"RunTwo.getReserva - Fecha objetivo para reserva: {fecha_str}")

            # Validar si la fecha cae en fin de semana
            if fecha_objetivo.weekday() in [5, 6]:  # 5 = sábado, 6 = domingo
                log(f"RunTwo.getReserva - Omitiendo reserva porque la fecha {fecha_str} cae en fin de semana.")
                return {
                    "status": "OMITIDO",
                    "message": f"RunTwo.getReserva - Omitiendo reserva porque la fecha {fecha_str} cae en fin de semana."
                }

            # Validar si es feriado
            if es_feriado_avanzado(fecha_objetivo, "reserva"):
                log(f"RunTwo.getReserva - Omitiendo reserva porque la fecha {fecha_str} es feriado no trasladado.")
                return {
                    "status": "OMITIDO",
                    "message": f"RunTwo.getReserva - Omitiendo reserva porque la fecha {fecha_str} es feriado no trasladado."
                }

            # Verificar si ya existe una reserva para ese dia
            verificador = VerificadorReserva()
            reserva_existente = verificador.existe_reserva(token, workerid, fecha_str)

            if reserva_existente:
                log(f"RunTwo.getReserva - Ya existe una reserva para el trabajador {workerid} el dia {fecha_str}. ID: {reserva_existente}")
                return {
                    "status": "OMITIDO",
                    "message": f"RunTwo.getReserva - Omitiendo reserva porque ya existe una reserva para la fecha {fecha_str}.",
                    "reservationid": reserva_existente
                }

            # Preparar body para la reserva
            body = deepcopy(step_reserva["body"])
            body = deepcopy(step_reserva["getReservation"][0]["body"])
            body.update({
                "startdate": f"{fecha_str} 07:00:00",
                "enddate": f"{fecha_str} 19:00:00",
                "workerid": workerid,
                "workplaceid": workplaceid,
                "floorid": floorid,
                "typeId": typeid
            })

            log(f"RunTwo.getReserva - Datos para reserva: {body}")

            url = step_reserva["url"]
            headers = {"Content-Type": "application/x-www-form-urlencoded", "token": token}

            response = requests.post(url, headers=headers, data=body, timeout=10)
            data = response.json()

            status = data.get("status")
            reply = data.get("reply", {}) if status == "OK" else {}

            reservation_id = reply.get("reservationid", "")
            if not reservation_id and isinstance(reply, list) and reply:
                reservation_id = reply[0].get("reservationid", "")

            log(f"RunTwo.getReserva - Respuesta getReserva: {data}")
            return {
                "status": status,
                "message": "RunTwo.getReserva - Reserva realizada con exito." if status == "OK" else "RunTwo.getReserva - Error en respuesta de reservation",
                "reservationid": reservation_id
            }

        except Exception as e:
            log(f"RunTwo.getReserva - Excepcion en getReserva: {str(e)}")
            return {"status": "ERROR", "message": f"RunTwo.getReserva - Excepcion en getReserva: {str(e)}"}

    def getCheckIn(self, usar_delay: bool = False, delay_segundos: int = 0) -> dict:
        token = self.data_user.get("token_trx")
        workerid = self.data_user.get("workerid")
        try:
            log("RunTwo.getCheckIn - Ejecutando proceso para hacer CheckIn.")

            step_verify = next((ep for ep in self.endpoints if "getVerification" in ep), None)
            if not step_verify:
                return {"status": "ERROR", "message": "No se encontro configuracion para getVerification."}

            step_checkin = next((ep for ep in self.endpoints if "getCheckIn" in ep), None)
            if not step_checkin:
                return {"status": "ERROR", "message": "No se encontro configuracion para getCheckIn."}
    
            if not token or not workerid:
                return {"status": "ERROR", "message": "Token o workerId no disponible."}
    
            hoy = datetime.date.today()
            if es_feriado_avanzado(hoy, "checkin"):
                return {"status": "OMITIDO", "message": f"Omitiendo CheckIn porque la fecha {hoy.strftime('%d-%m-%Y')} es feriado efectivo."}

            fecha_str = hoy.strftime("%d-%m-%Y")
            url_get = step_verify["getVerification"][0]["url"].replace("{workerid}", str(workerid)).replace("{fecha}", fecha_str)
            headers = {"token": token}
    
            response = requests.get(url_get, headers=headers, timeout=10)
            data = response.json()
    
            status = data.get("status")
            reply = data.get("reply", []) if status == "OK" else []
    
            if status == "OK" and isinstance(reply, list) and reply:
                reservationid = reply[0].get("reservationid", "")
                delay_segundos = random.randint(15, 180)
    
                if usar_delay:
                    log(f"Usando delay de {delay_segundos} segundos antes de hacer CheckIn.")
                    time.sleep(delay_segundos)
    
                url_put = step_checkin["getCheckIn"][0]["url"].replace("{reservationid}", str(reservationid))
    
                # Intentar hasta 3 veces si status != OK o hay error de conexión
                intentos = 0
                data_put = {}
                while intentos < 3:
                    try:
                        response_put = requests.put(url_put, headers=headers, timeout=10)
                        data_put = response_put.json()
                        log(f"Intento {intentos+1} - Respuesta PUT: {data_put}")
    
                        if data_put.get("status") == "OK":
                            break  # Éxito, salir del bucle
                    except requests.exceptions.RequestException as e:
                        log(f"Error de conexión en intento {intentos+1}: {str(e)}")
    
                    intentos += 1
                    if intentos < 3:
                        log("Reintentando en 60 segundos...")
                        time.sleep(60)
    
                return {
                    "status": data_put.get("status", "ERROR"),
                    "message": "CheckIn realizado con exito." if data_put.get("status") == "OK" else "Error en CheckIn",
                    "response": data_put
                }
            else:
                return {"status": "ERROR", "message": "No se encontro reserva para hoy.", "response": data}
    
        except Exception as e:
            log(f"Excepcion en getCheckIn: {str(e)}")
            return {"status": "ERROR", "message": f"Excepcion en getCheckIn: {str(e)}"}
            
