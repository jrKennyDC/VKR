import tkinter as tk
import psycopg2

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

        text_widgets = []
        for column in columns:
            text_widget = tk.Text(root, height=10, width=30)
            text_widget.pack()
            text_widgets.append(text_widget)
            get_characteristics_from_db(column, text_widget)

        root.mainloop()

def main():
    root = tk.Tk()
    root.title("Random Data")

    button = tk.Button(root, text="Show All Characteristics", command=on_button_click)
    button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
