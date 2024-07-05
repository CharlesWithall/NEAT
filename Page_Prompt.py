import tkinter as tk
from Defines import get_colour_style, default_font_name

header_text = "Are you sure?"

class PromptWindow:
    def __init__(self, root, text, confirm_callback):
        self.confirm_callback = confirm_callback
        window = tk.Toplevel(root, bg=get_colour_style(0))
        window.wm_title(header_text)
        window.update()
        x_pos = int(window.winfo_screenwidth() / 2 - window.winfo_width() / 2)
        y_pos = int(window.winfo_screenheight() / 2 - window.winfo_height() / 2)

        window.geometry("+{0}+{1}".format(x_pos, y_pos))
        window.resizable(width=False, height=False)
        window.grab_set()

        label = tk.Label(window, text=text, bg=get_colour_style(0), font=default_font_name)
        button_reset = tk.Button(window, text="Confirm", command=lambda: self.confirm(window), width=10,
                                 fg=get_colour_style(0), bg=get_colour_style(5), font=default_font_name)
        button_cancel = tk.Button(window, text="Cancel", command=window.destroy, width=10,
                                  fg=get_colour_style(0), bg=get_colour_style(5), font=default_font_name)

        label.grid(column=0, row=0, columnspan=2, sticky="EW", padx=10, pady=5)
        button_reset.grid(column=0, row=1, padx=10, pady=10)
        button_cancel.grid(column=1, row=1, padx=10, pady=10)

    def confirm(self, prompt_window):
        prompt_window.destroy()
        self.confirm_callback()
