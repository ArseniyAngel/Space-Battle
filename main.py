# main.py
import arcade
from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from views.menu_view import MenuView


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.set_fullscreen(True)
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()