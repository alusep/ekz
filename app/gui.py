"""Tkinter GUI: окно входа с капчей-пазлом + панель администратора."""
import random
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageTk
from app import auth

CAPTCHA_DIR = Path(__file__).parent / "static" / "captcha"
PIECES = ["1.png", "2.png", "3.png", "4.png"]
CELL = 110  # размер одной плитки


# ─────────────────── Окно входа ───────────────────
class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Вход в систему")
        self.root.geometry("360x620")
        self.root.resizable(False, False)

        self.order = PIECES[:]
        self.sel = None
        self.images = {}
        self._load_images()
        self._build()
        self._shuffle()

    def _load_images(self):
        """Загружаем 4 картинки и масштабируем под размер плитки."""
        for name in PIECES:
            img = Image.open(CAPTCHA_DIR / name).resize((CELL, CELL), Image.LANCZOS)
            self.images[name] = ImageTk.PhotoImage(img)

    def _build(self):
        tk.Label(self.root, text="Вход в систему",
                 font=("Arial", 18, "bold")).pack(pady=(25, 15))

        tk.Label(self.root, text="Логин", anchor="w").pack(fill="x", padx=40)
        self.username = tk.Entry(self.root, font=("Arial", 12))
        self.username.pack(fill="x", padx=40, pady=(0, 10))

        tk.Label(self.root, text="Пароль", anchor="w").pack(fill="x", padx=40)
        self.password = tk.Entry(self.root, font=("Arial", 12), show="*")
        self.password.pack(fill="x", padx=40, pady=(0, 15))

        tk.Label(self.root, text="Соберите картинку (клик по 2 фрагментам)",
                 font=("Arial", 10), fg="#555").pack()

        self.captcha_frame = tk.Frame(self.root)
        self.captcha_frame.pack(pady=10)

        self.piece_labels = []
        for i in range(4):
            r, c = divmod(i, 2)
            lbl = tk.Label(self.captcha_frame, borderwidth=2,
                           relief="flat", cursor="hand2")
            lbl.grid(row=r, column=c, padx=1, pady=1)
            lbl.bind("<Button-1>", lambda e, idx=i: self._click(idx))
            self.piece_labels.append(lbl)

        tk.Button(self.root, text="Обновить капчу",
                  command=self._shuffle).pack(pady=(5, 5))

        tk.Button(self.root, text="Войти", font=("Arial", 12, "bold"),
                  bg="#2a5298", fg="white",
                  command=self._login).pack(pady=10, ipadx=50, ipady=5)

        self.msg = tk.Label(self.root, text="", font=("Arial", 10),
                            wraplength=320, justify="center")
        self.msg.pack(pady=5)

    def _shuffle(self):
        """Перемешиваем порядок и гарантируем, что он не равен правильному."""
        self.order = PIECES[:]
        while self.order == PIECES:
            random.shuffle(self.order)
        self.sel = None
        self._draw()

    def _draw(self):
        """Перерисовываем плитки по текущему порядку."""
        for i, name in enumerate(self.order):
            self.piece_labels[i].config(
                image=self.images[name],
                relief="solid" if self.sel == i else "flat"
            )

    def _click(self, i):
        """Клик по плитке: первый — выделить, второй — обменять."""
        if self.sel is None:
            self.sel = i
            self._draw()
            return
        if self.sel == i:
            self.sel = None
            self._draw()
            return
        self.order[self.sel], self.order[i] = self.order[i], self.order[self.sel]
        self.sel = None
        self._draw()

    def _login(self):
        u = self.username.get().strip()
        p = self.password.get()

        if not u or not p:
            self._show("Заполните логин и пароль", "red")
            return

        if self.order != PIECES:
            self._show("Капча не пройдена", "red")
            self._shuffle()
            return

        user, err = auth.login(u, p)
        if err == "blocked":
            self._show("Вы заблокированы. Обратитесь к администратору", "red")
            return
        if err:
            self._show("Вы ввели неверный логин или пароль. "
                       "Пожалуйста проверьте ещё раз введенные данные", "red")
            self._shuffle()
            return

        self._show("Вы успешно авторизовались", "green")
        token = auth.make_token(user)
        self.root.after(700, lambda: self._open_next(user, token))

    def _show(self, text, color):
        self.msg.config(text=text, fg=color)

    def _open_next(self, user, token):
        self.root.destroy()
        if user.role == "admin":
            AdminWindow(token).root.mainloop()
        else:
            messagebox.showinfo("Профиль", f"Вы вошли как {user.username}")
            LoginWindow().root.mainloop()


# ─────────────────── Окно администратора ───────────────────
class AdminWindow:
    def __init__(self, token):
        self.token = token
        self.root = tk.Tk()
        self.root.title("Панель администратора")
        self.root.geometry("720x460")

        tk.Label(self.root, text="Панель администратора",
                 font=("Arial", 16, "bold")).pack(pady=15)

        # Форма добавления
        form = tk.Frame(self.root)
        form.pack(pady=5)
        tk.Label(form, text="Логин:").grid(row=0, column=0, padx=3)
        self.new_u = tk.Entry(form, width=15)
        self.new_u.grid(row=0, column=1)
        tk.Label(form, text="Пароль:").grid(row=0, column=2, padx=3)
        self.new_p = tk.Entry(form, width=15, show="*")
        self.new_p.grid(row=0, column=3)
        tk.Button(form, text="Добавить", bg="#2a5298", fg="white",
                  command=self._add).grid(row=0, column=4, padx=8)

        self.msg = tk.Label(self.root, text="", fg="#2a5298")
        self.msg.pack(pady=5)

        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self._refresh()

    def _refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        headers = ["Логин", "Роль", "Статус", "Действие"]
        for c, h in enumerate(headers):
            tk.Label(self.list_frame, text=h, font=("Arial", 10, "bold"),
                     bg="#f5f6fa", padx=10, pady=6, anchor="w"
                     ).grid(row=0, column=c, sticky="ew")
            self.list_frame.grid_columnconfigure(c, weight=1)

        for r, u in enumerate(auth.users.values(), start=1):
            tk.Label(self.list_frame, text=u.username, anchor="w",
                     padx=10, pady=5).grid(row=r, column=0, sticky="ew")
            tk.Label(self.list_frame, text=u.role, anchor="w",
                     padx=10, pady=5).grid(row=r, column=1, sticky="ew")
            tk.Label(self.list_frame,
                     text="Заблокирован" if u.blocked else "Активен",
                     fg="red" if u.blocked else "green",
                     anchor="w", padx=10, pady=5).grid(row=r, column=2, sticky="ew")

            btn_text = "Разблокировать" if u.blocked else "Блокировать"
            btn_color = "#1dd1a1" if u.blocked else "#c0392b"
            tk.Button(self.list_frame, text=btn_text,
                      bg=btn_color, fg="white", padx=8,
                      command=lambda n=u.username, b=u.blocked: self._toggle(n, not b)
                      ).grid(row=r, column=3, padx=5, pady=3)

    def _add(self):
        u = self.new_u.get().strip()
        p = self.new_p.get()
        if not u or not p:
            self.msg.config(text="Заполните поля", fg="red")
            return
        ok, text = auth.add_user(u, p)
        self.msg.config(text=text, fg="#2a5298" if ok else "red")
        if ok:
            self.new_u.delete(0, "end")
            self.new_p.delete(0, "end")
            self._refresh()

    def _toggle(self, name, blocked):
        auth.set_blocked(name, blocked)
        self._refresh()


# ─────────────────── Запуск ───────────────────
def run():
    LoginWindow().root.mainloop()


if __name__ == "__main__":
    run()