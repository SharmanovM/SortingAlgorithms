"""Модуль главного меню приложения."""

import customtkinter as ctk


def create_menu_screen(parent, on_screen1, on_screen2, on_screen3):
    """Создает фрейм главного меню с заголовком и кнопками перехода к заданиям."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    # Конфигурация сетки: строки 0 и 3 служат отступами для центрирования
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_rowconfigure(1, weight=0)
    frame.grid_rowconfigure(2, weight=0)
    frame.grid_rowconfigure(3, weight=1)

    frame.grid_columnconfigure((0, 1, 2), weight=1)

    # Заголовок раздела
    title_label = ctk.CTkLabel(
        frame,
        text="Алгоритмы сортировки",
        font=("Arial", 36, "bold")
    )
    title_label.grid(row=1, column=0, columnspan=3, pady=(0, 40))

    # Кнопка перехода к Заданию 1
    btn1 = ctk.CTkButton(
        frame,
        text="Алгоритмы внутренней сортировки\nСортировка пузырьком (BubbleSort)\nСортировка выбором (SelectionSort)\nБыстрая сортировка (QuickSort)\nПирамидальная сортировка (HeapSort)",
        command=on_screen1,
        height=80,
        font=("Arial", 16, "bold"),
        fg_color="#FF7373",
        hover_color="#3A3A3A"
    )
    btn1.grid(row=2, column=0, padx=15, sticky="ew")

    # Кнопка перехода к Заданию 2
    btn2 = ctk.CTkButton(
        frame,
        text="Алгоритмы внешней сортировки",
        command=on_screen2,
        height=80,
        font=("Arial", 16, "bold"),
        fg_color="#66BB6A",
        hover_color="#3A3A3A"
    )
    btn2.grid(row=2, column=1, padx=15, sticky="ew")

    # Кнопка перехода к Заданию 3
    btn3 = ctk.CTkButton(
        frame,
        text="Алгоритмы сортировки слов",
        command=on_screen3,
        height=80,
        font=("Arial", 16, "bold"),
        fg_color="#64B5F6",
        hover_color="#3A3A3A"
    )
    btn3.grid(row=2, column=2, padx=15, sticky="ew")

    return frame
