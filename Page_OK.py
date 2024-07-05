import tkinter as tk
from Defines import get_colour_style, default_font_name

_is_active = False

class OKWindow:
    def __init__(self, root, header, text):
        global _is_active
        if _is_active:
            return

        _is_active = True
        self.window = tk.Toplevel(root, bg=get_colour_style(0))
        self.window.wm_title(header)
        self.window.update()
        x_pos = int(self.window.winfo_screenwidth() / 2 - self.window.winfo_width() / 2)
        y_pos = int(self.window.winfo_screenheight() / 2 - self.window.winfo_height() / 2)

        self.window.geometry("+{0}+{1}".format(x_pos, y_pos))
        self.window.resizable(width=False, height=False)
        self.window.grab_set()

        label = tk.Label(self.window, text=text, bg=get_colour_style(0), font=default_font_name)
        button = tk.Button(self.window, text="OK", command=self.destroy, width=10, fg=get_colour_style(0),
                           bg=get_colour_style(5), font=default_font_name)

        button.bind("<Return>", self.destroy)
        button.focus()
        label.grid(column=0, row=0, columnspan=2, sticky="EW", padx=10, pady=5)
        button.grid(column=0, row=1, padx=10, pady=10)

    def destroy(self, event=None):
        global _is_active
        _is_active = False
        self.window.destroy()

