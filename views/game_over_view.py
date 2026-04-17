import arcade
from config import *


class GameOverView(arcade.View):
    def __init__(self, final_score: int, target: int = None, endless: bool = False):
        super().__init__()
        self.SCREEN_WIDTH = self.window.width
        self.SCREEN_HEIGHT = self.window.height
        self.window.set_fullscreen(True)
        self.final_score = final_score
        self.target = target
        self.endless = endless

        self.background = arcade.Sprite(f"{ASSETS_DIR}/bg_go.jpg")
        self.background.width = self.window.width
        self.background.height = self.window.height
        self.background.center_x = self.SCREEN_WIDTH / 2
        self.background.center_y = self.SCREEN_HEIGHT / 2

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.background)
        arcade.draw_text("GAME OVER", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 60,
                         arcade.color.RED, 36, anchor_x="center")
        arcade.draw_text(f"Score: {self.final_score}", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, 24, anchor_x="center")
        if self.endless:
            arcade.draw_text(f"Enemies killed: {self.final_score // SCORE_PER_KILL}",
                             self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 30,
                             arcade.color.ORANGE, 18, anchor_x="center")
        elif self.target:
            progress = min(100, int(self.final_score / self.target * 100))
            arcade.draw_text(f"Progress: {progress}% to {self.target}",
                             self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 30,
                             arcade.color.CYAN, 18, anchor_x="center")
        arcade.draw_text("Press R to Restart or ESC for Menu", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 - 80,
                         arcade.color.GRAY, 16, anchor_x="center")

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.R:

            from views.game_view import GameView
            self.window.show_view(GameView(self.target, self.endless))
        elif key == arcade.key.ESCAPE:
            from views.menu_view import MenuView
            self.window.show_view(MenuView())
