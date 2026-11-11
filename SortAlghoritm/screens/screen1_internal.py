"""Модуль экрана первого практического задания: алгоритмы внутренней сортировки."""

import math
import random
import customtkinter as ctk


def create_screen1(parent, on_back):
    """Создает фрейм для визуализации алгоритмов внутренней сортировки."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    # Конфигурация сетки основного экрана
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_rowconfigure(2, weight=0)

    # ==========================================
    # 1. СОСТОЯНИЕ ДАННЫХ (STATE)
    # ==========================================
    current_data = {
        "list_len": 15,
        "numbers": [random.randint(1, 99) for _ in range(15)],
        "initial_numbers": [],
        "step": 0,
        "delay_ms": 200,
        "is_running": False,
        "log_full_array": []
    }
    current_data["initial_numbers"] = list(current_data["numbers"])

    log_current_array = ["Лог:\n"]
    log = "".join(log_current_array)

    # ==========================================
    # 2. АЛГОРИТМЫ И ГЕНЕРАЦИЯ ЛОГОВ
    # ==========================================
    def generate_bubble_sort_log(numbers):
        """Прогоняет пузырьковую сортировку и собирает список всех шагов."""
        steps = []
        nums = list(numbers)
        n = len(nums)
        step_num = 1

        for i in range(n - 1, 0, -1):
            flag = False
            for j in range(i):
                a, b = nums[j], nums[j + 1]
                if a > b:
                    nums[j], nums[j + 1] = nums[j + 1], nums[j]
                    flag = True
                    steps.append({
                        "log_line": f"Шаг {step_num}: {a} > {b} ➔ обмен\n",
                        "explanation": f"Сравниваем {a} и {b}. Так как {a} > {b}, меняем их местами!",
                        "nums": list(nums),
                        "indices": (j, j + 1),
                        "action": "swap"
                    })
                else:
                    steps.append({
                        "log_line": f"Шаг {step_num}: {a} <= {b} ➔ на месте\n",
                        "explanation": f"Сравниваем {a} и {b}. Порядок верный, оставляем как есть.",
                        "nums": list(nums),
                        "indices": (j, j + 1),
                        "action": "compare"
                    })
                step_num += 1

            if not flag:
                steps.append({
                    "log_line": "За проход обменов нет. Готово!\n",
                    "explanation": "За полный проход не было ни одного обмена. Массив полностью отсортирован!",
                    "nums": list(nums),
                    "indices": (),
                    "action": "done"
                })
                break

        return steps

    def generate_selection_sort_log(numbers):
        """Прогоняет сортировку выбором и собирает список всех шагов."""
        steps = []
        nums = list(numbers)
        n = len(nums)
        step_num = 1

        for i in range(n - 1):
            min_idx = i
            # Поиск минимального элемента в оставшейся неотсортированной части массива
            for j in range(i + 1, n):
                a, b = nums[j], nums[min_idx]
                if a < b:
                    steps.append({
                        "log_line": f"Шаг {step_num}: {a} < {b} ➔ новый минимум (поз. {j})\n",
                        "explanation": f"Сравниваем элемент {a} (поз. {j}) с текущим минимумом {b} (поз. {min_idx}). Нашли меньший элемент! Запоминаем его позицию.",
                        "nums": list(nums),
                        "indices": (j, min_idx),
                        "action": "compare"
                    })
                    min_idx = j
                else:
                    steps.append({
                        "log_line": f"Шаг {step_num}: {a} >= {b} ➔ минимум прежний (поз. {min_idx})\n",
                        "explanation": f"Сравниваем элемент {a} (поз. {j}) с текущим минимумом {b} (поз. {min_idx}). Он не меньше, минимум остаётся прежним.",
                        "nums": list(nums),
                        "indices": (j, min_idx),
                        "action": "compare"
                    })
                step_num += 1

            # Перемещение найденного минимума на начало неотсортированной зоны
            if min_idx != i:
                old_val = nums[i]
                min_val = nums[min_idx]
                nums[i], nums[min_idx] = nums[min_idx], nums[i]
                steps.append({
                    "log_line": f"Шаг {step_num}: обмен {min_val} и {old_val} ➔ ставим минимум на поз. {i}\n",
                    "explanation": f"Ставим найденный минимум {min_val} на первую неотсортированную позицию {i}, меняя его с {old_val}!",
                    "nums": list(nums),
                    "indices": (i, min_idx),
                    "action": "swap"
                })
                step_num += 1
            else:
                steps.append({
                    "log_line": f"Шаг {step_num}: минимум {nums[i]} уже на позиции {i} ➔ без обмена\n",
                    "explanation": f"Минимальный элемент неотсортированной части {nums[i]} уже находится на нужной позиции {i}. Перестановка не требуется.",
                    "nums": list(nums),
                    "indices": (i, i),
                    "action": "compare"
                })
                step_num += 1

        # Финальный шаг для фиксации завершения сортировки массива
        steps.append({
            "log_line": "Сортировка выбором завершена. Готово!\n",
            "explanation": "Все элементы поочередно расставлены на свои места. Массив полностью отсортирован!",
            "nums": list(nums),
            "indices": (),
            "action": "done"
        })

        return steps

    def generate_quick_sort_log(numbers):
        """Прогоняет быструю сортировку Хоара и собирает список всех шагов."""
        steps = []
        nums = list(numbers)
        step_num = 1

        def quick_sort(low, high):
            nonlocal step_num
            # Базовый случай рекурсии: отрезок из одного элемента или пустой
            if low >= high:
                return

            # Выбор опорного элемента по центру отрезка (стратегия разделения Хоара)
            mid = (low + high) // 2
            pivot = nums[mid]

            steps.append({
                "log_line": f"Шаг {step_num}: отрезок [{low}..{high}], опорный {pivot} (поз. {mid})\n",
                "explanation": f"Выбираем опорный элемент {pivot} на позиции {mid} для подмассива с индексами от {low} до {high}.",
                "nums": list(nums),
                "indices": (low, high),
                "action": "compare"
            })
            step_num += 1

            i = low
            j = high

            # Встречное движение указателей и разделение массива относительно pivot
            while i <= j:
                # Поиск слева элемента, который больше либо равен pivot
                while nums[i] < pivot:
                    steps.append({
                        "log_line": f"Шаг {step_num}: {nums[i]} < {pivot} (опорный) ➔ верно, идём вправо\n",
                        "explanation": f"Сравниваем {nums[i]} (поз. {i}) с опорным {pivot}. Элемент меньше опорного, оставляем слева.",
                        "nums": list(nums),
                        "indices": (i, mid),
                        "action": "compare"
                    })
                    step_num += 1
                    i += 1

                # Поиск справа элемента, который меньше либо равен pivot
                while nums[j] > pivot:
                    steps.append({
                        "log_line": f"Шаг {step_num}: {nums[j]} > {pivot} (опорный) ➔ верно, идём влево\n",
                        "explanation": f"Сравниваем {nums[j]} (поз. {j}) с опорным {pivot}. Элемент больше опорного, оставляем справа.",
                        "nums": list(nums),
                        "indices": (j, mid),
                        "action": "compare"
                    })
                    step_num += 1
                    j -= 1

                # Обмен элементов, оказавшихся не в своих половинах массива
                if i <= j:
                    if i < j:
                        a, b = nums[i], nums[j]
                        nums[i], nums[j] = nums[j], nums[i]
                        # Сохраняем актуальный индекс опорного элемента при перемещении
                        if mid == i:
                            mid = j
                        elif mid == j:
                            mid = i
                        steps.append({
                            "log_line": f"Шаг {step_num}: обмен {a} и {b} ➔ позиции {i} и {j}\n",
                            "explanation": f"Меняем местами {a} на позиции {i} и {b} на позиции {j}, чтобы меньшие оказались слева, а большие справа.",
                            "nums": list(nums),
                            "indices": (i, j),
                            "action": "swap"
                        })
                        step_num += 1
                    i += 1
                    j -= 1

            # Рекурсивная обработка левой и правой сформированных частей
            if low < j:
                quick_sort(low, j)
            if i < high:
                quick_sort(i, high)

        if len(nums) > 1:
            quick_sort(0, len(nums) - 1)

        # Финальный шаг фиксации завершения быстрой сортировки
        steps.append({
            "log_line": "Быстрая сортировка завершена. Готово!\n",
            "explanation": "Все подмассивы разделены и отсортированы. Массив полностью упорядочен!",
            "nums": list(nums),
            "indices": (),
            "action": "done"
        })

        return steps

    def generate_heap_sort_log(numbers):
        """Прогоняет пирамидальную сортировку (HeapSort) и собирает список всех шагов."""
        steps = []
        nums = list(numbers)
        n = len(nums)
        step_num = 1

        def sift_down(root, size):
            nonlocal step_num
            # Просеивание элемента вниз для поддержания свойства max-heap (родитель >= потомков)
            while True:
                left = 2 * root + 1
                right = 2 * root + 2
                largest = root

                # Проверка левого потомка на превосходство над текущим максимумом
                if left < size:
                    if nums[left] > nums[largest]:
                        steps.append({
                            "log_line": f"Шаг {step_num}: потомок {nums[left]} > {nums[largest]} ➔ претендент на обмен\n",
                            "explanation": f"Сравниваем левого потомка {nums[left]} (поз. {left}) с текущим максимумом {nums[largest]} (поз. {largest}). Потомок больше!",
                            "nums": list(nums),
                            "indices": (left, largest),
                            "action": "compare"
                        })
                        largest = left
                    else:
                        steps.append({
                            "log_line": f"Шаг {step_num}: потомок {nums[left]} <= {nums[largest]} ➔ порядок соблюден\n",
                            "explanation": f"Левый потомок {nums[left]} (поз. {left}) не превосходит {nums[largest]} (поз. {largest}). Порядок верен.",
                            "nums": list(nums),
                            "indices": (left, largest),
                            "action": "compare"
                        })
                    step_num += 1

                # Проверка правого потомка на превосходство над текущим максимумом
                if right < size:
                    if nums[right] > nums[largest]:
                        steps.append({
                            "log_line": f"Шаг {step_num}: потомок {nums[right]} > {nums[largest]} ➔ новый претендент на обмен\n",
                            "explanation": f"Сравниваем правого потомка {nums[right]} (поз. {right}) с {nums[largest]} (поз. {largest}). Правый потомок оказался еще больше!",
                            "nums": list(nums),
                            "indices": (right, largest),
                            "action": "compare"
                        })
                        largest = right
                    else:
                        steps.append({
                            "log_line": f"Шаг {step_num}: потомок {nums[right]} <= {nums[largest]} ➔ порядок соблюден\n",
                            "explanation": f"Правый потомок {nums[right]} (поз. {right}) не превосходит {nums[largest]} (поз. {largest}). Порядок верен.",
                            "nums": list(nums),
                            "indices": (right, largest),
                            "action": "compare"
                        })
                    step_num += 1

                # Если наибольший среди потомков превосходит корень, выполняем обмен и продолжаем спуск
                if largest != root:
                    a, b = nums[root], nums[largest]
                    nums[root], nums[largest] = nums[largest], nums[root]
                    steps.append({
                        "log_line": f"Шаг {step_num}: обмен {a} и {b} ➔ просеивание вниз\n",
                        "explanation": f"Меняем родителя {a} (поз. {root}) с большим потомком {b} (поз. {largest}), восстанавливая свойства кучи.",
                        "nums": list(nums),
                        "indices": (root, largest),
                        "action": "swap"
                    })
                    step_num += 1
                    root = largest
                else:
                    break

        if n > 1:
            steps.append({
                "log_line": f"Шаг {step_num}: Фаза 1 ➔ построение пирамиды\n",
                "explanation": "Начинаем построение двоичной кучи (пирамиды), просеивая элементы снизу вверх.",
                "nums": list(nums),
                "indices": (),
                "action": "compare"
            })
            step_num += 1

            # Фаза 1: построение кучи снизу вверх, начиная с первого нелистового узла
            for i in range(n // 2 - 1, -1, -1):
                sift_down(i, n)

            steps.append({
                "log_line": f"Шаг {step_num}: Фаза 2 ➔ извлечение максимума и сортировка\n",
                "explanation": "Куча сформирована: в вершине максимальный элемент. Начинаем переносить максимумы в конец массива.",
                "nums": list(nums),
                "indices": (),
                "action": "compare"
            })
            step_num += 1

            # Фаза 2: перемещение текущего максимума из корня в отсортированный конец
            for end in range(n - 1, 0, -1):
                a, b = nums[0], nums[end]
                nums[0], nums[end] = nums[end], nums[0]
                steps.append({
                    "log_line": f"Шаг {step_num}: обмен вершины {a} и элемента {b} ➔ максимум на позицию {end}\n",
                    "explanation": f"Переносим максимальный элемент {a} из вершины кучи на его итоговое место {end}.",
                    "nums": list(nums),
                    "indices": (0, end),
                    "action": "swap"
                })
                step_num += 1
                sift_down(0, end)

        # Финальный шаг фиксации завершения пирамидальной сортировки
        steps.append({
            "log_line": "Пирамидальная сортировка завершена. Готово!\n",
            "explanation": "Все элементы из кучи извлечены и заняли правильные места по возрастанию!",
            "nums": list(nums),
            "indices": (),
            "action": "done"
        })

        return steps

    def on_select_algorithm(value):
        """Выбирает алгоритм, сбрасывает массив, очищает холст и пересчитывает логи."""
        # Остановка автовоспроизведения при смене алгоритма
        if current_data["is_running"]:
            toggle_play()

        # Отмена активной анимации перемещения пузырьков
        nonlocal anim_job_id, is_animating
        if anim_job_id is not None:
            frame.after_cancel(anim_job_id)
            anim_job_id = None
        is_animating = False

        # Полный сброс прогресса и возврат массива к исходным значениям
        current_data["step"] = 0
        current_data["numbers"] = list(current_data["initial_numbers"])

        # Расчет списка шагов для выбранного пользователем алгоритма
        if value == "BubbleSort":
            current_data["log_full_array"] = generate_bubble_sort_log(current_data["numbers"])
        elif value == "SelectionSort":
            current_data["log_full_array"] = generate_selection_sort_log(current_data["numbers"])
        elif value == "QuickSort":
            current_data["log_full_array"] = generate_quick_sort_log(current_data["numbers"])
        elif value == "HeapSort":
            current_data["log_full_array"] = generate_heap_sort_log(current_data["numbers"])

        # Очистка лога шагов на экране
        log_current_array.clear()
        log_current_array.append("Лог:\n")
        update_log_display()

        # Обновление текстовых меток состояния
        step_label.configure(text=f"Шаг: {current_data['step']}")
        explanation_label.configure(text=f"Выбран алгоритм: {value}. Исходное состояние.")

        # Отрисовка начального состояния в соответствующем виде (шарики или столбики)
        if value == "BubbleSort":
            bubble_render()
        else:
            sort_render()

    # ==========================================
    # 3. ОСНОВНЫЕ ФРЕЙМЫ ИНТЕРФЕЙСА
    # ==========================================
    # Верхняя панель
    top_frame = ctk.CTkFrame(frame, fg_color="transparent")
    top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

    # Центральная область
    content_frame = ctk.CTkFrame(frame, fg_color="transparent")
    content_frame.grid(row=1, column=0, sticky="nsew")
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_rowconfigure(1, weight=0)

    canvas_container = ctk.CTkFrame(content_frame, fg_color="transparent")
    canvas_container.grid(row=0, column=0, sticky="nsew")
    canvas_container.grid_columnconfigure(0, weight=1)
    canvas_container.grid_columnconfigure(1, weight=3)
    canvas_container.grid_rowconfigure(0, weight=1)

    info_container = ctk.CTkFrame(content_frame, fg_color="transparent")
    info_container.grid(row=1, column=0, sticky="ew", pady=(10, 0))
    info_container.grid_columnconfigure(0, weight=1)
    info_container.grid_columnconfigure(1, weight=2)
    info_container.grid_columnconfigure(2, weight=1)

    # Нижняя панель
    bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
    bottom_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
    bottom_frame.grid_columnconfigure(0, weight=0)
    bottom_frame.grid_columnconfigure(1, weight=1)
    bottom_frame.grid_columnconfigure(2, weight=0)
    bottom_frame.grid_columnconfigure(3, weight=1)
    bottom_frame.grid_columnconfigure(4, weight=0)

    # ==========================================
    # 4. ВИДЖЕТЫ ВЕРХНЕЙ ПАНЕЛИ
    # ==========================================
    btn_back = ctk.CTkButton(
        top_frame,
        command=on_back,
        text="← Назад",
        height=40,
        width=80,
        font=("Arial", 12, "bold"),
        fg_color="#4A4A4A",
        hover_color="#3A3A3A"
    )
    btn_back.grid(row=0, column=0, padx=(0, 20), pady=5)

    algo_selector = ctk.CTkSegmentedButton(
        top_frame,
        values=["BubbleSort", "SelectionSort", "QuickSort", "HeapSort"],
        command=on_select_algorithm,
        height=40,
        font=("Arial", 12, "bold")
    )
    algo_selector.set("BubbleSort")
    algo_selector.grid(row=0, column=1, padx=10, pady=5)

    # ==========================================
    # 5. ВИДЖЕТЫ ЦЕНТРАЛЬНОЙ ОБЛАСТИ (ХОЛСТ И ЛОГИ)
    # ==========================================
    log_textbox = ctk.CTkTextbox(
        canvas_container,
        font=("Arial", 23),
        text_color="#1E293B",
        fg_color="transparent",
        activate_scrollbars=True
    )
    log_textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    canvas = ctk.CTkCanvas(canvas_container, width=1750, height=700, bg="#FFFFFF", highlightthickness=0)
    canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
    # Интерактивное перемещение холста зажатой мышью
    canvas.bind("<ButtonPress-1>", lambda event: canvas.scan_mark(event.x, event.y) if not is_animating else None)
    canvas.bind("<B1-Motion>", lambda event: canvas.scan_dragto(event.x, event.y, gain=1) if not is_animating else None)
    canvas.bind("<Configure>", lambda event: bubble_render() if algo_selector.get() == "BubbleSort" else sort_render())
    canvas.zoom_level = 1.0
    def zoom(event):
        if is_animating:
            return

        if event.delta:
            direction = event.delta
        else:
            direction = 1 if event.num == 4 else -1

        scale_factor = 1.1 if direction > 0 else 0.9

        new_zoom = canvas.zoom_level * scale_factor
        if 0.1 <= new_zoom <= 5.0:
            canvas.zoom_level = new_zoom

            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)
            canvas.scale("all", x, y, scale_factor, scale_factor)
    # Привязываем прокрутку колесика мыши
    canvas.bind("<MouseWheel>", zoom)  # Для Windows и macOS
    canvas.bind("<Button-4>", zoom)  # Для Linux (прокрутка вверх)
    canvas.bind("<Button-5>", zoom)  # Для Linux (прокрутка вниз)

    step_label = ctk.CTkLabel(
        info_container,
        text=f"Шаг: {current_data['step']}",
        font=("Arial", 22, "bold")
    )
    step_label.grid(row=0, column=0, sticky="w", padx=(10, 0), pady=5)

    explanation = "Нажмите «▶ Старт» для начала визуализации"
    explanation_label = ctk.CTkLabel(
        info_container,
        text=f"{explanation}",
        font=("Arial", 22),
        text_color="#4338CA"
    )
    explanation_label.grid(row=0, column=1, sticky="nsew", pady=5)

    def update_log_display():
        """Обновляет текст лога на экране и прокручивает к последней строке."""
        log_textbox.configure(state="normal")
        log_textbox.delete("1.0", "end")
        log_textbox.insert("1.0", "".join(log_current_array))
        log_textbox.see("end")
        log_textbox.configure(state="disabled")

    update_log_display()

    # Уникальная визуализация пузырька
    babbles = []
    is_animating = False
    anim_job_id = None

    def set_bubble_style(b_item, state):
        """Переключает цветовую палитру шарика в стиле Apple Liquid Glass."""
        oval_tag = b_item["oval_tag"]
        palettes = {
            "idle": ("#0A84FF", "#60A5FA", "#38BDF8", "#BAE6FD"),
            "compare": ("#FF9500", "#FCD34D", "#FBBF24", "#FEF3C7"),
            "swap": ("#FF3B30", "#FCA5A5", "#F87171", "#FEE2E2"),
            "done": ("#34C759", "#86EFAC", "#4ADE80", "#DCFCE7")
        }
        body, border, lens, crest = palettes.get(state, palettes["idle"])
        canvas.itemconfigure(oval_tag, fill=body, outline=border)
        canvas.itemconfigure(f"{oval_tag}_lens", fill=lens)
        canvas.itemconfigure(f"{oval_tag}_crest", fill=crest)

    def bubble_render():
        """Отрисовывает шарики на холсте с динамическим радиусом."""
        canvas.delete("all")
        babbles.clear()
        canvas.zoom_level = 1.0

        # Центрирование по вертикали
        canvas_height = canvas.winfo_height()
        if canvas_height < 50:
            canvas_height = 400
        y_center = canvas_height // 2

        # формула расстояния и радиусов для исключения наложения
        r_min = 22
        r_max = 44
        gap = 48
        slot_width = 2 * r_max + gap
        start_x = r_max + 40

        nums = current_data["numbers"]
        min_val = min(nums) if nums else 1
        max_val = max(nums) if nums else 100
        val_range = max_val - min_val if max_val != min_val else 1

        for index, num in enumerate(nums):
            # Расчет радиуса по формуле нормализации
            r = int(r_min + ((num - min_val) / val_range) * (r_max - r_min))
            x_center = start_x + index * slot_width

            x1 = x_center - r
            y1 = y_center - r
            x2 = x_center + r
            y2 = y_center + r

            tag_name = f"bubble_{index}"
            oval_tag = f"oval_{index}"
            babbles.append({
                "point": (x1, y1, x2, y2),
                "r": r,
                "x_center": x_center,
                "tag": tag_name,
                "oval_tag": oval_tag
            })

            # 1. Мягкая диффузная тень
            canvas.create_oval(
                x_center - r * 0.75, y_center + r * 0.78,
                x_center + r * 0.75, y_center + r * 1.08,
                fill="#F1F5F9", outline="",
                tags=(tag_name,)
            )
            canvas.create_oval(
                x_center - r * 0.55, y_center + r * 0.82,
                x_center + r * 0.55, y_center + r * 1.02,
                fill="#E2E8F0", outline="",
                tags=(tag_name,)
            )

            # 2. Основная сфера
            canvas.create_oval(
                x1, y1, x2, y2,
                fill="#0A84FF",
                outline="#60A5FA",
                width=1,
                tags=(tag_name, oval_tag)
            )

            # 3. Верхний оптический объем линзы (рассеянный свет стекла)
            canvas.create_oval(
                x_center - r * 0.78, y_center - r * 0.82,
                x_center + r * 0.78, y_center - r * 0.12,
                fill="#38BDF8", outline="",
                tags=(tag_name, f"{oval_tag}_lens")
            )

            # 4. Верхний стеклянный гребень
            canvas.create_oval(
                x_center - r * 0.48, y_center - r * 0.86,
                x_center + r * 0.48, y_center - r * 0.48,
                fill="#BAE6FD", outline="",
                tags=(tag_name, f"{oval_tag}_crest")
            )
            canvas.create_oval(
                x_center - r * 0.22, y_center - r * 0.82,
                x_center + r * 0.22, y_center - r * 0.60,
                fill="#FFFFFF", outline="",
                tags=(tag_name,)
            )

            # 5. Цифра по центру (Apple SF Pro / Segoe UI стиль)
            font_size = max(11, int(r * 0.44))
            canvas.create_text(
                x_center, y_center + int(r * 0.12),
                text=str(num),
                fill="#FFFFFF",
                font=("Segoe UI", font_size, "bold"),
                tags=(tag_name,)
            )

    def babble_swich_animation(idx1, idx2, action, on_complete=None):
        """Анимация облета по дуге (снизу/сверху) при обмене или тряски при равенстве."""
        nonlocal is_animating, anim_job_id
        if idx1 >= len(babbles) or idx2 >= len(babbles):
            if on_complete:
                on_complete()
            return

        is_animating = True
        b1 = babbles[idx1]
        b2 = babbles[idx2]
        tag1 = b1["tag"]
        tag2 = b2["tag"]

        # Подсветка активных шариков в стиле Liquid Glass
        set_bubble_style(b1, action)
        set_bubble_style(b2, action)

        if action == "swap":
            total_frames = 16
            coords1 = canvas.coords(b1["oval_tag"])
            coords2 = canvas.coords(b2["oval_tag"])
            if coords1 and coords2:
                start_x1 = (coords1[0] + coords1[2]) / 2.0
                start_y1 = (coords1[1] + coords1[3]) / 2.0
                start_x2 = (coords2[0] + coords2[2]) / 2.0
                start_y2 = (coords2[1] + coords2[3]) / 2.0
                dist = start_x2 - start_x1
            else:
                dist = b2["x_center"] - b1["x_center"]
                start_x1 = b1["x_center"]
                start_x2 = b2["x_center"]
                canvas_height = canvas.winfo_height()
                if canvas_height < 50:
                    canvas_height = 400
                start_y1 = canvas_height // 2
                start_y2 = start_y1

            # Новая адаптивная высота дуги: гарантирует свободный зазор без наложения с учетом масштаба
            current_zoom = getattr(canvas, "zoom_level", 1.0)
            arc_h = max(85.0 * current_zoom, ((b1["r"] + b2["r"]) * 1.1 + 15) * current_zoom)
            current_frame = 0

            step_delay = max(10, min(int(current_data["delay_ms"] * 0.75 / total_frames), 35))

            def anim_step():
                nonlocal current_frame, is_animating, anim_job_id
                current_frame += 1

                t_prev = (current_frame - 1) / total_frames
                t_curr = current_frame / total_frames

                # Плавная физика Ease-In-Out по горизонтали (мягкий разгон и торможение)
                prog_prev = (1.0 - math.cos(math.pi * t_prev)) / 2.0
                prog_curr = (1.0 - math.cos(math.pi * t_curr)) / 2.0
                step_progress = prog_curr - prog_prev

                # Левый шарик летит вправо по нижней дуге
                dx1 = dist * step_progress
                dy1 = arc_h * (math.sin(math.pi * t_curr) - math.sin(math.pi * t_prev))
                canvas.move(tag1, dx1, dy1)

                # Правый шарик летит влево по верхней дуге
                dx2 = -dist * step_progress
                dy2 = -arc_h * (math.sin(math.pi * t_curr) - math.sin(math.pi * t_prev))
                canvas.move(tag2, dx2, dy2)

                if current_frame < total_frames:
                    anim_job_id = frame.after(step_delay, anim_step)
                else:
                    # Фиксация точных целевых координат (b1 встает на место b2, а b2 - на место b1)
                    c1 = canvas.coords(b1["oval_tag"])
                    c2 = canvas.coords(b2["oval_tag"])
                    if c1:
                        cur_x1 = (c1[0] + c1[2]) / 2.0
                        cur_y1 = (c1[1] + c1[3]) / 2.0
                        canvas.move(tag1, start_x2 - cur_x1, start_y2 - cur_y1)
                    if c2:
                        cur_x2 = (c2[0] + c2[2]) / 2.0
                        cur_y2 = (c2[1] + c2[3]) / 2.0
                        canvas.move(tag2, start_x1 - cur_x2, start_y1 - cur_y2)

                    set_bubble_style(b1, "idle")
                    set_bubble_style(b2, "idle")

                    # Обновляем центры и меняем местами в массиве babbles
                    b1["x_center"], b2["x_center"] = b2["x_center"], b1["x_center"]
                    babbles[idx1], babbles[idx2] = babbles[idx2], babbles[idx1]

                    anim_job_id = None
                    is_animating = False
                    if on_complete:
                        on_complete()

            anim_step()
        else:
            # Тряска (Shake) при сравнении без обмена
            total_frames = 10
            shake_amp = 6.0 * getattr(canvas, "zoom_level", 1.0)
            current_frame = 0
            step_delay = max(10, min(int(current_data["delay_ms"] * 0.5 / total_frames), 25))

            def shake_step():
                nonlocal current_frame, is_animating, anim_job_id
                current_frame += 1

                t_prev = (current_frame - 1) / total_frames
                t_curr = current_frame / total_frames

                dx = shake_amp * (math.sin(4 * math.pi * t_curr) - math.sin(4 * math.pi * t_prev))
                canvas.move(tag1, dx, 0)
                canvas.move(tag2, dx, 0)

                if current_frame < total_frames:
                    anim_job_id = frame.after(step_delay, shake_step)
                else:
                    set_bubble_style(b1, "idle")
                    set_bubble_style(b2, "idle")

                    anim_job_id = None
                    is_animating = False
                    if on_complete:
                        on_complete()

            shake_step()

    # Визуализация любой сортировки через столбики
    def sort_render(indices=(), action="idle"):
        """Отрисовывает массив в виде вертикальных столбиков без анимации.

        Вызывается на каждом шаге для SelectionSort, QuickSort и HeapSort.
        Подсвечивает сравниваемые (compare), перемещаемые (swap) и завершенные (done) элементы.
        """
        canvas.delete("all")
        canvas.zoom_level = 1.0

        # Определение доступной рабочей области холста
        canvas_width = canvas.winfo_width()
        if canvas_width < 100:
            canvas_width = 1000
        canvas_height = canvas.winfo_height()
        if canvas_height < 100:
            canvas_height = 600

        nums = current_data["numbers"]
        n = len(nums)
        if n == 0:
            return

        margin_x = 40
        y_bottom = canvas_height - 60
        y_top = 50
        avail_h = max(50, y_bottom - y_top)
        avail_w = max(100, canvas_width - 2 * margin_x)

        max_num = max(nums) if nums else 1
        if max_num <= 0:
            max_num = 1

        # Расчет ширины столбиков и зазоров между ними
        slot_w = avail_w / n
        gap = max(2, int(slot_w * 0.12))
        bar_w = max(4, slot_w - gap)
        start_x = margin_x + (avail_w - n * slot_w) / 2

        # Отрисовка базовой горизонтальной линии (опоры)
        canvas.create_line(
            margin_x - 10, y_bottom,
            canvas_width - margin_x + 10, y_bottom,
            fill="#CBD5E1", width=2
        )

        # Отрисовка столбиков с цветовой дифференциацией по типу действия
        for i, num in enumerate(nums):
            if action == "done" and not indices:
                fill_color = "#34C759"
                outline_color = "#2E7D32"
            elif i in indices:
                if action == "swap":
                    fill_color = "#FF3B30"
                    outline_color = "#B91C1C"
                elif action == "compare":
                    fill_color = "#FF9500"
                    outline_color = "#D97706"
                elif action == "done":
                    fill_color = "#34C759"
                    outline_color = "#2E7D32"
                else:
                    fill_color = "#0A84FF"
                    outline_color = "#1D4ED8"
            else:
                fill_color = "#0A84FF"
                outline_color = "#0284C7"

            # Вычисление высоты и координат текущего столбика
            bar_h = max(16, int((num / max_num) * avail_h))
            x1 = start_x + i * slot_w + gap / 2
            x2 = x1 + bar_w
            y1 = y_bottom - bar_h
            y2 = y_bottom

            # Отрисовка прямоугольника столбика
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=fill_color,
                outline=outline_color,
                width=1.5
            )

            # Отображение числовых значений и индексов при достаточной ширине
            if bar_w >= 14:
                font_size = max(8, min(14, int(bar_w * 0.38)))
                # Значение элемента сверху над столбиком
                canvas.create_text(
                    (x1 + x2) / 2, y1 - 10,
                    text=str(num),
                    fill="#1E293B",
                    font=("Segoe UI", font_size, "bold")
                )
                # Индекс массива под базовой линией
                canvas.create_text(
                    (x1 + x2) / 2, y_bottom + 14,
                    text=str(i),
                    fill="#64748B",
                    font=("Segoe UI", max(8, font_size - 2))
                )

    # ==========================================
    # 6. ВИДЖЕТЫ НИЖНЕЙ ПАНЕЛИ И ОБРАБОТЧИКИ
    # ==========================================
    player_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
    player_frame.grid(row=0, column=0, sticky="w")

    play_job_id = None

    def on_step_forward():
        """Шаг вперед: берет следующий кадр из log_full_array."""
        if is_animating:
            return False

        if current_data["step"] < len(current_data["log_full_array"]):
            step_item = current_data["log_full_array"][current_data["step"]]
            current_data["step"] += 1

            log_current_array.append(step_item["log_line"])
            update_log_display()

            step_label.configure(text=f"Шаг: {current_data['step']}")
            explanation_label.configure(text=step_item["explanation"])

            current_data["numbers"] = list(step_item["nums"])

            # Отображение шага: анимация для BubbleSort либо обновление столбиков для остальных
            if algo_selector.get() == "BubbleSort":
                if step_item.get("indices"):
                    idx1, idx2 = step_item["indices"]
                    action = step_item.get("action", "compare")

                    def after_animation():
                        if current_data["is_running"]:
                            nonlocal play_job_id
                            play_job_id = frame.after(current_data["delay_ms"], play_tick)

                    babble_swich_animation(idx1, idx2, action, on_complete=after_animation)
                    return True
                else:
                    bubble_render()
                    if step_item.get("action") == "done":
                        for b in babbles:
                            set_bubble_style(b, "done")
            else:
                sort_render(
                    indices=step_item.get("indices", ()),
                    action=step_item.get("action", "compare")
                )

            if current_data["is_running"]:
                nonlocal play_job_id
                play_job_id = frame.after(current_data["delay_ms"], play_tick)
            return True
        return False

    def on_step_back():
        """Шаг назад: откатывает лог и положение шариков."""
        if is_animating:
            return

        if current_data["step"] > 0:
            current_data["step"] -= 1

            if len(log_current_array) > 1:
                log_current_array.pop()
            update_log_display()

            step_label.configure(text=f"Шаг: {current_data['step']}")
            if current_data["step"] > 0:
                prev_item = current_data["log_full_array"][current_data["step"] - 1]
                explanation_label.configure(text=prev_item["explanation"])
                current_data["numbers"] = list(prev_item["nums"])
                if algo_selector.get() == "BubbleSort":
                    bubble_render()
                else:
                    sort_render(
                        indices=prev_item.get("indices", ()),
                        action=prev_item.get("action", "compare")
                    )
            else:
                explanation_label.configure(text="Исходное состояние массива")
                current_data["numbers"] = list(current_data["initial_numbers"])
                if algo_selector.get() == "BubbleSort":
                    bubble_render()
                else:
                    sort_render()

    def play_tick():
        """Один такт автовоспроизведения."""
        nonlocal play_job_id
        if not current_data["is_running"] or is_animating:
            return

        if current_data["step"] < len(current_data["log_full_array"]):
            on_step_forward()
        else:
            toggle_play()
            explanation_label.configure(text="Сортировка завершена!")

    def toggle_play():
        """Старт и пауза воспроизведения."""
        nonlocal play_job_id
        current_data["is_running"] = not current_data["is_running"]

        if current_data["is_running"]:
            if current_data["step"] >= len(current_data["log_full_array"]):
                on_reset()
                current_data["is_running"] = True

            btn_play.configure(
                text="⏸ Пауза",
                fg_color="#C62828",
                hover_color="#8E0000"
            )
            play_job_id = frame.after(current_data["delay_ms"], play_tick)
        else:
            if play_job_id is not None:
                frame.after_cancel(play_job_id)
                play_job_id = None
            btn_play.configure(
                text="▶ Старт",
                fg_color="#2E7D32",
                hover_color="#1B5E20"
            )

    def on_reset():
        """Сброс к исходному состоянию."""
        nonlocal play_job_id, anim_job_id, is_animating
        if current_data["is_running"]:
            toggle_play()

        if anim_job_id is not None:
            frame.after_cancel(anim_job_id)
            anim_job_id = None
        is_animating = False

        current_data["step"] = 0
        current_data["numbers"] = list(current_data["initial_numbers"])
        if algo_selector.get() == "BubbleSort":
            bubble_render()
        else:
            sort_render()

        log_current_array.clear()
        log_current_array.append("Лог:\n")
        update_log_display()

        step_label.configure(text=f"Шаг: {current_data['step']}")
        explanation_label.configure(text="Сброс к исходному состоянию")

    btn_step_back = ctk.CTkButton(
        player_frame,
        text="←",
        width=48,
        height=36,
        font=("Arial", 16, "bold"),
        fg_color="#37474F",
        hover_color="#263238",
        command=on_step_back
    )
    btn_step_back.grid(row=0, column=0, padx=(0, 5))

    btn_play = ctk.CTkButton(
        player_frame,
        text="▶ Старт",
        width=95,
        height=36,
        font=("Arial", 12, "bold"),
        fg_color="#2E7D32",
        hover_color="#1B5E20",
        command=toggle_play
    )
    btn_play.grid(row=0, column=1, padx=5)

    btn_step_forward = ctk.CTkButton(
        player_frame,
        text="→",
        width=48,
        height=36,
        font=("Arial", 16, "bold"),
        fg_color="#37474F",
        hover_color="#263238",
        command=on_step_forward
    )
    btn_step_forward.grid(row=0, column=2, padx=5)

    btn_reset = ctk.CTkButton(
        player_frame,
        text="🔄",
        width=48,
        height=36,
        font=("Arial", 13, "bold"),
        fg_color="#37474F",
        hover_color="#263238",
        command=on_reset
    )
    btn_reset.grid(row=0, column=3, padx=(5, 0))

    # Зона скорости
    speed_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
    speed_frame.grid(row=0, column=2)

    lbl_delay = ctk.CTkLabel(
        speed_frame,
        text=f"Задержка: {current_data['delay_ms']} мс",
        font=("Arial", 18, "bold")
    )
    lbl_delay.grid(row=0, column=0, padx=(0, 10))

    def on_delay_change(val):
        current_data["delay_ms"] = int(val)
        lbl_delay.configure(text=f"Задержка: {int(val)} мс")

    delay_slider = ctk.CTkSlider(
        speed_frame,
        from_=10,
        to=1000,
        number_of_steps=99,
        width=160,
        command=on_delay_change
    )
    delay_slider.set(current_data["delay_ms"])
    delay_slider.grid(row=0, column=1)

    # Зона генератора массива
    generator_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
    generator_frame.grid(row=0, column=4, sticky="e")

    lbl_size = ctk.CTkLabel(
        generator_frame,
        text="Размер:",
        font=("Arial", 12, "bold")
    )
    lbl_size.grid(row=0, column=0, padx=(0, 8))

    entry_size = ctk.CTkEntry(
        generator_frame,
        width=70,
        height=36,
        placeholder_text="1–100",
        font=("Arial", 12)
    )
    entry_size.insert(0, str(current_data["list_len"]))
    entry_size.grid(row=0, column=1, padx=(0, 8))

    lbl_error = ctk.CTkLabel(
        generator_frame,
        text="",
        font=("Arial", 11),
        text_color="#FF5252"
    )
    lbl_error.grid(row=1, column=0, columnspan=3, pady=(2, 0))

    def on_generate():
        """Генерация нового массива и пересчет логов."""
        val_str = entry_size.get().strip()

        if not val_str.isdigit():
            lbl_error.configure(text="Введите целое число!")
            entry_size.configure(border_color="#FF5252")
            return

        val = int(val_str)
        if val < 2 or val > 100:
            lbl_error.configure(text="Диапазон: от 2 до 100")
            entry_size.configure(border_color="#FF5252")
            return

        if current_data["is_running"]:
            toggle_play()

        nonlocal anim_job_id, is_animating
        if anim_job_id is not None:
            frame.after_cancel(anim_job_id)
            anim_job_id = None
        is_animating = False

        lbl_error.configure(text="")
        entry_size.configure(border_color=["#979DA2", "#565B5E"])
        current_data["list_len"] = val
        current_data["numbers"] = [random.randint(1, 99) for _ in range(val)]
        current_data["initial_numbers"] = list(current_data["numbers"])
        current_data["step"] = 0

        # Пересчитываем лог выбранного алгоритма
        on_select_algorithm(algo_selector.get())

        log_current_array.clear()
        log_current_array.append("Лог:\n")
        update_log_display()

        if algo_selector.get() == "BubbleSort":
            bubble_render()
        else:
            sort_render()

        step_label.configure(text=f"Шаг: {current_data['step']}")
        explanation_label.configure(text=f"Сгенерирован новый массив из {val} элементов")

    btn_generate = ctk.CTkButton(
        generator_frame,
        text="🎲 Создать",
        width=90,
        height=36,
        font=("Arial", 12, "bold"),
        command=on_generate
    )
    btn_generate.grid(row=0, column=2)

    # Инициализация первого запуска
    on_select_algorithm(algo_selector.get())
    bubble_render()

    return frame
