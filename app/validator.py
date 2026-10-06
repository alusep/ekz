"""Окно валидации данных клиента."""
import tkinter as tk
from app.transfer_sim import get_full_name

# Переменные уровня модуля — чтобы работали колбэки кнопок
_data_var = None   # куда выводим ФИО
_result_var = None # куда выводим результат проверки


def _on_get():
    """Кнопка «Получить данные»: берём ФИО у API и показываем на форме."""
    data = get_full_name()
    _data_var.set(data)
    _result_var.set("")  # очищаем прошлый результат


def _on_test():
    """Кнопка «Отправить результат теста»: валидация ФИО на запрещённые символы."""
    from app.transfer_sim import validate_full_name

    data = _data_var.get()
    if not data:
        _result_var.set("Сначала нажмите «Получить данные»")
        return

    ok, msg = validate_full_name(data)
    _result_var.set(msg)


def run():
    """Запускает окно приложения."""
    global _data_var, _result_var

    root = tk.Tk()
    root.title("Валидация данных")
    root.geometry("520x200")
    root.resizable(False, False)

    _data_var = tk.StringVar()
    _result_var = tk.StringVar()

    # Левая колонка — кнопки
    btn_frame = tk.Frame(root)
    btn_frame.pack(side="left", padx=20, pady=20, anchor="n")

    tk.Button(btn_frame, text="Получить данные",
              width=22, command=_on_get).pack(pady=6)
    tk.Button(btn_frame, text="Отправить результат теста",
              width=22, command=_on_test).pack(pady=6)

    # Правая колонка — вывод ФИО и результата
    info_frame = tk.Frame(root)
    info_frame.pack(side="left", padx=10, pady=20, anchor="n")

    tk.Label(info_frame, textvariable=_data_var,
             font=("Arial", 12), anchor="w", justify="left",
             wraplength=260).pack(anchor="w", pady=(6, 20))
    tk.Label(info_frame, textvariable=_result_var,
             font=("Arial", 12), anchor="w", justify="left",
             wraplength=260).pack(anchor="w")

    root.mainloop()