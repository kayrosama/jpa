import os
import sys
import json
from utils.logger import log

CONFIG_ENDPOINT = "static/json/endpoints.json"
CONFIG_USER = "static/json/data_user.json"

def get_app_path() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def save_user_config(config: dict, path: str = CONFIG_USER):
    try:
        full_path = os.path.join(get_app_path(), path)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        log(f"Configuración de usuario guardada en {full_path}.")
    except Exception as e:
        log(f"Error al guardar configuración de usuario: {str(e)}")
        raise

def cargar_endpoints() -> list:
    path = os.path.join(get_app_path(), CONFIG_ENDPOINT)
    if os.path.exists(path):
        try:
            log(f"Cargando endpoints desde {path}.")
            with open(path, "r", encoding="utf-8") as f:
                endpoints = json.load(f)
            log(f"Endpoints cargados correctamente: {len(endpoints)} configuraciones encontradas.")
            return endpoints
        except Exception as e:
            log(f"Error al cargar endpoints desde {path}: {str(e)}")
            raise RuntimeError(f"Error al cargar endpoints: {e}")
    return []

def cargar_usuario() -> dict:
    path = os.path.join(get_app_path(), CONFIG_USER)
    if os.path.exists(path):
        try:
            log(f"Cargando usuario desde {path}.")
            with open(path, "r", encoding="utf-8") as vusr:
                data_user = json.load(vusr)
            log(f"Usuario cargado correctamente: {data_user.get('username', 'desconocido')}.")
            return data_user
        except Exception as e:
            log(f"Error al cargar data_user desde {path}: {str(e)}")
            raise RuntimeError(f"Error al cargar data_user: {e}")
    return {}
