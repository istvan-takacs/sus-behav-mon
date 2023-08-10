from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
# from PIL import ImageTk, Image


root = Tk()
root.title("GUI")
# root.geometry("1050x400")

frame = LabelFrame(root, text="My Frame", padx=50, pady=50)
frame.pack(padx=100, pady=100)

e = Entry(root, width=50)
e.pack()
e.insert(0, "Enter shtg:")




var2 = StringVar()
var2.set("Sunday")

drop = OptionMenu(root,var2, "Monday",  "Tuesday", "Wednesday", "ETC.")
drop.pack()


# root.filename = filedialog.askopenfile(initialdir="Home", title="Select a file", filetypes=(("pdf files", "*.pdf"), ("all files", "*.*")))

# lbl = Label(root, text=root.filename).pack()

vertical = Scale(frame, from_=0, to=200)
vertical.pack()

horizontal = Scale(frame, orient=HORIZONTAL)
horizontal.pack()

var = StringVar()

c = Checkbutton(root, text="Anything I want", variable=var, onvalue="ON", offvalue="OFF")
c.pack()


def show():
    my_lbl = Label(root,text=var.get()).pack()

my_btn = Button(root, text="dhkdscjh", command=show).pack()

def slide():
    some_label = Label(root, text = horizontal.get()).pack()
    root.geometry(str(horizontal.get()) + "x400").pack()

some_button = Button(root, text="Click me", command=slide).pack()

def myClick():
    hello = e.get()
    myLabel2 = Label(frame, text=hello)
    myLabel2.pack()

# r = IntVar()
# r.set("2")
def open():
    top = Toplevel()
    lbl = Label(top, text="New Window!").pack()
    btn = Button(top, text="Close window", command=top.destroy).pack()

btn2 = Button(frame, text="open new window", command=open).pack()

MODES = [
    ("Pepperoni", "Pepperoni"), 
    ("Cheese", "Cheese"), 
    ("Corn", "Corn")
]

pizza = StringVar()
pizza.set("Pepperoni")

for text, mode in MODES:
    Radiobutton(root, text=text, variable=pizza, value=mode, command=lambda: clicked(pizza.get())).pack(anchor=W)

myButton = Button(frame, text="Click me daddy!", command=myClick, fg="black", bg="white").pack()

# Radiobutton(root, text="Option1", variable=r, value=1, command= lambda: clicked(r.get())).pack()
# Radiobutton(root, text="Option2", variable=r, value=2, command= lambda: clicked(r.get())).pack()

def clicked(value):
    myLabel = Label(root, text=value)
    myLabel.pack()



myLabel = Label(root, text=pizza.get()).pack()
# myLabel1.grid(row=0, column=0)
# myLabel2.grid(row=1, column=0)
def popup():
    response = messagebox.askyesno("This is my Popup", "Hello!") # returns 1 for yes 0 for no
    if response ==1:
        Label(root, text="YES!!").pack()

Button(root, text="Popup", command=popup).pack()



button_quit = Button(root, text="Exit", command=root.quit).pack()


root.mainloop()