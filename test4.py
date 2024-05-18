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

        # Создаем Tkinter окно
        root = tk.Tk()
        root.title("Player Characteristics")

        # Виджет для отображения характеристик
        characteristics_frame = ttk.LabelFrame(root, text="Player Characteristics", width=50)
        characteristics_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Создаем список игроков
        player_listbox = tk.Listbox(root, width=20)
        player_listbox.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        for player_id in range(1, 11):
            player_listbox.insert(tk.END, f"Player {player_id}")

        # Функция для отображения характеристик выбранного игрока
        def show_player_characteristics(event):
            if player_listbox.curselection():
                selected_player = player_listbox.curselection()[0] + 1
                display_player_characteristics(selected_player)

        player_listbox.bind('<<ListboxSelect>>', show_player_characteristics)

        def display_player_characteristics(selected_player):
            for widget in characteristics_frame.winfo_children():
                widget.destroy()
            for column, value in players_data[selected_player]:
                label_text = f"{column.capitalize()}: {value}"
                column_label = tk.Label(characteristics_frame, text=label_text, wraplength=150)
                column_label.pack()

        # Функция для отображения окна внесения изменений
        def show_change_menu():
            selected_players = []  # List to store IDs of selected players

            # Function to handle changes for selected players
            def apply_changes():
                for player_id in selected_players:
                    print(f"Updating characteristics for Player {player_id}...")
                    update_player_characteristics(player_id)
                # Commit changes to the database
                conn.commit()
                # Refresh player data
                refresh_players_data_from_db()

            # UI for selecting players
            player_selection_frame = ttk.LabelFrame(root, text="Select Players")
            player_selection_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

            def select_player(event):
                selected_players.clear()
                for index in player_listbox.curselection():
                    selected_players.append(index + 1)

            player_listbox_select = tk.Listbox(player_selection_frame, width=20, selectmode=tk.MULTIPLE)
            player_listbox_select.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
            player_listbox_select.bind('<<ListboxSelect>>', select_player)

            for player_id in range(1, 11):
                player_listbox_select.insert(tk.END, f"Player {player_id}")

            # UI for changing characteristics
            change_characteristics_frame = ttk.LabelFrame(root, text="Change Characteristics")
            change_characteristics_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

            selected_characteristics = []  # List to store selected characteristics

            # Function to apply changes to selected players
            apply_button = tk.Button(root, text="Apply Changes", command=apply_changes)
            apply_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

            # Function to handle changes for selected players
            def update_player_characteristics(player_id):
                # Get updated values for selected player
                updated_values = [(column, var.get()) for column, var in selected_characteristics if var.get()]
                if updated_values:
                    cursor = conn.cursor()
                    try:
                        for column, value in updated_values:
                            cursor.execute(f"UPDATE player_characteristics SET {column} = %s WHERE id = %s",
                                           (value, player_id))
                        print(f"Characteristics updated for Player {player_id}: {updated_values}")
                    except psycopg2.Error as e:
                        conn.rollback()
                        print("Error updating player characteristics:", e)
                    finally:
                        cursor.close()
                else:
                    print(f"No values selected for update for Player {player_id}")

            # Function to display checkboxes for selecting characteristics
            def display_selected_characteristics():
                for widget in change_characteristics_frame.winfo_children():
                    widget.destroy()
                for column in columns:
                    var = tk.StringVar()
                    checkbox = ttk.Checkbutton(change_characteristics_frame, text=column.capitalize(), variable=var)
                    checkbox.pack(side=tk.TOP, padx=5, pady=5)
                    selected_characteristics.append((column, var))

            # Button to display checkboxes for selecting characteristics
            display_button = tk.Button(root, text="Select Characteristics to Update",
                                       command=display_selected_characteristics)
            display_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Создаем кнопку "Меню ведущего"
        menu_button = tk.Button(root, text="Меню ведущего", command=show_change_menu)
        menu_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Виджет для видеопотока
        video_label = tk.Label(root)
        video_label.grid(row=0, column=2, rowspan=4, padx=10, pady=10, sticky="nsew")

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
