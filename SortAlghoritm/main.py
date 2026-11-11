"""Главный модуль приложения для демонстрации алгоритмов сортировки."""

import customtkinter as ctk

from screens.menu_screen import create_menu_screen
from screens.screen1_internal import create_screen1
from screens.screen2_external import create_screen2
from screens.screen3_words import create_screen3

# Конфигурация главного окна
app = ctk.CTk()
app.title("SortAlghoritm")
app.geometry("1080x720")

app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)


# Навигация между экранами
def show_screen(target_frame):
    """Скрывает все зарегистрированные экраны и отображает переданный."""
    for frame in screens:
        frame.grid_remove()
    target_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=40)


# Инициализация экранов приложения
screens = []

menu_screen = create_menu_screen(
    app,
    on_screen1=lambda: show_screen(screen1),
    on_screen2=lambda: show_screen(screen2),
    on_screen3=lambda: show_screen(screen3)
)
screen1 = create_screen1(app, on_back=lambda: show_screen(menu_screen))
screen2 = create_screen2(app, on_back=lambda: show_screen(menu_screen))
screen3 = create_screen3(app, on_back=lambda: show_screen(menu_screen))

screens.extend([menu_screen, screen1, screen2, screen3])

# Отображение стартового экрана
show_screen(menu_screen)
app.mainloop()
