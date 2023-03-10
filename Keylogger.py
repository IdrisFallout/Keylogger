from tkinter import *
import subprocess

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
        ip_lbl.config(text=f"Use one of these IP(s) on the other computer: ")
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


def connect():
    if option_var.get() == "Server":
        logs_txt.insert(END, f"Starting server on {host_entry.get()}:{port_entry.get()}...\n")
    elif option_var.get() == "Client":
        logs_txt.insert(END, f"Connecting to server on {host_entry.get()}:{port_entry.get()}...\n")


####################FUNCTIONS####################

prepare_environment.check = False
selected_option = None
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
