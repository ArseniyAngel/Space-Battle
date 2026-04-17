# views/victory_view.py
import arcade
from config import *
from views.menu_view import MenuView


class VictoryView(arcade.View):
    def __init__(self, final_score: int, target: int):
        super().__init__()
        self.SCREEN_WIDTH = self.window.width
        self.SCREEN_HEIGHT = self.window.height
        self.window.set_fullscreen(True)
        self.final_score = final_score
        self.target = target

        self.background = arcade.Sprite(f"{ASSETS_DIR}/bg_victory.jpg")
        self.background.width = self.window.width
        self.background.height = self.window.height
        self.background.center_x = self.SCREEN_WIDTH / 2
        self.background.center_y = self.SCREEN_HEIGHT / 2

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.background)
        arcade.draw_text("🎉 VICTORY! 🎉", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 60,
                         arcade.color.GOLD, 32, anchor_x="center")
        arcade.draw_text(f"Score: {self.final_score}", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text(f"Goal reached: {self.target}", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 40,
                         arcade.color.CYAN, 18, anchor_x="center")
        arcade.draw_text("Press R to Play Again or ESC to Menu", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 90,
                         arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.R or key == arcade.key.ESCAPE:
            self.window.show_view(MenuView())