# IMPORTS
import pygame as pg
import os
pg.font.init()
from color import *
font_path = os.path.dirname(__file__) + "/fonts/"
if not os.path.exists(font_path): raise FileExistsError(f"Cannot found fonts at '{font_path}'!")


# METHODS

# Render a text
def render_text(text: str, font: pg.font.Font, color: RGBColor, interpolation: bool = True) -> pg.Surface:
    return font.render(text, interpolation, color)

# Load a font from file
def load_file_font(file_path: str, font_size: int) -> pg.font.Font:
    return pg.font.Font(file_path, font_size)

# Load a font from system
def load_system_font(name: str, font_size: int, bold: bool = False, italic: bool = False) -> pg.font.Font:
    return pg.font.SysFont(name, font_size, bold, italic)


# VARIABLES

# Fonts
HARNGTON_30 = load_file_font(font_path + "HARNGTON.TTF", 30)
HARNGTON_40 = load_file_font(font_path + "HARNGTON.TTF", 40)
HARNGTON_50 = load_file_font(font_path + "HARNGTON.TTF", 50)
HARNGTON_60 = load_file_font(font_path + "HARNGTON.TTF", 60)
HARNGTON_70 = load_file_font(font_path + "HARNGTON.TTF", 70)

HP_SIMPLIFIED_18 = load_file_font(font_path + "hpsimplifiedjpan-regular.ttf", 18)
HP_SIMPLIFIED_20 = load_file_font(font_path + "hpsimplifiedjpan-regular.ttf", 20)
HP_SIMPLIFIED_22 = load_file_font(font_path + "hpsimplifiedjpan-regular.ttf", 22)
HP_SIMPLIFIED_25 = load_file_font(font_path + "hpsimplifiedjpan-regular.ttf", 25)
HP_SIMPLIFIED_30 = load_file_font(font_path + "hpsimplifiedjpan-regular.ttf", 30)
HP_SIMPLIFIED_35 = load_file_font(font_path + "hpsimplifiedjpan-regular.ttf", 35)

NOTOMONO_12 = load_file_font(font_path + "NotoMono-Regular.ttf", 12)
NOTOMONO_14 = load_file_font(font_path + "NotoMono-Regular.ttf", 14)
NOTOMONO_16 = load_file_font(font_path + "NotoMono-Regular.ttf", 16)
NOTOMONO_20 = load_file_font(font_path + "NotoMono-Regular.ttf", 20)
NOTOMONO_24 = load_file_font(font_path + "NotoMono-Regular.ttf", 24)

MAIAN_16 = load_file_font(font_path + "MAIAN.ttf", 16)
MAIAN_18 = load_file_font(font_path + "MAIAN.ttf", 18)
MAIAN_20 = load_file_font(font_path + "MAIAN.ttf", 20)
MAIAN_22 = load_file_font(font_path + "MAIAN.ttf", 22)
MAIAN_25 = load_file_font(font_path + "MAIAN.ttf", 25)
MAIAN_30 = load_file_font(font_path + "MAIAN.ttf", 30)
