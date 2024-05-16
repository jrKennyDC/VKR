import psycopg2
import random
import dearpygui.dearpygui as dpg

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

        # Очищаем предыдущий вывод, если есть
        dpg.delete_item("output")

        # Создаем таблицу
        dpg.add_table("output", headers=columns)

        # Выбираем случайный столбец из списка столбцов
        random_column_index = random.randint(0, len(columns) - 1)
        random_column = columns[random_column_index]

        # Выводим 10 значений из выбранного столбца
        cursor.execute(f"SELECT {random_column} FROM player_characteristics")
        values = cursor.fetchmany(10)
        for value in values:
            dpg.add_row("output", [str(val) for val in value])

        # Удаляем выбранный столбец из списка столбцов
        del columns[random_column_index]

        # Если остались ещё столбцы, выбираем новый случайный столбец и выводим из него 10 значений
        while columns:
            random_column_index = random.randint(0, len(columns) - 1)
            random_column = columns[random_column_index]

            # Выводим 10 значений из выбранного столбца
            cursor.execute(f"SELECT {random_column} FROM player_characteristics")
            values = cursor.fetchmany(10)
            for value in values:
                dpg.add_row("output", [str(val) for val in value])

            del columns[random_column_index]

        conn.close()

# Создаем окно Dear PyGui



# Создаем окно Dear PyGui
def main():
    with dpg.window(label="Database Data", width=700, height=500):
        # Добавляем кнопку для получения данных из базы данных
        dpg.add_button(label="Get Data", callback=get_random_characteristics_from_db)

    # Запускаем основной цикл Dear PyGui
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()


if __name__ == "__main__":
    main()

