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

def get_characteristics_from_db(column, text_widget):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT {column} FROM player_characteristics")
        values = cursor.fetchmany(10)
        text_widget.insert(tk.END, f"Values from column '{column}':\n")
        for value in values:
            text_widget.insert(tk.END, f"{value[0]}\n")

        conn.close()

def on_button_click():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()

        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'player_characteristics'")
        columns = [column[0] for column in cursor.fetchall()]

        conn.close()

        root = tk.Tk()
        root.title("Random Data")

        # Создаем текстовые виджеты для каждого пакета данных
        profession_text_widget = tk.Text(root, height=10, width=30)
        biology_text_widget = tk.Text(root, height=10, width=30)
        health_text_widget = tk.Text(root, height=10, width=30)
        hobby_text_widget = tk.Text(root, height=10, width=30)
        luggage_text_widget = tk.Text(root, height=10, width=30)
        additional_fact_text_widget = tk.Text(root, height=10, width=30)
        special_condition_text_widget = tk.Text(root, height=10, width=30)

        # Располагаем текстовые виджеты на форме
        profession_text_widget.grid(row=0, column=0)
        biology_text_widget.grid(row=0, column=1)
        health_text_widget.grid(row=1, column=0)
        hobby_text_widget.grid(row=1, column=1)
        luggage_text_widget.grid(row=2, column=0)
        additional_fact_text_widget.grid(row=2, column=1)
        special_condition_text_widget.grid(row=3, column=0, columnspan=2)

        for column in columns:
            # Получаем значения для каждого столбца и вставляем их в соответствующий текстовый виджет
            text_widget = get_text_widget_by_column(column, locals())
            get_characteristics_from_db(column, text_widget)

        root.mainloop()

def get_text_widget_by_column(column, widgets):
    # Определяем, в какой текстовый виджет вставлять значения для данного столбца
    if column == 'profession':
        return widgets['profession_text_widget']
    elif column == 'biology':
        return widgets['biology_text_widget']
    elif column == 'health':
        return widgets['health_text_widget']
    elif column == 'hobby':
        return widgets['hobby_text_widget']
    elif column == 'luggage':
        return widgets['luggage_text_widget']
    elif column == 'additional_fact':
        return widgets['additional_fact_text_widget']
    elif column == 'special_condition':
        return widgets['special_condition_text_widget']

def main():
    root = tk.Tk()
    root.title("Random Data")

    button = tk.Button(root, text="Show All Characteristics", command=on_button_click)
    button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
