SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)

PLAYER_SPEED = 2.0
PLAYER_JUMP_POWER = -8.0
PLAYER_GRAVITY = 0.5
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
FPS = 60

ASSETS_PATH = "assets"

DREAM_TYPES = [
    "мечтательный",
    "грустный",
    "веселый",
    "страшный",
    "насыщенный",
    "фантастический"
]
DREAM_TYPE_TO_SPRITE = {
    "мечтательный": "dream_particle_0",
    "грустный": "dream_particle_1",
    "веселый": "dream_particle_2",
    "страшный": "dream_particle_3",
    "насыщенный": "dream_particle_4",
    "фантастический": "dream_particle_5"
}
COLLECT_DISTANCE = 30
FINISH_CHECK_DISTANCE = 30
ERASER_RADIUS = 30
HELP_BUTTON_RADIUS = 20
HELP_BUTTON_POS = (30, SCREEN_HEIGHT - 30)

# Цвета UI
UI_COLORS = {
    'BUTTON_BG': (100, 150, 200),
    'BUTTON_BORDER': (60, 100, 160),
    'STATUS_OK': (100, 255, 100),
    'STATUS_MISSING': (255, 100, 100),
    'STATUS_EXTRA': (255, 200, 100),
    'WIN_PANEL_BG': (240, 230, 210),
    'WIN_PANEL_BORDER': (180, 160, 140),
}
# Константы внешнего вида
PANEL_BG_COLOR = (25, 25, 35)
DIVIDER_COLOR = (60, 60, 80)

BTN_WIDTH = 150
BTN_HEIGHT = 55
BTN_GAP = 10
BTN_BORDER_RADIUS = 8

SELECTED_COLORS = {
    'bg': (60, 140, 220),
    'border': (120, 220, 255),
    'text': (255, 255, 255)
}

DEFAULT_COLORS = {
    'bg': (45, 45, 55),
    'border': (70, 70, 85),
    'text': (180, 180, 190)
}