import json
import datetime
from utils.logger import log

def es_feriado_avanzado(fecha: datetime.date, modo: str) -> bool:
    año = fecha.year
    log(f"Verificando si la fecha {fecha} es feriado para el modo '{modo}'.")

    try:
        with open("static/json/feriados.json", "r", encoding="utf-8") as f:
            feriados_data = json.load(f)
        log("Datos de feriados cargados correctamente desde feriados.json.")
    except Exception as e:
        log(f"Error al cargar feriados.json: {str(e)}")
        return False

    feriados_fijos = {
        datetime.date(año, item["mes"], item["dia"])
        for item in feriados_data.get("feriados_fijos", [])
    }

    trasladables = [
        (item["mes"], item["dia"])
        for item in feriados_data.get("feriados_trasladables", [])
    ]

    traslados = {}
    feriados_efectivos = set(feriados_fijos)

    for mes, dia in trasladables:
        original = datetime.date(año, mes, dia)
        dsem = original.weekday()
        if dsem in [1, 2]:  # martes o miércoles
            traslado = original - datetime.timedelta(days=(dsem + 1))
            traslados[original] = traslado
            feriados_efectivos.add(traslado)
            log(f"Feriado trasladable {original} movido a {traslado}.")
        else:
            traslados[original] = original
            feriados_efectivos.add(original)
            log(f"Feriado trasladable {original} no trasladado.")

    if modo == "reserva":
        for original, traslado in traslados.items():
            if fecha == original and traslado != original:
                log(f"{fecha} fue trasladado, se permite reserva.")
                return False
            if fecha == original and traslado == original:
                log(f"{fecha} no fue trasladado, no se permite reserva.")
                return True
        resultado = fecha in feriados_fijos
        log(f"{fecha} {'es' if resultado else 'no es'} feriado fijo para reserva.")
        return resultado

    elif modo == "checkin":
        resultado = fecha in feriados_fijos or fecha in traslados.values()
        log(f"{fecha} {'es' if resultado else 'no es'} feriado para checkin.")
        return resultado

    log(f"Modo '{modo}' no reconocido. Retornando False.")
    return False
    