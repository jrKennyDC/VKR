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
            for player_id in range(1, 11):  # Assuming there are 10 players
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
        characteristics_frame = ttk.LabelFrame(root, text="Player Characteristics")
        characteristics_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Создаем список игроков
        player_listbox = tk.Listbox(root, width=20)
        player_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

        for player_id in range(1, 11):
            player_listbox.insert(tk.END, f"Player {player_id}")

        # Функция для отображения характеристик выбранного игрока
        def show_player_characteristics(event):
            selected_player = player_listbox.curselection()[0] + 1
            for widget in characteristics_frame.winfo_children():
                widget.destroy()
            for column, value in players_data[selected_player]:
                label_text = f"{column.capitalize()}: {value}"
                column_label = tk.Label(characteristics_frame, text=label_text)
                column_label.pack()

        player_listbox.bind('<<ListboxSelect>>', show_player_characteristics)

        # Виджет для видеопотока
        video_label = tk.Label(root)
        video_label.pack(side=tk.BOTTOM, padx=10, pady=10)

        # Функция для отображения видеопотока
        def show_video_stream():
            cap = cv2.VideoCapture(0)

            def update():
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = Image.fromarray(frame)
                    frame = ImageTk.PhotoImage(frame)
                    video_label.configure(image=frame)
                    video_label.image = frame
                video_label.after(10, update)

            update()

            cap.release()

        show_video_stream()

        root.mainloop()

# Вызываем метод для вывода распределенных данных игроков
get_random_characteristics_from_db()
