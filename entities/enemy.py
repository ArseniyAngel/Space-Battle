import arcade
from config import ENEMY_HP
class Enemy(arcade.Sprite):
    def __init__(self, texture_path):
        super().__init__(texture_path, scale=0.1)
        self.hp = ENEMY_HP
        self.shoot_timer = 0.0
