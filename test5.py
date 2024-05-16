import psycopg2
import random

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

        # Получаем список всех строк в таблице player
        cursor.execute("SELECT * FROM player_characteristics")
        rows = cursor.fetchall()

        # Выбираем 10 случайных строк
        random_rows = random.sample(rows, 10)

        # Выводим случайные значения из каждого столбца для каждой выбранной строки
        for row in random_rows:
            print("------------")
            for _ in range(10):  # Выводим 10 случайных значений из каждой строки
                random_column = random.choice(columns)
                value_index = columns.index(random_column)
                value = row[value_index]  # Получаем значение из выбранного столбца

                print(f"{random_column.capitalize()}: {value}")

        conn.close()

# Вызываем метод для вывода случайных значений
get_random_characteristics_from_db()
