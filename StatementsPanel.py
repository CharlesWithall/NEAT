import math
import tkinter as tk
from Defines import get_colour_style, get_negative_colour_style, default_font_name, get_colour_gradient
from Page_OK import OKWindow
from ScoresPanel import ScoresPanel

slot_offset = 1
slot_spacing = 25
x_alignment = 40
empty_slot_size = 2

def get_slot(y_coord):
    return int(round(float(y_coord) / slot_spacing)) - slot_offset

class StatementEntry:
    def __init__(self, canvas, statement, scores):
        self.label_id = canvas.create_text(0, 0, text=statement, tags="statement", anchor="w", font=default_font_name)
        bounds = canvas.bbox(self.label_id)
        self.box_id = canvas.create_rectangle(bounds[0] - 2, bounds[1] - 2, bounds[2] + 2, bounds[3] + 2, tags="statement")
        canvas.tag_raise(self.label_id)

        self.rename_id = None
        self.rename_entry = None
        self.statement = statement
        self.scores = scores
        self.cached_abbreviated_statement = None

    def expand_statement(self, canvas):
        full_text = self.statement
        display_text = canvas.itemcget(self.label_id, 'text')
        self.cached_abbreviated_statement = display_text
        if full_text != display_text:
            new_display_text = ""
            max_text_length = len(display_text) - 3
            words = full_text.split()
            line_length = 0
            for word in words:
                line_length += (len(word) + 1)
                if line_length < max_text_length:
                    new_display_text += "{0} ".format(word)
                else:
                    new_display_text += "\n{0} ".format(word)
                    line_length = len(word)
            canvas.itemconfig(self.label_id, text=new_display_text)
            bounds = canvas.bbox(self.label_id)
            canvas.coords(self.box_id, bounds[0] - 2, bounds[1] - 2, bounds[2] + 2, bounds[3] + 2)

    def get_abbreviated_statement(self, canvas, x2):
        if self.cached_abbreviated_statement is not None:
            return self.cached_abbreviated_statement

        while canvas.bbox(self.label_id)[2] >= x2:
            existing_text = canvas.itemcget(self.label_id, 'text')
            words = existing_text.split()
            new_text = ' '.join(words[:-1]) + "..."
            return new_text
        return canvas.itemcget(self.label_id, 'text')

    def relax_statement(self, canvas, x2):
        text = self.get_abbreviated_statement(canvas, x2)
        canvas.itemconfig(self.label_id, text=text)
        bounds = canvas.bbox(self.label_id)
        canvas.coords(self.box_id, bounds[0] - 2, bounds[1] - 2, bounds[2] + 2, bounds[3] + 2)
        self.cached_abbreviated_statement = None

    def delete(self, canvas):
        canvas.delete(self.label_id)
        canvas.delete(self.box_id)

    def to_rename(self, canvas, is_valid_callback, update_statements_callback):
        if self.rename_id is None:
            coords = canvas.bbox(self.label_id)
            entry_frame = tk.Frame(canvas, width=coords[2] - coords[0], height=coords[3] - coords[1])
            entry_frame.grid_columnconfigure(0, weight=1)
            entry_frame.grid_propagate(False)
            self.rename_entry = tk.Entry(entry_frame, bg=canvas.itemcget(self.box_id, 'fill'))
            self.rename_entry.insert(0, self.statement)
            self.rename_entry.grid(sticky="we")
            self.rename_entry.focus()
            self.rename_entry.bind('<Return>', lambda event: self.from_rename(canvas, is_valid_callback, update_statements_callback))
            self.rename_entry.bind('<Escape>', lambda event: self.from_rename(canvas, is_valid_callback, update_statements_callback, None, True))
            self.rename_id = canvas.create_window(coords[0], [coords[1]], anchor="nw", window=entry_frame)

    def from_rename(self, canvas, is_valid_callback, update_statements_callback, event=None, is_cancel=False):
        if event is not None and event.widget is self.rename_entry:
            return

        if self.rename_id is not None:
            text = self.rename_entry.get() if len(self.rename_entry.get()) > 0 and not is_cancel else self.statement
            old_text = self.statement
            self.statement = ""
            if is_valid_callback(text, self.statement):
                canvas.itemconfig(self.label_id, text=text)
                self.statement = text
                bounds = canvas.bbox(self.label_id)
                canvas.coords(self.box_id, bounds[0] - 2, bounds[1] - 2, bounds[2] + 2, bounds[3] + 2)

                self.rename_entry.destroy()
                canvas.delete(self.rename_id)
                self.rename_entry = None
                self.rename_id = None
            else:
                self.statement = old_text

        update_statements_callback()

    def get_slot(self, canvas):
        return get_slot(canvas.coords(self.label_id)[1])

    def draw(self, canvas, x, y, colour):
        self.move(canvas, x, y)
        canvas.itemconfig(self.box_id, fill=colour)

    def append(self, canvas, x, y, block, old_block):
        canvas.move(self.label_id, x, y)
        canvas.move(self.box_id, x, y)
        block.statements.append(self)
        canvas.itemconfig(self.box_id, fill=block.colour)
        self.scores.append(100 if block.is_correct_block else 0)
        old_block.statements.remove(self)

    def move(self, canvas, x, y, block=None, index=None):
        canvas.move(self.label_id, x, y)
        canvas.move(self.box_id, x, y)

        if block and index is not None:
            block.statements[index] = self
            canvas.itemconfig(self.box_id, fill=block.colour)
            if block.is_correct_block:
                for i in range(len(self.scores)):
                    self.scores[i] = 100 if i == index else 0

    def score_highlight(self, canvas, colour_index, hide_text):
        colour_gradient = ""
        try:
            colour_gradient = get_colour_gradient(colour_index)
            canvas.itemconfig(self.box_id, fill=colour_gradient)
            if hide_text:
                canvas.itemconfig(self.label_id, fill=colour_gradient)
        except:
            print("Box Id: {0}, colour_index: {1}, colour gradient: {2}".format(self.box_id, colour_index, colour_gradient))

    def on_highlight(self, canvas):
        canvas.itemconfig(self.box_id, fill=get_colour_gradient(100))

    def on_unhighlight(self, canvas, block):
        canvas.itemconfig(self.box_id, fill=block.colour)
        canvas.itemconfig(self.label_id, fill=get_colour_style(100))

class StatementBlock:
    def __init__(self, canvas, header, statements, slot_y, correct_block=False):
        self.canvas = canvas
        self.statements = statements
        self.slot_y = slot_y
        self.colour = get_colour_style(1) if correct_block else get_negative_colour_style(1)
        self.is_correct_block = correct_block
        self.header_id = canvas.create_text(x_alignment, self.slot_y * slot_spacing, text=header, anchor="w", font=default_font_name)
        for i, statement in enumerate(statements):
            statement.draw(self.canvas, x_alignment, (self.slot_y + i + 1) * slot_spacing, self.colour)
        self.empty_slot = self.slot_y + len(self.statements) + 1 - slot_offset
        self.numbers = []
        self.empty_slot_box = None
        if correct_block:
            for i, statement in enumerate(self.statements):
                self.draw_number(i)

    def expose_empty_slot(self):
        if self.empty_slot_box is None:
            y = (self.empty_slot + slot_offset) * slot_spacing
            text_arg = "Correct" if self.is_correct_block else "Wrong"
            x1 = x_alignment - 3
            y1 = ((self.empty_slot + 1/2) * slot_spacing) + 2
            x2 = 350
            y2 = ((self.empty_slot + 1/2) * slot_spacing) + 2 + slot_spacing * empty_slot_size
            box = self.canvas.create_rectangle(x1, y1, x2, y2, outline="grey")
            text = self.canvas.create_text(x1 + (x2 - x1)/2, y1 + (y2 - y1)/2, text=str.format("...Move to {0} Answers...", text_arg),
                                           font=default_font_name, fill="grey")
            self.canvas.tag_lower(box)
            self.canvas.tag_lower(text)
            self.empty_slot_box = (box, text)

    def clear_empty_slot(self):
        if self.empty_slot_box is not None:
            for item in self.empty_slot_box:
                self.canvas.delete(item)
            self.empty_slot_box = None

    def draw_number(self, i):
        if self.is_correct_block:
            self.numbers.append(self.canvas.create_text(x_alignment/1.5, (self.slot_y + i + 1) * slot_spacing,
                                                        text="{0}:".format(i+1), anchor="e", font=default_font_name))

    def add_new_statement(self, statement_entry):
        self.statements.append(statement_entry)
        statement_entry.draw(self.canvas, x_alignment, (self.slot_y + len(self.statements)) * slot_spacing, self.colour)
        self.update_numbers(1)

    def delete_statement(self, statement_entry):
        self.statements.remove(statement_entry)
        statement_entry.delete(self.canvas)

    def remove_number(self):
        self.canvas.delete(self.numbers.pop(-1))

    def update_numbers(self, delta):
        self.empty_slot += delta
        if self.is_correct_block:
            if delta > 0:
                for i in range(delta):
                    self.draw_number(len(self.statements) + i - 1)
            else:
                for i in range(-delta):
                    self.remove_number()

    def show_score_colours(self, statement_entry):
        for i, statement in enumerate(self.statements):
            statement.score_highlight(self.canvas, statement_entry.scores[i], statement is not statement_entry)

    def hide_score_colours(self):
        for statement in self.statements:
            statement.on_unhighlight(self.canvas, self)

    def get_bottom(self):
        return self.slot_y + len(self.statements) + 2

    def move(self, slot_y):
        dy = slot_y - self.slot_y
        self.slot_y = slot_y

        self.canvas.move(self.header_id, 0, dy * slot_spacing)
        self.move_statements()

    def move_statements(self):
        for i, statement in enumerate(self.statements):
            delta_y = ((self.slot_y + i + 1) - (statement.get_slot(self.canvas) + slot_offset)) * slot_spacing
            statement.move(self.canvas, 0, delta_y)

    def get_statement_by_slot(self, slot):
        index = slot - self.slot_y + slot_offset - 1
        return self.statements[index] if 0 <= index < len(self.statements) else None

    def recalculate_score_count(self, correct_score_count, removal_index=None):
        for i, statement in enumerate(self.statements):
            if len(statement.scores) > correct_score_count:
                for j in range(len(statement.scores) - correct_score_count):
                    if removal_index is None:
                        statement.scores.pop(-1)
                    else:
                        statement.scores.pop(removal_index)
            elif len(statement.scores) < correct_score_count:
                for j in range(correct_score_count - len(statement.scores)):
                    statement.scores.append(0)
            for j in range(len(statement.scores)):
                if not self.is_correct_block:
                    statement.scores[j] = 0

class StatementPanel(tk.Frame):
    def __init__(self, root, callback):
        tk.Frame.__init__(self, root)

        self.statements_changed_callback = callback
        self.canvas = tk.Canvas(root, bg=get_colour_style(0))
        self.canvas.grid(row=0, column=0, sticky="NEWS")
        self.canvas.bind("<MouseWheel>", self.mouse_wheel_scroll)

        self.highlighted_statement = None
        self.right_answer_block = None
        self.wrong_answer_block = None
        self.scores_panel = None

        self._drag_data = {"x": 0, "y": 0, "item": None, "original_slot": 0, "first_drag": True}

        self.canvas.bind("<Configure>", self.update)

        self.canvas.tag_bind("statement", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("statement", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("statement", "<B1-Motion>", self.drag)
        self.canvas.tag_bind("statement", "<Button-3>", self.on_right_click)

        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.scroll_command)
        self.canvas.config(yscrollcommand=self.on_scroll, yscrollincrement=slot_spacing)
        self.scrollbar.grid(row=0, column=1, sticky="NS")
        self.scrollbar_offset = 0
        self.cached_scrollbar_size = 0

        self.right_click = tk.Menu(self.canvas, tearoff=0)
        self.right_click.add_command(label="Rename", command=self.rename_statement)
        self.right_click.add_command(label="Delete", command=self.delete_statement)
        self.right_click_data = None

        self.x_limit_of_statements = 100

    def scroll_command(self, command=None, value=1, unit_type=None):
        if command == "scroll":
            self.canvas.yview_scroll(1 if float(value) > 0 else -1, "units")
        else:
            self.canvas.yview(command, value)

    def mouse_wheel_scroll(self, event):
        y1, y2 = self.scrollbar.get()
        is_up = event.delta > 0
        if (y1 == 0 and is_up) or (y2 == 1 and not is_up):
            return

        self.scroll_command("scroll", -event.delta)

    def on_scroll(self, y1, y2):
        fy1, fy2 = float(y1), float(y2)
        self.scrollbar.set(y1, y2)
        bar_size = fy2-fy1 if fy2 < 1 else self.cached_scrollbar_size
        if bar_size > 0:
            self.cached_scrollbar_size = bar_size
            scrollbar_placement = (self.canvas.winfo_height() * fy1) / slot_spacing
            self.scrollbar_offset = math.floor(scrollbar_placement / bar_size)

    def update(self, event=None):
        self.scores_panel.update(event)
        self.set_x_limit_of_statements()
        self.size_all_boxes_to_longest_statement_or_half_canvas_width()

    def on_left_click(self, event):
        self.scores_panel.on_left_click(event)
        for entry in self.right_answer_block.statements + self.wrong_answer_block.statements:
            entry.from_rename(self.canvas, self.is_valid_statement, self.size_all_boxes_to_longest_statement_or_half_canvas_width, event)

    def on_right_click(self, event):
        try:
            x = event.x
            y = event.y + (self.scrollbar_offset * slot_spacing)
            statement = self.get_statement_by_id(self.canvas.find_closest(x, y)[0])
            self.right_click_data = statement
            self.right_click.tk_popup(event.x_root, event.y_root)
        finally:
            self.right_click.grab_release()

    def set_x_limit_of_statements(self):
        largest_x2 = 0
        for statement in self.right_answer_block.statements + self.wrong_answer_block.statements:
            self.canvas.itemconfig(statement.label_id, text=statement.statement)
            bounds = self.canvas.bbox(statement.label_id)
            largest_x2 = max(bounds[2] + 2, largest_x2)
        self.canvas.update()
        canvas_width = ((2 * self.canvas.winfo_width()) / 3) - 2
        self.x_limit_of_statements = min(largest_x2, canvas_width)

    def size_all_boxes_to_longest_statement_or_half_canvas_width(self):
        largest_x2 = self.x_limit_of_statements

        for statement in self.right_answer_block.statements + self.wrong_answer_block.statements:
            bounds = self.canvas.coords(statement.box_id)
            self.canvas.coords(statement.box_id, bounds[0], bounds[1], largest_x2, bounds[3])

        self.size_all_visible_text_to_boxes(largest_x2)

    def size_all_visible_text_to_boxes(self, x2):
        for statement in self.right_answer_block.statements + self.wrong_answer_block.statements:
            while self.canvas.bbox(statement.label_id)[2] >= x2:
                existing_text = self.canvas.itemcget(statement.label_id, 'text')
                words = existing_text.split()
                new_text = ' '.join(words[:-1]) + "..."
                self.canvas.itemconfig(statement.label_id, text=new_text)

    def is_valid_statement(self, text, exception=None):
        header = "Validation Error"
        if len(text) == 0:
            OKWindow(self.canvas, header, "Cannot add statement.\nStatement cannot be empty.")
            return False
        elif text.upper() in [entry.statement.upper() for entry in self.right_answer_block.statements + self.wrong_answer_block.statements if entry is not exception]:
            OKWindow(self.canvas, header, "Cannot add statement.\nThis statement already exists.")
            return False
        return True

    def add_statement(self, text):
        if self.is_valid_statement(text):
            statement_entry = StatementEntry(self.canvas, text, [])
            self.wrong_answer_block.add_new_statement(statement_entry)
            self.set_x_limit_of_statements()
            self.on_statements_changed()

    def delete_statement(self, statement=None):
        statement_entry = self.right_click_data if statement is None else statement
        if statement_entry in self.right_answer_block.statements:
            self.right_answer_block.delete_statement(statement_entry)
            self.redraw_blocks(-1, 0)
        else:
            self.wrong_answer_block.delete_statement(statement_entry)
            self.redraw_blocks(0, -1)
        self.wrong_answer_block.update_numbers(-1)
        self.set_x_limit_of_statements()
        self.on_statements_changed()

    def rename_statement(self, statement=None):
        statement_entry = self.right_click_data if statement is None else statement
        statement_entry.to_rename(self.canvas, self.is_valid_statement, self.from_rename)

    def from_rename(self):
        self.set_x_limit_of_statements()
        self.size_all_boxes_to_longest_statement_or_half_canvas_width()

    def load_statements(self, test_data):
        right_answers, wrong_answers = self.build_statement_entries(test_data)
        self.right_answer_block = StatementBlock(self.canvas, "Correct Answers:", right_answers, slot_offset, True)
        self.wrong_answer_block = StatementBlock(self.canvas, "Wrong Answers:", wrong_answers,
                                                 self.right_answer_block.get_bottom() + (empty_slot_size - 1), False)
        self.scores_panel = ScoresPanel(self.canvas, self.right_answer_block)
        self.on_statements_changed()

    # def build_statement_entries(self, test_data):
    #     right_answers = []
    #     wrong_answers = []
    #     if test_data is not None:
    #         statements = test_data.statements
    #         for text in list(statements.keys()):
    #             is_wrong_answer = True
    #             for score in statements[text]:
    #                 if score > 0:
    #                     is_wrong_answer = False
    #                     break
    #             statement_entry = StatementEntry(self.canvas, text, statements[text])
    #             if is_wrong_answer:
    #                 wrong_answers.append(statement_entry)
    #             else:
    #                 right_answers.append(statement_entry)
    #     return right_answers, wrong_answers

    def build_statement_entries(self, test_data):
        right_answers = []
        wrong_answers = []
        if test_data is not None:
            statements = test_data.statements
            for i, text in enumerate(list(statements.keys())):
                statement_entry = StatementEntry(self.canvas, text, statements[text])
                if i >= test_data.answer_count:
                    wrong_answers.append(statement_entry)
                else:
                    right_answers.append(statement_entry)
        return right_answers, wrong_answers

    def swap(self, original_statement, swap_statement, delta_y_original, delta_y_swap):
        original_block, original_i = self.get_block_and_index(swap_statement)
        swap_block, swap_i = self.get_block_and_index(original_statement)
        swap_statement.move(self.canvas, 0, delta_y_swap, swap_block, swap_i)
        original_statement.move(self.canvas, 0, delta_y_original, original_block, original_i)

    def get_statement_by_slot(self, slot):
        statement = self.right_answer_block.get_statement_by_slot(slot)
        return statement if statement is not None else self.wrong_answer_block.get_statement_by_slot(slot)

    def get_statement_by_id(self, statement_id):
        for statement in self.right_answer_block.statements + self.wrong_answer_block.statements:
            if statement.label_id == statement_id or statement.box_id == statement_id:
                return statement
        return None

    def redraw_blocks(self, right_delta, wrong_delta):
        self.size_all_boxes_to_longest_statement_or_half_canvas_width()
        self.right_answer_block.update_numbers(right_delta)
        self.right_answer_block.move_statements()
        self.wrong_answer_block.move(self.right_answer_block.get_bottom() + (empty_slot_size - 1))

    def on_statements_changed(self, removal_index=None):
        self.right_answer_block.recalculate_score_count(len(self.right_answer_block.statements), removal_index)
        self.wrong_answer_block.recalculate_score_count(len(self.right_answer_block.statements))
        self.size_all_boxes_to_longest_statement_or_half_canvas_width()
        self.statements_changed_callback()
        self.canvas.configure(scrollregion=(0, 0, 100, (self.wrong_answer_block.get_bottom() + slot_offset + 1) * slot_spacing))

    def set_highlight(self, statement_entry):
        def unhighlight(root, statement, block):
            if statement is not None:
                statement.on_unhighlight(root.canvas, block)
                root.scores_panel.clear()
                root.highlighted_statement = None

        if statement_entry in self.right_answer_block.statements:
            if self.highlighted_statement is statement_entry:
                unhighlight(self, statement_entry, self.right_answer_block)
            else:
                unhighlight(self, self.highlighted_statement, self.right_answer_block)
                self.highlighted_statement = statement_entry
                statement_entry.on_highlight(self.canvas)
                self.scores_panel.draw(statement_entry, self.canvas.winfo_width() - 10, slot_offset + 1, slot_spacing)
        elif self.highlighted_statement is not None:
            unhighlight(self, self.highlighted_statement, self.wrong_answer_block)

    def is_deletion_request(self, x, y):
        if self.scores_panel.delete_box_id is None:
            return False

        coords = self.canvas.coords(self.scores_panel.delete_box_id)
        if len(coords) != 4:
            return False

        if coords[0] < x < coords[2] and coords[1] < y < coords[3]:
            return True

        return False

    def drag_start(self, event):
        x = event.x
        y = event.y + (self.scrollbar_offset * slot_spacing)
        self._drag_data["original_slot"] = get_slot(y)
        statement = self.get_statement_by_slot(self._drag_data["original_slot"])
        if statement is None:
            self._drag_data["original_slot"] = 0
            return
        self._drag_data["item"] = statement
        self._drag_data["x"] = x
        self._drag_data["y"] = y
        self._drag_data["first_drag"] = True
        self.canvas.tag_raise(statement.box_id)
        self.canvas.tag_raise(statement.label_id)

    def drag_stop(self, event):
        if self._drag_data["item"] is None:
            return

        x = event.x
        y = event.y + (self.scrollbar_offset * slot_spacing)
        statement_item = self._drag_data["item"]
        statement_item.relax_statement(self.canvas, self.x_limit_of_statements)
        coords = self.canvas.coords(statement_item.label_id)
        proposed_slot = get_slot(y)
        delta_x = x_alignment - coords[0]
        removal_index = None

        self.wrong_answer_block.clear_empty_slot()
        self.right_answer_block.clear_empty_slot()

        if self.is_deletion_request(x, y):
            self.delete_statement(statement_item)
            self.scores_panel.from_delete_panel()
            return
        self.scores_panel.from_delete_panel()
        if self.is_empty_slot(proposed_slot):
            delta_y = ((proposed_slot + slot_offset) * slot_spacing) - coords[1]
            empty_slot_remove_success, removal_index = self.move_to_empty_slot(proposed_slot, statement_item, delta_x, delta_y)
            if not empty_slot_remove_success:
                delta_y = ((self._drag_data["original_slot"] + slot_offset) * slot_spacing) - coords[1]
                statement_item.move(self.canvas, delta_x, delta_y)
        elif not self.is_valid_slot(proposed_slot):
            delta_y = ((self._drag_data["original_slot"] + slot_offset) * slot_spacing) - coords[1]
            statement_item.move(self.canvas, delta_x, delta_y)
        else:
            to_statement = self.get_statement_by_slot(proposed_slot)
            if to_statement is statement_item:
                self.set_highlight(to_statement)
                delta_y = ((self._drag_data["original_slot"] + slot_offset) * slot_spacing) - coords[1]
                statement_item.move(self.canvas, delta_x, delta_y)
            else:
                delta_y_swap = (self._drag_data["original_slot"] - proposed_slot) * slot_spacing
                delta_y_original = ((proposed_slot + slot_offset) * slot_spacing) - coords[1]
                self.swap(statement_item, to_statement, delta_y_original, delta_y_swap)
                statement_item.move(self.canvas, delta_x, 0)

        self.on_statements_changed(removal_index)

        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self._drag_data["original_slot"] = 0

    def drag(self, event):
        if self._drag_data["item"] is None:
            return

        if self._drag_data["first_drag"]:
            self._drag_data["item"].expand_statement(self.canvas)
            self.scores_panel.clear()
            self.scores_panel.to_delete_panel(self.scrollbar_offset * slot_spacing)
            if self._drag_data["item"] in self.right_answer_block.statements:
                self.wrong_answer_block.expose_empty_slot()
            else:
                self.right_answer_block.expose_empty_slot()
            self._drag_data["first_drag"] = False
            self.highlighted_statement = None

        x = event.x
        y = event.y + (self.scrollbar_offset * slot_spacing)

        delta_x = x - self._drag_data["x"]
        delta_y = y - self._drag_data["y"]

        self._drag_data["item"].move(self.canvas, delta_x, delta_y)

        self._drag_data["x"] = x
        self._drag_data["y"] = y

    def is_valid_slot(self, proposed_slot):
        return self.get_statement_by_slot(proposed_slot) is not None

    def is_occupied_slot(self, proposed_slot):
        return self.is_valid_slot(proposed_slot)

    def is_empty_slot(self, proposed_slot):
        for i in range(empty_slot_size):
            if proposed_slot == self.right_answer_block.empty_slot + i or proposed_slot == self.wrong_answer_block.empty_slot + i:
                return True
        return False

    def move_to_empty_slot(self, empty_slot, statement, delta_x, delta_y):
        is_right_answer_slot = empty_slot in [self.right_answer_block.empty_slot + i for i in range(empty_slot_size)]
        is_right_statement = statement in self.right_answer_block.statements
        correct_remove_index = None if not is_right_statement else self.right_answer_block.statements.index(statement)
        if is_right_statement != is_right_answer_slot:
            new_block = self.wrong_answer_block if is_right_statement else self.right_answer_block
            old_block = self.right_answer_block if is_right_statement else self.wrong_answer_block
            statement.append(self.canvas, delta_x, delta_y, new_block, old_block)
            self.redraw_blocks(1 if is_right_answer_slot else -1, -1 if is_right_answer_slot else 1)
            return True, correct_remove_index

        return False, None

    def get_block_and_index(self, statement):
        for i, statement_entry in enumerate(self.right_answer_block.statements):
            if statement_entry == statement:
                return self.right_answer_block, i

        for i, statement_entry in enumerate(self.wrong_answer_block.statements):
            if statement_entry == statement:
                return self.wrong_answer_block, i