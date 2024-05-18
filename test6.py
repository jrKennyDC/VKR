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
        root.title("Player Characteristics, Voting Menu, and Host Menu")

        # Создаем фрейм для характеристик игроков
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

        # Функция для отображения меню голосования
        def show_voting_menu():
            # Функция для обработки голосования
            def vote():
                selected_player = player_listbox.curselection()
                if selected_player:
                    player_id = selected_player[0] + 1
                    print(f"Player {player_id} received a vote!")
                    # Здесь можно добавить код для сохранения голоса в базе данных
                else:
                    print("Please select a player to vote for.")

            # Создаем новое окно для голосования
            voting_window = tk.Toplevel(root)
            voting_window.title("Voting Menu")

            # Виджет для списка игроков
            player_listbox = tk.Listbox(voting_window, width=20)
            player_listbox.pack(padx=10, pady=10)

            for player_id in range(1, 11):
                player_listbox.insert(tk.END, f"Player {player_id}")

            # Кнопка для голосования
            vote_button = tk.Button(voting_window, text="Vote", command=vote)
            vote_button.pack(pady=10)

        # Функция для отображения меню ведущего
        def show_host_menu():
            # В данном примере просто печатаем сообщение при выборе ведущего
            print("Host menu selected.")

        # Создаем кнопку "Меню голосования"
        voting_menu_button = tk.Button(root, text="Меню голосования", command=show_voting_menu)
        voting_menu_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Создаем кнопку "Меню ведущего"
        host_menu_button = tk.Button(root, text="Меню ведущего", command=show_host_menu)
        host_menu_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Виджет для видеопотока
        video_label = tk.Label(root)
        video_label.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="nsew")

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
