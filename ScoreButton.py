import tkinter as tk
from Defines import get_colour_gradient, score_lower_limit, score_upper_limit

class ScoreButton(tk.Button):
    def __init__(self, frame):
        self.text = tk.StringVar()
        tk.Button.__init__(self, frame, textvariable=self.text, width=4, state=tk.DISABLED, disabledforeground="black")
        self.drag_position = 0
        self.text.set("0%")
        self.configure(bg=get_colour_gradient(0))

        self.bind("<ButtonPress-1>", self.drag_start)
        self.bind("<B1-Motion>", self.drag)

    def drag_start(self, event):
        self.drag_position = event.y

    def drag(self, event):
        delta_y = event.y - self.drag_position
        result = self.get_score_as_int() - delta_y
        if score_lower_limit <= result <= score_upper_limit:
            self.drag_position = event.y
            self.set_score(result)

    def get_score_as_int(self):
        return int(self.text.get().split('%')[0])

    def set_score(self, score):
        self.text.set(str(score) + "%")
        self.configure(bg=get_colour_gradient(score))

class HeaderButton(tk.Button):
    def __init__(self, frame, i):
        tk.Button.__init__(self, frame, text=str(i+1), width=4, state=tk.DISABLED, disabledforeground="black")
