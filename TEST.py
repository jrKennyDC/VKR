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

        # Выбираем случайный столбец из списка столбцов
        random_column_index = random.randint(0, len(columns) - 1)
        random_column = columns[random_column_index]

        # Выводим 10 значений из выбранного столбца
        print(f"Values from column '{random_column}':")
        cursor.execute(f"SELECT {random_column} FROM player_characteristics")
        values = cursor.fetchmany(10)
        for value in values:
            print(value[0])

        # Удаляем выбранный столбец из списка столбцов
        del columns[random_column_index]

        # Если остались ещё столбцы, выбираем новый случайный столбец и выводим из него 10 значений
        while columns:
            random_column_index = random.randint(0, len(columns) - 1)
            random_column = columns[random_column_index]

            print(f"\nValues from column '{random_column}':")
            cursor.execute(f"SELECT {random_column} FROM player_characteristics")
            values = cursor.fetchmany(10)
            for value in values:
                print(value[0])

            del columns[random_column_index]

        conn.close()

# Вызываем метод для вывода случайных значений из случайных столбцов таблицы
get_random_characteristics_from_db()
