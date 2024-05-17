import psycopg2
import random
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk

# Подключение к базе данных
def connect_to_db():
    try:
        conn = psycopg2.connect(dbname='bunker', user='postgres', password='64701813092001m', host='localhost')
        return conn
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL:", e)
        return None

# Функция для получения случайных характеристик игроков из базы данных
def get_random_characteristics_from_db():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()

        # Получаем список всех столбцов в таблице player
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'player_characteristics'")
        columns = [column[0] for column in cursor.fetchall()]

        # Создаем словарь для хранения данных игроков
        players_data = {}

        # Выбираем случайный столбец
        for column in columns:
            # Получаем все значения из текущего столбца
            cursor.execute(f"SELECT {column} FROM player_characteristics")
            values = cursor.fetchall()

            # Случайно выбираем значение для каждого игрока
            for player_id in range(1, 11):  # Предполагаем, что есть 10 игроков
                random_value = random.choice(values)[0]
                # Добавляем значение к данным игрока
                if player_id not in players_data:
                    players_data[player_id] = []
                players_data[player_id].append((column, random_value))

        conn.close()

        # Создаем Tkinter окно
        root = tk.Tk()
        root.title("Player Characteristics")

        # Виджет для отображения характеристик
        characteristics_frame = ttk.LabelFrame(root, text="Player Characteristics",
                                               width=50)  # Фиксированная ширина в 200 пикселей
        characteristics_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Создаем список игроков
        player_listbox = tk.Listbox(root, width=20)
        player_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        for player_id in range(1, 11):
            player_listbox.insert(tk.END, f"Player {player_id}")

        # Функция для отображения характеристик выбранного игрока
        def show_player_characteristics(event):
            if player_listbox.curselection():
                selected_player = player_listbox.curselection()[0] + 1
                for widget in characteristics_frame.winfo_children():
                    widget.destroy()
                for column, value in players_data[selected_player]:
                    label_text = f"{column.capitalize()}: {value}"
                    column_label = tk.Label(characteristics_frame, text=label_text, wraplength=150)
                    column_label.pack()
            else:
                print("No player selected.")

        player_listbox.bind('<<ListboxSelect>>', show_player_characteristics)

        # Функция для отображения окна внесения изменений
        def show_change_menu():
            # Очистка окна характеристик
            for widget in characteristics_frame.winfo_children():
                widget.destroy()

            # Создание флажков для выбора столбцов
            selected_columns = []

            for column in columns:
                var = tk.BooleanVar()
                checkbox = tk.Checkbutton(characteristics_frame, text=column.capitalize(), variable=var)
                checkbox.pack(side=tk.TOP, padx=5, pady=5)
                selected_columns.append((column, var))

            # Кнопка для применения выбора
            apply_button = tk.Button(characteristics_frame, text="Применить", command=lambda: change_player_characteristics(selected_columns))
            apply_button.pack(side=tk.TOP, padx=5, pady=5)

        # Функция для изменения характеристик определенного игрока
        def change_player_characteristics(selected_columns):
            if player_listbox.curselection():
                selected_player_id = player_listbox.curselection()[0] + 1

                # Очистка окна характеристик
                for widget in characteristics_frame.winfo_children():
                    widget.destroy()

                # Создание списка выпадающих меню для выбора новых значений характеристик
                selection_menus = []

                # Подключение к базе данных
                conn = connect_to_db()
                if conn:
                    cursor = conn.cursor()
                    for column, var in selected_columns:
                        if var.get():
                            # Получение уникальных значений для каждого выбранного столбца
                            cursor.execute(f"SELECT DISTINCT {column} FROM player_characteristics")
                            values = [value[0] for value in cursor.fetchall()]

                            # Создание выпадающего меню
                            label = tk.Label(characteristics_frame, text=f"{column.capitalize()}:")
                            label.pack(side=tk.TOP, padx=5, pady=5)
                            selection = ttk.Combobox(characteristics_frame, values=values)
                            selection.pack(side=tk.TOP, padx=5, pady=5)
                            selection_menus.append((column, selection))

                    # Функция для обновления характеристик игрока
                    def update_player_characteristics():
                        new_values = [selection.get() for _, selection in selection_menus]
                        # Обновление записи в базе данных для выбранного игрока
                        conn = connect_to_db()
                        if conn:
                            cursor = conn.cursor()
                            for column, value in zip(selected_columns, new_values):
                                if column[1].get():
                                    cursor.execute(f"UPDATE player_characteristics SET {column[0]} = %s WHERE id = %s",
                                                   (value, selected_player_id))
                            conn.commit()
                            conn.close()
                            root.destroy()  # Закрываем окно внесения изменений после обновления
                            get_random_characteristics_from_db()  # Перезагружаем данные игроков для отображения обновленных характеристик
                        else:
                            print("Error: Unable to connect to the database.")

                    # Кнопка для подтверждения изменений
                    confirm_button = tk.Button(characteristics_frame, text="Подтвердить", command=update_player_characteristics)
                    confirm_button.pack(side=tk.TOP, padx=5, pady=5)

                else:
                    print("Error: Unable to connect to the database.")
            else:
                print("Error: No player selected.")

        # Создаем кнопку "Меню ведущего"
        menu_button = tk.Button(root, text="Меню ведущего", command=show_change_menu)
        menu_button.pack(side=tk.TOP, padx=10, pady=10)

        # Виджет для видеопотока
        video_label = tk.Label(root)
        video_label.pack(side=tk.BOTTOM, padx=10, pady=10)

        # Функция для отображения видеопотока
        def show_video_stream():
            def update():
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = Image.fromarray(frame)
                    frame = ImageTk.PhotoImage(frame)
                    video_label.configure(image=frame)
                    video_label.image = frame
                video_label.after(10, update)

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():  # Проверяем, удалось ли открыть камеру
                print("Failed to open camera")
                return

            update()  # Запускаем первое обновление

        show_video_stream()

        root.mainloop()

    else:
        print("Error: Unable to connect to the database.")

# Вызываем метод для вывода распределенных данных игроков
get_random_characteristics_from_db()


