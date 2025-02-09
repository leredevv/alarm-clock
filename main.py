import customtkinter as ctk
from tkinter import filedialog, messagebox
import time
from threading import Thread, Event
import pygame  # Импортируем pygame

# Инициализация pygame mixer
pygame.mixer.init()

# Глобальные переменные
stop_alarm_event = Event()
alarm_thread_instance = None
alarm_window = None
sound = None  # Глобальная переменная для хранения объекта sound
relax_sound = None  # Глобальная переменная для хранения объекта расслабляющего звука
relax_thread_instance = None  # Поток для расслабляющего звука

# Настройка темы customtkinter
ctk.set_appearance_mode("System")  # Системная тема (светлая/темная)
ctk.set_default_color_theme("blue")  # Цветовая тема

# Функция для запуска будильника
def start_alarm():
    global alarm_thread_instance, sound
    # Получаем выбранное время
    hours = int(hour_var.get())
    minutes = int(minute_var.get())
    alarm_time = f"{hours:02}:{minutes:02}"  # Формат времени: часы и минуты

    # Получаем путь к звуковому файлу
    sound_file = file_path.get()
    if not sound_file:
        messagebox.showerror("Ошибка", "Выберите звуковой файл для будильника!")
        return

    # Меняем текст кнопки и функцию
    start_button.configure(text="Отменить будильник", command=stop_alarm)

    # Запускаем будильник в отдельном потоке
    def alarm_thread():
        global alarm_thread_instance, alarm_window, sound
        try:
            while not stop_alarm_event.is_set():
                current_time = time.strftime("%H:%M")  # Текущее время без секунд
                if current_time == alarm_time:
                    # Создаем окно с кнопками
                    root.after(0, create_alarm_window)
                    try:
                        sound = pygame.mixer.Sound(sound_file)
                        sound.play()
                    except Exception as e:
                        print(f"Ошибка воспроизведения звука: {e}")
                    break
                time.sleep(1)
        except Exception as e:
            print(f"Ошибка в потоке будильника: {e}")
        finally:
            stop_alarm_event.clear()  # Сбрасываем флаг для следующего запуска
            root.after(0, reset_alarm_settings)  # Сбрасываем настройки времени
            root.after(0, start_button.configure, {"text": "Запустить будильник", "command": start_alarm})  # Возвращаем кнопку в исходное состояние
            alarm_thread_instance = None  # Сбрасываем ссылку на поток
            stop_relax_sound()  # Останавливаем расслабляющий звук

    stop_alarm_event.clear()  # Убедитесь, что флаг сброшен перед запуском
    alarm_thread_instance = Thread(target=alarm_thread, daemon=True)
    alarm_thread_instance.start()

# Функция для создания окна с кнопками
def create_alarm_window():
    global alarm_window
    alarm_window = ctk.CTkToplevel(root)
    alarm_window.title("Будильник")
    alarm_window.geometry("200x100")
    alarm_window.protocol("WM_DELETE_WINDOW", stop_alarm)  # Обработка закрытия окна

    # Кнопка "Выключить"
    off_button = ctk.CTkButton(alarm_window, text="Выключить", command=stop_alarm)
    off_button.pack(pady=10, padx=10, side=ctk.LEFT)

    # Кнопка "Отложить"
    snooze_button = ctk.CTkButton(alarm_window, text="Отложить", command=snooze)
    snooze_button.pack(pady=10, padx=10, side=ctk.RIGHT)

# Функция для остановки будильника
def stop_alarm():
    global alarm_thread_instance, alarm_window, sound
    stop_alarm_event.set()  # Устанавливаем флаг остановки
    # Останавливаем воспроизведение звука, если оно идет
    if sound:
        sound.stop()
        sound = None  # Сбрасываем ссылку на объект sound
    # Сбрасываем настройки и возвращаем кнопку в исходное состояние
    if alarm_window:
        alarm_window.destroy()
    stop_relax_sound()  # Останавливаем расслабляющий звук

# Функция для откладывания будильника
def snooze():
    global alarm_window
    stop_alarm()  # Останавливаем текущий будильник

    # Получаем текущее время и добавляем 5 минут
    current_time = time.localtime()
    new_time = time.mktime(current_time) + 300  # Добавляем 5 минут (300 секунд)
    new_time = time.localtime(new_time)

    # Устанавливаем новое время для будильника
    hour_var.set(f"{new_time.tm_hour:02}")
    minute_var.set(f"{new_time.tm_min:02}")

    start_alarm()  # Запускаем будильник снова
    if alarm_window:
        alarm_window.destroy()

# Функция для сброса настроек времени
def reset_alarm_settings():
    hour_var.set("00")
    minute_var.set("00")

# Функция для выбора звукового файла для будильника
def choose_alarm_file():
    file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if file:
        file_path.set(file)
        alarm_file_label.configure(text=file.split("/")[-1])  # Отображаем имя файла

# Функция для выбора звукового файла для расслабляющего звука
def choose_relax_file():
    file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
    if file:
        relax_file_path.set(file)
        relax_file_label.configure(text=file.split("/")[-1])  # Отображаем имя файла

# Функция для запуска расслабляющего звука
def start_relax_sound():
    global relax_sound, relax_thread_instance
    relax_file = relax_file_path.get()
    if not relax_file:
        messagebox.showerror("Ошибка", "Выберите звуковой файл для расслабляющего звука!")
        return

    # Останавливаем предыдущий звук, если он играет
    stop_relax_sound()

    # Запускаем расслабляющий звук в отдельном потоке
    def relax_thread():
        global relax_sound
        try:
            relax_sound = pygame.mixer.Sound(relax_file)
            relax_sound.play(-1)  # Бесконечное воспроизведение
        except Exception as e:
            print(f"Ошибка воспроизведения расслабляющего звука: {e}")

    relax_thread_instance = Thread(target=relax_thread, daemon=True)
    relax_thread_instance.start()

# Функция для остановки расслабляющего звука
def stop_relax_sound():
    global relax_sound, relax_thread_instance
    if relax_sound:
        relax_sound.stop()
        relax_sound = None
    if relax_thread_instance:
        relax_thread_instance = None

# Функция для прокрутки чисел колесиком мыши
def on_mouse_wheel(event, var, min_val, max_val):
    if event.delta > 0:
        new_value = int(var.get()) + 1
    else:
        new_value = int(var.get()) - 1
    # Обеспечиваем "бесконечное" перелистывание
    if new_value > max_val:
        new_value = min_val
    elif new_value < min_val:
        new_value = max_val
    var.set(f"{new_value:02}")

# Создаем главное окно
root = ctk.CTk()
root.title("Будильник")
root.geometry("400x350")  # Увеличиваем высоту окна

# Переменные для хранения выбранного времени и пути к файлу
hour_var = ctk.StringVar(value="00")
minute_var = ctk.StringVar(value="00")
file_path = ctk.StringVar()
relax_file_path = ctk.StringVar()

# Контейнер для выбора времени
time_frame = ctk.CTkFrame(root)
time_frame.pack(pady=20)

# Поле для часов
hour_label = ctk.CTkLabel(time_frame, textvariable=hour_var, font=("Arial", 24), width=50, height=50, corner_radius=10, fg_color="gray", text_color="white")
hour_label.pack(side=ctk.LEFT, padx=10)
hour_label.bind("<MouseWheel>", lambda event: on_mouse_wheel(event, hour_var, 0, 23))

# Двоеточие
colon_label = ctk.CTkLabel(time_frame, text=":", font=("Arial", 24))
colon_label.pack(side=ctk.LEFT, padx=10)

# Поле для минут
minute_label = ctk.CTkLabel(time_frame, textvariable=minute_var, font=("Arial", 24), width=50, height=50, corner_radius=10, fg_color="gray", text_color="white")
minute_label.pack(side=ctk.LEFT, padx=10)
minute_label.bind("<MouseWheel>", lambda event: on_mouse_wheel(event, minute_var, 0, 59))

# Кнопка для выбора звука будильника
alarm_button = ctk.CTkButton(root, text="Выбрать звук будильника", command=choose_alarm_file)
alarm_button.pack(pady=10)

# Метка для отображения выбранного звука будильника
alarm_file_label = ctk.CTkLabel(root, text="Файл не выбран", font=("Arial", 12))
alarm_file_label.pack()

# Кнопка для выбора расслабляющего звука
relax_button = ctk.CTkButton(root, text="Выбрать расслабляющий звук", command=choose_relax_file)
relax_button.pack(pady=10)

# Метка для отображения выбранного расслабляющего звука
relax_file_label = ctk.CTkLabel(root, text="Файл не выбран", font=("Arial", 12))
relax_file_label.pack()

# Кнопка запуска расслабляющего звука
start_relax_button = ctk.CTkButton(root, text="Запустить расслабляющий звук", command=start_relax_sound)
start_relax_button.pack(pady=10)

# Кнопка запуска будильника
start_button = ctk.CTkButton(root, text="Запустить будильник", command=start_alarm)
start_button.pack(pady=20)

# Запуск главного цикла
root.mainloop()