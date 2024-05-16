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

        # Создаем вкладки для списка игроков и характеристик
        notebook = ttk.Notebook(root)
        notebook.pack(fill='both', expand=True)

        # Вкладка для списка игроков
        player_list_tab = ttk.Frame(notebook)
        notebook.add(player_list_tab, text='Player List')

        # Создаем список игроков
        player_listbox = tk.Listbox(player_list_tab, width=20)
        player_listbox.pack(pady=10)

        for player_id in range(1, 11):
            player_listbox.insert(tk.END, f"Player {player_id}")

        # Вкладка для отображения характеристик игрока
        characteristics_tab = ttk.Frame(notebook)
        notebook.add(characteristics_tab, text='Player Characteristics')

        # Функция для отображения характеристик выбранного игрока
        def show_player_characteristics(event):
            selected_player = player_listbox.curselection()[0] + 1
            characteristics_frame = ttk.LabelFrame(characteristics_tab, text=f"Player {selected_player} Characteristics")
            characteristics_frame.pack(padx=10, pady=10)

            for column, value in players_data[selected_player]:
                label_text = f"{column.capitalize()}: {value}"
                column_label = tk.Label(characteristics_frame, text=label_text)
                column_label.pack()

        player_listbox.bind('<<ListboxSelect>>', show_player_characteristics)

        # Вкладка для видеопотока
        video_tab = ttk.Frame(notebook)
        notebook.add(video_tab, text='Video Stream')

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

        video_label = tk.Label(video_tab)
        video_label.pack()

        show_video_stream()

        root.mainloop()

# Вызываем метод для вывода распределенных данных игроков
get_random_characteristics_from_db()
