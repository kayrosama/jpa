from models.runstepuno import RunOne
from models.runstepdos import RunTwo
from utils.data_config import cargar_usuario
from utils.logger import log

def ejecutar_jobpoint():
    log("Inicio de ejecución diaria de JobPoint Automate.")

    try:
        data_user = cargar_usuario()
        log("Usuario cargado correctamente en main.")
        token_log = data_user.get("token_log")
        token_trx = data_user.get("token_trx")
    except Exception as e:
        log(f"Error al cargar usuario: {e}")
        return

    if not token_log or not token_trx:
        log("Tokens no encontrados. Intentando actualizar tokens.")
        try:
            IchiBan = RunOne()

            login = IchiBan.getLogin()
            if login["status"] != "OK":
                log("Login fallido. Proceso abortado.")
                return
            else:
                log("Login exitoso.")

            trans = IchiBan.getTrans()
            if trans["status"] != "OK":
                log("Transacción fallida. Proceso abortado.")
                return
            else:
                log("Transacción exitosa.")
        except Exception as e:
            log(f"Error inesperado en RunOne: {e}")
            return

    try:
        NiBan = RunTwo()
    except Exception as e:
        log(f"Error al inicializar RunTwo: {e}")
        return

    try:
        reserva = NiBan.getReserva()
        if reserva["status"] != "OK":
            log("Reserva fallida. Se continúa con el proceso de CheckIn.")
        else:
            log("Reserva completada correctamente.")
    except Exception as e:
        log(f"Error inesperado en getReserva: {e}")

    try:
        checkin = NiBan.getCheckIn()
        if checkin["status"] != "OK":
            log(f"CheckIn fallido.")
        else:
            log("CheckIn completado correctamente.")
    except Exception as e:
        log(f"Error inesperado en getCheckIn: {e}")

    log("Ejecución diaria completada.")

if __name__ == "__main__":
    ejecutar_jobpoint()

