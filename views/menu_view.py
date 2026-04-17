# views/menu_view.py
import arcade
import math
import time
from config import *
from utils.sounds import SoundManager



class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.SCREEN_WIDTH = self.window.width
        self.SCREEN_HEIGHT = self.window.height
        self.window.set_fullscreen(True)

        # Фон
        self.background = arcade.Sprite(f"{ASSETS_DIR}/bg.jpg")
        self.background.width = self.window.width
        self.background.height = self.window.height
        self.background.center_x = self.SCREEN_WIDTH / 2
        self.background.center_y = self.SCREEN_HEIGHT / 2

        # Опции меню
        self.options = [
            ("▶ Start - Easy (1000 pts)", "start_easy"),
            ("▶ Start - Medium (3000 pts)", "start_medium"),
            ("▶ Start - Hard (6000 pts)", "start_hard"),
            ("Endless Mode", "start_endless"),
            ("How to Play", "help"),
            ("Quit", "quit"),
        ]
        self.selected = 0

        # Тексты
        self.title_text = arcade.Text(
            "SPACE BATTLE", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2 + 120,
            arcade.color.CYAN, 32, anchor_x="center", bold=True
        )
        self.instruction = arcade.Text(
            "Use ↑↓ or WD to select, ENTER to confirm, ESC for menu",
            self.SCREEN_WIDTH / 2, 60, arcade.color.ANTI_FLASH_WHITE, 12, anchor_x="center",
        )

        # Звуки
        self.sound_manager = SoundManager()
        self.sound_manager.play_music()

    def get_blink_alpha(self, speed: float = 4.0) -> int:
        return int(127.5 + 127.5 * math.sin(time.time() * speed))

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.background)

        # Полупрозрачная панель
        box_width = 390
        box_height = 380
        overlay_color = (20, 20, 20, 110)
        arcade.draw_rect_filled(
            arcade.XYWH(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, box_width, box_height),
            overlay_color
        )

        self.title_text.draw()

        for i, (text, mode) in enumerate(self.options):
            y = self.SCREEN_HEIGHT / 2 + 20 - i * 40
            color = arcade.color.YELLOW if i == self.selected else arcade.color.WHITE
            arcade.draw_text(text, self.SCREEN_WIDTH / 2, y, color, 18, anchor_x="center")

        alpha = self.get_blink_alpha(speed=3.0)
        self.instruction.color = (*self.instruction.color[:3], alpha)
        self.instruction.draw()

    def on_key_press(self, key: int, modifiers: int):
        from views.game_view import GameView
        from views.help_view import HelpView
        if key in (arcade.key.UP, arcade.key.W):
            self.selected = (self.selected - 1) % len(self.options)
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.selected = (self.selected + 1) % len(self.options)
        elif key == arcade.key.ENTER:
            action = self.options[self.selected][1]
            if action == "start_easy":
                self.window.show_view(GameView(target_score=1000, endless_mode=False))
            elif action == "start_medium":
                self.window.show_view(GameView(target_score=3000, endless_mode=False))
            elif action == "start_hard":
                self.window.show_view(GameView(target_score=6000, endless_mode=False))
            elif action == "start_endless":
                self.window.show_view(GameView(target_score=None, endless_mode=True))
            elif action == "help":
                self.window.show_view(HelpView())
            elif action == "quit":
                arcade.close_window()
        elif key == arcade.key.ESCAPE:
            arcade.close_window()