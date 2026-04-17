# views/help_view.py
import arcade
from config import *


class HelpView(arcade.View):
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

        # Тексты
        self.title = arcade.Text("HOW TO PLAY", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT - 80,
                                 arcade.color.CYAN, 28, anchor_x="center", bold=True)
        self.controls_title = arcade.Text("CONTROLS", self.SCREEN_WIDTH / 4, self.SCREEN_HEIGHT / 2 + 40,
                                          arcade.color.YELLOW, 20, anchor_x="center")
        self.shields_title = arcade.Text("SHIELD SYSTEM", 3 * self.SCREEN_WIDTH / 4, self.SCREEN_HEIGHT / 2 + 40,
                                         arcade.color.YELLOW, 20, anchor_x="center")
        self.back_text = arcade.Text("Press ESC or ENTER to return", self.SCREEN_WIDTH / 2, 40,
                                     arcade.color.ANTI_FLASH_WHITE, 14, anchor_x="center")

        self.controls = [
            "W — Двигаться вперёд",
            "A / D — Поворот корабля",
            "ЛКМ — Залп левого борта",
            "ПКМ — Залп правого борта",
            "SPACE — Перекачка энергии в щит",
            "1/2/3/4 — Выбрать сектор щита",
        ]
        self.control_texts = [
            arcade.Text(text, self.SCREEN_WIDTH / 4, self.SCREEN_HEIGHT / 2 - i * 30,
                        arcade.color.WHITE, 14, anchor_x="center")
            for i, text in enumerate(self.controls)
        ]

        self.shields_info = [
            "• 4 сектора: FRONT, RIGHT, BACK, LEFT",
            "• Щиты поглощают урон со своей стороны",
            "• Когда щит пробит — урон идёт по корпусу",
            "• Удерживай SPACE для восстановления щита",
            "• Энергия восстанавливается, когда SPACE отпущен",
        ]
        self.shield_texts = [
            arcade.Text(text, 3 * self.SCREEN_WIDTH / 4, self.SCREEN_HEIGHT / 2 - i * 30,
                        arcade.color.WHITE, 13, anchor_x="center")
            for i, text in enumerate(self.shields_info)
        ]

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.background)

        # Панель
        box_width = self.SCREEN_WIDTH - 40
        box_height = self.SCREEN_HEIGHT - 100
        overlay_color = (20, 20, 20, 210)
        arcade.draw_rect_filled(
            arcade.XYWH(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, box_width, box_height),
            overlay_color
        )
        arcade.draw_rect_outline(
            arcade.XYWH(self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, box_width, box_height),
            arcade.color.GRAY, 2
        )

        self.title.draw()
        self.controls_title.draw()
        self.shields_title.draw()

        for text in self.control_texts + self.shield_texts:
            text.draw()

        self.back_text.draw()

    def on_key_press(self, key: int, modifiers: int):
        if key in (arcade.key.ESCAPE, arcade.key.ENTER):
            from views.menu_view import MenuView
            self.window.show_view(MenuView())