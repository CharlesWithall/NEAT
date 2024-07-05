import Defines
from Defines import get_colour_style
from Page_OK import OKWindow
from Page_Prompt import PromptWindow
from SaveManager import SaveManager
from StatementsPanel import StatementPanel

import tkinter as tk

default_test_name = "New Test (click here to rename)"
test_title_text = "test_title_text"
test_title_entry = "test_title_entry"

class ConfigPage:
    def __init__(self, root, return_callback, test_data=None):
        self.return_callback = return_callback
        self.title_edit_mode = False

        # Declare Frames
        self.main_frame = tk.Frame(root)
        self.left_frame = tk.Frame(self.main_frame, bg=get_colour_style(5))
        self.right_frame = tk.Frame(self.main_frame, bg=get_colour_style(0))

        self.title_frame = tk.Frame(self.main_frame)
        self.title_label = tk.Label(self.title_frame, text=default_test_name, fg=get_colour_style(0),
                                    font=Defines.font_style_title, bg=get_colour_style(4), name=test_title_text)
        self.description_label = tk.Label(self.left_frame, text="Test Instructions:", font=Defines.font_style_subtitle,
                                          anchor="w", fg=get_colour_style(0), bg=get_colour_style(5))
        self.description_text = tk.Text(self.left_frame, wrap=tk.WORD)
        self.pass_threshold_frame = tk.Frame(self.left_frame)
        self.pass_threshold_var = tk.IntVar()
        self.pass_threshold_var.set(100)
        self.pass_threshold_var.trace_add('write', self.on_pass_threshold_change)
        self.pass_threshold_label = tk.Label(self.pass_threshold_frame, text="Pass Mark: ", font=Defines.font_style_subtitle,
                                             anchor="e", fg=get_colour_style(0), bg=get_colour_style(5))
        self.pass_threshold_slider = tk.Scale(self.pass_threshold_frame, variable=self.pass_threshold_var, orient=tk.HORIZONTAL, showvalue=0, bg=get_colour_style(5))
        self.pass_threshold_pass_mark_label = tk.Label(self.pass_threshold_frame, text="{0}%".format(self.pass_threshold_var.get()),
                                                       font=Defines.font_style_subtitle, fg=get_colour_style(0), bg=get_colour_style(5))
        self.statement_panel = StatementPanel(self.right_frame, self.on_statements_changed)
        self.empty_statements_label = tk.Label(self.right_frame, text="No statements added.\nUse the box below to start adding statements for this test", bg=get_colour_style(0), font=Defines.default_font_name)
        self.new_statement_frame = tk.Frame(self.right_frame, bg=get_colour_style(0))
        self.generation_frame = tk.Frame(self.left_frame)

        # Define Frames
        self.main_frame.bind_all("<Button-1>", self._on_left_click)
        self.description_text['height'] = 4
        self.description_text['width'] = 40
        self.__init_new_statement()
        self.__init_generate_buttons()

        # Draw Frames
        self.title_frame.grid(column=0, row=0, columnspan=3, sticky="WE")
        self.title_label.pack(fill=tk.BOTH, expand=True)
        self.draw_left_panel()
        self.draw_right_panel()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        self.pass_threshold_pass_mark_label.config(width=5)
        self.__init_test_data(test_data)

    def draw_left_panel(self):
        self.description_label.grid(column=0, row=0, columnspan=2, sticky="WE")
        self.description_text.grid(column=0, row=1, columnspan=2, sticky="NEWS", padx=5, pady=5)
        self.pass_threshold_frame.grid(column=0, row=2, columnspan=2, sticky="WE", padx=5, pady=5)
        self.pass_threshold_label.grid(column=0, row=0, sticky="WE")
        self.pass_threshold_slider.grid(column=1, row=0, sticky="WE")
        self.pass_threshold_pass_mark_label.grid(column=2, row=0, sticky="WE")
        self.pass_threshold_frame.grid_columnconfigure(1, weight=1)
        self.generation_frame.grid(column=0, row=3, columnspan=2, sticky="WE", padx=5, pady=(0, 5))
        self.left_frame.grid(column=0, row=1, sticky="NEWS")
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(1, weight=1)

    def draw_right_panel(self):
        self.empty_statements_label.grid(column=0, row=0, sticky="NEWS")
        self.new_statement_frame.grid(column=0, row=1, sticky="WE", padx=5, pady=5)
        self.right_frame.grid(column=1, row=1, sticky="NEWS")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

    def __init_new_statement(self):
        self.new_statement_entry = tk.Entry(self.new_statement_frame)
        self.new_statement_entry.bind('<Return>', self.add_statement)
        button = tk.Button(self.new_statement_frame, text="Add Statement", command=lambda: self.add_statement(self.new_statement_entry.get()))
        self.new_statement_entry.grid(column=0, row=0, sticky="WE", padx=(0, 5))
        button.grid(column=1, row=0)
        self.new_statement_frame.grid_columnconfigure(0, weight=1)

    def __init_generate_buttons(self):
        generate_btn = tk.Button(self.generation_frame, text="Save", bg=get_colour_style(5), fg=get_colour_style(0), font=Defines.default_font_name, command=self.save_prompt)
        cancel_btn = tk.Button(self.generation_frame, text="Cancel", bg=get_colour_style(5), fg=get_colour_style(0), font=Defines.default_font_name, command=self.to_home_mode_prompt)
        generate_btn.grid(row=0, column=0, sticky="WE")
        cancel_btn.grid(row=0, column=1, sticky="WE")
        for i in range(2):
            self.generation_frame.grid_columnconfigure(i, weight=1)

    def __init_test_data(self, test_data):
        self.on_statements_changed()
        if test_data is not None:
            self.title_label["text"] = test_data.name
            self.description_text.insert(tk.END, test_data.description)
            self.pass_threshold_var.set(test_data.pass_threshold)
        self.statement_panel.load_statements(test_data)
        self.cached_test_index = len(SaveManager.instance().save_data) if test_data is None else test_data.display_index
        self.cached_test_name = "" if test_data is None else test_data.name

    def _on_left_click(self, event):
        self.statement_panel.on_left_click(event)
        widget_name = str(event.widget).split(".")[-1]
        if widget_name == test_title_text:
            self.title_entry = tk.Entry(self.title_frame, name=test_title_entry, bg=get_colour_style(4), fg=get_colour_style(0), font=Defines.font_style_title, justify=tk.CENTER)
            self.title_entry.bind('<Return>', self.set_title)
            self.title_entry.delete(0, 'end')
            test_name = self.title_label['text']
            if test_name != default_test_name:
                self.title_entry.insert(0, test_name)
            self.title_label.pack_forget()
            self.title_entry.pack(fill=tk.BOTH, expand=True)
            self.title_entry.focus_set()
            self.title_edit_mode = True
        elif self.title_edit_mode and widget_name != test_title_entry:
            self.set_title()

    def on_pass_threshold_change(self, unused_var, unused_index, unused_mode):
        score = self.pass_threshold_var.get()
        self.pass_threshold_pass_mark_label['text'] = "{0}%".format(score)
        self.pass_threshold_pass_mark_label.config(width=5)

    def on_statements_changed(self):
        sp = self.statement_panel
        right_statements_count = 0 if sp.right_answer_block is None else len(sp.right_answer_block.statements)
        wrong_statements_count = 0 if sp.wrong_answer_block is None else len(sp.wrong_answer_block.statements)
        if right_statements_count + wrong_statements_count > 0:
            self.empty_statements_label.grid_forget()
        else:
            self.empty_statements_label.grid(column=0, row=0, sticky="NSEW")

    def set_title(self, event=None):
        self.title_label['text'] = self.title_entry.get()
        self.title_entry.destroy()
        self.title_label.pack(fill=tk.BOTH, expand=True)
        self.title_edit_mode = False

    def add_statement(self, text=None):
        text = text if type(text) == str else self.new_statement_entry.get()

        self.new_statement_entry.delete(0, 'end')
        self.statement_panel.add_statement(text)
        self.statement_panel.scores_panel.clear()

    def save_prompt(self):
        title_text = self.title_label['text']
        if title_text == default_test_name or len(title_text) == 0:
            OKWindow(self.main_frame, "Save Error", str.format("Your test doesn't have a name!\nClick '{0}' at the top of the window to name your test.", default_test_name))
        elif title_text.upper() in [o.name.upper() for o in SaveManager.instance().save_data] and title_text.upper() != self.cached_test_name.upper():
            OKWindow(self.main_frame, "Save Error", str.format("There is already a test by this name!\nPlease give your test a unique name."))
        else:
            prompt_text = "You are about to save this test.\nProceed?"
            for statement in self.statement_panel.right_answer_block.statements:
                found = False
                for score in statement.scores:
                    if score == 100:
                        found = True
                        break
                if not found:
                    prompt_text = "Not all answers have a 100% correct answer!\nYou can still save this test, but nobody will be able to get a score of 100%\nProceed?"

            PromptWindow(self.main_frame, prompt_text, self.save)

    def save(self):
        statements_to_save = {}
        sp = self.statement_panel
        title = self.title_label["text"]
        for statement in sp.right_answer_block.statements + sp.wrong_answer_block.statements:
            statements_to_save[statement.statement] = statement.scores
        SaveManager.instance().save_test(title, self.description_text.get(1.0, tk.END).strip("\n"),
                                         self.pass_threshold_var.get(), len(sp.right_answer_block.statements),
                                         statements_to_save, self.cached_test_index)
        if self.cached_test_name != "" and self.cached_test_name != title:
            SaveManager.instance().delete_test(self.cached_test_name)
        self.to_home_mode()

    def to_home_mode_prompt(self):
        prompt_text = "You are about to return to the home screen.\nAll changes will be lost.\nAre you sure you wish to proceed?"
        PromptWindow(self.main_frame, prompt_text, self.to_home_mode)

    def to_home_mode(self):
        self.statement_panel.scores_panel.clear()
        self.statement_panel.canvas.delete("all")
        self.main_frame.unbind_all("<Button-1>")
        self.main_frame.destroy()
        self.return_callback()

