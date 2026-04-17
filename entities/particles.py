# entities/particles.py
import random
import math
import arcade
from config import PARTICLE_COLORS

class ExplosionFlash(arcade.Sprite):
    """Яркая вспышка в центре взрыва"""

    def __init__(self, x, y):
        super().__init__(arcade.make_soft_circle_texture(40, arcade.color.WHITE, 80))
        self.center_x = x
        self.center_y = y
        self.lifetime = 0.15  # Очень короткая вспышка
        self.alpha = 255
        self.scale = 1.0

    def update(self, delta_time: float):
        self.lifetime -= delta_time
        self.alpha = max(0, int(255 * (self.lifetime / 0.15)))
        self.scale = 1.5 - (self.lifetime / 0.15)  # Уменьшается
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()


class ExplosionParticle(arcade.Sprite):
    """Основная частица взрыва с огнём и дымом"""

    def __init__(self, x, y, color, size, speed, lifetime):
        super().__init__(arcade.make_circle_texture(size, color))
        self.center_x = x
        self.center_y = y
        angle = random.uniform(0, 360)
        rad = math.radians(angle)
        self.change_x = math.cos(rad) * speed * random.uniform(0.7, 1.3)
        self.change_y = math.sin(rad) * speed * random.uniform(0.7, 1.3)
        self.lifetime = lifetime
        self.start_alpha = 255
        self.alpha = 255
        self.gravity = -20  # Частицы немного "всплывают"

    def update(self, delta_time: float):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        self.change_y += self.gravity * delta_time  # Гравитация
        self.lifetime -= delta_time

        # Плавное затухание
        if self.lifetime < 0.3:
            self.alpha = max(0, int(255 * (self.lifetime / 0.3)))
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()


class Shockwave(arcade.Sprite):
    """Расширяющееся ударное кольцо"""

    def __init__(self, x, y):
        super().__init__(arcade.make_circle_texture(10, arcade.color.CYAN))
        self.center_x = x
        self.center_y = y
        self.radius = 10
        self.expansion_speed = 400  # пикселей в секунду
        self.lifetime = 0.4
        self.alpha = 200

    def update(self, delta_time: float):
        self.radius += self.expansion_speed * delta_time
        self.lifetime -= delta_time
        self.alpha = max(0, int(200 * (self.lifetime / 0.4)))
        self.width = self.radius * 2
        self.height = self.radius * 2
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()

    def draw(self):
        # Рисуем кольцо (не закрашенный круг)
        arcade.draw_circle_outline(
            self.center_x, self.center_y,
            self.radius,
            arcade.color.CYAN + (self.alpha,),
            border_width=4
        )


class EngineParticle(arcade.Sprite):
    """Частица двигателя - принимает готовый вектор скорости"""

    def __init__(self, x, y, change_x, change_y):
        super().__init__(arcade.make_circle_texture(5, arcade.color.LIGHT_RED_OCHRE))
        self.center_x = x
        self.center_y = y
        self.change_x = change_x  # Скорость по X
        self.change_y = change_y  # Скорость по Y
        self.lifetime = 0.5
        self.alpha = 255

    def update(self, delta_time: float):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        self.lifetime -= delta_time
        self.alpha = max(0, int(255 * (self.lifetime / 0.5)))
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()


class Particle(arcade.Sprite):
    """Простая частица для эффекта взрыва"""

    def __init__(self, x, y, color):
        super().__init__(arcade.make_circle_texture(3, color))
        self.center_x = x
        self.center_y = y
        self.change_x = random.uniform(-150, 150)
        self.change_y = random.uniform(-150, 150)
        self.lifetime = random.uniform(0.3, 0.7)  # секунды жизни
        self.alpha = 255

    def update(self, delta_time: float):
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time
        self.lifetime -= delta_time
        self.alpha = max(0, int(255 * (self.lifetime / 0.7)))
        if self.lifetime <= 0:
            self.remove_from_sprite_lists()
