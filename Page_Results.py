import tkinter as tk
from Defines import PositionAccuracy as Accuracy
from Defines import get_colour_gradient, get_colour_style, font_style_title, default_font_name
from SaveManager import SaveManager

class ResultsPage:
    def __init__(self, root, title, answer_book, return_callback):
        self.return_callback = return_callback

        # Declare Frames
        self.main_frame = tk.Frame(root)
        self.final_score, self.statements, self.accuracies = answer_book.calculate_result()

        self.title_label = tk.Label(self.main_frame, text=title, font=font_style_title,
                                    fg=get_colour_style(0), bg=get_colour_style(4))
        self.result_label = tk.Label(self.main_frame, text="{0}%".format(self.final_score), font=(default_font_name, 44), bg=get_colour_gradient(self.final_score))
        self.answers_frame = tk.Frame(self.main_frame, bg=get_colour_style(0))
        self.scrollbar = tk.Scrollbar(self.answers_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        pass_threshold = SaveManager.instance().get_test(title).pass_threshold
        is_success_text = "Congratulations! You have passed." if self.final_score >= pass_threshold else "You have failed."
        self.win_lose_label = tk.Label(self.main_frame, text=is_success_text, font=font_style_title, bg=get_colour_gradient(self.final_score))
        self.back_button = tk.Button(self.main_frame, text="Home", command=self.to_home_mode,
                                     fg=get_colour_style(0), bg=get_colour_style(5), font=default_font_name)

        # Define Frames
        self.__init_answer_frame()

        # Draw Frames
        self.title_label.grid(column=0, row=0, sticky="WE")
        self.result_label.grid(column=0, row=1, sticky="WE")
        self.answers_frame.grid(column=0, row=2, sticky="NEWS")
        self.win_lose_label.grid(column=0, row=3, sticky="WE")
        self.back_button.grid(column=0, row=4, sticky="WE")

        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def __init_answer_frame(self):
        text = tk.Text(self.answers_frame, wrap=tk.WORD, tabs="0.75c")
        text.pack(expand=True, fill=tk.BOTH)
        text.tag_config("wrong", foreground='red', font=default_font_name)
        text.tag_config("partial", foreground=get_colour_gradient(50), font=default_font_name)
        text.tag_config("correct", foreground='green', font=default_font_name)
        text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=text.yview)
        for i in range(len(self.statements)):
            statement, tag = self.format_answer_statement(i)
            text.insert(tk.END, statement, tag)
            text.insert(tk.END, "\n")
        text.config(state=tk.DISABLED)

    def format_answer_statement(self, i):
        statement = self.statements[i]
        accuracy = self.accuracies[i]

        if accuracy == Accuracy.INCORRECT:
            tag = "wrong"
            mark = "x"
        elif accuracy == Accuracy.PARTIALLY_CORRECT:
            tag = "partial"
            mark = "-"
        elif accuracy == Accuracy.CORRECT:
            tag = "correct"
            mark = "+"
        else:
            tag = "wrong"
            mark = "x"
            statement = "(Unanswered)"
        text = "{0:02d}:\t{1} {2}".format(i + 1, mark, statement)

        return text, tag

    def to_home_mode(self):
        self.main_frame.destroy()
        self.return_callback()
