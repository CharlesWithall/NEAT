from enum import Enum

class PositionAccuracy(Enum):
    INVALID = 0
    INCORRECT = 1
    PARTIALLY_CORRECT = 2
    CORRECT = 3

class OptionButtonsRow(Enum):
    NEW = 0
    EDIT = 1
    DELETE = 2
    OPEN = 3
    ABOUT = 4
    COUNT = 5

class ConfigurationPageRow(Enum):
    TEST_NAME = 0
    TEST_DESCRIPTION = 1
    EXISTING_STATEMENTS = 2
    NEW_STATEMENT = 3
    DIVIDER = 4
    OUTPUT = 5
    GENERATE = 6
    COUNT = 7

class StatementColumn(Enum):
    STATEMENT = 0
    SCORES = 1
    DELETE = 2
    COUNT = 3

class TestPageRow(Enum):
    TITLE = 0
    DESCRIPTION = 1
    TESTCANVAS = 2
    OPTIONS = 3
    COUNT = 4

default_font_name = "BahnSchrift"
font_style_title = (default_font_name, 24)
font_style_subtitle = (default_font_name, 12)
font_style_home_button = (default_font_name, 10)

app_name = "Normalised Essay Assessment Tool"
app_abbreviation = "NEAT"
app_version = "0.5"
default_size_x = 1100
default_size_y = 550

score_lower_limit = 0
score_upper_limit = 100

score_lower_limit_colour = (0xc1, 0x38, 0x38)
score_upper_limit_colour = (0x38, 0xc1, 0x38)

text_colour = "#FFFFFF"
def get_colour_style(value):
    if value <= 0:
        return "#FFFFFF"
    if value == 1:
        return "#D6FFEA"
    if value == 2:
        return "#68C89E"
    if value == 3:
        return "#54BE90"
    if value == 4:
        return "#18A866"
    if value == 5:
        return "#2A3832"
    return "#000000"

def get_negative_colour_style(value):
    if value <= 0:
        return "#FFFFFF"
    if value == 1:
        return "#e3a7a7"
    return "#000000"

vibrant_colour = "#00ff00"

def get_colour_gradient(value):
    if score_lower_limit <= value <= score_upper_limit:
        out_hex = []
        for i in range(3):
            diff = score_upper_limit_colour[i] - score_lower_limit_colour[i]
            add_value = diff * (value / (score_upper_limit - score_lower_limit))
            result = score_lower_limit_colour[i] + add_value
            out_hex.append(int(result))

        return '#%02x%02x%02x' % tuple(out_hex)
    return "#FFFFFF"

import sys
import os

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# PYINSTALLER ARGS
# --paths=venv\Lib\site-packages
# --onefile
# NEAT.py
# --add-data="default_save_data.json;."
# --add-data="NEAT.ico;."
# --icon="NEAT.ico"
# --noconsole
