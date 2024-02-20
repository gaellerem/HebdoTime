import json
import os
import sys
import tkinter as tk
from tkinter import ttk

DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
BREAK_IN_MINUTES = 60
WEEKLY_WORK_TIME = 2310

class Model:
    def __init__(self):
        self.__hours_arrival = {day: 0 for day in DAYS_OF_WEEK}
        self.__minutes_arrival = {day: 0 for day in DAYS_OF_WEEK}
        self.__hours_departure = {day: 0 for day in DAYS_OF_WEEK}
        self.__minutes_departure = {day: 0 for day in DAYS_OF_WEEK}
        self.__time = {day: (0,0) for day in DAYS_OF_WEEK}

    @property
    def hours_departure(self):
        return self.__hours_departure

    @property
    def minutes_departure(self):
        return self.__minutes_departure

    @property
    def hours_arrival(self):
        return self.__hours_arrival

    @property
    def minutes_arrival(self):
        return self.__minutes_arrival
    
    @property
    def time(self):
        return self.__time

    @hours_arrival.setter
    def hours_arrival(self, values):
        hours_arrival = {}
        errors = []
        for day, value in values.items() :
            if value.isdigit():
                value = int(value)
                if value >= 0 and value <= 24:
                    hours_arrival[day] = value
                    continue
            errors.append(day)
        if len(errors) != 0 :
            raise ValueError(errors)
        self.__hours_arrival = hours_arrival
    
    @minutes_arrival.setter
    def minutes_arrival(self, values):
        minutes_arrival = {}
        errors = []
        for day, value in values.items() : 
            if value.isdigit():
                value = int(value)
                if value >= 0 and value <= 60:
                    minutes_arrival[day] = value
                    continue
            errors.append(day)
        if len(errors) != 0 :
            raise ValueError(errors)
        self.__minutes_arrival = minutes_arrival
    
    @hours_departure.setter
    def hours_departure(self, values):
        hours_departure = {}
        errors = []
        for day, value in values.items() : 
            if value.isdigit():
                value = int(value)
                if value >= 0 and value <= 24 :
                    hours_departure[day] = value
                    continue
            errors.append(day)
        if len(errors) != 0 :
            raise ValueError(errors)
        self.__hours_departure = hours_departure
    
    @minutes_departure.setter
    def minutes_departure(self, values):
        minutes_departure = {}
        errors = []
        for day, value in values.items() : 
            if value.isdigit():
                value = int(value)
                if value >= 0 and value <= 60:
                    minutes_departure[day] = value
                    continue
            errors.append(day)
        if len(errors) != 0 :
            raise ValueError(errors)
        self.__minutes_departure = minutes_departure

    def process(self):
        def calculate_time(hours_arrival, minutes_arrival, hours_departure, minutes_departure):
            nonlocal total_minutes
            hours = hours_departure - hours_arrival
            minutes = minutes_departure - minutes_arrival - BREAK_IN_MINUTES
            while minutes < 0 :
                minutes += 60
                hours -=1
            if hours < 0 : 
                return (0, 0)
            total_minutes += hours * 60 + minutes
            return (hours, minutes)
        
        def calculate_total(minutes):
            hours = minutes // 60
            minutes = minutes % 60
            return (hours, minutes)
        
        total_minutes = 0
        for day in DAYS_OF_WEEK :
            self.__time[day] = calculate_time(
                self.hours_arrival[day], 
                self.minutes_arrival[day], 
                self.hours_departure[day], 
                self.minutes_departure[day]
            )
        
        time_left = WEEKLY_WORK_TIME - total_minutes
        self.__time["Total"] = calculate_total(total_minutes)
        self.__time["Left"] = calculate_total(time_left)

    def save_data(self):
        data = {}
        for day in DAYS_OF_WEEK:
            data[day] = {
                "hours_arrival": self.hours_arrival[day],
                "minutes_arrival": self.minutes_arrival[day],
                "hours_departure": self.hours_departure[day],
                "minutes_departure": self.minutes_departure[day],
            }

        with open("data.txt", "w") as f:
            json.dump(data, f)

    def load_data(self):
        try:
            with open("data.txt", "r") as f:
                data = json.load(f)
            for day in DAYS_OF_WEEK:
                self.hours_arrival[day] = data[day]["hours_arrival"]
                self.minutes_arrival[day] = data[day]["minutes_arrival"]
                self.hours_departure[day] = data[day]["hours_departure"]
                self.minutes_departure[day] = data[day]["minutes_departure"]
        except FileNotFoundError:
            pass
    
    def get_data(self):
        return [self.hours_arrival, self.minutes_arrival, self.hours_departure, self.minutes_departure]

class View(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.var_hours_arrival : dict [str, tk.StringVar] = {}
        self.var_minutes_arrival : dict [str, tk.StringVar] = {}
        self.var_hours_departure : dict [str, tk.StringVar] = {}
        self.var_minutes_departure : dict [str, tk.StringVar] = {}
        self.error_labels : dict [str, ttk.Label] = {}
        self.work_time : dict [str, ttk.Label] = {}

        ttk.Label(self, text="Arrivée").grid(row=0, column=1, columnspan=2)
        ttk.Label(self, text="Départ").grid(row=0, column=4, columnspan=2)
        ttk.Label(self, text="Temps de\ntravail", justify=tk.CENTER).grid(row=0, column=7, columnspan=2)

        ttk.Label(self, text=" ").grid(row=0, rowspan=8, column=3, padx=2)
        
        for i, day in enumerate(DAYS_OF_WEEK, 1):
            ttk.Label(self, text=day + ':').grid(row=i, column=0, padx=10)
            
            options = {'width' : 4, 'font' : ("Helvetica", 12)}

            # arrival hours entry
            self.var_hours_arrival[day] = tk.StringVar()
            ttk.Entry(self, textvariable=self.var_hours_arrival.get(day), **options).grid(row=i, column=1, sticky=tk.NSEW, pady=3)

            # arrival minutes entry
            self.var_minutes_arrival[day] = tk.StringVar()
            ttk.Entry(self, textvariable=self.var_minutes_arrival.get(day), **options).grid(row=i, column=2, sticky=tk.NSEW, pady=3)

            # departure hours entry
            self.var_hours_departure[day] = tk.StringVar()
            ttk.Entry(self, textvariable=self.var_hours_departure.get(day), **options).grid(row=i, column=4, sticky=tk.NSEW, pady=3)

            # departure minutes entry
            self.var_minutes_departure[day] = tk.StringVar()
            ttk.Entry(self, textvariable=self.var_minutes_departure.get(day), **options).grid(row=i, column=5, sticky=tk.NSEW, pady=3)

            self.error_labels[day] = ttk.Label(self, text = "     ")
            self.error_labels[day].grid(row=i, column=6, pady=3, padx=5)

            self.work_time[day] = ttk.Label(self, text = "    ")
            self.work_time[day].grid(row=i, column=7, pady=3, padx=5)

        ttk.Button(self, text='Valider', command=self.validate_button_clicked).grid(row=6, column=0, columnspan=5, pady=6)

        ttk.Label(self, text="Total").grid(row=6, column=5, columnspan=2)
        self.total_work_time = ttk.Label(self, text="     ")
        self.total_work_time.grid(row=6, column=7, pady=3, padx=5)

        ttk.Label(self, text="Temps restant").grid(row=7, column=4, columnspan=3)
        self.left_work_time = ttk.Label(self, text="     ")
        self.left_work_time.grid(row=7, column=7, pady=3, padx=5)

        # set the controller
        self.controller = None

    def update_view(self, data): 
        for day in DAYS_OF_WEEK:
            self.var_hours_arrival[day].set(data[0][day])
            self.var_minutes_arrival[day].set(data[1][day])
            self.var_hours_departure[day].set(data[2][day])
            self.var_minutes_departure[day].set(data[3][day])
    
    def set_controller(self, controller):
        self.controller = controller

    def validate_button_clicked(self):
        if self.controller:
            hours_arrival = {}
            minutes_arrival = {}
            hours_departure = {}
            minutes_departure = {}
            for day in DAYS_OF_WEEK:
                self.error_labels[day]['text'] = "        "
                hours_arrival[day] = self.var_hours_arrival.get(day).get()
                minutes_arrival[day] = self.var_minutes_arrival.get(day).get()
                hours_departure[day] = self.var_hours_departure.get(day).get()
                minutes_departure[day] = self.var_minutes_departure.get(day).get()
            
            self.controller.validate(hours_arrival, minutes_arrival, hours_departure, minutes_departure)

    def show_error(self, days):
        for day in days :
            self.error_labels[day]['text'] = "Invalid value(s)"
            self.error_labels[day]['foreground'] = 'red'
            self.error_labels[day].after(5000, lambda: self.hide_message(day))

    def show_time(self, time : dict):
        for key, (hours, minutes) in time.items() :
            if key == "Total":
                self.total_work_time['text'] = f"{hours}:"+"{:02d}".format(minutes)
            elif key == "Left" :
                self.left_work_time['text'] = f"{hours}:"+"{:02d}".format(minutes)
            else :
                self.work_time[key]['text'] = f"{hours}:"+"{:02d}".format(minutes)

    def hide_message(self, day):
        self.error_labels[day]['text'] = "        "


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def validate(self, hours_arrival, minutes_arrival, hours_departure, minutes_departure):
        try:
            self.model.hours_arrival = hours_arrival
            self.model.minutes_arrival = minutes_arrival
            self.model.hours_departure = hours_departure
            self.model.minutes_departure = minutes_departure

            self.model.process()
            
            self.view.show_time(self.model.time)

        except ValueError as error:
            days, *_ = error.args
            self.view.show_error(days)

    def save_data(self):
        self.view.validate_button_clicked()
        self.model.save_data()
        self.view.master.destroy()

    def load_data(self):
        self.model.load_data()
        self.view.update_view(self.model.get_data())


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('HebdoTime')
        self.tk.call("wm", "iconphoto", self._w, tk.PhotoImage(file=os.path.join(BASE_PATH, "icon.png")))
        
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12))
        # create a model
        model = Model()

        # create a view and place it on the root window
        view = View(self)
        view.grid(row=0, column=0, padx=10, pady=10)

        # create a controller
        controller = Controller(model, view)
        controller.load_data()

        # set the controller to view
        view.set_controller(controller)

        self.protocol("WM_DELETE_WINDOW", controller.save_data)


if __name__ == '__main__':
    if getattr(sys, "frozen", False):
        BASE_PATH = sys._MEIPASS
    else:
        BASE_PATH = os.path.abspath(".")
    app = App()
    app.mainloop()