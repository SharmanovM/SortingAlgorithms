"""Модуль экрана второго практического задания: алгоритмы внешней сортировки."""

import customtkinter as ctk
from tkinter import filedialog
import csv
import os
from itertools import islice
import copy


def create_screen2(parent, on_back):
    """Создает фрейм для внешней сортировки табличных файлов."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    # Конфигурация сетки основного контейнера экрана:
    # верхняя и нижняя панели имеют фиксированный размер, центральная растягивается
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_rowconfigure(2, weight=0)

    # ==========================================
    # 1. СОСТОЯНИЕ ДАННЫХ ЭКРАНА (STATE)
    # ==========================================
    current_data = {
        "step": 0,
        "delay_ms": 200,
        "is_running": False,
        "log_full_array": [],
        "headers": [],
        "table": [],
        "key_column": 0,
        "sort_direction": None  # Направление: 'asc' (▲), 'desc' (▼) или None (не выбрано)
    }

    log_current_array = ["Лог:\n"]
    log_full_array = ["Лог:\n"]
    initial_data = {}  # Глубокая копия состояния для возврата при сбросе (on_reset)

    # ==========================================
    # 2. ОСНОВНЫЕ ФРЕЙМЫ ИНТЕРФЕЙСА
    # ==========================================
    top_frame = ctk.CTkFrame(frame, fg_color="transparent")
    top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

    content_frame = ctk.CTkFrame(frame, fg_color="transparent")
    content_frame.grid(row=1, column=0, sticky="nsew")
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_rowconfigure(1, weight=0)

    # Контейнер для отображения лога и будущей таблицы
    main_container = ctk.CTkFrame(content_frame, fg_color="transparent")
    main_container.grid(row=0, column=0, sticky="nsew")
    main_container.grid_columnconfigure(0, weight=1)
    main_container.grid_columnconfigure(1, weight=3)
    main_container.grid_rowconfigure(0, weight=1)

    # Информационная строка состояния и пояснений
    info_container = ctk.CTkFrame(content_frame, fg_color="transparent")
    info_container.grid(row=1, column=0, sticky="ew", pady=(10, 0))
    info_container.grid_columnconfigure(0, weight=1)
    info_container.grid_columnconfigure(1, weight=2)
    info_container.grid_columnconfigure(2, weight=1)

    # Нижняя панель элементов управления
    bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
    bottom_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
    bottom_frame.grid_columnconfigure(0, weight=0)
    bottom_frame.grid_columnconfigure(1, weight=1)
    bottom_frame.grid_columnconfigure(2, weight=0)
    bottom_frame.grid_columnconfigure(3, weight=1)
    bottom_frame.grid_columnconfigure(4, weight=0)
    player_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
    player_frame.grid(row=0, column=0, sticky="w")
    speed_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")  # Зона настройки задержки воспроизведения
    speed_frame.grid(row=0, column=2)
    file_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
    file_frame.grid(row=0, column=4, sticky="e")

    # ==========================================
    # 3. ВИДЖЕТЫ ВЕРХНЕЙ ПАНЕЛИ
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

    # ==========================================
    # 4. ВИДЖЕТЫ ЦЕНТРАЛЬНОЙ ОБЛАСТИ (ЛОГ И ПОЯСНЕНИЯ)
    # ==========================================

    def update_log_display():
        """Обновляет содержимое текстового лога на экране."""
        log_textbox.configure(state="normal")
        log_textbox.delete("1.0", "end")
        log_textbox.insert("1.0", "".join(log_current_array))
        log_textbox.see("end")
        log_textbox.configure(state="disabled")

    def render_table():
        """Отрисовывает таблицу данных с интерактивными кнопками сортировки в заголовках.

        Считывает метаданные (заголовки) и строки превью из current_data.
        Каждая кнопка заголовка циклически переключается между тремя состояниями:
        1. Не выбрана (нейтральный заголовок без стрелки).
        2. Выбрана по возрастанию (активный цвет и стрелка ▲).
        3. Выбрана по убыванию (активный цвет и стрелка ▼).
        """
        # Скрываем исходный контейнер-заглушку, если он все еще отображается на экране
        try:
            table_container.grid_remove()
        except NameError:
            pass

        # Очищаем ячейку сетки от ранее отрисованных таблиц во избежание утечки памяти и наслоения виджетов
        for widget in main_container.grid_slaves(row=0, column=1):
            try:
                if widget is not table_container:
                    widget.destroy()
            except NameError:
                widget.destroy()

        # Контейнер для отображения лога и будущей таблицы
        table_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        table_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        headers = current_data.get("headers", [])
        table_rows = current_data.get("table", [])

        # Если файл еще не выбран или пуст, отображаем поясняющую плашку-заглушку
        if not headers:
            placeholder = ctk.CTkLabel(
                table_frame,
                text="Таблица пока не загружена.\nНажмите «Загрузить CSV» для выбора файла.",
                font=("Arial", 16),
                text_color="#64748B"
            )
            placeholder.pack(expand=True, fill="both")
            return

        # Прокручиваемый контейнер: объединение кнопок заголовков и строк в общую сетку
        # гарантирует строгое попиксельное совпадение ширины колонок таблицы
        scroll_frame = ctk.CTkScrollableFrame(
            table_frame,
            fg_color="#F8FAFC",
            corner_radius=10
        )
        scroll_frame.grid(row=0, column=0, sticky="nsew")

        # Настраиваем адаптивное распределение колонок по всей доступной ширине
        for col_idx in range(len(headers)):
            scroll_frame.grid_columnconfigure(col_idx, weight=1)

        active_col = current_data.get("key_column")
        sort_direction = current_data.get("sort_direction")

        def on_header_click(col_index: int):
            """Обрабатывает клик по колонке, выполняя циклический переход состояний сортировки."""
            if current_data.get("key_column") == col_index:
                # Циклический переход для текущей колонки: ▲ (asc) -> ▼ (desc) -> сброс (None)
                if current_data.get("sort_direction") == "asc":
                    current_data["sort_direction"] = "desc"
                elif current_data.get("sort_direction") == "desc":
                    current_data["sort_direction"] = None
                    current_data["key_column"] = None
                else:
                    current_data["sort_direction"] = "asc"
            else:
                # При клике на новую колонку сбрасываем предыдущую и начинаем с сортировки по возрастанию
                current_data["key_column"] = col_index
                current_data["sort_direction"] = "asc"

            # Синхронизация статуса в нижней информационной панели с выбранным атрибутом
            current_dir = current_data.get("sort_direction")
            if current_dir == "asc":
                explanation_label.configure(
                    text=f"Ключевой атрибут: «{headers[col_index]}» (по возрастанию ▲)"
                )
            elif current_dir == "desc":
                explanation_label.configure(
                    text=f"Ключевой атрибут: «{headers[col_index]}» (по убыванию ▼)"
                )
            else:
                explanation_label.configure(
                    text="Ключевой атрибут не выбран. Нажмите на заголовок для выбора."
                )

            # Перерисовываем таблицу с обновленными индикаторами на кнопках
            render_table()

        # Отрисовка кнопок атрибутов в верхней строке (row=0)
        for col_idx, header_text in enumerate(headers):
            is_active = (col_idx == active_col and sort_direction is not None)

            # Формирование внешнего вида кнопки в зависимости от текущего состояния
            if is_active and sort_direction == "asc":
                btn_text = f"{header_text} ▲"
                btn_fg = "#4338CA"
                btn_hover = "#3730A3"
            elif is_active and sort_direction == "desc":
                btn_text = f"{header_text} ▼"
                btn_fg = "#4338CA"
                btn_hover = "#3730A3"
            else:
                btn_text = header_text
                btn_fg = "#37474F"
                btn_hover = "#263238"

            header_button = ctk.CTkButton(
                scroll_frame,
                text=btn_text,
                font=("Arial", 12, "bold"),
                height=32,
                fg_color=btn_fg,
                hover_color=btn_hover,
                text_color="#FFFFFF",
                command=lambda c=col_idx: on_header_click(c)
            )
            header_button.grid(row=0, column=col_idx, sticky="ew", padx=2, pady=(2, 6))

        # Отрисовка строк данных с чередованием цвета (зебра) для улучшения читаемости
        for row_idx, row_values in enumerate(table_rows):
            row_bg = "#FFFFFF" if row_idx % 2 == 0 else "#F1F5F9"
            for col_idx, cell_value in enumerate(row_values):
                if col_idx < len(headers):
                    cell_label = ctk.CTkLabel(
                        scroll_frame,
                        text=str(cell_value),
                        font=("Arial", 12),
                        text_color="#1E293B",
                        fg_color=row_bg,
                        corner_radius=4,
                        height=28
                    )
                    cell_label.grid(row=row_idx + 1, column=col_idx, sticky="ew", padx=2, pady=1)

    def sort_table():
        """Выполняет внешнюю сортировку таблицы порциями по 10 строк с формированием лога шагов.

        Моделирует работу с ограниченным объемом оперативной памяти (RAM-буфер = 10 записей).
        Исходные данные в current_data не модифицируются; метод возвращает список
        состояний и сообщений лога для пошагового воспроизведения анимации.

        Returns:
            list[dict]: Список шагов сортировки, где каждый шаг содержит:
                - 'log_line': текстовая запись для добавления в журнал;
                - 'explanation': понятное объяснение выполняемого действия;
                - 'table': срез строк таблицы (до 20 записей) для предпросмотра;
                - 'action': тип операции ('read_chunk', 'sort_chunk', 'merge', 'done').
        """
        file_path = current_data.get("file_path")
        key_col = current_data.get("key_column")
        sort_direction = current_data.get("sort_direction")
        headers = current_data.get("headers", [])

        # Проверка наличия исходного файла на диске
        if not file_path or not os.path.exists(file_path):
            return [{
                "log_line": "Ошибка: Файл таблицы не загружен.\n",
                "explanation": "Сначала загрузите CSV-файл через кнопку «Загрузить CSV».",
                "table": [],
                "action": "error"
            }]

        # Проверка выбора ключевого атрибута и направления сортировки
        if key_col is None or key_col < 0 or key_col >= len(headers) or sort_direction is None:
            return [{
                "log_line": "Предупреждение: Ключевой атрибут сортировки не выбран.\n",
                "explanation": "Кликните по заголовку желаемой колонки таблицы, чтобы задать направление сортировки (▲ или ▼).",
                "table": current_data.get("table", []),
                "action": "warning"
            }]

        col_name = headers[key_col]
        is_reverse = (sort_direction == "desc")
        direction_text = "по убыванию (▼)" if is_reverse else "по возрастанию (▲)"

        def get_comparison_key(value):
            """Формирует универсальный ключ сравнения для безопасного сопоставления чисел и строк."""
            if isinstance(value, (int, float)):
                return (0, value)
            return (1, str(value).casefold())

        def compare_ordered(val_a, val_b):
            """Определяет, находится ли val_a перед val_b с учетом направления сортировки."""
            key_a, key_b = get_comparison_key(val_a), get_comparison_key(val_b)
            if is_reverse:
                return key_a >= key_b
            return key_a <= key_b

        steps = []
        chunk_size = 10

        # Стартовая запись в лог с описанием параметров задачи
        steps.append({
            "log_line": (
                f"=== СТАРТ ВНЕШНЕЙ СОРТИРОВКИ ===\n"
                f"Файл: {os.path.basename(file_path)}\n"
                f"Ключевой атрибут: [{col_name}] (индекс {key_col})\n"
                f"Направление: {direction_text}\n"
                f"Размер буфера оперативной памяти: {chunk_size} строк\n\n"
            ),
            "explanation": f"Начинаем внешнюю сортировку по атрибуту «{col_name}» {direction_text}. Память ограничена 10 строками.",
            "table": current_data.get("table", []),
            "action": "start"
        })

        # ==========================================================
        # ФАЗА 1: Чтение порциями по 10 строк и создание серий в RAM
        # ==========================================================
        runs = []
        chunk_index = 0

        with open(file_path, mode="r", encoding="utf-8-sig") as file_handle:
            # Определение разделителя CSV-файла
            sample = file_handle.read(2048)
            file_handle.seek(0)
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=";,|\t,").delimiter
            except Exception:
                delimiter = ","

            reader = csv.reader(file_handle, delimiter=delimiter)
            # Пропускаем строку заголовков
            next(reader, None)

            while True:
                # Читаем строго до chunk_size (10) строк за один раз, моделируя ограниченный буфер RAM
                chunk = []
                for row in islice(reader, chunk_size):
                    if row:
                        chunk.append([parse_cell(cell) for cell in row])

                if not chunk:
                    break

                chunk_index += 1

                # Шаг фиксации загрузки очередной порции в оперативную память
                steps.append({
                    "log_line": f"[Фаза 1: Серия {chunk_index}] Загрузка {len(chunk)} строк в RAM-буфер...\n",
                    "explanation": f"Считываем с диска порцию №{chunk_index} ({len(chunk)} записей) в оперативную память.",
                    "table": chunk[:20],
                    "action": "read_chunk"
                })

                # Внутренняя сортировка загруженной порции по ключевому полю
                sorted_chunk = sorted(
                    chunk,
                    key=lambda record: get_comparison_key(record[key_col]),
                    reverse=is_reverse
                )
                runs.append(sorted_chunk)

                # Шаг фиксации готовности отсортированной серии
                first_val = sorted_chunk[0][key_col]
                last_val = sorted_chunk[-1][key_col]
                steps.append({
                    "log_line": (
                        f"[Фаза 1: Серия {chunk_index}] Отсортировано во внутренней памяти. "
                        f"Диапазон ключа: [{first_val} ... {last_val}]. Серия сохранена во временное хранилище.\n"
                    ),
                    "explanation": f"Порция №{chunk_index} отсортирована в памяти и сохранена как готовая серия.",
                    "table": sorted_chunk[:20],
                    "action": "sort_chunk"
                })

        steps.append({
            "log_line": f"\n[Фаза 1 завершена] Сформировано начальных серий: {len(runs)}. Переход к слиянию.\n\n",
            "explanation": f"Все данные разбиты на {len(runs)} отсортированных серий. Начинаем попарное слияние.",
            "table": runs[0][:20] if runs else [],
            "action": "phase1_done"
        })

        # ==========================================================
        # ФАЗА 2: Попарное двухпутевое слияние отсортированных серий
        # ==========================================================
        merge_pass = 1

        while len(runs) > 1:
            next_runs = []

            for i in range(0, len(runs), 2):
                # Если пары нет (нечетная серия в проходе), она без изменений переходит в следующий проход
                if i + 1 >= len(runs):
                    next_runs.append(runs[i])
                    continue

                run_left = runs[i]
                run_right = runs[i + 1]
                idx_left, idx_right = 0, 0
                merged_run = []

                # Поточечное слияние двух упорядоченных списков с логированием каждого сравнения
                while idx_left < len(run_left) and idx_right < len(run_right):
                    val_left = run_left[idx_left][key_col]
                    val_right = run_right[idx_right][key_col]

                    if compare_ordered(val_left, val_right):
                        chosen_record = run_left[idx_left]
                        chosen_val = val_left
                        other_val = val_right
                        chosen_source = "Левая серия"
                        idx_left += 1
                    else:
                        chosen_record = run_right[idx_right]
                        chosen_val = val_right
                        other_val = val_left
                        chosen_source = "Правая серия"
                        idx_right += 1

                    merged_run.append(chosen_record)

                    # Логирование сравнения двух граничных элементов сливаемых серий
                    steps.append({
                        "log_line": (
                            f"[Проход {merge_pass}: Слияние] Сравнение: «{chosen_val}» и «{other_val}» ➔ "
                            f"выбираем «{chosen_val}» ({chosen_source})\n"
                        ),
                        "explanation": f"Сравниваем «{val_left}» и «{val_right}». По критерию выбираем меньший/больший элемент ({chosen_val}).",
                        "table": merged_run[:20],
                        "action": "merge"
                    })

                # Дописываем оставшиеся элементы из непустой серии
                if idx_left < len(run_left):
                    merged_run.extend(run_left[idx_left:])
                if idx_right < len(run_right):
                    merged_run.extend(run_right[idx_right:])

                next_runs.append(merged_run)

            runs = next_runs
            merge_pass += 1

        # Финальный шаг: сортировка завершена, получаем итоговую таблицу
        final_table = runs[0] if runs else []
        steps.append({
            "log_line": f"\n=== СОРТИРОВКА УСПЕШНО ЗАВЕРШЕНА ===\nВсего записей обработано: {len(final_table)}\n",
            "explanation": "Все серии объединены в единую упорядоченную таблицу. Внешняя сортировка завершена!",
            "table": final_table[:20],
            "full_table": final_table,
            "action": "done"
        })

        return steps


    # Текстовое поле лога с автоматической прокруткой
    log_textbox = ctk.CTkTextbox(
        main_container,
        font=("Arial", 20),
        text_color="#1E293B",
        fg_color="transparent",
        activate_scrollbars=True
    )
    log_textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    # Контейнер для отображения таблицы (будет наполнен при загрузке файла)
    table_container = ctk.CTkFrame(main_container, fg_color="#F8FAFC", corner_radius=10)
    table_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)

    lbl_table_placeholder = ctk.CTkLabel(
        table_container,
        text="Таблица пока не загружена.\nНажмите «Загрузить файл» для выбора CSV-файла.",
        font=("Arial", 16),
        text_color="#64748B"
    )
    lbl_table_placeholder.pack(expand=True, fill="both")

    # Отображение текущего номера шага
    step_label = ctk.CTkLabel(
        info_container,
        text=f"Шаг: {current_data['step']}",
        font=("Arial", 22, "bold")
    )
    step_label.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=5)

    # Плашка с текстовым пояснением текущего действия
    explanation = "Загрузите файл таблицы для начала работы"
    explanation_label = ctk.CTkLabel(
        info_container,
        text=explanation,
        font=("Arial", 22),
        text_color="#4338CA"
    )
    explanation_label.grid(row=0, column=1, sticky="nsew", pady=5)

    update_log_display()

    # ==========================================
    # 5. ОБРАБОТЧИКИ УПРАВЛЕНИЯ BOTTOM PANEL
    # ==========================================

    # Идентификатор активного таймера Tkinter для отмены автовоспроизведения при паузе/сбросе
    play_job_id = None

    def on_step_forward():
        """Выполняет один шаг сортировки вперед с выводом записи в лог и обновлением таблицы."""
        # Если шаги еще не сгенерированы, вычисляем их через sort_table
        if not current_data.get("log_full_array"):
            steps = sort_table()
            current_data["log_full_array"] = steps
            current_data["step"] = 0

            # Если вернулось сообщение об ошибке (например, файл не загружен или не выбран атрибут)
            if steps and steps[0].get("action") in ("error", "warning"):
                log_current_array.append(steps[0]["log_line"])
                update_log_display()
                explanation_label.configure(text=steps[0]["explanation"])
                return False

        # Проверяем, есть ли следующий шаг в очереди
        if current_data["step"] < len(current_data["log_full_array"]):
            step_item = current_data["log_full_array"][current_data["step"]]
            current_data["step"] += 1

            # Добавляем строку операции в текстовый лог экрана
            log_current_array.append(step_item["log_line"])
            update_log_display()

            # Обновляем счетчик шагов и понятное текстовое пояснение
            step_label.configure(text=f"Шаг: {current_data['step']}")
            explanation_label.configure(text=step_item["explanation"])

            # Напрямую обновляем данные таблицы в current_data для синхронизации отображения
            if "table" in step_item:
                current_data["table"] = list(step_item["table"])
                if "full_table" in step_item:
                    current_data["sorted_full_table"] = list(step_item["full_table"])
                render_table()

            # Если включен режим непрерывного автовоспроизведения, планируем следующий такт
            if current_data["is_running"]:
                nonlocal play_job_id
                play_job_id = frame.after(current_data["delay_ms"], play_tick)
            return True
        else:
            # Все шаги выполнены: останавливаем воспроизведение
            if current_data["is_running"]:
                toggle_play()
                explanation_label.configure(text="Сортировка завершена!")
            return False

    def on_step_back():
        """Откатывает один шаг назад, удаляет запись из лога и возвращает состояние таблицы."""
        # Ручной шаг назад автоматически ставит воспроизведение на паузу
        if current_data["is_running"]:
            toggle_play()

        if current_data["step"] > 0:
            current_data["step"] -= 1

            # Удаляем последнюю строку шага из лога (сохраняя начальные строки заголовка)
            if len(log_current_array) > 1:
                log_current_array.pop()
            update_log_display()

            step_label.configure(text=f"Шаг: {current_data['step']}")

            # Возвращаем пояснение и срез таблицы предыдущего шага либо начальное состояние
            if current_data["step"] > 0:
                prev_item = current_data["log_full_array"][current_data["step"] - 1]
                explanation_label.configure(text=prev_item["explanation"])
                if "table" in prev_item:
                    current_data["table"] = list(prev_item["table"])
                    render_table()
            else:
                explanation_label.configure(text="Исходное состояние данных. Шаг 0.")
                if initial_data and "table" in initial_data:
                    current_data["table"] = copy.deepcopy(initial_data["table"])
                    render_table()

    def play_tick():
        """Один такт циклического воспроизведения шагов по таймеру."""
        nonlocal play_job_id
        if not current_data["is_running"]:
            return

        if current_data["step"] < len(current_data["log_full_array"]):
            on_step_forward()
        else:
            toggle_play()
            explanation_label.configure(text="Сортировка успешно завершена!")

    def toggle_play():
        """Переключает воспроизведение между активным режимом и паузой."""
        nonlocal play_job_id

        # Если шаги еще не были рассчитаны, вычисляем их
        if not current_data.get("log_full_array"):
            steps = sort_table()
            current_data["log_full_array"] = steps
            current_data["step"] = 0

            # В случае ошибки выбора атрибута или файла прерываем старт
            if steps and steps[0].get("action") in ("error", "warning"):
                log_current_array.append(steps[0]["log_line"])
                update_log_display()
                explanation_label.configure(text=steps[0]["explanation"])
                return

        # Инвертируем состояние активности плеера
        current_data["is_running"] = not current_data["is_running"]

        if current_data["is_running"]:
            # Если дошли до конца и снова нажали Старт — перезапускаем воспроизведение с начала
            if current_data["step"] >= len(current_data["log_full_array"]):
                current_data["step"] = 0
                if initial_data and "table" in initial_data:
                    current_data["table"] = copy.deepcopy(initial_data["table"])
                    render_table()
                log_current_array.clear()
                log_current_array.append("Лог:\n")
                update_log_display()
                step_label.configure(text="Шаг: 0")

            # Визуальное переключение кнопки в состояние «Пауза»
            btn_play.configure(
                text="⏸ Пауза",
                fg_color="#C62828",
                hover_color="#8E0000"
            )
            # Запуск первого шага с текущей задержкой
            play_job_id = frame.after(current_data["delay_ms"], play_tick)
        else:
            # Остановка фонового таймера Tkinter при постановке на паузу
            if play_job_id is not None:
                frame.after_cancel(play_job_id)
                play_job_id = None

            # Возврат кнопки в состояние «Старт»
            btn_play.configure(
                text="▶ Старт",
                fg_color="#2E7D32",
                hover_color="#1B5E20"
            )

    def on_reset():
        """Сбрасывает процесс воспроизведения к исходному начальному состоянию."""
        nonlocal play_job_id
        if current_data["is_running"]:
            toggle_play()

        if play_job_id is not None:
            frame.after_cancel(play_job_id)
            play_job_id = None

        # Полное восстановление состояния current_data из глубокой копии начального состояния
        if initial_data:
            current_data.clear()
            current_data.update(copy.deepcopy(initial_data))
            render_table()
        else:
            current_data["step"] = 0
            current_data["log_full_array"] = []

        # Сброс текстового лога к начальной информации о файле
        log_current_array.clear()
        log_current_array.append("Лог:\n")
        if current_data.get("file_path"):
            log_current_array.append(
                f"[Файл]: {os.path.basename(current_data['file_path'])}\n"
                f"[Статус]: Выполнен сброс шагов к исходному состоянию.\n\n"
            )
        update_log_display()

        step_label.configure(text=f"Шаг: {current_data['step']}")
        explanation_label.configure(text="Состояние сброшено в начало. Нажмите «▶ Старт» или «→».")

    def save_file():
        """Сохраняет текущую отсортированную таблицу в выбранный CSV-файл на диске."""
        headers = current_data.get("headers", [])
        table_rows = current_data.get("sorted_full_table") or current_data.get("table", [])

        # Проверка наличия данных перед сохранением
        if not headers and not table_rows:
            explanation_label.configure(text="Нет данных для сохранения! Сначала загрузите файл.")
            return

        # Формирование предлагаемого имени результирующего файла
        orig_name = os.path.basename(current_data.get("file_path", "table.csv"))
        suggested_name = f"sorted_{orig_name}"

        save_path = filedialog.asksaveasfilename(
            title="Сохранить отсортированную таблицу",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=suggested_name
        )

        if not save_path:
            return

        try:
            # Сохранение с сохранением кодировки и исходного разделителя таблицы
            delimiter = current_data.get("delimiter", ";")
            with open(save_path, mode="w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=delimiter)
                if headers:
                    writer.writerow(headers)
                writer.writerows(table_rows)

            saved_name = os.path.basename(save_path)
            explanation_label.configure(text=f"Таблица успешно сохранена: {saved_name}")
            log_current_array.append(
                f"\n[Файл сохранен]: {saved_name}\n"
                f"[Записей]: {len(table_rows)}\n"
                f"[Путь]: {save_path}\n\n"
            )
            update_log_display()

        except Exception as e:
            explanation_label.configure(text=f"Ошибка сохранения файла: {e}")

    def on_delay_change(val):
        """Обновляет значение задержки шагов в миллисекундах."""
        current_data["delay_ms"] = int(val)
        lbl_delay.configure(text=f"Задержка: {int(val)} мс")

    def parse_cell(val: str):
        """Очищает строку от пробелов и приводит к числу, если это возможно."""
        val = val.strip()
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            pass
        return val

    def load_file():
        """Загружает метаданные и первые 20 строк файла для предпросмотра."""
        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if not file_path:
            return

        try:
            preview_limit = 20

            with open(file_path, mode="r", encoding="utf-8-sig") as f:
                # Читаем небольшой фрагмент для определения разделителя
                sample = f.read(2048)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t,")
                    delimiter = dialect.delimiter
                except Exception:
                    delimiter = ","

                reader = csv.reader(f, delimiter=delimiter)

                # Считываем только заголовок (первая строка)
                headers = next(reader, None)
                if not headers:
                    explanation_label.configure(text="Выбранный файл пуст!")
                    return

                headers = [h.strip() for h in headers]

                # Считываем ровно до 20 строк для превью через итератор
                preview_rows = []
                for row in islice(reader, preview_limit):
                    if row:
                        preview_rows.append([parse_cell(cell) for cell in row])

            # Сохраняем метаданные и превью в состояние
            current_data["file_path"] = file_path
            current_data["headers"] = headers
            current_data["table"] = preview_rows  # Только превью! Полный файл остается на диске
            current_data["delimiter"] = delimiter
            current_data["step"] = 0
            current_data["log_full_array"] = []
            current_data["sort_direction"] = None
            current_data["key_column"] = None

            # Глубокое копирование начального состояния для восстановления при сбросе
            initial_data.clear()
            initial_data.update(copy.deepcopy(current_data))

            file_name = os.path.basename(file_path)

            # Выводим информацию в лог
            log_current_array.clear()
            log_current_array.append("Лог:\n")
            log_current_array.append(
                f"[Файл выбран]: {file_name}\n"
                f"[Колонки]: {', '.join(headers)}\n"
                f"[Превью]: Загружено первых {len(preview_rows)} записей для показа.\n"
                f"[Режим]: Внешняя сортировка порциями (буфер RAM = 10 строк).\n\n"
            )
            update_log_display()

            # Обновление статус-бара
            step_label.configure(text="Шаг: 0")
            explanation_label.configure(
                text=f"Файл открыт: {file_name} (показано превью {len(preview_rows)} строк). Выберите атрибут."
            )

            # Прячем заглушку таблицы
            lbl_table_placeholder.pack_forget()
            render_table()

        except Exception as e:
            explanation_label.configure(text=f"Ошибка чтения: {e}")

    # ==========================================
    # 6. ВИДЖЕТЫ НИЖНЕЙ ПАНЕЛИ
    # ==========================================

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

    lbl_delay = ctk.CTkLabel(
        speed_frame,
        text=f"Задержка: {current_data['delay_ms']} мс",
        font=("Arial", 18, "bold")
    )
    lbl_delay.grid(row=0, column=0, padx=(0, 10))

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

    btn_load = ctk.CTkButton(
        file_frame,
        text="📂 Загрузить CSV",
        width=48,
        height=36,
        font=("Arial", 13, "bold"),
        fg_color="#37474F",
        hover_color="#263238",
        command=load_file
    )
    btn_load.grid(row=0, column=0, padx=(5, 0))

    btn_save = ctk.CTkButton(
        file_frame,
        text="💾 Сохранить результат",
        width=48,
        height=36,
        font=("Arial", 13, "bold"),
        fg_color="#37474F",
        hover_color="#263238",
        command=save_file
    )
    btn_save.grid(row=0, column=1, padx=(5, 0))

    return frame
