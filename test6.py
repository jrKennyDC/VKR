import psycopg2
import random
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import socket
import threading

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

        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'player_characteristics'")
        columns = [column[0] for column in cursor.fetchall()]

        players_data = {}

        for column in columns:
            cursor.execute(f"SELECT {column} FROM player_characteristics")
            values = cursor.fetchall()

            for player_id in range(1, 11):
                random_value = random.choice(values)[0]
                if player_id not in players_data:
                    players_data[player_id] = []
                players_data[player_id].append((column, random_value))

        root = tk.Tk()
        root.title("Player Characteristics")

        characteristics_frame = ttk.LabelFrame(root, text="Player Characteristics", width=50)
        characteristics_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        player_listbox = tk.Listbox(root, width=20)
        player_listbox.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        for player_id in range(1, 11):
            player_listbox.insert(tk.END, f"Player {player_id}")

        def show_player_characteristics(event):
            if player_listbox.curselection():
                selected_player = player_listbox.curselection()[0] + 1
                display_player_characteristics(selected_player)

        player_listbox.bind('<<ListboxSelect>>', show_player_characteristics)

        def display_player_characteristics(selected_player):
            for widget in characteristics_frame.winfo_children():
                widget.destroy()
            for column, value in players_data[selected_player]:
                label_text = f"{column.capitalize()}: {value}"
                column_label = tk.Label(characteristics_frame, text=label_text, wraplength=150)
                column_label.pack()

        def show_change_menu():
            selected_players = []

            def apply_changes():
                for player_id in selected_players:
                    print(f"Updating characteristics for Player {player_id}...")
                    update_player_characteristics(player_id)
                    update_player_display(player_id)
                conn.commit()

            player_selection_frame = ttk.LabelFrame(root, text="Select Players")
            player_selection_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

            def select_player(event):
                selected_players.clear()
                for index in player_listbox.curselection():
                    selected_players.append(index + 1)

            player_listbox_select = tk.Listbox(player_selection_frame, width=20, selectmode=tk.MULTIPLE)
            player_listbox_select.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)
            player_listbox_select.bind('<<ListboxSelect>>', select_player)

            for player_id in range(1, 11):
                player_listbox_select.insert(tk.END, f"Player {player_id}")

            change_characteristics_frame = ttk.LabelFrame(root, text="Change Characteristics")
            change_characteristics_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

            selected_characteristics = []

            apply_button = tk.Button(root, text="Apply Changes", command=apply_changes)
            apply_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

            def update_player_characteristics(player_id):
                updated_values = [(column, var.get()) for column, var in selected_characteristics if var.get()]
                if updated_values:
                    cursor = conn.cursor()
                    try:
                        for column, value in updated_values:
                            cursor.execute(f"UPDATE player_characteristics SET {column} = %s WHERE id = %s",
                                           (value, player_id))
                        print(f"Characteristics updated for Player {player_id}: {updated_values}")
                    except psycopg2.Error as e:
                        conn.rollback()
                        print("Error updating player characteristics:", e)
                    finally:
                        cursor.close()
                else:
                    print(f"No values selected for update for Player {player_id}")

            def display_selected_characteristics():
                for widget in change_characteristics_frame.winfo_children():
                    widget.destroy()
                for column in columns:
                    var = tk.StringVar()
                    checkbox = ttk.Checkbutton(change_characteristics_frame, text=column.capitalize(), variable=var)
                    checkbox.pack(side=tk.TOP, padx=5, pady=5)
                    selected_characteristics.append((column, var))

            display_button = tk.Button(root, text="Select Characteristics to Update",
                                       command=display_selected_characteristics)
            display_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

            voting_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        def show_voting_menu():
            global votes
            votes = []

            def vote_for_player():
                if player_listbox.curselection():
                    selected_player = player_listbox.curselection()[0] + 1
                    votes.append(selected_player)
                    voted_label.config(text=f"Голос за игрока {selected_player} засчитан")

            def end_voting():
                vote_count = {}
                for player_id in range(1, 11):
                    vote_count[player_id] = 0

                for vote in votes:
                    vote_count[vote] += 1

                max_votes_player = max(vote_count, key=vote_count.get)

                expelled_label.config(
                    text=f"Игрок под номером {max_votes_player} получил большинство голосов и был изгнан")

            voting_window = tk.Toplevel(root)
            voting_window.title("Voting Menu")

            player_label = tk.Label(voting_window, text="Выберите игрока для голосования:")
            player_label.pack()

            player_listbox = tk.Listbox(voting_window, width=20)
            player_listbox.pack()

            for player_id in range(1, 11):
                player_listbox.insert(tk.END, f"Player {player_id}")

            vote_button = tk.Button(voting_window, text="Проголосовать", command=vote_for_player)
            vote_button.pack()

            voted_label = tk.Label(voting_window, text="")
            voted_label.pack()

            end_voting_button = tk.Button(voting_window, text="Окончить этап голосования", command=end_voting)
            end_voting_button.pack()

            expelled_label = tk.Label(voting_window, text="")
            expelled_label.pack()

        menu_button = tk.Button(root, text="Меню ведущего", command=show_change_menu)
        menu_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        voting_button = tk.Button(root, text="Меню голосования", command=show_voting_menu)
        voting_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        video_label = tk.Label(root)
        video_label.grid(row=0, column=2, rowspan=4, padx=10, pady=10, sticky="nsew")

        def show_video_stream():
            def update():
                nonlocal frame_image  # Declare frame_image as nonlocal
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = Image.fromarray(frame)
                    frame_image = ImageTk.PhotoImage(frame)
                    video_label.configure(image=frame_image)  # Update image in the label
                    video_label.image = frame_image
                video_label.after(10, update)

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Failed to open camera")
                return

            frame_image = None  # Initialize frame_image variable
            update()

        show_video_stream()

        def update_player_display(player_id):
            conn = connect_to_db()
            if conn:
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM player_characteristics WHERE id = %s", (player_id,))
                player_characteristics = cursor.fetchone()

                if player_characteristics:
                    for widget in characteristics_frame.winfo_children():
                        widget.destroy()
                    for i in range(len(columns)):
                        column_label = tk.Label(characteristics_frame,
                                                text=f"{columns[i].capitalize()}: {player_characteristics[i + 1]}",
                                                wraplength=150)
                        column_label.pack()
                else:
                    print(f"No data found for Player {player_id}")

                conn.close()
            else:
                print("Error: Unable to connect to the database.")

        root.mainloop()

    else:
        print("Error: Unable to connect to the database.")


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


# Function to start a TCP server in a separate thread
def start_server():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))  # Bind to localhost on port 9999
    server_socket.listen(5)  # Listen for incoming connections

    print("Server started.")

    # Function to handle client connections
    def handle_client(client_socket):
        while True:
            data = client_socket.recv(1024)  # Receive data from the client
            if not data:
                break
            print("Received:", data.decode())
            # Here you can implement logic to process received data

        client_socket.close()

    # Accept incoming connections and start a new thread for each client
    while True:
        client_socket, address = server_socket.accept()
        print("Accepted connection from:", address)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

# Function to send data to the server
def send_data(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 9999))  # Connect to the server
    client_socket.send(data.encode())  # Send data to the server
    client_socket.close()

# Example usage in your tkinter application
# Assuming you have a button that sends data when clicked

def button_click():
    data = "Hello from client"
    send_data(data)

# Start the server in a separate thread
server_thread = threading.Thread(target=start_server)
server_thread.start()

root = tk.Tk()
root.title("Random Catastrophe Information")

info_frame = ttk.LabelFrame(root, text="Random Catastrophe Information")
info_frame.pack(padx=10, pady=10)


def update_catastrophe_info():
    for widget in info_frame.winfo_children():
        widget.destroy()

    catastrophe_type = get_random_catastrophe()
    bunkers = get_random_bunkers()
    threats = get_random_threats()

    tk.Label(info_frame, text="Random Catastrophe Type:").pack()
    tk.Label(info_frame, text=catastrophe_type).pack()

    tk.Label(info_frame, text="Random Bunkers:").pack()
    for bunker in bunkers:
        tk.Label(info_frame, text=bunker).pack()

    tk.Label(info_frame, text="Random Threats:").pack()
    for threat in threats:
        tk.Label(info_frame, text=threat).pack()


update_button = ttk.Button(root, text="Update Information", command=update_catastrophe_info)
update_button.pack(pady=10)

update_catastrophe_info()
get_random_characteristics_from_db()
root.mainloop()
