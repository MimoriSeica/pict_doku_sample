import tkinter
import numpy as np
from tkinter import colorchooser
from PIL import Image, ImageDraw, ImageFilter
import random

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('tkinter canvas trial')
        self.configure(background = '#DDEEEE')
        self.pencil_color = 'black'
        self.pack()
        self.create_widgets()
        self.setup()

        self.sudoku_pad = 30
        self.sudoku_width = 30

    def create_widgets(self):
        self.vr = tkinter.IntVar()
        self.vr.set(1)
        self.change_color_button = tkinter.Button(self, text='change color', command=self.change_color)
        self.change_color_button.grid(row=0, column=0)
        self.write_radio = tkinter.Radiobutton(self, text='write', variable=self.vr, value=1, command=self.change_radio)
        self.write_radio.grid(row=0, column=1)
        self.erase_radio = tkinter.Radiobutton(self, text='erase', variable=self.vr, value=2, command=self.change_radio)
        self.erase_radio.grid(row=0, column=2)

        self.clear_button = tkinter.Button(self, text='clear all', command=self.clear_canvas)
        self.clear_button.grid(row=0, column=3)

        self.save_button = tkinter.Button(self, text='make', command=self.make_sudoku)
        self.save_button.grid(row=0, column=4)

        self.paint_canvas = tkinter.Canvas(self, bg='white', width=600, height=600)
        self.paint_canvas.grid(row=1, column=0, columnspan=4)
        self.paint_canvas.bind('<B1-Motion>', self.paint)
        self.paint_canvas.bind('<ButtonRelease-1>', self.reset)

        self.sudoku_canvas = tkinter.Canvas(self, bg='white', width=600, height=600)
        self.sudoku_canvas.grid(row=1, column=5, columnspan=4)

        self.numbers = np.zeros((3, 3))

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.eraser_on = False
        self.clear_canvas()
        self.make_sudoku()

    def change_color(self):
        self.pencil_color = colorchooser.askcolor()[1]
        self.change_color_button.bg = self.pencil_color

    def change_radio(self):
        if self.vr.get() == 1:
            self.eraser_on = False
        else:
            self.eraser_on = True

    def clear_canvas(self):
        self.paint_canvas.delete(tkinter.ALL)
        self.im = Image.new('RGB', (600, 600), 'white')
        self.draw = ImageDraw.Draw(self.im)

    def save_canvas(self):
        self.im.save('out.jpg')

    def draw_line(self, from_x, from_y, to_x, to_y, color, width):
        self.paint_canvas.create_line(from_x, from_y, to_x, to_y, width=width, fill=color, capstyle=tkinter.ROUND, smooth=tkinter.TRUE, splinesteps=36)
        self.draw.line((from_x, from_y, to_x, to_y), fill=color, width=width)

    def paint(self, event):
        if self.eraser_on:
            paint_color = 'white'
        else:
            paint_color = self.pencil_color
        if self.old_x and self.old_y:
            self.draw_line(self.old_x, self.old_y, event.x, event.y, paint_color, 10)

        self.old_x = event.x
        self.old_y = event.y

    def make_sudoku(self):
        self.sudoku_canvas.delete(tkinter.ALL)
        arr = np.array(self.im.convert("L").filter(ImageFilter.FIND_EDGES), 'int')
        h, w = arr.shape
        for i in range(h):
            for j in range(w-1):
                arr[i, j+1] += arr[i, j]

        for j in range(w):
            for i in range(h-1):
                arr[i+1, j] += arr[i, j]

        hint_place = []
        for i in range(9):
            for j in range(9):
                from_x = 30 + 60 * j
                from_y = 30 + 60 * i
                to_x = 30 + 60 * (j + 1)
                to_y = 30 + 60 * (i + 1)

                if arr[to_y - 10, to_x - 10] - arr[from_y + 9, to_x - 10] - arr[to_y - 10, from_x + 9] + arr[from_y + 9, from_x + 9] == 0:
                    continue

                self.sudoku_canvas.create_rectangle(from_x, from_y, to_x, to_y, fill = '#AAAAAA', stipple = 'gray25')
                hint_place.append([i, j])

        random.shuffle(hint_place)
        nums = [[set() for i in range(9)] for j in range(9)]

        for hint in hint_place:
            y = hint[0]
            x = hint[1]
            from_x = 30 + 60 * x
            from_y = 30 + 60 * y
            to_x = 30 + 60 * (x + 1)
            to_y = 30 + 60 * (y + 1)

            lis = list(range(1, 10))
            random.shuffle(lis)
            for num in lis:
                if num in nums[y][x]:
                    continue

                nums[y][x].add(num)
                self.sudoku_canvas.create_text(30 + from_x, 30 + from_y, text = '{}'.format(num), font = ('', 40))
                for i in range(9):
                    nums[i][x].add(num)
                for i in range(9):
                    nums[y][i].add(num)

                for i in range(9):
                    if (i // 3) != (y // 3):
                        continue
                    for j in range(9):
                        if (j // 3) != (x // 3):
                            continue

                        nums[i][j].add(num)

                break

        for x in range(30, 571, 60):
            w = 5
            if (x - 30) % 90 == 0:
                w = 10.
            self.sudoku_canvas.create_line(x, 30, x, 570, width=w, fill='black', capstyle=tkinter.ROUND, smooth=tkinter.TRUE, splinesteps=36)

        for y in range(30, 571, 60):
            w = 5
            if (y - 30) % 90 == 0:
                w = 10.
            self.sudoku_canvas.create_line(30, y, 570, y, width=w, fill='black', capstyle=tkinter.ROUND, smooth=tkinter.TRUE, splinesteps=36)

        # self.sudoku_canvas.create_text(60, 60, text = '1', font = ('', 40))

    def reset(self, event):
        self.old_x, self.old_y = None, None

root = tkinter.Tk()
app = Application(master=root)
app.mainloop()
