# CLASSES

# RGB Color Class
class RGBColor(tuple):

    # CONSTRUCTOR
    def __new__(cls, red: int, green: int, blue: int):
        return tuple.__new__(cls, (red, green, blue))


    # METHODS

    # Modify a color
    def modify(self, modifier):

        result = [self[i] + modifier[i] for i in range(0, 3)]

        for index, value in enumerate(result):
            if value > 255:
                result[index] = 255
            if value < 0:
                result[index] = 0

        return RGBColor(*result)

    # Mix two colors
    def mix(self, other):

        return RGBColor(*((self[i] + other[i]) // 2 for i in range(0, 3)))


# VARIABLES

# Colors
DARK_BLACK = RGBColor(0, 0, 0)
BLACK = RGBColor(20, 20, 20)
DARK_GRAY = RGBColor(60, 60, 60)
GRAY = RGBColor(110, 110, 110)
LIGHT_GRAY = RGBColor(190, 190, 190)
WHITE = RGBColor(230, 230, 230)
LIGHT_WHITE = RGBColor(255, 255, 255)

LIGHT_YELLOW = RGBColor(252, 255, 163)
YELLOW = RGBColor(255, 255, 25)
DARK_YELLOW = RGBColor(224, 217, 0)
ORANGE = RGBColor(255, 187, 51)
DARK_ORANGE = RGBColor(230, 153, 0)
LIGHT_RED = RGBColor(255, 136, 77)
RED = RGBColor(255, 0, 0)
DARK_RED = RGBColor(204, 0, 0)
PINK = RGBColor(255, 102, 255)
LIGHT_PURPLE = RGBColor(196, 77, 255)
PURPLE = RGBColor(115, 0, 230)
DARK_PURPLE = RGBColor(64, 0, 128)
BROWN = RGBColor(117, 0, 0)
DARK_BROWN = RGBColor(74, 0, 0)

LIGHT_AQUA = RGBColor(153, 255, 255)
AQUA = RGBColor(0, 255, 255)
DARK_AQUA = RGBColor(0, 179, 179)
LIGHT_BLUE = RGBColor(128, 170, 255)
BLUE = RGBColor(0, 42, 255)
DARK_BLUE = RGBColor(0, 0, 179)

LIGHT_LIME = RGBColor(179, 255, 179)
LIME = RGBColor(128, 255, 149)
DARK_LIME = RGBColor(0, 255, 0)
GREEN = RGBColor(0, 204, 0)
DARK_GREEN = RGBColor(0, 128, 0)
