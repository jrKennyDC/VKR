import tkinter as tk
from tkinter import ttk
import psycopg2


# Подключение к базе данных
def connect_to_db():
    try:
        conn = psycopg2.connect(dbname='bunker', user='postgres', password='64701813092001m', host='localhost')
        return conn
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL:", e)
        return None


def get_random_catastrophe():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT type FROM catastrophe ORDER BY random() LIMIT 1")
        catastrophe_type = cursor.fetchone()[0]
        conn.close()
        return catastrophe_type


def get_random_bunkers():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT bunkers FROM catastrophe ORDER BY random() LIMIT 3")
        bunkers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return bunkers


def get_random_threats():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT threat FROM catastrophe ORDER BY random() LIMIT 2")
        threats = [row[0] for row in cursor.fetchall()]
        conn.close()
        return threats


# Создаем графический интерфейс
root = tk.Tk()
root.title("Random Catastrophe Information")

# Фрейм для отображения информации
info_frame = ttk.LabelFrame(root, text="Random Catastrophe Information")
info_frame.pack(padx=10, pady=10)


# Функция для обновления информации о катастрофе
def update_catastrophe_info():
    # Очищаем предыдущую информацию
    for widget in info_frame.winfo_children():
        widget.destroy()

    # Получаем случайные значения
    catastrophe_type = get_random_catastrophe()
    bunkers = get_random_bunkers()
    threats = get_random_threats()

    # Выводим полученную информацию
    tk.Label(info_frame, text="Random Catastrophe Type:").pack()
    tk.Label(info_frame, text=catastrophe_type).pack()

    tk.Label(info_frame, text="Random Bunkers:").pack()
    for bunker in bunkers:
        tk.Label(info_frame, text=bunker).pack()

    tk.Label(info_frame, text="Random Threats:").pack()
    for threat in threats:
        tk.Label(info_frame, text=threat).pack()


# Кнопка для обновления информации
update_button = ttk.Button(root, text="Update Information", command=update_catastrophe_info)
update_button.pack(pady=10)

# Инициализация первоначальной информации
update_catastrophe_info()

root.mainloop()
