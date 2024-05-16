import psycopg2
import random
import tkinter as tk

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

        # Создаем метки для отображения данных игроков
        for player_id, data in players_data.items():
            player_frame = tk.Frame(root, relief=tk.RIDGE, borderwidth=2)
            player_frame.pack(pady=5)

            player_label = tk.Label(player_frame, text=f"Player {player_id}:", font=("Arial", 12, "bold"))
            player_label.pack()

            for column, value in data:
                label_text = f"{column.capitalize()}: {value}"
                column_label = tk.Label(player_frame, text=label_text)
                column_label.pack()

        root.mainloop()

# Вызываем метод для вывода распределенных данных игроков
get_random_characteristics_from_db()

