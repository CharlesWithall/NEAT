from AnswerBook import AnswerBook
from Defines import TestPageRow, get_colour_style, default_font_name, font_style_title, font_style_subtitle
from Page_Results import ResultsPage
from Page_Prompt import PromptWindow
import tkinter as tk

class TestPage:
    def __init__(self, root, return_callback, test_data):
        self.return_callback = return_callback
        self.root = root
        cached_window_size = "{0}x{1}".format(root.winfo_width(), root.winfo_height())
        # Declare
        self.main_frame = tk.Frame(root)
        self.title_label = tk.Label(self.main_frame, text=test_data.name, font=font_style_title,
                                    bg=get_colour_style(4), fg=get_colour_style(0))
        self.description_label = tk.Label(self.main_frame, text=test_data.description, font=font_style_subtitle,
                                          fg=get_colour_style(0), bg=get_colour_style(5))
        self.answer_book = AnswerBook(self.main_frame, test_data.statements, test_data.answer_count)
        self.options_frame = tk.Frame(self.main_frame)

        # Define
        self.description_label.bind('<Configure>', self.set_description_wrap)
        self.__init_options()

        # Draw
        self.title_label.grid(column=0, row=TestPageRow.TITLE.value, columnspan=2, sticky="WE")
        self.description_label.grid(column=0, row=TestPageRow.DESCRIPTION.value, columnspan=2, sticky="WE")
        self.options_frame.grid(column=0, row=TestPageRow.OPTIONS.value, columnspan=2, sticky="WE")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame.grid_rowconfigure(TestPageRow.TESTCANVAS.value, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        root.geometry(cached_window_size)

    def __init_options(self):
        confirm_button = tk.Button(self.options_frame, text="Finish", command=self.to_results_mode_prompt,
                                   fg=get_colour_style(0), bg=get_colour_style(5), font=default_font_name)
        reset_button = tk.Button(self.options_frame, text="Reset", command=self.answer_book.reset_prompt,
                                 fg=get_colour_style(0), bg=get_colour_style(5), font=default_font_name)
        back_button = tk.Button(self.options_frame, text="Back", command=self.to_home_mode_prompt,
                                fg=get_colour_style(0), bg=get_colour_style(5), font=default_font_name)

        confirm_button.grid(row=0, column=0, sticky="WE")
        reset_button.grid(row=0, column=1, sticky="WE")
        back_button.grid(row=0, column=2, sticky="WE")

        for i in range(3):
            self.options_frame.grid_columnconfigure(i, weight=1)

    def set_description_wrap(self, event):
        self.description_label["wraplength"] = self.main_frame.winfo_width()

    def to_home_mode_prompt(self):
        prompt_text = """You are about to quit the test.\nAll changes will be lost.\nAre you sure you wish to proceed?"""
        PromptWindow(self.root, prompt_text, self.to_home_mode)

    def to_home_mode(self):
        self.main_frame.destroy()
        self.return_callback()

    def to_results_mode_prompt(self):
        show_warning = not self.answer_book.get_all_slots_filled()
        not_all_questions_answered_text = "WARNING: Not all sections have been answered!\n" if show_warning else ""
        main_text = "Are you sure you want to complete this test and see your results?"
        prompt_text = "{0}{1}".format(not_all_questions_answered_text, main_text)
        PromptWindow(self.root, prompt_text, self.to_results_mode)

    def to_results_mode(self):
        ResultsPage(self.root, self.title_label['text'], self.answer_book, self.return_callback)
        self.main_frame.destroy()

