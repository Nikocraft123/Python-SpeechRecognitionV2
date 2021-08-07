# IMPORTS
import pygame as pg
from color import *
from constants import *
import font
from main import Controller


# METHODS

# Draw the credit line
def credit_line(screen: pg.Surface, theme: str, color: RGBColor, screen_scale: tuple[int, int]) -> None:

    # Draw the frame
    pg.draw.rect(screen, color, [1, (screen_scale[1] - 23), (screen_scale[0] - 2), 22], 2)

    # Draw the text
    screen.blit(font.render_text(f"Author: {AUTHOR}", font.NOTOMONO_12, color), (8, (screen_scale[1] - 19)))
    if theme == "": screen.blit(font.render_text(f"Speech Recognition", font.NOTOMONO_12, color), ((screen_scale[0] // 2 - font.render_text(f"Speech Recognition", font.NOTOMONO_12, color).get_width() // 2), (screen_scale[1] - 19)))
    else: screen.blit(font.render_text(f"Speech Recognition - {theme}", font.NOTOMONO_12, color), ((screen_scale[0] // 2 - font.render_text(f"Speech Recognition - {theme}", font.NOTOMONO_12, color).get_width() // 2), (screen_scale[1] - 19)))
    screen.blit(font.render_text(f"Version: {VERSION}", font.NOTOMONO_12, color), ((screen_scale[0] - font.render_text(f"Version: {VERSION}", font.NOTOMONO_12, color).get_width() - 8), (screen_scale[1] - 19)))

# Get a button input
def button_input(x: int, y: int, width: int, height: int, window: Controller) -> tuple[bool, bool]:

    # Get mouse position
    mouse_x, mouse_y = window.m_pos

    # If the mouse is on the button, set mouse on to true, else false
    if mouse_x > x and mouse_x < x + width and mouse_y > y and mouse_y < y + height: mouse_on = True
    else: mouse_on = False

    # Return is hovered and is clicked
    return mouse_on, mouse_on and window.m_left_down


# Draw a color button
def draw_color_button(x: int, y: int, width: int, height: int, window: Controller, surface: pg.Surface, color: RGBColor, modifier: tuple[int, int, int], frame_color: RGBColor = BLACK):

    # Get button input
    hovered, clicked = button_input(x, y, width, height, window)

    # Draw the button
    if hovered: pg.draw.rect(surface, color.modify(modifier), (x, y, width, height))
    else: pg.draw.rect(surface, color, (x, y, width, height))
    pg.draw.rect(surface, frame_color, (x, y, width, height), 2)

    # Return button input data
    return hovered, clicked


# Draw a color button with text
def draw_color_text_button(x: int, y: int, width: int, height: int, window: Controller, surface: pg.Surface, text: str, text_font: pg.font.Font, color: RGBColor, modifier: tuple[int, int, int], text_color: RGBColor, frame_color: RGBColor = BLACK):

    # Get button input and draw the button self
    hovered, clicked = draw_color_button(x, y, width, height, window, surface, color, modifier, frame_color)

    # Create and draw the text
    text_obj = font.render_text(text, text_font, text_color)
    surface.blit(text_obj, ((x + width // 2 - text_obj.get_width() // 2, height // 2 + y - text_obj.get_height() // 2)))

    # Return button input data
    return hovered, clicked
