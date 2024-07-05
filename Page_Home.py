import Defines
from Defines import get_colour_style
from Defines import OptionButtonsRow as OptionsRow
from Page_OK import OKWindow
from Page_Configuration import ConfigPage
from Page_Prompt import PromptWindow
from Page_Test import TestPage
from SaveManager import SaveManager
import tkinter as tk

def sort_display_index(item):
    return item.display_index

class HomePage:
    def __init__(self, root):
        # Declare
        self.root = root
        self.main_frame = tk.Frame(root, bg=get_colour_style(0))
        self.main_frame.bind_all('<Delete>', self.delete_test_prompt)
        title_label = tk.Label(self.main_frame, text="{0}: {1}".format(Defines.app_abbreviation, Defines.app_name),
                               anchor="w", font=Defines.font_style_title, fg=get_colour_style(0), bg=get_colour_style(4))
        subtitle_label = tk.Label(self.main_frame, text="Saved Tests", anchor="w", font=Defines.font_style_subtitle,
                                  fg=get_colour_style(100), bg=get_colour_style(0))
        self.tests_listbox = tk.Listbox(self.main_frame)
        self.tests_listbox.bind("<Button-1>", self.set_drag_drop_test)
        self.tests_listbox.bind("<B1-Motion>", self.move_drag_drop_test)
        self.drag_drop_test = None
        self.buttons_frame = tk.Frame(self.main_frame, bg=get_colour_style(5))

        # Define
        self.__init_buttons()
        self.update_listbox()

        # Draw
        title_label.grid(column=0, row=0, columnspan=2, sticky="WE")
        subtitle_label.grid(column=1, row=1, sticky="WE")

        self.tests_listbox.grid(column=1, row=2, sticky="NEWS", padx=5, pady=5)
        self.buttons_frame.grid(column=0, row=1, rowspan=2, sticky="NS")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

    def __init_buttons(self):
        bg_c = get_colour_style(5)
        fg_c = get_colour_style(0)
        font_style = Defines.font_style_home_button
        new_button = tk.Button(self.buttons_frame, text="New", bg=bg_c, fg=fg_c, font=font_style,
                               command=self.to_configuration_mode, width=15)
        edit_button = tk.Button(self.buttons_frame, text="Edit", font=font_style, fg=fg_c, bg=bg_c,
                                command=self.edit_test)
        delete_button = tk.Button(self.buttons_frame, text="Delete", bg=bg_c, fg=fg_c, font=font_style,
                                  command=self.delete_test_prompt)
        open_button = tk.Button(self.buttons_frame, text="Take Test", bg=bg_c, fg=fg_c, font=font_style,
                                command=self.to_test_mode)
        about_button = tk.Button(self.buttons_frame, text="About", bg=bg_c, fg=fg_c, font=font_style,
                                 command=self.show_about_window)

        new_button.grid(column=0, row=OptionsRow.NEW.value, sticky="WE")
        edit_button.grid(column=0, row=OptionsRow.EDIT.value, sticky="WE")
        delete_button.grid(column=0, row=OptionsRow.DELETE.value, sticky="WE")
        open_button.grid(column=0, row=OptionsRow.OPEN.value, sticky="WE")
        about_button.grid(column=0, row=OptionsRow.ABOUT.value, sticky="WE")

    def set_drag_drop_test(self, event):
        self.drag_drop_test = self.tests_listbox.nearest(event.y)

    def move_drag_drop_test(self, event):
        i = self.tests_listbox.nearest(event.y)
        if i == self.drag_drop_test:
            return

        move_value = 1 if i < self.drag_drop_test else -1
        temp_listbox_entry = self.tests_listbox.get(i)
        self.tests_listbox.delete(i)
        self.tests_listbox.insert(i + move_value, temp_listbox_entry)
        temp_save_data_entry = SaveManager.instance().save_data[i]
        del SaveManager.instance().save_data[i]
        SaveManager.instance().save_data.insert(i + move_value, temp_save_data_entry)
        self.drag_drop_test = i

        SaveManager.instance().save_display_order(self.tests_listbox.get(0, tk.END))

    def update_listbox(self):
        self.tests_listbox.delete(0, tk.END)
        SaveManager.instance().save_data.sort(key=sort_display_index)

        self.tests_listbox.insert("end", *[entry.name for entry in SaveManager.instance().save_data])
        SaveManager.instance().save_display_order(self.tests_listbox.get(0, tk.END))

    def edit_test(self):
        selection = self.tests_listbox.curselection()
        if len(selection) > 0:
            test_name = self.tests_listbox.get(self.tests_listbox.curselection())
            test_data = SaveManager.instance().get_test(test_name)
            self.to_configuration_mode(test_data)

    def delete_test_prompt(self, event=None):
        selection = self.tests_listbox.curselection()
        if len(selection) > 0:
            test_name = self.tests_listbox.get(self.tests_listbox.curselection())
            prompt_text = "You are about to delete '{0}'\nAre you sure you wish to proceed?".format(test_name)
            PromptWindow(self.root, prompt_text, self.delete_test)

    def delete_test(self):
        selection = self.tests_listbox.curselection()
        if len(selection) > 0:
            test_name = self.tests_listbox.get(self.tests_listbox.curselection())
            SaveManager.instance().delete_test(test_name)
            self.update_listbox()

    def to_configuration_mode(self, test_data=None):
        self.main_frame.forget()
        self.main_frame.unbind_all('<Delete>')
        ConfigPage(self.root, self.from_configuration_mode, test_data)

    def from_configuration_mode(self):
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.update_listbox()
        self.main_frame.bind_all('<Delete>')

    def to_test_mode(self):
        selected_test = self.tests_listbox.curselection()
        if len(selected_test) > 0:
            self.main_frame.unbind_all('<Delete>')
            self.main_frame.forget()
            TestPage(self.root, self.from_test_mode, SaveManager.instance().save_data[selected_test[0]])

    def from_test_mode(self):
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.bind_all('<Delete>')

    def show_about_window(self):
        OKWindow(self.main_frame, "About", "Designed by Sunim Koria\nDeveloped by Charles Withall")
