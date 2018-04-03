import tkinter as tk
import tkinter.ttk
from interpreter import *
import time


colors = ['#90a955', '#31572c', '#47772d', '#132a13']


class GUI(tk.Tk):
    def __init__(self, machine):
        tk.Tk.__init__(self)
        self.main_screen = MainScreen(self, machine)
        self.main_screen.pack(fill=tk.BOTH, expand=True)
        self.title('BioLock')
        self.minsize(width=800, height=800)
        self.protocol('WM_DELETE_WINDOW', lambda: self.on_closing())
        menubar = tk.Menu(self)
        menubar.add_command(label="Hello!")
        menubar.add_command(label="Quit!")
        self.config(menu=menubar)

    def on_closing(self):
        self.destroy()


class ButtonBL(tk.Canvas):
    """
    A class used to create round-cornered buttons
    """
    def __init__(self, root, bg, w=0, h=0, r=20, color='red', hover_color='blue', press_color='green',
                 command=lambda: None, text="", font="TkDefaultFont 30", fg="white", enabled=True):
        tk.Canvas.__init__(self, root, width=w, height=h, bg=bg, highlightthickness=0)

        # set geometry
        self.button_parts = [
            self.create_arc(0, 0, r, r, start=90, extent=90),
            self.create_arc(w - r, 0, w, r, start=0, extent=90),
            self.create_arc(0, h - r, r, h, start=180, extent=90),
            self.create_arc(w - r, h - r, w, h, start=270, extent=90),
            self.create_rectangle(r / 2, 0, w - r / 2, h),
            self.create_rectangle(0, r / 2, w, h - r / 2)
        ]
        # set color and text
        self.set_color(color)
        self.create_text(w/2, h/2, font=font, text=text, fill=fg)

        # set hover parameters and button function
        self.color, self.hover_color, self.press_color = color, hover_color, press_color
        self.command = command
        self.set_bindings()

        # allow button disabling
        self.enabled = True
        if not enabled:
            self.disable()

    def set_color(self, color):
        for i in self.button_parts:
            self.itemconfig(i, fill=color, outline=color)

    def set_bindings(self):
        self.bind('<Enter>', lambda event: self.set_color(self.hover_color))
        self.bind('<Leave>', lambda event: self.set_color(self.color))

        self.bind('<Button-1>', lambda event: self.set_color(self.press_color))
        self.bind('<ButtonRelease-1>', self.command)

    def disable(self):
        if not self.enabled:
            return
        self.enabled = False
        self.set_color('#AAAAAA')
        for b in ['<Button-1>', '<ButtonRelease-1>', '<Enter>', '<Leave>']:
            self.unbind(b)

    def enable(self):
        if self.enabled:
            return
        self.enabled = True
        self.set_color(self.color)
        self.set_bindings()


class MainScreen(tk.Frame):
    def __init__(self, master, machine):
        tk.Frame.__init__(self, master, bg=colors[1])
        self.master = master
        self.machine = machine
        self.toolbar = tk.Frame(self, bg=colors[1])

        self.run_img = tk.PhotoImage(file="graphics/run.gif").subsample(8, 8)
        self.pause_img = tk.PhotoImage(file="graphics/pause.gif").subsample(8, 8)
        self.stop_img = tk.PhotoImage(file="graphics/stop.gif").subsample(8, 8)
        self.step_img = tk.PhotoImage(file="graphics/step.gif").subsample(8, 8)

        self.upper_frame = tk.Frame(self, bg='#1212ff')

        self.editor = tk.Text(self.upper_frame)
        self.right_frame = tk.Frame(self.upper_frame)
        self.terminal = tk.Text(self.right_frame, bg='#000000',fg='#ffffff')
        self.input = tk.Entry(self.right_frame)
        self.input.bind('<Return>', self.go_entry)
        self.buffer = Buffer(self.right_frame)

        self.table = Table(self, 10, 10)
        self.table.highlight(0, 0, '#ff0000')

        self.run_button = ButtonBL(self.toolbar, bg=colors[1], w=70, h=70, r=20, color=colors[2],
                            hover_color=colors[0],
                            press_color=colors[3],
                            command=self.run)

        self.pause = ButtonBL(self.toolbar, bg=colors[1], w=70, h=70, r=20, color=colors[2],
                              hover_color=colors[0],
                              press_color=colors[3],
                              )
        self.stop = ButtonBL(self.toolbar, bg=colors[1], w=70, h=70, r=20, color=colors[2],
                             hover_color=colors[0],
                             press_color=colors[3])
        self.step_button = ButtonBL(self.toolbar, bg=colors[1], w=70, h=70, r=20, color=colors[2],
                                    hover_color=colors[0],
                                    press_color=colors[3], command=self.step)
        self.compile = ButtonBL(self.toolbar, bg=colors[1], w=100, h=70, r=20, color=colors[2],
                             hover_color=colors[0],
                             press_color=colors[3],text='Compile',
                                font='TkinterDefault12', command=self.compile)
        self.run_button.create_image(35, 35, image=self.run_img)
        self.pause.create_image(35, 35, image=self.pause_img)
        self.stop.create_image(35, 35, image=self.stop_img)
        self.step_button.create_image(35, 35, image=self.step_img)
        self.scale = tk.Scale(self.toolbar, orient=tk.HORIZONTAL,bg=colors[1]
                              ,highlightbackground=colors[1])

        self.run_button.grid(row=0, column=0, padx=1, pady=1)
        self.pause.grid(row=0, column=1, padx=1, pady=1)
        self.stop.grid(row=0, column=2, padx=1, pady=1)
        self.step_button.grid(row=0, column=3, padx=1, pady=1)
        self.scale.grid(row=0, column=4, padx=1, pady=1)
        self.compile.grid(row=0, column=5, padx=10, pady=1)

    def pack(self, **kwargs):
        tk.Frame.pack(self, **kwargs)
        self.toolbar.pack(fill=tk.BOTH, side=tk.TOP)
        self.upper_frame.pack(fill=tk.BOTH)
        self.editor.pack(side=tk.LEFT)
        self.right_frame.pack(side=tk.RIGHT)
        self.terminal.pack()
        self.input.pack()
        self.buffer.pack()
        self.table.pack(fill=tk.BOTH)

    def step(self, _):
        p = self.machine.data_pointer
        self.machine.tick()
        self.update_memory(p)
        self.update_buffer()
        if self.machine.flag:
            self.terminal.insert(tk.END, chr(self.machine.output))
            self.machine.flag = False
        self.terminal.update()

    def update_memory(self, p):
        pw = p // 10
        ph = p % 10
        self.table.highlight(pw, ph, '#aaaaaa')
        w = self.machine.data_pointer//10
        h = self.machine.data_pointer % 10
        self.table.highlight(w, h, '#ff0000')
        for x in range(10):
            for y in range(10):
                self.table.set(x, y, self.machine.memory[x*10+y])
        self.table.update()

    def update_buffer(self):
        for i in range(20):
            self.buffer.set(0, i, self.machine.buffer[i])
            if self.machine.buffer[i] == 0:
                self.buffer.set(1, i, '\\0')
            else:
                self.buffer.set(1, i, chr(self.machine.buffer[i]))
        self.buffer.update()

    def compile(self, _):
        contents = self.editor.get(1.0, tk.END)
        self.machine.program = contents

    def run(self, _):
        while self.machine.instruction_pointer != len(self.machine.program):
            self.step('a')
            # self.after(100)

    def go_entry(self, _):
        stri = self.input.get()
        self.machine.load(stri)
        self.update_buffer()
        self.input.delete(0, 'end')


class Table(tk.Frame):
    def __init__(self, parent, rows=10, columns=5):
        # use black background so it "peeks through" to
        # form grid lines
        tk.Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = tk.Label(self, text="0",
                                 borderwidth=0, width=10, bg='#aaaaaa')
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

    def highlight(self, row, column, color):
        widget = self._widgets[row][column]
        widget.configure(bg=color)


class Buffer(tk.Frame):
    def __init__(self, parent, rows=2, columns=20):
        # use black background so it "peeks through" to
        # form grid lines
        tk.Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = tk.Label(self, text="0",
                                 borderwidth=0, width=10, bg='#aaaaaa')
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

    def highlight(self, row, column, color):
        widget = self._widgets[row][column]
        widget.configure(bg=color)

    def load(self, line):
        for i, char in enumerate(line[:20]):
            self._widgets[0][i].configure(text=ord(char))
            self._widgets[1][i].configure(text=char)


mach = Machine('+++++++>+++++')
gui = GUI(mach)
gui.mainloop()
