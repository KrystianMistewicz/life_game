

from tkinter import Tk,  Frame, Button, Label, Canvas, ttk, PhotoImage, DoubleVar, Scale, BooleanVar, Checkbutton, StringVar, Toplevel
from tkinter.messagebox import askyesno, showinfo
import matplotlib.pyplot as plt
from math import floor, ceil
import gc


#%% Definition of the Cell class
class Cell():
    def __init__(self, x_position, y_position, is_alive, status_change, neighbors_number, button):
        self.x_position = x_position
        self.y_position = y_position
        self.is_alive = is_alive
        self.status_change = status_change # True if status of the cell has changed during last iteration
        self.neighbors_number = neighbors_number # the number of alive neighbors
        self.button = button

    def change_cell_status(self):
        self.is_alive = not self.is_alive
        self.status_change = True

    def iteration(self):
        self.status_change = False
        if self.is_alive:
            if self.neighbors_number < 2 or self.neighbors_number > 3:
                self.change_cell_status()
        else:
            if self.neighbors_number == 3:
                self.change_cell_status()


# It is Cells_array class that contains an array of the cells objects that belong to the Cell class
class Cells_array():
    def __init__(self, array_width, array_height, array):
        self.array_width = array_width
        self.array_height = array_height
        self.array = array

    # This method creates an array of the cells
    def create_array(self):
        cells_array = []
        for i in range(self.array_height):
            array_row = []
            for j in range(self.array_width):
                specific_cell = Cell(i, j, False, False, None, None)
                array_row.append(specific_cell)
            cells_array.append(array_row)
        self.array = cells_array


#%% Definition of the Application class
class Application():
    def __init__(self, game_version, array_width, continuous_iteration, stable_array, iterations_number, cells_array, statistics):
        self.game_version = game_version
        self.array_width = array_width
        self.continuous_iteration = continuous_iteration
        self.stable_array = stable_array
        self.iterations_number = iterations_number
        self.cells_array = cells_array
        self.statistics = statistics

    def calculate_neighbor_numbers(self):
        for i in range(len(self.cells_array)):
            for j in range(len(self.cells_array[0])):
                c = self.cells_array[i][j]
                neighbor_number = 0
                for k in range(-1, 2):
                    for t in range(-1, 2):
                        if (k != 0 or t != 0) and i+k >= 0 and i+k <= len(self.cells_array)-1 and j+t >= 0 and j+t <= len(self.cells_array[0])-1:
                            c_neigh = self.cells_array[i+k][j+t]
                            if c_neigh.is_alive:
                                neighbor_number += 1
                c.neighbors_number = neighbor_number
                self.cells_array[i][j] = c

    def do_single_iteration(self):
        global show_died_cells
        self.stable_array = True
        self.calculate_neighbor_numbers()
        living_cells_number = 0 # The number of alive cells for statistics
        for i in range(len(self.cells_array)):
            for j in range(len(self.cells_array[0])):
                c = self.cells_array[i][j]
                if c.is_alive:
                    living_cells_number += 1
                c.iteration()
                self.cells_array[i][j] = c
                if c.status_change:
                    self.stable_array = False
                    if c.is_alive:
                        c.button.configure(bg='green')
                    else:
                        if show_died_cells.get():
                            c.button.configure(bg='grey80')
                        else:
                            c.button.configure(bg='white')
        self.statistics.append(living_cells_number)
        if not self.stable_array:
            self.iterations_number += 1
            iterations_number_label.configure(text=str(self.iterations_number))
        else:
            showinfo(title='Information', message='The array of cells is stable.')
            button_load.configure(state='normal')
            button_one_iteration.configure(state='normal')
            button_statistics.configure(state='normal')
            button_clear_board.configure(state='normal')
            button_quit.configure(state='normal')
        gc.collect()

    def play(self):
        # global iteration_speed, frame4, button_play
        time_interval = -4*iteration_speed.get()+500 # Function used to calculate time interval between subsequent iterations in ms units
        root.after(int(time_interval))
        self.do_single_iteration()
        frame4.update()
        if self.stable_array:
            button_play.configure(text="PLAY", font='Helvetica 12 bold')
            self.continuous_iteration = False
        else:
            if self.continuous_iteration:
                self.play()

    def play_pause(self):
        self.stable_array = False
        self.continuous_iteration = not self.continuous_iteration
        if self.continuous_iteration:
            button_load.configure(state='disabled')
            button_play.configure(text="PAUSE", font='Helvetica 12 bold')
            button_one_iteration.configure(state='disabled')
            button_statistics.configure(state='disabled')
            button_clear_board.configure(state='disabled')
            button_quit.configure(state='disabled')
            self.play()
        else:
            button_load.configure(state='normal')
            button_play.configure(text="PLAY", font='Helvetica 12 bold')
            button_one_iteration.configure(state='normal')
            button_statistics.configure(state='normal')
            button_clear_board.configure(state='normal')
            button_quit.configure(state='normal')

    def button_action(self, i, j):
        cell = self.cells_array[i][j]
        cell.change_cell_status()
        self.cells_array[i][j] = cell
        if cell.is_alive:
            cell.button.configure(bg='green')
        else:
            cell.button.configure(bg='white')

    def button_array(self, button_size):
        for i in range(len(self.cells_array)):
            for j in range(len(self.cells_array[0])):
                c = self.cells_array[i][j]
                # Creation of the square buttons in 'frame_button'
                # The 'frame_button' is a frame inside the 'frame4'
                frame_button = Frame(frame4, width=button_size, height=button_size)
                frame_button.grid_propagate(False)
                frame_button.columnconfigure(0, weight=1)
                frame_button.rowconfigure(0, weight=1)
                b = Button(frame_button, bg='white', command=lambda i=i, j=j: self.button_action(i, j))
                c.button = b
                b.grid(sticky='WENS')
                frame_button.grid(row=i, column=j, sticky='WENS')

    def clear_board(self, ask_for_confirmation):
        # global iterations_number_label
        if ask_for_confirmation:
            clear_condition = askyesno(title='Clear board confirmation', message='Are you sure you want to clear board? All data in board will be erased.')
        else:
            clear_condition = True
        if clear_condition:
            for i in range(len(self.cells_array)):
                for j in range(len(self.cells_array[0])):
                    c = self.cells_array[i][j]
                    c.is_alive = False
                    c.status_change = False
                    c.neighbors_number = 0
                    c.button.configure(bg='white')
            self.iterations_number = 0
            self.statistics = []
            iterations_number_label.configure(text=str(self.iterations_number))

    def quit(self, window, confirmation):
        if confirmation:
            if askyesno(title='Quit confirmation', message='Are you sure you want to exit?'):
                window.destroy()
        else:
            window.destroy()

    def show_statistics(self):
        if len(self.statistics) > 0:
            x_values = []
            for i in range(len(self.statistics)):
                x_values.append(i)
            plt.plot(x_values, self.statistics)
            plt.title('Statistics', fontsize=20, fontweight='bold')
            plt.xlabel('number of iteration', fontsize=16, fontweight='bold')
            plt.ylabel('number of living cells', fontsize=16, fontweight='bold')
            new_x_list = range(floor(min(x_values)), ceil(max(x_values)) + 1)  # It is done to show only integer values in the x axis
            new_y_list = range(floor(min(self.statistics)), ceil(max(self.statistics)) + 1)  # It is done to show only integer values in the y axis
            plt.xticks(new_x_list)  # It is done to show only integer values in the x axis
            plt.yticks(new_y_list)  # It is done to show only integer values in the y axis
            plt.locator_params(axis='both', nbins=10)
            plt.show()
        else:
            showinfo(title='Error', message='There is no data to show.')

    def load_pattern_on_board(self, pattern, window):
        self.clear_board(False)
        x_coordinate_list = []
        y_coordinate_list = []
        if pattern == 'Glider':
            pattern_list = [[0, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
        elif pattern == 'Light-weight spaceship':
            pattern_list = [[0, 0], [0, 3], [1, 4], [2, 0], [2, 4], [3, 1], [3, 2], [3, 3], [3, 4]]
        elif pattern == 'Middle-weight spaceship':
            pattern_list = [[0, 2], [1, 0], [1, 4], [2, 5], [3, 0], [3, 5], [4, 1], [4, 2], [4, 3], [4, 4], [4, 5]]
        elif pattern == 'Heavy-weight spaceship':
            pattern_list = [[0, 2], [0, 3], [1, 0], [1, 5], [2, 6], [3, 0], [3, 6], [4, 1], [4, 2], [4, 3], [4, 4], [4, 5], [4, 6]]
        elif pattern == 'Pulsar':
            pattern_list = [[0, 2], [0, 3], [0, 4], [0, 8], [0, 9], [0, 10], [2, 0], [2, 5], [2, 7], [2, 12], [3, 0], [3, 5], [3, 7], [3, 12], [4, 0], [4, 5], [4, 7], [4, 12], [5, 2], [5, 3], [5, 4], [5, 8], [5, 9], [5, 10], [7, 2], [7, 3], [7, 4], [7, 8], [7, 9], [7, 10], [8, 0], [8, 5], [8, 7], [8, 12], [9, 0], [9, 5], [9, 7], [9, 12], [10, 0], [10, 5], [10, 7], [10, 12], [12, 2], [12, 3], [12, 4], [12, 8], [12, 9], [12, 10]]
        elif pattern == 'Penta-decathlon':
            pattern_list = [[0, 1], [1, 1], [2, 0], [2, 2], [3, 1], [4, 1], [5, 1], [6, 1], [7, 0], [7, 2], [8, 1], [9, 1]]
        elif pattern == 'Gosper glider gun':
            pattern_list = [[0, 24], [1, 22], [1, 24], [2, 12], [2, 13], [2, 20], [2, 21], [2, 34], [2, 35], [3, 11], [3, 15], [3, 20], [3, 21], [3, 34], [3, 35], [4, 0], [4, 1], [4, 10], [4, 16], [4, 20], [4, 21], [5, 0], [5, 1], [5, 10], [5, 14], [5, 16], [5, 17], [5, 22], [5, 24], [6, 10], [6, 16], [6, 24], [7, 11], [7, 15], [8, 12], [8, 13]]
        for item in pattern_list:
            x_coordinate_list.append(item[0])
            y_coordinate_list.append(item[1])
        pattern_x_size = max(x_coordinate_list)
        pattern_y_size = max(y_coordinate_list)
        center_x = int((len(self.cells_array)-pattern_x_size)/2)
        center_y = int((len(self.cells_array[0])-pattern_y_size)/2)
        if pattern == 'Glider':
            x0 = 1
            y0 = 1
        elif pattern == 'Light-weight spaceship' or pattern == 'Middle-weight spaceship' or pattern == 'Heavy-weight spaceship':
            x0 = center_x
            y0 = 1
        elif pattern == 'Pulsar' or pattern == 'Penta-decathlon':
            x0 = center_x
            y0 = center_y
        elif pattern == 'Gosper glider gun':
            x0 = 1
            y0 = center_y
        if len(self.cells_array) > pattern_x_size and len(self.cells_array[0]) > pattern_y_size:
            for item in pattern_list:
                c = self.cells_array[item[0]+x0][item[1]+y0]
                c.is_alive = True
                c.button.configure(bg='green')
        else:
            showinfo(title='Error', message='The array is too small to load the selected pattern.')
        window.destroy()

    def pattern_selected(self, selection, pattern_canvas):
        global pattern_image # The image is set as a global variable in order to avoid be collected by the Garbage Collector
        if selection == 'Glider':
            pattern_image = PhotoImage(file='patterns\glider.png')
        elif selection == 'Light-weight spaceship':
            pattern_image = PhotoImage(file='patterns\light-weight_spaceship.png')
        elif selection == 'Middle-weight spaceship':
            pattern_image = PhotoImage(file='patterns\middle-weight_spaceship.png')
        elif selection == 'Heavy-weight spaceship':
            pattern_image = PhotoImage(file='patterns\heavy-weight_spaceship.png')
        elif selection == 'Pulsar':
            pattern_image = PhotoImage(file='patterns\pulsar.png')
        elif selection == 'Penta-decathlon':
            pattern_image = PhotoImage(file='patterns\penta-decathlon.png')
        elif selection == 'Gosper glider gun':
            pattern_image = PhotoImage(file='patterns\gosper_glider_gun.png')
        pattern_canvas.create_image(200, 155, image=pattern_image)

    def load_pattern(self):
        # global load_pattern_window
        # if not self.continuous_iteration:
        load_pattern_window = Toplevel(root)
        load_pattern_window.iconbitmap('icon.ico')
        load_pattern_window.grab_set() # Hold the load_pattern_window on top. Must be used along with Toplevel object
        window_width = 800
        window_height = 550
        w = load_pattern_window.winfo_screenwidth()
        h = load_pattern_window.winfo_screenheight()
        x = int((w - window_width)/2)
        y = int((h - window_height)/2)
        load_pattern_window.title('Load pattern')
        load_pattern_window.configure(bg='white')
        load_pattern_window.geometry("%ix%i+%i+%i" % (window_width, window_height, x, y))
        frame1 = Frame(load_pattern_window)
        frame1.configure(bg='white')
        frame1.pack()
        text1 = Label(frame1, bg='white', text="\nSelect pattern to load from list given below\n", font='Helvetica 14 bold')
        text1.pack()
        frame2_pattern = Frame(load_pattern_window)
        frame2_pattern.configure(bg='white')
        frame2_pattern.pack()
        options_list = ['Glider', 'Light-weight spaceship', 'Middle-weight spaceship', 'Heavy-weight spaceship', 'Pulsar', 'Penta-decathlon', 'Gosper glider gun']
        chosen_pattern = StringVar()
        select_menu = ttk.Combobox(frame2_pattern, textvariable=chosen_pattern, values=options_list, state='readonly')
        select_menu.current(0)
        empty_label = Label(frame2_pattern, bg='white', text=" ", font='Helvetica 14 bold')
        pattern_canvas = Canvas(frame2_pattern, bg='white', width=400, height=310)
        select_menu.grid(row=0, column=0, sticky='N')
        empty_label.grid(row=0, column=1)
        pattern_canvas.grid(row=0, column=2)
        self.pattern_selected('Glider', pattern_canvas)
        select_menu.bind("<<ComboboxSelected>>", lambda _ : self.pattern_selected(chosen_pattern.get(), pattern_canvas))
        frame3 = Frame(load_pattern_window)
        frame3.configure(bg='white')
        frame3.pack()
        text2 = Label(frame3, bg='white', text="\n", font='Tahoma 14 bold')
        text2.pack()
        frame4 = Frame(load_pattern_window)
        frame4.configure(bg='white')
        frame4.pack()
        button_load = Button(frame4, bg='alice blue', text="Load pattern", font='Helvetica 12 bold', width=10, height=3, command=lambda:self.load_pattern_on_board(chosen_pattern.get(), load_pattern_window))
        button_load.grid(row=1, column=1)
        text11 = Label(frame4, bg='white', text='', width=5, font='Helvetica 12')
        text11.grid(row=1, column=2)
        button_exit = Button(frame4, bg='alice blue', text="Cancel", font='Helvetica 12 bold', width=10, height=3, command=lambda:self.quit(load_pattern_window, False))
        button_exit.grid(row=1, column=3)
        load_pattern_window.mainloop()

    def destroy_welcome_window(self):
        welcome_window.destroy()

    def create_welcome_window(self):
        global welcome_window
        welcome_window = Tk()
        welcome_window.iconbitmap('icon.ico')
        window_width = 1000
        window_height = 650
        w = welcome_window.winfo_screenwidth()
        h = welcome_window.winfo_screenheight()
        x = int((w - window_width)/2)
        y = int((h - window_height)/2)
        welcome_window.title('Welcome to Life game')
        welcome_window.configure(bg='white')
        welcome_window.geometry("%ix%i+%i+%i" % (window_width, window_height, x, y))
        frame1 = Frame(welcome_window)
        frame1.configure(bg='white')
        frame1.pack()
        text1 = Label(frame1, bg='white', text="\n", font='Tahoma 8 bold')
        text1.pack()
        canvas = Canvas(frame1, bg='white', width=700, height=250)
        canvas.pack()
        intro_image = PhotoImage(file='graphical_intro.png')
        canvas.create_image(350, 125, image=intro_image)
        text2 = Label(frame1, bg='white', text="\nversion %s\n" % str(self.game_version), font='Tahoma 16 bold')
        text2.pack()
        frame2 = Frame(welcome_window)
        frame2.configure(bg='white')
        frame2.pack()
        text3 = Label(frame2, bg='white', text="The rules of \"Life game\" accroding to John Horton Conway:", font='Helvetica 16 bold')
        text3.grid(row=0, column=2)
        frame3 = Frame(welcome_window)
        # frame3.configure(bg='white')
        # frame3.pack()
        text4 = Label(frame2, bg='white', text="1)", font='Helvetica 16 bold', width=3)
        text4.grid(row=1, column=1)
        text5 = Label(frame2, bg='white', text="Any live cell with two or three live neighbours survives.", font='Helvetica 16')
        text5.grid(sticky='W', row=1, column=2)
        text6 = Label(frame2, bg='white', text="2)", font='Helvetica 16 bold', width=3)
        text6.grid(row=2, column=1)
        text7 = Label(frame2, bg='white', text="Any dead cell with three live neighbours becomes a live cell.", font='Helvetica 16')
        text7.grid(sticky='W', row=2, column=2)
        text8 = Label(frame2, bg='white', text="3)", font='Helvetica 16 bold', width=3)
        text8.grid(row=3, column=1)
        text9 = Label(frame2, bg='white', text="All other live cells die in the next generation. Similarly, all other dead cells stay dead.", font='Helvetica 16')
        text9.grid(sticky='W', row=3, column=2)
        text10 = Label(frame2, bg='white', text='\n', font='Helvetica 12')
        text10.grid(row=4, column=2)
        ttk.Separator(frame2, orient='vertical').grid(column=0, row=0, rowspan=4, sticky='nse')
        ttk.Separator(frame2, orient='vertical').grid(column=2, row=0, rowspan=4, sticky='nse')
        ttk.Separator(frame2, orient='horizontal').grid(column=0, row=0, columnspan=3, sticky='wen')
        ttk.Separator(frame2, orient='horizontal').grid(column=0, row=1, columnspan=3, sticky='wen')
        ttk.Separator(frame2, orient='horizontal').grid(column=0, row=4, columnspan=3, sticky='wen')
        frame4 = Frame(welcome_window)
        frame4.configure(bg='white')
        frame4.pack()
        button_continue = Button(frame4, bg='alice blue', text="Continue", font='Helvetica 12 bold', width=10, height=3, command=lambda:self.create_main_window())
        button_continue.grid(row=1, column=1)
        text11 = Label(frame4, bg='white', text='', width=5, font='Helvetica 12')
        text11.grid(row=1, column=2)
        button_exit = Button(frame4, bg='alice blue', text="Exit", font='Helvetica 12 bold', width=10, height=3, command=lambda:self.destroy_welcome_window())
        button_exit.grid(row=1, column=3)
        welcome_window.mainloop()

    def create_main_window(self):
        global root, frame4, button_load, button_play, button_one_iteration, button_statistics, button_clear_board, button_quit, iterations_number_label, iteration_speed, show_died_cells
        welcome_window.destroy()
        root = Tk()
        root.iconbitmap('icon.ico')
        root.state('zoomed')
        root.title("Life game by Krystian Mistewicz ver. %1.1f" % self.game_version)
        window_width = root.winfo_screenwidth()
        window_height = root.winfo_screenheight()
        root.geometry("%dx%d" % (window_width, window_height))
        bgc = 'lightgrey' # the color of the app background
        root.configure(bg=bgc)
        # Creating the main frames in the app window
        frame_bar1 = Frame(root, bg=bgc, width=window_width)
        frame_bar1.pack()
        frame1 = Frame(root)
        frame1.configure(bg=bgc, width=window_width)
        frame1.pack()
        # frame1.pack_propagate(0)
        frame_bar2 = Frame(root, bg=bgc, width=window_width)
        frame_bar2.pack()
        frame_bar3 = Frame(root, bg='grey60', width=window_width)
        frame_bar3.pack()
        frame2 = Frame(root)
        frame2_height = 4/5*window_height
        frame2.configure(bg='blue', height=frame2_height)
        frame2.pack()
        frame3 = Frame(frame2)
        frame3_width = 200
        frame3.grid(row=0, column=0, sticky='NSEW')
        frame3.configure(bg='grey', width=frame3_width)
        frame4 = Frame(frame2)
        frame4.grid(row=0, column=1, sticky='NSEW')
        frame_bar4 = Frame(root, bg='grey60', width=window_width)
        frame_bar4.pack()
        frame5 = Frame(frame2)
        frame5.grid(row=0, column=2, sticky='NSEW')
        frame5_width = 200
        frame5.configure(bg='grey', width=frame5_width)
        empty_label1 = Label(frame1, bg=bgc, text='', width=15)
        empty_label2 = Label(frame1, bg=bgc, text='', width=15)
        empty_label3 = Label(frame1, bg=bgc, text='', width=15)
        empty_label4 = Label(frame1, bg=bgc, text='', width=15)
        empty_label5 = Label(frame1, bg=bgc, text='', width=15)
        # button_size = 1.0 Temporary value of the button_size parameter. It is updated below.
        button_load = Button(frame1, bg='alice blue', text="LOAD\nPATTERN", font='Helvetica 12 bold', width=10, height=3, command=lambda:self.load_pattern())
        button_play = Button(frame1, bg='alice blue', text="PLAY", font='Helvetica 12 bold', width=10, height=3, command=lambda:self.play_pause())
        button_one_iteration = Button(frame1, bg='alice blue', text="ONE\nITERATION", font='Helvetica 12 bold', width=10, height=3, command=lambda:self.do_single_iteration())
        button_statistics = Button(frame1, bg='alice blue', text="STATISTICS", font='Helvetica 12 bold', width=10, height=3, command=lambda:self.show_statistics())
        button_clear_board = Button(frame1, bg='alice blue', text="CLEAR\nBOARD", font='Helvetica 12 bold', width=10, height=3, command=lambda:self.clear_board(True))
        button_quit = Button(frame1, bg='alice blue', text="QUIT", font='Helvetica 12 bold', width=10, height=3, command=lambda:self.quit(root, True))
        button_load.grid(row=0, column=0)
        empty_label1.grid(row=0, column=1, sticky='NSEW')
        button_play.grid(row=0, column=2)
        empty_label2.grid(row=0, column=3, sticky='NSEW')
        button_one_iteration.grid(row=0, column=4)
        empty_label3.grid(row=0, column=5, sticky='NSEW')
        button_statistics.grid(row=0, column=6, sticky='NSEW')
        empty_label4.grid(row=0, column=7, sticky='NSEW')
        button_clear_board.grid(row=0, column=8, sticky='NSEW')
        empty_label5.grid(row=0, column=9, sticky='NSEW')
        button_quit.grid(row=0, column=10)
        root.update()
        bar_height=1/20*window_height - frame1.winfo_height()/4
        frame_bar1.configure(height=bar_height)
        frame_bar2.configure(height=bar_height)
        frame_bar3.configure(height=bar_height)
        frame_bar4.configure(height=bar_height)
        empty_label3 = Label(frame3, bg='grey', text='', height=3)
        empty_label3.pack()
        image = PhotoImage()
        label1 = Label(frame3, bg='grey', image=image, font='Helvetica 12 bold', width=frame3_width)
        label1.pack()
        label2 = Label(frame3, bg='grey', text='NUMBER OF\nITERATIONS', font='Helvetica 12 bold')
        label2.pack()
        iterations_number_label = Label(frame3, bg='grey', text=str(self.iterations_number), font='Helvetica 18 bold')
        iterations_number_label.pack()
        empty_label4 = Label(frame3, bg='grey', text='', height=3)
        empty_label4.pack()
        label3 = Label(frame3, bg='grey', text='ITERATION\nSPEED', font='Helvetica 12 bold')
        label3.pack()
        label4 = Label(frame3, bg='grey', text='LOW', font='Helvetica 10 bold')
        label4.pack()
        iteration_speed = DoubleVar()
        speed_scale = Scale(frame3, variable=iteration_speed, showvalue=0)
        speed_scale.configure(bg='grey')
        speed_scale.set(50)
        speed_scale.pack()
        label5 = Label(frame3, bg='grey', text='HIGH', font='Helvetica 10 bold')
        label5.pack()
        empty_label5 = Label(frame3, bg='grey', text='', height=3)
        empty_label5.pack()
        show_died_cells = BooleanVar()
        # style = ttk.Style(root)
        # style.configure('TCheckbutton', font=40)
        checkbutton1 = Checkbutton(frame3, bg='grey', activebackground='grey', text='SHOW\nIN GRAY\n CELLS\nWHO DIED', font='Helvetica 12 bold', variable=show_died_cells, onvalue=True, offvalue=False)
        checkbutton1.pack()
        right_margin = 0
        frame_width = root.winfo_width()-frame3_width-right_margin
        button_size = int(frame_width / self.array_width)
        array_height = int((window_height-5*bar_height-frame1.winfo_height())/button_size)
        # The creation of the cells array
        cells_array = Cells_array(self.array_width, array_height, None)
        cells_array.create_array()
        self.cells_array = cells_array.array
        self.button_array(button_size)
        root.mainloop()


#%% The primary parameters of the application
game_version = 4.6
M = 50 # The number of cells in the width of the array
statistics = []

if __name__ == '__main__':
    application = Application(game_version, M, False, False, 0, None, statistics)
    application.create_welcome_window()
