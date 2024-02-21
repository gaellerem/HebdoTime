import json
import os
import sys
import tkinter as tk
import customtkinter as ctk

DAYS_OF_WEEK = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
BREAK_IN_MINUTES = 60
WEEKLY_WORK_TIME = 2310


class Model:
    def __init__(self):
        self.reset()

    @property
    def arrivals(self):
        return self.__arrivals

    @property
    def departures(self):
        return self.__departures

    @property
    def time(self):
        return self.__time

    @arrivals.setter
    def arrivals(self, values):
        arrivals = {}
        errors = []
        for day, (hours, minutes) in values.items() :
            if hours.isdigit() and minutes.isdigit():
                hours = int(hours)
                minutes = int(minutes)
                if hours >= 0 and hours <= 24 and minutes >= 0 and minutes <= 60:
                    arrivals[day] = (hours, minutes)
                    continue
            errors.append(day)
        if len(errors) != 0 :
            raise ValueError(errors)
        self.__arrivals = arrivals

    @departures.setter
    def departures(self, values):
        departures = {}
        errors = []
        for day, (hours, minutes) in values.items() :
            if hours.isdigit() and minutes.isdigit():
                hours = int(hours)
                minutes = int(minutes)
                if hours >= 0 and hours <= 24 and minutes >= 0 and minutes <= 60:
                    departures[day] = (hours, minutes)
                    continue
            errors.append(day)
        if len(errors) != 0 :
            raise ValueError(errors)
        self.__departures = departures

    def reset(self):
        self.__arrivals = {day: (0,0) for day in DAYS_OF_WEEK}
        self.__departures = {day: (0,0) for day in DAYS_OF_WEEK}
        self.__time = {day: (0,0) for day in DAYS_OF_WEEK}

    def process(self):
        def calculate_time(arrival, departure):
            nonlocal total_minutes
            hours = departure[0] - arrival[0]
            minutes = departure[1] - arrival[1] - BREAK_IN_MINUTES
            while minutes < 0 :
                minutes += 60
                hours -=1
            if hours < 0 : 
                return (0, 0)
            total_minutes += hours * 60 + minutes
            return (hours, minutes)
        
        def calculate_total(total_minutes):
            hours = abs(total_minutes) // 60
            minutes = abs(total_minutes) % 60
            if total_minutes > 0 :
                return (hours, minutes) 
            elif hours == 0 :
                return (hours, -minutes)
            else :
                return (-hours, minutes)
        
        total_minutes = 0
        for day in DAYS_OF_WEEK :
            self.__time[day] = calculate_time(
                self.arrivals[day],
                self.departures[day]
            )
        
        time_left = WEEKLY_WORK_TIME - total_minutes
        self.__time["Total"] = calculate_total(total_minutes)
        self.__time["Left"] = calculate_total(time_left)

    def save_data(self):
        data = {}
        for day in DAYS_OF_WEEK:
            data[day] = {
                "arrivals": self.arrivals[day],
                "departures": self.departures[day],
            }

        with open("data.txt", "w") as f:
            json.dump(data, f)

    def load_data(self):
        try:
            with open("data.txt", "r") as f:
                data = json.load(f)
            for day in DAYS_OF_WEEK:
                try :
                    self.arrivals[day] = data[day]["arrivals"]
                    self.departures[day] = data[day]["departures"]
                except KeyError:
                    self.arrivals[day] = (0,0)
                    self.departures[day] = (0,0)
        except FileNotFoundError:
            pass

    def get_data(self):
        return [self.arrivals, self.departures]


class View(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.var_hours_arrival : dict [str, tk.StringVar] = {}
        self.var_minutes_arrival : dict [str, tk.StringVar] = {}
        self.var_hours_departure : dict [str, tk.StringVar] = {}
        self.var_minutes_departure : dict [str, tk.StringVar] = {}
        self.error_labels : dict [str, ctk.CTkLabel] = {}
        self.work_time : dict [str, ctk.CTkLabel] = {}

        my_font = ctk.CTkFont(family="Helvetica", size=16)

        ctk.CTkLabel(self, text="Arrivée", font=my_font).grid(row=0, column=1, columnspan=2)
        ctk.CTkLabel(self, text="Départ", font=my_font).grid(row=0, column=4, columnspan=2)
        ctk.CTkLabel(self, text="Temps de\ntravail", font=my_font).grid(row=0, column=7, padx=5, pady=5)

        ctk.CTkLabel(self, text="   ").grid(row=0, rowspan=8, column=3, padx=2)
        ctk.CTkLabel(self, text="   ").grid(row=0, rowspan=8, column=8, padx=3)
        options = {"width" : 45, "height" : 30, "font" : my_font}
        
        for i, day in enumerate(DAYS_OF_WEEK, 1):
            ctk.CTkLabel(self, text=day + ':', font=my_font).grid(row=i, column=0, padx=10)

            # arrival hours entry
            self.var_hours_arrival[day] = tk.StringVar()
            ctk.CTkEntry(self, textvariable=self.var_hours_arrival.get(day), **options).grid(row=i, column=1, sticky=tk.NSEW, pady=3)

            # arrival minutes entry
            self.var_minutes_arrival[day] = tk.StringVar()
            ctk.CTkEntry(self, textvariable=self.var_minutes_arrival.get(day), **options).grid(row=i, column=2, sticky=tk.NSEW, pady=3)

            # departure hours entry
            self.var_hours_departure[day] = tk.StringVar()
            ctk.CTkEntry(self, textvariable=self.var_hours_departure.get(day), **options).grid(row=i, column=4, sticky=tk.NSEW, pady=3)

            # departure minutes entry
            self.var_minutes_departure[day] = tk.StringVar()
            ctk.CTkEntry(self, textvariable=self.var_minutes_departure.get(day), **options).grid(row=i, column=5, sticky=tk.NSEW, pady=3)

            self.error_labels[day] = ctk.CTkLabel(self, text = "     ", font=my_font)
            self.error_labels[day].grid(row=i, column=6, pady=3, padx=5)

            self.work_time[day] = ctk.CTkLabel(self, text = "    ", font=my_font)
            self.work_time[day].grid(row=i, column=7, pady=3, padx=5)

        ctk.CTkButton(self, text='Valider', command=self.validate_button_clicked, width = 100, font=my_font).grid(row=6, column=0, columnspan=3, pady=6)
        ctk.CTkButton(self, text='Réinitialiser', command=self.reset_clicked, width = 100, font=my_font).grid(row=7, column=0, columnspan=3, pady=6)

        ctk.CTkLabel(self, text="Total", font=my_font).grid(row=6, column=4, columnspan=3)
        self.total_work_time = ctk.CTkLabel(self, text="     ", font=my_font)
        self.total_work_time.grid(row=6, column=7, pady=3, padx=5)

        ctk.CTkLabel(self, text="Temps restant", font=my_font).grid(row=7, column=4, columnspan=3)
        self.left_work_time = ctk.CTkLabel(self, text="     ", font=my_font)
        self.left_work_time.grid(row=7, column=7, pady=3, padx=5)

        self.controller = None

    def update_view(self, data): 
        for day in DAYS_OF_WEEK:
            self.var_hours_arrival[day].set(data[0][day][0])
            self.var_minutes_arrival[day].set("{:02d}".format(data[0][day][1]))
            self.var_hours_departure[day].set(data[1][day][0])
            self.var_minutes_departure[day].set("{:02d}".format(data[1][day][1]))
    
    def set_controller(self, controller):
        self.controller = controller

    def reset_clicked(self):
        if self.controller:
            self.controller.reset()
        for day in DAYS_OF_WEEK:
            self.var_hours_arrival[day].set(0)
            self.var_minutes_arrival[day].set(0)
            self.var_hours_departure[day].set(0)
            self.var_minutes_departure[day].set(0)

    def validate_button_clicked(self):
        if self.controller:
            arrivals = {}
            departures = {}
            for day in DAYS_OF_WEEK:
                self.error_labels[day]['text'] = "        "
                arrivals[day] = (self.var_hours_arrival.get(day).get(), self.var_minutes_arrival.get(day).get())
                departures[day] = (self.var_hours_departure.get(day).get(), self.var_minutes_departure.get(day).get())
            self.controller.validate(arrivals, departures)

    def show_error(self, days):
        for day in days :
            self.error_labels[day].configure(text="Invalid value(s)")
            self.error_labels[day]['foreground'] = 'red'
            self.error_labels[day].after(5000, lambda: self.hide_message(day))

    def show_time(self, time : dict):
        for key, (hours, minutes) in time.items() :
            if key == "Total":
                self.total_work_time.configure(text=f"{hours}:"+"{:02d}".format(minutes))
            elif key == "Left" :
                self.left_work_time.configure(text=f"{hours}:"+"{:02d}".format(minutes))
            else :
                self.work_time[key].configure(text=f"{hours}:"+"{:02d}".format(minutes))

    def hide_message(self, day):
        self.error_labels[day]['text'] = "        "


class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def validate(self, arrivals, departures):
        try:
            self.model.arrivals = arrivals
            self.model.departures = departures

            self.model.process()
            
            self.view.show_time(self.model.time)

        except ValueError as error:
            days, *_ = error.args
            self.view.show_error(days)

    def reset(self):
        self.model.reset()

    def save_data(self):
        self.view.validate_button_clicked()
        self.model.save_data()
        self.view.master.destroy()

    def load_data(self):
        self.model.load_data()
        self.view.update_view(self.model.get_data())


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title('HebdoTime')
        #self.geometry("420x320")
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

        # create a model
        model = Model()

        # create a view and place it on the root window
        view = View(self)
        view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

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
