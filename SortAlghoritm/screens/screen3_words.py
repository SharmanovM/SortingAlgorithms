"""Модуль экрана третьего практического задания: лексикографическая сортировка слов и анализ производительности."""

import customtkinter as ctk
from tkinter import filedialog
import re
import os
import time

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# ==========================================================
# БАЗОВЫЙ СЛОВАРЬ ДЛЯ ГЕНЕРАЦИИ ВЫБОРОК ПРИ ОТСУТСТВИИ ФАЙЛА
# ==========================================================

DEFAULT_WORDS = [
    "algorithm", "array", "binary", "bubble", "buffer", "byte", "character", "code",
    "computer", "data", "element", "fast", "file", "heap", "index", "iteration",
    "key", "linear", "list", "logarithm", "memory", "merge", "node", "order",
    "pointer", "program", "quick", "radix", "record", "search", "sequence", "sort",
    "stack", "step", "string", "structure", "table", "text", "time", "tree", "word"
]


# ==========================================================
# 1. АЛГОРИТМЫ СОРТИРОВКИ СТРОК В ЛЕКСИКОГРАФИЧЕСКОМ ПОРЯДКЕ
# ==========================================================

def radix_sort_strings(arr):
    """Поразрядная сортировка строк (LSD / ABC-сортировка).
    
    Сортирует строки справа налево (от младших разрядов к старшим).
    Для каждой позиции символа выполняется устойчивое распределение по корзинам символов.
    Сложность: O(N * L), где N — количество строк, L — максимальная длина слова.
    """
    if not arr:
        return []
    max_len = max(len(s) for s in arr)
    res = list(arr)

    # Проходим по всем позициям символов от конца к началу (LSD)
    for d in range(max_len - 1, -1, -1):
        buckets = {}
        for s in res:
            # Для строк короче позиции d используем код -1 (располагаются раньше всех)
            char_code = ord(s[d]) if d < len(s) else -1
            if char_code not in buckets:
                buckets[char_code] = []
            buckets[char_code].append(s)

        # Собираем строки в устойчивом порядке кодов символов
        res = []
        for code in sorted(buckets.keys()):
            res.extend(buckets[code])
    return res


def quick_sort_strings(arr):
    """Быстрая сортировка Хоара (QuickSort) для массива строк.
    
    Использует разделение массива относительно центрального опорного элемента.
    Сложность в среднем: O(N * log N).
    """
    if len(arr) <= 1:
        return list(arr)
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort_strings(left) + middle + quick_sort_strings(right)


def merge_sort_strings(arr):
    """Сортировка слиянием (MergeSort) для массива строк.
    
    Рекурсивно делит массив пополам и упорядоченно сливает отсортированные части.
    Гарантированная сложность: O(N * log N), устойчивая сортировка.
    """
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = merge_sort_strings(arr[:mid])
    right = merge_sort_strings(arr[mid:])

    # Слияние двух упорядоченных подмассивов
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def heap_sort_strings(arr):
    """Пирамидальная сортировка (HeapSort) для массива строк.
    
    Строит двоичную max-кучу и последовательно извлекает максимальные элементы.
    Сложность: O(N * log N), не требует дополнительной памяти.
    """
    nums = list(arr)
    n = len(nums)

    def heapify(length, root):
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2

        if left < length and nums[left] > nums[largest]:
            largest = left
        if right < length and nums[right] > nums[largest]:
            largest = right

        if largest != root:
            nums[root], nums[largest] = nums[largest], nums[root]
            heapify(length, largest)

    # Фаза 1: построение max-кучи
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)

    # Фаза 2: последовательное перемещение максимума в конец массива
    for i in range(n - 1, 0, -1):
        nums[0], nums[i] = nums[i], nums[0]
        heapify(i, 0)

    return nums


def count_word_frequencies(sorted_words):
    """Подсчитывает частоту слов в отсортированном массиве за один линейный проход O(N).
    
    Поскольку одинаковые слова в отсортированной последовательности идут друг за другом,
    частота вычисляется сравнением с предыдущим элементом без хэш-таблиц.
    """
    if not sorted_words:
        return []

    frequencies = []
    current_word = sorted_words[0]
    count = 1

    for word in sorted_words[1:]:
        if word == current_word:
            count += 1
        else:
            frequencies.append((current_word, count))
            current_word = word
            count = 1
    frequencies.append((current_word, count))
    return frequencies


# ==========================================================
# 2. МЕТОДЫ ГЕНЕРАЦИИ СПИСКОВ СЛОВ ДЛЯ ТЕСТИРОВАНИЯ ОТ 1 ДО N
# ==========================================================

def generate_word_list(size: int, source_words: list = None) -> list:
    """Генерирует список слов заданной размерности size.
    
    Если передан список source_words, выборка формируется на его основе.
    Если source_words пуст, используется встроенный пул базовых слов DEFAULT_WORDS.
    При необходимости пул циклически повторяется до достижения требуемой длины.
    """
    pool = source_words if source_words else DEFAULT_WORDS
    if not pool:
        pool = DEFAULT_WORDS

    # Если запрошенный размер не превышает длину пула, берем начальный срез
    if size <= len(pool):
        return list(pool[:size])

    # Иначе циклически расширяем пул до нужного количества элементов
    repeats = (size // len(pool)) + 1
    extended = (pool * repeats)[:size]
    return extended


def generate_test_batches(max_n: int, source_words: list = None, num_points: int = 12) -> list:
    """Формирует серию тестовых списков слов различной размерности от 1 до max_n.
    
    Возвращает список кортежей (размер N, список слов длины N).
    Количество промежуточных точек оптимизировано (от 1 до num_points) для
    обеспечения высокой скорости замеров и плавности кривой на графике.
    """
    if max_n <= 1:
        return [(1, generate_word_list(1, source_words))]

    # Если N мало, тестируем буквально каждую размерность: 1, 2, 3...
    if max_n <= num_points:
        sizes = list(range(1, max_n + 1))
    else:
        # Иначе распределяем точки от 1 до max_n с равномерным шагом
        step = max(1, max_n // num_points)
        sizes = [1] + list(range(step, max_n, step))
        if sizes[-1] != max_n:
            sizes.append(max_n)

    batches = []
    for s in sizes:
        batches.append((s, generate_word_list(s, source_words)))
    return batches


# ==========================================================
# 3. ИНТЕРФЕЙС ЭКРАНА ЗАДАНИЯ 3
# ==========================================================

def create_screen3(parent, on_back):
    """Создает фрейм для анализа частотности слов и сравнения алгоритмов сортировки."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    # Сетка экрана: строка 0 - верхняя панель, строка 1 - рабочая область
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)

    # Локальное состояние экрана
    screen3_data = {
        "all_words": [],
        "sorted_words": [],
        "frequencies": [],
        "file_name": "",
        "benchmark_results": {}
    }

    # ==========================================
    # ВЕРХНЯЯ ПАНЕЛЬ: Кнопка Назад и Переключатели графиков
    # ==========================================
    top_frame = ctk.CTkFrame(frame, fg_color="transparent")
    top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    top_frame.grid_columnconfigure(0, weight=0)
    top_frame.grid_columnconfigure(1, weight=1)

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
    btn_back.grid(row=0, column=0, padx=(0, 15), pady=5)

    # Контейнер для переключателей отображения алгоритмов
    toggle_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
    toggle_frame.grid(row=0, column=1, sticky="e")

    var_quick = ctk.BooleanVar(value=True)
    var_merge = ctk.BooleanVar(value=True)
    var_radix = ctk.BooleanVar(value=True)
    var_heap = ctk.BooleanVar(value=True)

    def on_toggle_algo():
        """Перерисовывает график при включении/отключении отображения кривой алгоритма."""
        render_plot()

    cb_quick = ctk.CTkCheckBox(
        toggle_frame,
        text="QuickSort",
        text_color="#2563EB",
        fg_color="#2563EB",
        font=("Arial", 12, "bold"),
        variable=var_quick,
        command=on_toggle_algo
    )
    cb_quick.grid(row=0, column=0, padx=8)

    cb_merge = ctk.CTkCheckBox(
        toggle_frame,
        text="MergeSort",
        text_color="#EA580C",
        fg_color="#EA580C",
        font=("Arial", 12, "bold"),
        variable=var_merge,
        command=on_toggle_algo
    )
    cb_merge.grid(row=0, column=1, padx=8)

    cb_radix = ctk.CTkCheckBox(
        toggle_frame,
        text="RadixSort (LSD)",
        text_color="#16A34A",
        fg_color="#16A34A",
        font=("Arial", 12, "bold"),
        variable=var_radix,
        command=on_toggle_algo
    )
    cb_radix.grid(row=0, column=2, padx=8)

    cb_heap = ctk.CTkCheckBox(
        toggle_frame,
        text="HeapSort",
        text_color="#9333EA",
        fg_color="#9333EA",
        font=("Arial", 12, "bold"),
        variable=var_heap,
        command=on_toggle_algo
    )
    cb_heap.grid(row=0, column=3, padx=(8, 0))

    # ==========================================
    # ОСНОВНАЯ ОБЛАСТЬ: Левая и Правая колонки
    # ==========================================
    content_frame = ctk.CTkFrame(frame, fg_color="transparent")
    content_frame.grid(row=1, column=0, sticky="nsew")
    content_frame.grid_columnconfigure(0, weight=2)
    content_frame.grid_columnconfigure(1, weight=3)
    content_frame.grid_rowconfigure(0, weight=1)

    # ------------------------------------------
    # ЛЕВАЯ КОЛОНКА: Список слов и частотности
    # ------------------------------------------
    left_panel = ctk.CTkFrame(content_frame, fg_color="#F8FAFC", corner_radius=10)
    left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
    left_panel.grid_columnconfigure(0, weight=1)
    left_panel.grid_rowconfigure(0, weight=0)
    left_panel.grid_rowconfigure(1, weight=0)
    left_panel.grid_rowconfigure(2, weight=1)
    left_panel.grid_rowconfigure(3, weight=0)

    lbl_words_title = ctk.CTkLabel(
        left_panel,
        text="Список повторяющихся слов",
        font=("Arial", 16, "bold"),
        text_color="#1E293B"
    )
    lbl_words_title.grid(row=0, column=0, padx=15, pady=(12, 2), sticky="w")

    lbl_words_stats = ctk.CTkLabel(
        left_panel,
        text="Загрузите файл .txt для анализа частотности",
        font=("Arial", 12),
        text_color="#64748B"
    )
    lbl_words_stats.grid(row=1, column=0, padx=15, pady=(0, 6), sticky="w")

    words_textbox = ctk.CTkTextbox(
        left_panel,
        font=("Consolas", 13),
        text_color="#1E293B",
        fg_color="#FFFFFF",
        activate_scrollbars=True
    )
    words_textbox.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
    words_textbox.configure(state="disabled")

    def load_text_file():
        """Загружает текстовый файл, парсит слова и вычисляет их частотность."""
        file_path = filedialog.askopenfilename(
            title="Выберите текстовый файл",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                content = f.read()

            # Извлечение отдельных слов в нижнем регистре с очисткой от знаков препинания
            words = re.findall(r'\b[a-zA-Zа-яА-ЯёЁ0-9_-]+\b', content.lower())
            if not words:
                lbl_words_stats.configure(text="В выбранном файле не найдено слов!")
                return

            screen3_data["all_words"] = words
            file_name = os.path.basename(file_path)
            screen3_data["file_name"] = file_name

            # Лексикографическая сортировка слов алгоритмом RadixSort
            sorted_words = radix_sort_strings(words)
            screen3_data["sorted_words"] = sorted_words

            # Подсчет количества повторов для каждого слова за один линейный проход
            freqs = count_word_frequencies(sorted_words)
            screen3_data["frequencies"] = freqs

            # Сортировка списка частот по убыванию количества повторений для наглядности
            freqs_by_count = sorted(freqs, key=lambda x: x[1], reverse=True)

            # Вывод частотного списка в текстовое поле
            words_textbox.configure(state="normal")
            words_textbox.delete("1.0", "end")
            words_textbox.insert("end", f"{'Слово':<24} | {'Количество'}\n")
            words_textbox.insert("end", "-" * 38 + "\n")
            for word, count in freqs_by_count:
                words_textbox.insert("end", f"{word:<24} | {count} раз(а)\n")
            words_textbox.configure(state="disabled")

            lbl_words_stats.configure(
                text=f"Файл: {file_name} | Всего слов: {len(words)} | Уникальных: {len(freqs)}"
            )

            # Автоматическая настройка слайдера под размер загруженного текста
            slider_max = max(len(words), 500)
            slider_sample_size.configure(to=slider_max)
            slider_sample_size.set(min(len(words), 500))
            lbl_sample_size.configure(text=f"Размерность массива (N): {int(slider_sample_size.get())} слов")

        except Exception as e:
            lbl_words_stats.configure(text=f"Ошибка чтения: {e}")

    btn_load_text = ctk.CTkButton(
        left_panel,
        text="📂 Загрузить текст (.txt)",
        height=38,
        font=("Arial", 13, "bold"),
        fg_color="#37474F",
        hover_color="#263238",
        command=load_text_file
    )
    btn_load_text.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    # ------------------------------------------
    # ПРАВАЯ КОЛОНКА: График и Ползунок размера
    # ------------------------------------------
    right_panel = ctk.CTkFrame(content_frame, fg_color="#F8FAFC", corner_radius=10)
    right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
    right_panel.grid_columnconfigure(0, weight=1)
    right_panel.grid_rowconfigure(0, weight=0)
    right_panel.grid_rowconfigure(1, weight=1)
    right_panel.grid_rowconfigure(2, weight=0)

    lbl_chart_title = ctk.CTkLabel(
        right_panel,
        text="График зависимости: Время (Y, мс) от Размера массива (X, слов)",
        font=("Arial", 16, "bold"),
        text_color="#1E293B"
    )
    lbl_chart_title.grid(row=0, column=0, padx=15, pady=(12, 5), sticky="w")

    chart_container = ctk.CTkFrame(right_panel, fg_color="#FFFFFF", corner_radius=8)
    chart_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

    # Инициализация объекта Figure и холста Matplotlib
    fig = Figure(figsize=(5.5, 4.0), dpi=100, facecolor="#F8FAFC")
    ax = fig.add_subplot(111)

    # Список активных отрисованных кривых для интерактивного наведения
    active_lines = []

    # Всплывающая плашка-подсказка с точными координатами точки
    annot = ax.annotate(
        "", xy=(0, 0), xytext=(12, 12), textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.5", fc="#1E293B", ec="#2563EB", lw=1.5, alpha=0.95),
        color="white", fontsize=10, fontweight="bold"
    )
    annot.set_visible(False)

    canvas = FigureCanvasTkAgg(fig, master=chart_container)

    # Навигационная панель инструментов (масштабирование, лупа, перемещение, сброс вида)
    toolbar = NavigationToolbar2Tk(canvas, chart_container)
    toolbar.config(background="#F8FAFC")
    for child in toolbar.winfo_children():
        try:
            child.config(background="#F8FAFC")
        except Exception:
            pass
    toolbar.update()

    canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=(0, 5))

    def on_hover(event):
        """Отображает всплывающую карточку с точными координатами при наведении курсора на точку."""
        if event.inaxes != ax:
            if annot.get_visible():
                annot.set_visible(False)
                canvas.draw_idle()
            return

        found = False
        for line, name, color in active_lines:
            cont, ind = line.contains(event)
            if cont:
                idx = ind["ind"][0]
                x = line.get_xdata()[idx]
                y = line.get_ydata()[idx]
                annot.xy = (x, y)
                annot.set_text(f"{name}\nN = {int(x)} слов\nВремя = {y:.3f} мс")
                annot.get_bbox_patch().set_edgecolor(color)
                annot.set_visible(True)
                canvas.draw_idle()
                found = True
                break

        if not found and annot.get_visible():
            annot.set_visible(False)
            canvas.draw_idle()

    def on_scroll(event):
        """Осуществляет плавное приближение и отдаление графика колесиком мыши относительно курсора."""
        if event.inaxes != ax:
            return

        scale_factor = 1.2 if event.button == "up" else (1 / 1.2)
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()

        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None:
            return

        new_w = (cur_xlim[1] - cur_xlim[0]) / scale_factor
        new_h = (cur_ylim[1] - cur_ylim[0]) / scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        ax.set_xlim([xdata - new_w * (1 - relx), xdata + new_w * relx])
        ax.set_ylim([ydata - new_h * (1 - rely), ydata + new_h * rely])
        canvas.draw_idle()

    canvas.mpl_connect("motion_notify_event", on_hover)
    canvas.mpl_connect("scroll_event", on_scroll)

    def render_plot():
        """Отрисовывает или обновляет график через matplotlib с плавной перерисовкой."""
        nonlocal active_lines, annot
        ax.clear()
        ax.set_facecolor("#FFFFFF")
        active_lines = []

        # Воссоздаем аннотацию после очистки осей ax.clear()
        annot = ax.annotate(
            "", xy=(0, 0), xytext=(12, 12), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", fc="#1E293B", ec="#2563EB", lw=1.5, alpha=0.95),
            color="white", fontsize=10, fontweight="bold"
        )
        annot.set_visible(False)

        # Форматирование отображения координат в нижней строке состояния тулбара
        ax.format_coord = lambda x, y: f"N: {int(x) if x > 0 else 0} слов | Время: {max(0, y):.3f} мс"

        algo_configs = [
            ("QuickSort", var_quick.get(), "#2563EB", "o-"),
            ("MergeSort", var_merge.get(), "#EA580C", "s-"),
            ("RadixSort (LSD)", var_radix.get(), "#16A34A", "^-"),
            ("HeapSort", var_heap.get(), "#9333EA", "d-"),
        ]

        has_data = False
        bench_data = screen3_data.get("benchmark_results", {})

        for name, is_enabled, color, marker in algo_configs:
            if is_enabled and name in bench_data and bench_data[name]:
                x_vals = [pt[0] for pt in bench_data[name]]
                y_vals = [pt[1] for pt in bench_data[name]]
                line, = ax.plot(
                    x_vals,
                    y_vals,
                    marker,
                    label=name,
                    color=color,
                    linewidth=2,
                    markersize=6,
                    picker=5
                )
                active_lines.append((line, name, color))
                has_data = True

        ax.set_title("Сравнение времени сортировки от размера массива N", fontsize=11, fontweight="bold", pad=10, color="#1E293B")
        ax.set_xlabel("Размер массива слов (N)", fontsize=10, color="#1E293B")
        ax.set_ylabel("Время выполнения (мс)", fontsize=10, color="#1E293B")
        ax.grid(True, linestyle="--", alpha=0.5, color="#CBD5E1")
        ax.tick_params(colors="#475569")
        for spine in ax.spines.values():
            spine.set_color("#CBD5E1")

        if has_data:
            ax.legend(loc="upper left", fontsize=9, framealpha=0.9, edgecolor="#CBD5E1")
        else:
            ax.text(
                0.5, 0.5,
                "Нажмите «▶ Запустить замеры» для построения графика\n(Колесико мыши: масштаб, наведение на точку: координаты)",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
                fontsize=11,
                color="#64748B"
            )

        fig.tight_layout()
        toolbar.update()
        canvas.draw()

    render_plot()

    # Панель управления графиком (ползунок и кнопка замеров)
    bottom_controls = ctk.CTkFrame(right_panel, fg_color="transparent")
    bottom_controls.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
    bottom_controls.grid_columnconfigure(0, weight=1)
    bottom_controls.grid_columnconfigure(1, weight=0)

    slider_frame = ctk.CTkFrame(bottom_controls, fg_color="transparent")
    slider_frame.grid(row=0, column=0, sticky="ew", padx=(0, 15))
    slider_frame.grid_columnconfigure(0, weight=1)

    lbl_sample_size = ctk.CTkLabel(
        slider_frame,
        text="Размерность массива (N): 500 слов",
        font=("Arial", 13, "bold"),
        text_color="#1E293B"
    )
    lbl_sample_size.grid(row=0, column=0, sticky="w")

    def on_slider_change(val):
        lbl_sample_size.configure(text=f"Размерность массива (N): {int(val)} слов")

    slider_sample_size = ctk.CTkSlider(
        slider_frame,
        from_=10,
        to=5000,
        number_of_steps=99,
        command=on_slider_change
    )
    slider_sample_size.set(500)
    slider_sample_size.grid(row=1, column=0, sticky="ew", pady=(4, 0))

    def run_benchmark():
        """Запускает серию замеров времени сортировки для размеров списков от 1 до max_n."""
        words_source = screen3_data.get("all_words", [])
        max_n = int(slider_sample_size.get())

        # Генерируем серию выборок слов различной длины от 1 до max_n
        batches = generate_test_batches(max_n, words_source)

        # Список алгоритмов, отмеченных чекбоксами
        algos = []
        if var_quick.get():
            algos.append(("QuickSort", quick_sort_strings))
        if var_merge.get():
            algos.append(("MergeSort", merge_sort_strings))
        if var_radix.get():
            algos.append(("RadixSort (LSD)", radix_sort_strings))
        if var_heap.get():
            algos.append(("HeapSort", heap_sort_strings))

        if not algos:
            lbl_words_stats.configure(text="Выберите хотя бы один алгоритм вверху!")
            return

        results = {name: [] for name, _ in algos}

        # Замеряем время сортировки на каждой размерности
        for n, sample_words in batches:
            for name, func in algos:
                # Передаем копию списка, чтобы все алгоритмы сортировали исходный массив в одинаковом состоянии
                sample_copy = list(sample_words)
                t0 = time.perf_counter()
                func(sample_copy)
                t1 = time.perf_counter()
                elapsed_ms = (t1 - t0) * 1000.0
                results[name].append((n, round(elapsed_ms, 3)))

        screen3_data["benchmark_results"] = results
        render_plot()

        source_label = f"файлу ({screen3_data['file_name']})" if screen3_data.get("file_name") else "сгенерированному словарю"
        lbl_words_stats.configure(
            text=f"Замеры выполнены: от 1 до {max_n} слов (точек: {len(batches)}) по {source_label}."
        )

    btn_benchmark = ctk.CTkButton(
        bottom_controls,
        text="▶ Запустить замеры",
        height=38,
        font=("Arial", 13, "bold"),
        fg_color="#2E7D32",
        hover_color="#1B5E20",
        command=run_benchmark
    )
    btn_benchmark.grid(row=0, column=1, sticky="e")

    return frame
