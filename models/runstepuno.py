import requests
import random 
import datetime
import time 
from copy import deepcopy
from utils.data_config import cargar_endpoints , cargar_usuario, save_user_config
from utils.data_feriados import es_feriado_avanzado
from utils.verificador import VerificadorReserva
from utils.logger import log


class RunOne:
    def __init__(self):
        log("RunOne - Cargando de endpoints.")
        self.endpoints = cargar_endpoints()
        log("RunOne - Cargando datos de usuario.")
        self.data_user = cargar_usuario()
        

    def getLogin(self) -> dict:
        try:
            log("RunOne.getLogin - Ejecutando proceso para obtener token login.")
            step_login_entry = next((ep.get("getLogin") for ep in self.endpoints if "getLogin" in ep), None)
            if not step_login_entry:
                return {"status": "ERROR", "message": "RunOne.getLogin - No se encontro parametros para getLogin."}
            step_login = step_login_entry[0] 

            body = deepcopy(step_login["body"])
            body["username"] = self.data_user.get("username")
            body["password"] = self.data_user.get("password")
            body["business"] = self.data_user.get("business")

            url = step_login["url"]
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = requests.post(url, headers=headers, data=body, timeout=10)
            data = response.json()

            status = data.get("status")
            reply = data.get("reply", {}) if status == "OK" else {}

            self.data_user.update({
                "token_log": reply.get("token")
                })
            save_user_config(self.data_user)

            log(f"RunOne.getLogin - Respuesta getLogin: {data}")
            return {
                "status": status,
                "message": "RunOne.getLogin - Login exitoso." if status == "OK" else "RunOne.getLogin - Error en respuesta de login.",
                "token": reply.get("token"),
                "workerId": reply.get("workerId")
            }

        except Exception as e:
            log(f"RunOne.getLogin - Excepcion en getLogin: {str(e)}")
            return {"status": "ERROR", "message": f"RunOne.getLogin - Excepcion en getLogin: {str(e)}"}

    def getTrans(self) -> dict:
        try:
            log("RunOne.getTrans - Ejecutando proceso para obtener token transaction.")
            step_trans_entry = next((ep.get("getTransaction") for ep in self.endpoints if "getTransaction" in ep), None)
            if not step_trans_entry:
                return {"status": "ERROR", "message": "RunOne.getTrans - No se encontro configuracion para getTransaction."}
            step_trans = step_trans_entry[0] 
            
            token = self.data_user.get("token_log")
            if not token:
                log("RunOne.getTrans - Token no disponible, omitiendo gestion en getTrans.")
                return {"status": "ERROR", "message": "RunOne.getTrans - Token del paso 1 no disponible, omitiendo gestion en getTrans."}

            body = deepcopy(step_trans["body"])
            body["token"] = token
            url = step_trans["url"]
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            response = requests.post(url, headers=headers, data=body, timeout=10)
            data = response.json()

            status = data.get("status")
            reply = data.get("reply", {}) if status == "OK" else {}

            self.data_user.update({
                "token_trx": reply.get("token")
                })
            save_user_config(self.data_user)

            log(f"Respuesta getTrans: {data}")
            return {
                "status": status,
                "message": "RunOne.getTrans - Transaction Token obtenido correctamente." if status == "OK" else "RunOne.getTrans - Error en respuesta de transaction.",
                "token": reply.get("token"),
                "response": data
            }

        except Exception as e:
            log(f"RunOne.getTrans - Excepcion en getTrans: {str(e)}")
            return {"status": "ERROR", "message": f"RunOne.getTrans - Excepcion en getTrans: {str(e)}"}
