from tkinter import *
from Defines import PositionAccuracy as Accuracy
from Defines import TestPageRow, get_colour_style, default_font_name
from Page_Prompt import PromptWindow
import math
import random

slot_offset = 2
slot_spacing = 25
starting_x_alignment = 20

class AnswerBookStatement:
    def __init__(self, canvas, x, y, statement, scores, slot):
        label_id = canvas.create_text(x, y, text=statement, tags="statement", anchor="w", font=default_font_name)
        bounds = canvas.bbox(label_id)
        box_id = canvas.create_rectangle(bounds[0] - 2, bounds[1] - 2, bounds[2] + 2, bounds[3] + 2, fill=get_colour_style(1), tags="statement")
        canvas.tag_raise(label_id)

        self.label_id = label_id
        self.box_id = box_id
        self.statement = statement
        self.scores = scores
        self.slot = slot
        self.is_answer = False
        self.original_slot = slot
        self.cached_abbreviated_statement = None

    def move(self, canvas, x, y):
        canvas.move(self.label_id, x, y)
        canvas.move(self.box_id, x, y)

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

class AnswerBook(Frame):
    def __init__(self, root, statements, answer_count):
        Frame.__init__(self, root)

        self.answer_count = answer_count
        self.statements = []
        self.answer_numbers = []
        self.starting_slots = []
        self.answer_slots = []
        self.answer_x_alignment = 0
        self.answer_header_id = 0

        self.canvas = Canvas(root, width=400, height=400, bg=get_colour_style(0))
        self.canvas.grid(row=TestPageRow.TESTCANVAS.value, column=0, sticky="NSEW")
        self.canvas.bind("<Configure>", self.resize)
        self.canvas.bind("<MouseWheel>", self.mouse_wheel_scroll)

        self._drag_data = {"x": 0, "y": 0, "item": None}

        self.add_statements(statements)
        self.canvas.update()
        self.bg_rect = self.canvas.create_rectangle(0, 0, 1, 1, fill="white smoke")
        self.add_headers()
        self.add_starting_slots()
        self.add_answer_slots()

        self.scrollbar = Scrollbar(root, orient="vertical", command=self.scroll_command)
        self.canvas.config(yscrollcommand=self.on_scroll, yscrollincrement=slot_spacing)
        self.scrollbar.grid(row=TestPageRow.TESTCANVAS.value, column=1, sticky="NS")
        self.cached_scrollbar_size = 0
        self.scrollbar_offset = 0
        self.canvas.configure(scrollregion=(0, 0, 100, (slot_offset + len(self.statements)) * slot_spacing))

        self.canvas.tag_bind("statement", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("statement", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("statement", "<B1-Motion>", self.drag)
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

    # OLD on_scroll - didn't work when dragging scrollbar really quickly
    # def on_scroll(self, y1, y2):
    #     self.scrollbar.set(y1, y2)
    #     yvalue = float(y1)
    #     if yvalue != self.previous_scrollbar_value:
    #         self.scrollbar_offset += 1 if yvalue > self.previous_scrollbar_value else -1
    #         self.previous_scrollbar_value = yvalue

    def set_x_limit_of_statements(self):
        largest_x2 = 0
        for entry in self.statements:
            self.canvas.itemconfig(entry.label_id, text=entry.statement)
            bounds = self.canvas.bbox(entry.label_id)
            largest_x2 = max(bounds[2] - bounds[0] + 5, largest_x2)
        self.canvas.update()
        canvas_width = (self.canvas.winfo_width() / 2) - 20 - starting_x_alignment
        self.x_limit_of_statements = min(largest_x2, canvas_width)

    def size_all_boxes_to_longest_statement_or_half_canvas_width(self):
        largest_x2 = self.x_limit_of_statements

        for entry in self.statements:
            bounds = self.canvas.coords(entry.box_id)
            self.canvas.coords(entry.box_id, bounds[0], bounds[1], bounds[0] + largest_x2, bounds[3])

        self.size_all_visible_text_to_boxes(largest_x2)

    def size_all_visible_text_to_boxes(self, x2):
        for entry in self.statements:
            while self.canvas.bbox(entry.label_id)[2] - self.canvas.bbox(entry.label_id)[0] >= x2:
                existing_text = self.canvas.itemcget(entry.label_id, 'text')
                words = existing_text.split()
                new_text = ' '.join(words[:-1]) + "..."
                self.canvas.itemconfig(entry.label_id, text=new_text)

    def resize(self, event):
        self.set_x_limit_of_statements()
        self.size_all_boxes_to_longest_statement_or_half_canvas_width()
        delta_x = event.width / 2 - self.answer_x_alignment
        self.answer_x_alignment = event.width / 2

        for number in self.answer_numbers:
            self.canvas.move(number, delta_x, 0)

        for statement in self.statements:
            if statement.is_answer:
                statement.move(self.canvas, delta_x, 0)

        self.canvas.move(self.answer_header_id, delta_x, 0)
        self.canvas.coords(self.bg_rect, (event.width / 2) - starting_x_alignment, -1, event.width, ((slot_offset + len(self.statements)) * slot_spacing) + event.height)

    def add_starting_slots(self):
        for i in range(len(self.statements)):
            x_pos = starting_x_alignment / 2
            y_pos = (slot_offset + i) * slot_spacing
            self.canvas.create_text(x_pos, y_pos, text="-", font=default_font_name)

    def add_headers(self):
        self.canvas.create_text(starting_x_alignment, (slot_offset-1) * slot_spacing, text="Statements:", anchor="w", font=default_font_name)
        self.answer_header_id = self.canvas.create_text(self.answer_x_alignment, (slot_offset-1) * slot_spacing, text="Answers:", anchor="w", font=default_font_name)

    def add_statements(self, statements):
        for i, text in enumerate(random.sample(list(statements.keys()), len(statements))):
            x = starting_x_alignment
            y = (slot_offset + i) * slot_spacing
            answer_book_statement = AnswerBookStatement(self.canvas, x, y, text, statements[text], i)
            self.answer_x_alignment = max(self.answer_x_alignment, self.canvas.bbox(answer_book_statement.label_id)[2])
            self.statements.append(answer_book_statement)
            self.starting_slots.append(i)
        self.answer_x_alignment += starting_x_alignment

    def add_answer_slots(self):
        for i in range(self.answer_count):
            x_pos = self.answer_x_alignment
            y_pos = (slot_offset + i) * slot_spacing
            number_id = self.canvas.create_text(x_pos, y_pos, text="{0}:".format(str(i + 1)), font=default_font_name)
            self.answer_numbers.append(number_id)
            self.answer_slots.append(i)

    def get_statement_by_id(self, statement_id):
        for statement in self.statements:
            if statement.label_id == statement_id or statement.box_id == statement_id:
                return statement
        return None

    def drag_start(self, event):
        x = event.x
        y = event.y + (self.scrollbar_offset * slot_spacing)
        statement = self.get_statement_by_id(self.canvas.find_closest(x, y)[0])
        if statement is not None:
            self._drag_data["item"] = statement
            self._drag_data["x"] = x
            self._drag_data["y"] = y
            self.canvas.tag_raise(statement.box_id)
            self.canvas.tag_raise(statement.label_id)
            statement.expand_statement(self.canvas)

    def drag_stop(self, event):
        statement_item = self._drag_data["item"]
        if statement_item is None:
            return

        x = event.x
        y = event.y + (self.scrollbar_offset * slot_spacing)
        statement_item.relax_statement(self.canvas, self.x_limit_of_statements)
        coords = self.canvas.coords(statement_item.label_id)
        proposed_slot = self.get_slot(y)
        is_answer_slot = x >= self.answer_x_alignment
        if self.is_available_slot(proposed_slot, is_answer_slot):
            for statement in self.statements:
                if statement.slot == statement_item.slot:
                    statement_item.slot = proposed_slot
            delta_x = self.answer_x_alignment + starting_x_alignment - coords[0] if is_answer_slot else starting_x_alignment - coords[0]
            delta_y = ((proposed_slot + slot_offset) * slot_spacing) - coords[1]
            statement_item.is_answer = is_answer_slot
        else:
            delta_x = self.answer_x_alignment + starting_x_alignment - coords[0] if statement_item.is_answer else starting_x_alignment - coords[0]
            delta_y = ((statement_item.slot + slot_offset) * slot_spacing) - coords[1]
        statement_item.move(self.canvas, delta_x, delta_y)

        self.size_all_boxes_to_longest_statement_or_half_canvas_width()
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def drag(self, event):
        statement = self._drag_data["item"]
        if statement is None:
            return
        x = event.x
        y = event.y + (self.scrollbar_offset * slot_spacing)
        delta_x = x - self._drag_data["x"]
        delta_y = y - self._drag_data["y"]

        statement.move(self.canvas, delta_x, delta_y)

        self._drag_data["x"] = x
        self._drag_data["y"] = y

    def is_available_slot(self, proposed_slot, is_answer):
        for statement in self.statements:
            if statement.slot == proposed_slot and statement.is_answer == is_answer:
                return False

        if not is_answer and proposed_slot not in self.starting_slots:
            return False

        if is_answer and proposed_slot not in self.answer_slots:
            return False

        return True

    def calculate_result(self):
        final_score = 0
        statements = [None for i in range(len(self.answer_numbers))]
        accuracies = [Accuracy.INVALID for i in range(len(self.answer_numbers))]
        for statement in self.statements:
            if statement.is_answer:
                score = statement.scores[statement.slot]
                statements[statement.slot] = statement.statement
                accuracies[statement.slot] = self.get_accuracy(score)
                final_score += score

        final_score /= self.answer_count
        return int(final_score), statements, accuracies

    def get_all_slots_filled(self):
        for i in range(self.answer_count):
            success = False
            for statement in self.statements:
                if statement.slot == i and statement.is_answer:
                    success = True
                    break
            if not success:
                return False

        return True

    def reset_prompt(self):
        prompt_text = "All answers will be reset.\n Are you sure you wish to proceed?"
        PromptWindow(self, prompt_text, self.reset)

    def reset(self):
        for statement in self.statements:
            delta_x = -self.answer_x_alignment if statement.is_answer else 0
            delta_y = (statement.original_slot - statement.slot) * slot_spacing
            statement.slot = statement.original_slot
            statement.move(self.canvas, delta_x, delta_y)
            statement.is_answer = False

    @staticmethod
    def get_slot(y_coord):
        return int(slot_spacing * round(float(y_coord) / slot_spacing) / slot_spacing) - slot_offset

    @staticmethod
    def get_accuracy(score):
        if score == 0:
            return Accuracy.INCORRECT
        if score == 100:
            return Accuracy.CORRECT
        return Accuracy.PARTIALLY_CORRECT

