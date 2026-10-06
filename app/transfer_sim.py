"""Работа с API TransferSimulator."""
import requests

# URL API (интернет-версия; в лаборатории — http://192.168.1.200:4444/TransferSimulator/)
BASE_URL = "http://127.0.0.1:4444/TransferSimulator"

# Резервный пример из ТЗ, если API вернул пусто
FALLBACK_FULLNAME = "Ива&нов 1ван 1ванович!"

# делает GET-запрос на /fullName
def get_full_name() -> str:
    """Запрашивает ФИО клиента у TransferSimulator. Если пусто — возвращает демо-пример."""
    try:
        r = requests.get(f"{BASE_URL}/fullName", timeout=5)
        if r.status_code == 200:
            text = r.text.strip()
            if text:
                # API возвращает JSON вида {"value": "..."}
                try:
                    data = r.json()
                    return data.get("value", text)
                except Exception:
                    return text
    except Exception:
        pass
    return FALLBACK_FULLNAME

# Разрешённые символы: русские и латинские буквы, пробел, дефис
ALLOWED = set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
              "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
              "abcdefghijklmnopqrstuvwxyz"
              "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
              " -")


def validate_full_name(name: str) -> tuple[bool, str]:
    """Проверяет ФИО. Возвращает (ok, сообщение)."""
    bad = [c for c in name if c not in ALLOWED]
    if bad:
        return False, "ФИО содержит запрещенные символы: " + " ".join(sorted(set(bad)))
    return True, "ФИО корректно"