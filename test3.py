import tkinter as tk
import psycopg2
import random

def connect_to_db():
    try:
        conn = psycopg2.connect(dbname='bunker', user='postgres', password='64701813092001m', host='localhost')
        return conn
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL:", e)
        return None

def get_random_characteristics_from_db(column):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()

        root = tk.Tk()
        root.title("Random Data")

        label = tk.Label(root, text=f"Values from column '{column}':")
        label.pack()

        # Выводим 10 значений из выбранного столбца
        cursor.execute(f"SELECT {column} FROM player_characteristics")
        values = cursor.fetchmany(10)
        for value in values:
            if column == 'special_condition':
                text = tk.Text(root, height=4, width=40)  # Увеличиваем высоту для столбца 'special_condition'
            else:
                text = tk.Text(root, height=2, width=40)
            text.insert(tk.END, value[0])
            text.pack()

        conn.close()

        root.mainloop()

def on_button_click(column):
    get_random_characteristics_from_db(column)

def main():
    root = tk.Tk()
    root.title("Random Data")

    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()

        # Получаем список всех столбцов в таблице player
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'player_characteristics'")
        columns = [column[0] for column in cursor.fetchall()]

        conn.close()

        # Создаем кнопку для каждого столбца
        for column in columns:
            button = tk.Button(root, text=f"Show {column}", command=lambda col=column: on_button_click(col))
            button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
