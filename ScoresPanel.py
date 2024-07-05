import math
import tkinter as tk
from Defines import get_colour_style, default_font_name

score_label_tag = "score_label"
score_entry_tag = "score_entry"
lock_tag = "lock"
score_tag = "score"
tag_divider = ':'

curve_slider_resolution = 0.01
steepness_slider_resolution = 0.02

def get_index_for_tag(tag, tag_name):
    divided_tag = tag.split(tag_divider)
    return -1 if len(divided_tag) != 2 or divided_tag[0] != tag_name else int(divided_tag[1])

class ScoreSlider:
    def __init__(self, frame, scale, label, canvas_id, score_var, lock):
        self.frame = frame
        self.scale = scale
        self.label = label
        self.entry = tk.Entry(self.frame, width=4, name=score_entry_tag)
        self.entry.bind("<Return>", self.from_edit)
        self.canvas_id = canvas_id
        self.score_var = score_var
        self.lock = lock
        self.is_in_edit_mode = False

    def is_valid_score(self):
        try:
            return 0 <= int(self.entry.get()) <= 100
        except ValueError:
            return False

    def to_edit(self):
        if not self.is_in_edit_mode and self.lock.get() == 0:
            self.entry.grid(column=0, row=0, sticky="NEWS")
            self.entry.insert(0, self.label['text'][0:-1])
            self.entry.focus()
            self.label.grid_forget()
            self.is_in_edit_mode = True

    def from_edit(self, event=None):
        if self.is_in_edit_mode:
            self.label.grid(column=0, row=0)
            score = self.entry.get()
            if self.is_valid_score():
                self.label["text"] = "{0}%".format(score)
                self.scale.set(score)
            self.entry.delete(0, tk.END)
            self.entry.grid_forget()
            self.is_in_edit_mode = False

class ScoresPanel:
    def __init__(self, canvas, right_answer_block):
        self.canvas = canvas
        self.answer_block = right_answer_block
        self.active_sliders = []
        self.active_statement = None

        self.lock_label = None
        self.lock_label_id = 0

        self.curve_slider_frame = None
        self.curve_slider_id = 0
        self.curve_slider = None
        self.curve_variable = tk.DoubleVar()
        self.curve_variable.trace_add('write', self.on_curve_change)

        self.steepness_slider_frame = None
        self.steepness_slider_id = 0
        self.steepness_slider = None
        self.steepness_variable = tk.DoubleVar()
        self.steepness_variable.trace_add('write', self.on_curve_change)

        self.delete_box_id = None
        self.delete_text_id = None

        self.focused_slider = None

        self.canvas.bind_all("<Left>", lambda event: self.fine_adjust_latest_slider(-1))
        self.canvas.bind_all("<Right>", lambda event: self.fine_adjust_latest_slider(+1))

    def fine_adjust_latest_slider(self, value):
        if self.focused_slider is not None:
            if self.focused_slider is self.curve_slider:
                value *= curve_slider_resolution
            elif self.focused_slider is self.steepness_slider:
                value *= steepness_slider_resolution
            self.focused_slider.set(self.focused_slider.get() + value)

    def on_left_click(self, event=None):
        if event is None:
            return

        w = event.widget
        name = w.winfo_name()

        if name != score_entry_tag:
            for score_slider in self.active_sliders:
                score_slider.from_edit()
        if name == score_label_tag:
            for score_slider in self.active_sliders:
                if score_slider.label is w:
                    score_slider.to_edit()
                    break

        should_focus_slider = False
        if w is self.curve_slider:
            self.focused_slider = self.curve_slider
            should_focus_slider = True
        elif w is self.steepness_slider:
            self.focused_slider = self.steepness_slider
            should_focus_slider = True
        else:
            for score_slider in self.active_sliders:
                if w is score_slider.label or w is score_slider.scale or w is score_slider.lock or w is score_slider.entry:
                    self.focused_slider = score_slider.scale
                    should_focus_slider = True
                    break

        if not should_focus_slider:
            self.focused_slider = None

    def draw(self, statement_entry, x, y, slot_spacing):
        self.curve_slider_frame = tk.Frame(self.canvas)
        self.steepness_slider_frame = tk.Frame(self.canvas)
        self.active_statement = statement_entry
        self.answer_block.show_score_colours(statement_entry)
        self.lock_label = tk.Label(self.canvas, text="Lock", bg=get_colour_style(0), font=(default_font_name, 10))
        self.lock_label_id = self.canvas.create_window(x, (y-1) * slot_spacing, anchor="e", window=self.lock_label)
        statement_index = self.answer_block.statements.index(self.active_statement)

        for i, score in enumerate(statement_entry.scores):
            var = tk.IntVar(name=score_tag+tag_divider+str(i))
            var.set(score)
            var.trace_add('write', self.on_score_change)
            scale_frame = tk.Frame(self.canvas)
            score_label = tk.Label(scale_frame, text="{0}%".format(score), bg=get_colour_style(0), font=default_font_name, name=score_label_tag)
            score_slider = tk.Scale(scale_frame, variable=var, orient=tk.HORIZONTAL, showvalue=0)
            lock_var = tk.IntVar(name=lock_tag+tag_divider+str(i))
            lock_var.trace_add('write', self.on_lock_change)
            lock_box = tk.Checkbutton(scale_frame, variable=lock_var)
            score_label.grid(row=0, column=0)
            score_slider.grid(row=0, column=1)
            lock_box.grid(row=0, column=2)
            frame_id = self.canvas.create_window(x, (y + i) * slot_spacing, anchor="e", window=scale_frame)
            self.active_sliders.append(ScoreSlider(scale_frame, score_slider, score_label, frame_id, var, lock_var))

            if i == statement_index:
                lock_var.set(1)

        curve_label = tk.Label(self.curve_slider_frame, text="Curve: ", bg=get_colour_style(0), font=default_font_name)
        self.curve_slider = tk.Scale(self.curve_slider_frame, variable=self.curve_variable, orient=tk.HORIZONTAL,
                                     showvalue=0, from_=0, to=1, resolution=curve_slider_resolution)
        curve_label.grid(column=0, row=0, sticky="NEWS")
        self.curve_slider.grid(column=1, row=0, sticky="NEWS")
        self.curve_slider_id = self.canvas.create_window(x, (y + len(self.active_sliders) + 1) * slot_spacing, anchor="e", window=self.curve_slider_frame)

        steepness_label = tk.Label(self.steepness_slider_frame, text="Steepness: ", bg=get_colour_style(0), font=default_font_name)
        self.steepness_slider = tk.Scale(self.steepness_slider_frame, variable=self.steepness_variable,orient=tk.HORIZONTAL,
                                         showvalue=0, from_=1, to=3, resolution=steepness_slider_resolution)
        steepness_label.grid(column=0, row=0, sticky="NEWS")
        self.steepness_slider.grid(column=1, row=0, sticky="NEWS")
        self.steepness_slider_id = self.canvas.create_window(x, (y + len(self.active_sliders) + 2) * slot_spacing,
                                                         anchor="e", window=self.steepness_slider_frame)

    def to_delete_panel(self, height_offset):
        x1 = (2 * self.canvas.winfo_width()) / 3
        x2 = self.canvas.winfo_width()
        y1 = height_offset - 1
        y2 = height_offset + self.canvas.winfo_height()
        self.delete_box_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white smoke")
        self.delete_text_id = self.canvas.create_text((x1+x2)/2, (y1+y2)/2, text="Drag Here To\nDelete Statement", anchor="c", font=default_font_name)
        self.canvas.tag_lower(self.delete_text_id)
        self.canvas.tag_lower(self.delete_box_id)

    def from_delete_panel(self):
        if self.delete_box_id is not None:
            self.canvas.delete(self.delete_box_id)
        if self.delete_text_id is not None:
            self.canvas.delete(self.delete_text_id)
        self.delete_box_id = None
        self.delete_text_id = None

    def on_lock_change(self, var, unused_index=None, unused_mode=None):
        index = get_index_for_tag(var, lock_tag)
        if 0 <= index < len(self.active_sliders):
            lock_state = tk.ACTIVE if self.active_sliders[index].lock.get() == 0 else tk.DISABLED
            self.active_sliders[index].scale.configure(state=lock_state)

    def on_curve_change(self, unused_var=None, unused_index=None, unused_mode=None):
        def steepness_formula(curve_value, steepness_value):
            return math.sin(steepness_value * (curve_value - ((math.pi / 2) - (math.pi / (2 * steepness_value)))))

        value = self.curve_variable.get()
        statement_index = self.answer_block.statements.index(self.active_statement)
        size = max(len(self.active_sliders) + 1 - statement_index, statement_index)
        steepness = self.steepness_variable.get()

        for i, active_slider in enumerate(self.active_sliders):
            if active_slider.lock.get() == 0:
                delta = math.fabs(statement_index - i)
                modifier = 1 if delta == 0 else min(1.0, (value * size) / delta)
                final = max(0.0, steepness_formula(modifier * math.pi * 0.5, steepness))
                active_slider.score_var.set(final*100)

    def update(self, event=None):
        canvas_width = self.canvas.winfo_width()
        for slider in self.active_sliders:
            coords = self.canvas.coords(slider.canvas_id)
            self.canvas.move(slider.canvas_id, int(canvas_width - coords[0]), 0)
        if self.curve_slider_frame is not None:
            coords = self.canvas.coords(self.curve_slider_id)
            self.canvas.move(self.curve_slider_id, int(canvas_width - coords[0]), 0)
        if self.steepness_slider_frame is not None:
            coords = self.canvas.coords(self.steepness_slider_id)
            self.canvas.move(self.steepness_slider_id, int(canvas_width - coords[0]), 0)
        coords = self.canvas.coords(self.lock_label_id)
        if self.lock_label is not None:
            self.canvas.move(self.lock_label_id, int(canvas_width - coords[0]), 0)

    def clear(self):
        self.active_statement = None
        for slider in self.active_sliders:
            slider.frame.destroy()
        if self.curve_slider_frame:
            self.curve_slider_frame.destroy()
        if self.steepness_slider_frame:
            self.steepness_slider_frame.destroy()
        self.active_sliders = []
        self.answer_block.hide_score_colours()
        if self.lock_label:
            self.lock_label.destroy()

    def on_score_change(self, var, unused_index, unused_mode):
        index = get_index_for_tag(var, score_tag)
        if 0 <= index < len(self.active_sliders):
            score = self.active_sliders[index].score_var.get()
            self.active_statement.scores[index] = score
            self.answer_block.show_score_colours(self.active_statement)
            try:
                self.active_sliders[index].label['text'] = "{0}%".format(score)
            except:
                print("Issue with i: {0} - setting score: {1} - {2}".format(index, score. self.active_sliders[index]))
