from tkinter import *
import subprocess
import socket
from pynput.keyboard import Key, Controller
from pynput import keyboard
import json
import threading

WIDTH = 500 / 1.3
HEIGHT = (600 / 1.3) + 100

font1 = ("Arial", 12)

the_ip = []

root = Tk()
root.title("Keylogger")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = ((screen_width / 2) - (WIDTH / 2))
y = ((screen_height / 2) - (HEIGHT / 2))

root.geometry(f'{int(WIDTH)}x{int(HEIGHT)}+{int(x)}+{int(y) - 30}')
root.resizable(False, False)


# selected_option = StringVar()
# selected_option.set("Server")


####################FUNCTIONS####################

def set_defaults():
    if option_var.get() == "Server":
        host_entry.delete(0, END)
        port_entry.delete(0, END)

        host_entry.insert(0, "0.0.0.0")
        port_entry.insert(0, "1234")

        ip_lbl.config(text=f"Use same port on both computers\nUse one of these IP(s) on the other computer: {get_ip()}")
        start_server_btn.config(text="Start Server")

        host_entry.config(state=DISABLED)

    elif option_var.get() == "Client":
        host_entry.config(state=NORMAL)
        ip_lbl.config(text=f"Check the other computer for IP")
        start_server_btn.config(text="Connect to Server")


def get_ip():
    prepare_environment.check = False
    the_ip.clear()
    result = subprocess.run(['ipconfig'], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")

    for line in lines:
        if line.startswith("Wireless LAN adapter") or line.startswith("Ethernet adapter Ethernet"):
            prepare_environment.check = True
        if prepare_environment.check:
            if "IPv4" in line:
                the_ip.append(line.split(":")[1].strip())
                prepare_environment.check = False
    return the_ip


def prepare_environment():
    get_ip()
    set_defaults()


def start_server(host, port):
    server = Server(host=f'{host}', port=int(port))
    server.start()


def start_client(host, port):
    client = Client(host=f'{host}', port=int(port))
    client.start()


def connect():
    host = host_entry.get()
    port = port_entry.get()
    if host == "" or port == "" or not port.isdigit() or not 0 < int(port) < 65535:
        logs_txt.insert(END, "Please enter a valid host and port.\n")
        return
    if option_var.get() == "Server":
        if not connect.is_connected:
            logs_txt.insert(END, f"Starting server on {host_entry.get()}:{port_entry.get()}...\n")
            server_thread = threading.Thread(target=start_server, args=(host, port))
            server_thread.start()
        else:
            logs_txt.insert(END, "Server is already running.\n")
    elif option_var.get() == "Client":
        if not connect.is_connected:
            logs_txt.insert(END, f"Connecting to server on {host_entry.get()}:{port_entry.get()}...\n")
            client_thread = threading.Thread(target=start_client, args=(host, port))
            client_thread.start()
        else:
            logs_txt.insert(END, "Client is already connected to the server.\n")


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.keyboard = Controller()
            logs_txt.insert(END, "Server started successfully.\n")
            start_server_btn.config(text="Disconnect", bg="red")
            connect.is_connected = True
        except:
            logs_txt.insert(END, "Error Starting the server.\n")
            connect.is_connected = False

    def start(self):
        # Set up the network connection
        self.s.bind((self.host, self.port))
        self.s.listen(1)
        conn, addr = self.s.accept()

        # Receive the keypresses from the client
        while True:
            data = conn.recv(1024)
            if not data:
                break
            try:
                json_data = data.decode()
                print(json_data)
                keypresses = json.loads(json_data)
                the_key = keypresses[0]['key']
                the_action = keypresses[0]['action']
                if the_key.split(".")[0] == "Key":
                    key_obj = getattr(Key, the_key.split(".")[1])
                    if the_action == "pressed":
                        pass
                        # self.keyboard.press(key_obj)
                    elif the_action == "released":
                        pass
                        # self.keyboard.release(key_obj)
                else:
                    if the_action == "pressed":
                        pass
                        # self.keyboard.press(the_key)
                    elif the_action == "released":
                        pass
                        # self.keyboard.release(the_key)
            except Exception as e:
                logs_txt.insert(END, f"Error: {e}\n")

        # Close the network connection when done
        conn.close()
        self.s.close()


class Client:
    def __init__(self, host, port):
        self.keypresses = []
        self.host = host
        self.port = port
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host, port))
            logs_txt.insert(END, "Connected to the server successfully.\n")
            start_server_btn.config(text="Disconnect", bg="red")
            connect.is_connected = True
        except:
            logs_txt.insert(END, "Error connecting to the server.\n")
            connect.is_connected = False

    # Send buffered keypress data to the server
    def send_buffer(self):
        print(self.keypresses)
        if len(self.keypresses) > 0:
            json_data = json.dumps(self.keypresses)
            self.s.sendall(json_data.encode())
            self.keypresses.clear()

    # Add keypress data to the buffer
    def on_press(self, event):
        try:
            key = event.char
        except:
            key = event
        data = {'key': f'{key}', 'action': 'pressed'}
        self.keypresses.append(data)
        self.send_buffer()

    def on_release(self, event):
        try:
            key = event.char
        except:
            key = event
        data = {'key': f'{key}', 'action': 'released'}
        self.keypresses.append(data)
        self.send_buffer()

    # Start the listener
    def start(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


####################FUNCTIONS####################

prepare_environment.check = False
selected_option = None
connect.is_connected = False

option_var = StringVar(value="Server")

group_box = LabelFrame(root, text="Login", font=("Arial", 12))
group_box.place(x=10, y=10, width=WIDTH - 20, height=HEIGHT - 300)

host_lbl = Label(group_box, text="Host", font=("Arial", 12))
host_lbl.place(x=10, y=10)

host_entry = Entry(group_box, font=font1)
host_entry.place(x=10, y=40, width=WIDTH - 50)

port_lbl = Label(group_box, text="Port", font=("Arial", 12))
port_lbl.place(x=10, y=80)

port_entry = Entry(group_box, font=font1)
port_entry.place(x=10, y=110, width=WIDTH - 50)

Label(group_box, text="Connect to:", font=("Arial", 12)).place(x=10, y=150)

radio_btn1 = Radiobutton(group_box, text="Me", font=("Arial", 12), variable=option_var, value="Server",
                         command=lambda: set_defaults())
radio_btn1.place(x=10, y=180)

radio_btn2 = Radiobutton(group_box, text="Other", font=("Arial", 12), variable=option_var, value="Client",
                         command=lambda: set_defaults())
radio_btn2.place(x=10, y=210)

group_box2 = LabelFrame(root, text="IP HINT", font=("Arial", 12))
group_box2.place(x=10, y=HEIGHT - 280, width=WIDTH - 20, height=100)

ip_lbl = Label(group_box2, text="IP(s):", font=("Arial", 11), wraplength=WIDTH - 50)
ip_lbl.place(x=10, y=10)

start_server_btn = Button(root, text="Start Server", font=("Arial", 12), command=lambda: connect())
start_server_btn.place(x=10, y=HEIGHT - 170, width=WIDTH - 20, height=40)

Label(root, text="Log:", font=("Arial", 12)).place(x=10, y=HEIGHT - 120)

logs_txt = Text(root, font=("Arial", 8), wrap=WORD, bg="black", fg="white", insertbackground="white", )
logs_txt.place(x=10, y=HEIGHT - 90, width=WIDTH - 20, height=100 - 25)

prepare_environment()

root.mainloop()
