from Defines import app_abbreviation, app_name, app_version, get_resource_path, default_size_x, default_size_y
from Page_Home import HomePage
from Page_Prompt import PromptWindow
import tkinter as tk

def exit_prompt(root):
    PromptWindow(root, "Are you sure you wish to quit the application?", root.destroy)

window_root = tk.Tk()
window_root.title("{0}: {1} - v{2}".format(app_abbreviation, app_name, app_version))
window_root.iconbitmap(get_resource_path("NEAT.ico"))
window_root.minsize(default_size_x, default_size_y)
window_root.wm_protocol("WM_DELETE_WINDOW", lambda: exit_prompt(window_root))  # does work
main = HomePage(window_root)
window_root.mainloop()