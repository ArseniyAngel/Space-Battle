# views/pause_view.py
import arcade
from config import *


class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.SCREEN_WIDTH = self.window.width
        self.SCREEN_HEIGHT = self.window.height
        self.game_view.paused = True

        self.options = [("Resume Game", "resume"), ("Main Menu", "menu")]
        self.selected = 0

        self.title = arcade.Text("PAUSED", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 80,
                                 arcade.color.YELLOW, 36, anchor_x="center", bold=True)
        self.instruction = arcade.Text("Use ↑↓ to select, ENTER to confirm",
                                       self.SCREEN_WIDTH / 2, 60, arcade.color.WHITE, 12, anchor_x="center")

    def on_draw(self):
        self.clear()
        arcade.draw_rect_filled(
            arcade.XYWH(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            (0, 0, 0, 180)
        )
        arcade.draw_rect_outline(
            arcade.XYWH(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, self.SCREEN_WIDTH - 40,
                        self.SCREEN_HEIGHT - 100),
            arcade.color.GRAY, 2
        )
        self.title.draw()
        for i, (text, action) in enumerate(self.options):
            y = self.SCREEN_HEIGHT / 2 - i * 50
            color = arcade.color.YELLOW if i == self.selected else arcade.color.WHITE
            if i == self.selected:
                arcade.draw_rect_filled(arcade.XYWH(self.SCREEN_WIDTH / 2, y + 10, 250, 35), arcade.color.DARK_GRAY)
            arcade.draw_text(text, self.SCREEN_WIDTH / 2, y, color, 20, anchor_x="center")
        self.instruction.draw()

    def on_key_press(self, key: int, modifiers: int):
        if key in (arcade.key.UP, arcade.key.W):
            self.selected = (self.selected - 1) % len(self.options)
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.selected = (self.selected + 1) % len(self.options)
        elif key == arcade.key.ENTER:
            action = self.options[self.selected][1]
            if action == "resume":
                self.game_view.paused = False
                self.window.show_view(self.game_view)
            elif action == "menu":
                from  views.menu_view import MenuView
                self.window.show_view(MenuView())
        elif key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)