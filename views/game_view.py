import random
import math
import arcade
from config import *
from entities import ExplosionFlash, ExplosionParticle, Shockwave, EngineParticle, Particle, Enemy

from utils.sounds import SoundManager


class GameView(arcade.View):
    def __init__(self, target_score: int = 3000, endless_mode: bool = False):
        super().__init__()
        self.SCREEN_WIDTH = self.window.width
        self.SCREEN_HEIGHT = self.window.height
        self.window.set_fullscreen(True)
        self.player = arcade.Sprite("assets/Spaceship.png", scale=0.25)

        self.player.center_x = self.SCREEN_WIDTH / 2
        self.player.center_y = self.SCREEN_HEIGHT / 2
        self.player.angle = 90.0

        self.keys_held = set()

        self.energy_pool = MAX_ENERGY
        self.shields = [MAX_SHIELD_PER_SECTOR * 0.3] * 4
        self.selected_shield = 0
        self.player_hp = 100

        self.bullets = arcade.SpriteList()
        self.enemy_bullets = arcade.SpriteList()
        self.bullet_texture = arcade.make_circle_texture(4, arcade.color.YELLOW)
        self.enemy_bullet_texture = arcade.make_circle_texture(4, arcade.color.RED)

        self.enemies = arcade.SpriteList()
        self.enemy_texture = "assets/stone_ship.png"
        self.spawn_timer = 0.0

        self.particles = arcade.SpriteList()
        self.engine_particles = arcade.SpriteList()
        self.score = 0
        # self.camera = arcade.camera.Camera2D()
        self.debug_text = arcade.Text("", 10, 20, arcade.color.WHITE, 12)
        self.shield_text = arcade.Text("", 10, 38, arcade.color.YELLOW, 12)
        self.hp_text = arcade.Text("", 10, self.SCREEN_HEIGHT - 25, arcade.color.RED, 14)
        self.score_text = arcade.Text("", self.SCREEN_WIDTH - 110, self.SCREEN_HEIGHT - 25, arcade.color.GREEN, 14)
        self.setup_camera()
        self.player.change_x = 0
        self.player.change_y = 0
        self.accel = 0.2
        self.drag = 0.98
        self.show_vectors = False
        self.firing_queue = []
        self.fire_timer = 0.0
        self.fire_side_offset = 0
        self.FIRE_DELAY = 0.08

        self.stars_far = arcade.SpriteList()
        self.stars_medium = arcade.SpriteList()
        self.stars_near = arcade.SpriteList()

        self.star_texture_far = arcade.make_circle_texture(2, arcade.color.LIGHT_CYAN)
        self.star_texture_medium = arcade.make_circle_texture(3, arcade.color.WHITE)
        self.star_texture_near = arcade.make_circle_texture(5, arcade.color.GRAY)

        self._generate_stars()
        self.target_score = target_score
        self.endless_mode = endless_mode
        self.kills_count = 0

        self.is_dead = False
        self.death_timer = 0.0

        if endless_mode:
            self.goal_text = arcade.Text("♾ ENDLESS MODE", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT - 50,
                                         arcade.color.PURPLE, 16, anchor_x="center")
        else:
            self.goal_text = arcade.Text(f"Goal: {target_score}", self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT - 50,
                                         arcade.color.GREEN, 16, anchor_x="center")

        if hasattr(self.window, 'current_view') and hasattr(self.window.current_view, 'music_player'):
            if self.window.current_view.music_player:
                self.window.current_view.music_player.delete()

        self.screen_shake = 0.0
        self.shake_duration = 0.0
        self.paused = False
        self.sound_manager = SoundManager()
        self.sound_manager.play_music()

    def _generate_stars(self):
        """Создаёт звёзды для всех слоёв"""
        for _ in range(100):
            star = arcade.Sprite(self.star_texture_far)
            star.center_x = random.randint(0, self.SCREEN_WIDTH)
            star.center_y = random.randint(0, self.SCREEN_HEIGHT)
            star.parallax_factor = 0.1  # Очень медленные
            self.stars_far.append(star)

        for _ in range(50):
            star = arcade.Sprite(self.star_texture_medium)
            star.center_x = random.randint(0, self.SCREEN_WIDTH)
            star.center_y = random.randint(0, self.SCREEN_HEIGHT)
            star.parallax_factor = 0.3  # Средняя скорость
            self.stars_medium.append(star)

        for _ in range(20):
            star = arcade.Sprite(self.star_texture_near)
            star.center_x = random.randint(0, self.SCREEN_WIDTH)
            star.center_y = random.randint(0, self.SCREEN_HEIGHT)
            star.parallax_factor = 0.6
            self.stars_near.append(star)

    def setup_camera(self):
        arcade.set_background_color(arcade.color.COOL_BLACK)
        self.prev_player_y = self.player.center_y
        self.prev_player_x = self.player.center_x

    def on_draw(self):
        self.clear()

        old_angle = self.player.angle
        self.player.angle -= 270

        self.stars_far.draw()
        self.stars_medium.draw()
        self.stars_near.draw()
        self.bullets.draw()
        self.enemy_bullets.draw()
        self.enemies.draw()
        self.particles.draw()
        self.engine_particles.draw()
        if not self.is_dead or self.death_timer < 0.3:
            arcade.draw_sprite(self.player)
        self.player.angle = old_angle
        self.particles.draw()

        self.draw_ui()
        self.draw_shield_effects()

        self.hp_text.text = f"HP: {self.player_hp}"
        self.hp_text.draw()
        self.score_text.text = f"Score: {self.score}"
        self.score_text.draw()
        self.goal_text.draw()
        if self.endless_mode:
            multiplier = max(1.0, ENEMY_SPAWN_INTERVAL / max(0.3, self.get_current_spawn_interval()))
            arcade.draw_text(f"Wave: x{multiplier:.1f}",
                             self.SCREEN_WIDTH - 200, self.SCREEN_HEIGHT - 25,
                             arcade.color.ORANGE, 12, anchor_x="center")

        if self.show_vectors:

            self.debug_text.text = f"Angle: {self.player.angle:.1f}°"
            self.debug_text.draw()
            self.shield_text.text = f"Selected: {SHIELD_LABELS[self.selected_shield]}"
            self.shield_text.draw()
            angle_rad = math.radians(90 - self.player.angle)
            forward_x = math.cos(angle_rad)
            forward_y = math.sin(angle_rad)

            nose_x = self.player.center_x + forward_x * 60
            nose_y = self.player.center_y + forward_y * 60
            arcade.draw_line(self.player.center_x, self.player.center_y, nose_x, nose_y, arcade.color.RED, 3)

            left_x = -forward_y
            left_y = forward_x
            arcade.draw_line(self.player.center_x, self.player.center_y,
                             self.player.center_x + left_x * 60, self.player.center_y + left_y * 60,
                             arcade.color.GREEN, 3)

            right_x = forward_y
            right_y = -forward_x
            arcade.draw_line(self.player.center_x, self.player.center_y,
                             self.player.center_x + right_x * 60, self.player.center_y + right_y * 60,
                             arcade.color.BLUE, 3)
            if self.screen_shake > 0:
                offset_x = random.uniform(-self.screen_shake, self.screen_shake)
                offset_y = random.uniform(-self.screen_shake, self.screen_shake)
                arcade.set_viewport(
                    offset_x,
                    self.SCREEN_WIDTH + offset_x,
                    offset_y,
                    self.SCREEN_HEIGHT + offset_y
                )
            if self.screen_shake > 0:
                arcade.set_viewport(0, self.SCREEN_WIDTH, 0, self.SCREEN_HEIGHT)

    def get_current_spawn_interval(self):
        if not self.endless_mode:
            return ENEMY_SPAWN_INTERVAL

        return max(0.3, ENEMY_SPAWN_INTERVAL / (1 + self.kills_count * 0.02))

    def draw_rotated_ellipse_arc(self, center_x, center_y, width, height,
                                 angle, start_angle, end_angle, color, thickness=2):

        rotation_rad = math.radians(angle)
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        a = width / 2
        b = height / 2

        num_points = 50
        points = []

        for i in range(num_points + 1):
            t = start_rad + (end_rad - start_rad) * i / num_points

            x = a * math.cos(t)
            y = b * math.sin(t)

            x_rot = x * math.cos(rotation_rad) + y * math.sin(rotation_rad)
            y_rot = x * math.sin(rotation_rad) - y * math.cos(rotation_rad)

            points.append((center_x - x_rot, center_y + y_rot))

        if len(points) > 1:
            arcade.draw_line_strip(points, color, thickness)

    def draw_shield_effects(self):

        shield_width = 200
        shield_height = 50

        for i in range(4):

            sector_start = i * 90 - 45
            sector_end = (i + 1) * 90 - 45

            shield_percent = self.shields[i] / MAX_SHIELD_PER_SECTOR
            if shield_percent > 0:
                color = (int(255 * (1 - shield_percent)),
                         int(200 * shield_percent),
                         255,
                         int(150 * shield_percent))

                for offset in range(0, 6, 2):
                    self.draw_rotated_ellipse_arc(
                        self.player.center_x,
                        self.player.center_y,
                        shield_width + offset,
                        shield_height + offset,
                        self.player.angle - 90,
                        sector_start,
                        sector_end,
                        color,
                        thickness=2
                    )

    def draw_ui(self):
        ui_y = 55
        bar_w, bar_h = 130, 16
        spacing = 160
        start_x = (self.SCREEN_WIDTH - 200) / 4

        arcade.draw_text("ENERGY", self.SCREEN_WIDTH / 2, ui_y + 60, arcade.color.WHITE, 11, anchor_x="center",
                         width=bar_w)
        arcade.draw_rect_filled(arcade.XYWH(self.SCREEN_WIDTH / 2, ui_y + 50, bar_w, bar_h), arcade.color.DARK_GRAY)
        energy_fill = (self.energy_pool / MAX_ENERGY) * bar_w
        if energy_fill > 0:
            arcade.draw_rect_filled(arcade.XYWH(self.SCREEN_WIDTH / 2, ui_y + 50, energy_fill, bar_h),
                                    arcade.color.CYAN)

        for i, label in enumerate(SHIELD_LABELS):
            x = start_x + i * spacing
            color = arcade.color.GREEN if i == self.selected_shield else arcade.color.WHITE
            arcade.draw_text(label, x + bar_w / 2, ui_y + 20, color, 10, anchor_x="center", width=bar_w)
            arcade.draw_rect_filled(arcade.XYWH(x + bar_w / 2, ui_y, bar_w, bar_h), arcade.color.DARK_GRAY)
            fill = (self.shields[i] / MAX_SHIELD_PER_SECTOR) * bar_w
            if fill > 0:
                base_color = arcade.color.ORANGE if i == self.selected_shield else (
                    arcade.color.RED if self.shields[i] < 25 else arcade.color.BLUE)
                arcade.draw_rect_filled(arcade.XYWH(x + fill / 2, ui_y, fill, bar_h), base_color)

    def on_update(self, delta_time: float):
        if self.paused:
            return
        if hasattr(self, 'prev_player_x'):

            dx = self.player.center_x - self.prev_player_x
            dy = self.player.center_y - self.prev_player_y

            for star_list in [self.stars_far, self.stars_medium, self.stars_near]:
                for star in star_list:
                    star.center_x -= dx * star.parallax_factor
                    star.center_y -= dy * star.parallax_factor

                    if star.center_x < 0:
                        star.center_x = self.SCREEN_WIDTH
                    elif star.center_x > self.SCREEN_WIDTH:
                        star.center_x = 0
                    if star.center_y < 0:
                        star.center_y = self.SCREEN_HEIGHT
                    elif star.center_y > self.SCREEN_HEIGHT:
                        star.center_y = 0

            self.prev_player_x = self.player.center_x
            self.prev_player_y = self.player.center_y
        if self.firing_queue:
            self.fire_timer -= delta_time

            if self.fire_timer <= 0:
                gun_offset = self.firing_queue.pop(0)

                self.fire_single_gun(gun_offset, self.fire_side_offset)

                self.fire_timer = self.FIRE_DELAY
        # 1. Поворот
        if arcade.key.A in self.keys_held:
            self.player.angle -= PLAYER_TURN_SPEED
        if arcade.key.D in self.keys_held:
            self.player.angle += PLAYER_TURN_SPEED

        # 2. Физика
        if arcade.key.W in self.keys_held:
            rad = math.radians(90 - self.player.angle)
            self.player.change_x += math.cos(rad) * ACCELERATION
            self.player.change_y += math.sin(rad) * ACCELERATION

            # 2. Ракетный хвост
            tail_rad = rad + math.pi
            tail_dist = 40

            spawn_x = self.player.center_x + math.cos(tail_rad) * tail_dist
            spawn_y = self.player.center_y + math.sin(tail_rad) * tail_dist

            # 3. Спавн частиц
            back_rad = math.radians(270 - self.player.angle)
            exhaust_speed = 200

            for _ in range(3):
                spread = random.uniform(-0.2, 0.2)
                vx = math.cos(back_rad + spread) * exhaust_speed
                vy = math.sin(back_rad + spread) * exhaust_speed

                self.engine_particles.append(EngineParticle(spawn_x, spawn_y, vx, vy))
        if arcade.key.P in self.keys_held:
            self.show_vectors = not (self.show_vectors)

        max_speed = 0.5
        current_speed = math.hypot(self.player.change_x, self.player.change_y)
        if current_speed > max_speed:
            ratio = max_speed / current_speed
            self.player.change_x *= ratio
            self.player.change_y *= ratio

        self.player.update()

        self.player.change_x *= DRAG
        self.player.change_y *= DRAG
        self.player.center_x = max(18, min(self.SCREEN_WIDTH - 18, self.player.center_x))
        self.player.center_y = max(18, min(self.SCREEN_HEIGHT - 18, self.player.center_y))

        # 2. Регенерация энергии
        if arcade.key.SPACE not in self.keys_held and self.energy_pool < MAX_ENERGY:
            self.energy_pool = min(MAX_ENERGY, self.energy_pool + ENERGY_REGEN_RATE * delta_time)

        # 3. Перекачка в щит
        if arcade.key.SPACE in self.keys_held and self.shields[self.selected_shield] < MAX_SHIELD_PER_SECTOR:
            if self.energy_pool > 0.0:
                transfer = SHIELD_TRANSFER_RATE * delta_time
                room = MAX_SHIELD_PER_SECTOR - self.shields[self.selected_shield]
                actual = min(transfer, room, self.energy_pool)
                self.energy_pool -= actual
                self.shields[self.selected_shield] += actual
                if self.energy_pool < 0.01: self.energy_pool = 0.0

        # 4. Обновление снарядов
        for bullet in self.bullets:
            bullet.center_x += bullet.change_x * delta_time
            bullet.center_y += bullet.change_y * delta_time
            if not (-50 < bullet.center_x < self.SCREEN_WIDTH + 50 and -50 < bullet.center_y < self.SCREEN_HEIGHT + 50):
                bullet.remove_from_sprite_lists()
        for bullet in self.enemy_bullets:
            bullet.center_x += bullet.change_x * delta_time
            bullet.center_y += bullet.change_y * delta_time
            if not (-50 < bullet.center_x < self.SCREEN_WIDTH + 50 and -50 < bullet.center_y < self.SCREEN_HEIGHT + 50):
                bullet.remove_from_sprite_lists()
        # 5. Спавн врагов
        self.spawn_timer += delta_time
        current_interval = self.get_current_spawn_interval()
        if self.spawn_timer >= current_interval:
            self.spawn_enemy()
            self.spawn_timer = 0.0

        # 6. ИИ врагов
        for enemy in self.enemies:
            enemy.shoot_timer += delta_time

            dist = math.hypot(self.player.center_x - enemy.center_x, self.player.center_y - enemy.center_y)
            angle_to_player = math.atan2(self.player.center_y - enemy.center_y,
                                         self.player.center_x - enemy.center_x)

            angle_diff = (angle_to_player - math.radians(enemy.angle) + math.pi) % (2 * math.pi) - math.pi
            enemy.angle += math.degrees(angle_diff) * 0.05
            if dist > 250:
                rad = math.radians(enemy.angle)
                enemy.center_x += math.cos(rad) * ENEMY_SPEED * delta_time
                enemy.center_y += math.sin(rad) * ENEMY_SPEED * delta_time
            if dist <= 350 and enemy.shoot_timer > 2.5:
                self.spawn_enemy_bullet(enemy.center_x, enemy.center_y, angle_to_player)
                enemy.shoot_timer = 0

        # 7. Коллизия врагов
        for bullet in self.bullets:
            hit_enemies = arcade.check_for_collision_with_list(bullet, self.enemies)
            if hit_enemies:
                for enemy in hit_enemies:
                    enemy.hp -= BULLET_DAMAGE
                    if enemy.hp <= 0:
                        self.score += SCORE_PER_KILL
                        self.kills_count += 1
                        self.spawn_explosion(enemy.center_x, enemy.center_y, size="medium")
                        self.sound_manager.play("explosion", volume=0.5)
                        enemy.remove_from_sprite_lists()
                bullet.remove_from_sprite_lists()
        for bullet in self.enemy_bullets:
            if arcade.check_for_collision(bullet, self.player):
                self.apply_damage_from_bullet(bullet)
                bullet.remove_from_sprite_lists()
        # 8. Коллизия игрока
        for enemy in self.enemies:
            if arcade.check_for_collision(self.player, enemy):
                self.apply_damage_to_player(enemy)
                enemy.remove_from_sprite_lists()
        self.particles.update(delta_time)
        if self.player_hp <= 0 and not self.is_dead:
            self.is_dead = True
            self.shields = [0] * 4
            self.spawn_explosion(self.player.center_x, self.player.center_y, size="large")
            self.sound_manager.play("explosion", volume=0.5)
            self.trigger_screen_shake(8, 0.4)
        elif self.is_dead:
            self.death_timer += delta_time
            if self.death_timer >= 1.0:
                from views.game_over_view import GameOverView
                self.window.show_view(GameOverView(self.score, self.target_score, self.endless_mode))
        elif not self.endless_mode and self.score >= self.target_score:
            from views.victory_view import VictoryView
            self.window.show_view(VictoryView(self.score, self.target_score))
        self.particles.update(delta_time)  # Взрывы
        self.engine_particles.update(delta_time)
        if self.shake_duration > 0:
            self.shake_duration -= delta_time
            if self.shake_duration <= 0:
                self.screen_shake = 0.0

    def trigger_screen_shake(self, strength: float, duration: float):
        self.screen_shake = strength
        self.shake_duration = duration

    def fire_single_gun(self, gun_offset, side_angle_offset):
        if self.energy_pool >= 2:
            self.energy_pool -= 2
            nose_rad = math.radians(90 - self.player.angle)
            forward_x = math.cos(nose_rad)
            forward_y = math.sin(nose_rad)

            if side_angle_offset > 0:
                shot_dir_x = -forward_y
                shot_dir_y = forward_x
            else:  # Правый
                shot_dir_x = forward_y
                shot_dir_y = -forward_x

            side_distance = 0

            bullet = arcade.Sprite(":resources:/images/space_shooter/laserBlue01.png", scale=0.4)

            bullet.center_x = self.player.center_x + forward_x * gun_offset + shot_dir_x * side_distance
            bullet.center_y = self.player.center_y + forward_y * gun_offset + shot_dir_y * side_distance

            bullet.angle = self.player.angle

            bullet.change_x = BULLET_SPEED * shot_dir_x
            bullet.change_y = BULLET_SPEED * shot_dir_y
            self.sound_manager.play("shoot", volume=0.3)
            self.bullets.append(bullet)

    def apply_damage_from_bullet(self, bullet):
        dx = bullet.center_x - self.player.center_x
        dy = bullet.center_y - self.player.center_y
        angle_from_player = math.degrees(math.atan2(dy, dx))
        visual_angle = self.player.angle - 270
        diff = (angle_from_player - visual_angle + 180) % 360 - 180

        if -45 <= diff < 45:
            shield_idx = 0
        elif 45 <= diff < 135:
            shield_idx = 1
        elif diff >= 135 or diff < -135:
            shield_idx = 2
        else:
            shield_idx = 3

        if self.shields[shield_idx] > 0:
            self.shields[shield_idx] = max(0, self.shields[shield_idx] - 10)
            self.sound_manager.play("hit", volume=0.2)
        else:
            self.player_hp -= 10
            self.sound_manager.play("hit", volume=0.5)
            if self.player_hp <= 0:
                self.spawn_explosion(self.player.center_x, self.player.center_y)

    def spawn_explosion(self, x, y, size: str = "medium"):
        configs = {
            "small": {"particles": 20, "speed": 150, "lifetime": 0.8, "flash": True},
            "medium": {"particles": 40, "speed": 250, "lifetime": 1.2, "flash": True},
            "large": {"particles": 70, "speed": 350, "lifetime": 1.8, "flash": True},
        }
        cfg = configs.get(size, configs["medium"])

        if cfg["flash"]:
            self.particles.append(ExplosionFlash(x, y))

        self.particles.append(Shockwave(x, y))

        hot_colors = [arcade.color.ORANGE, arcade.color.RED, arcade.color.YELLOW, arcade.color.GOLD]
        for _ in range(cfg["particles"] // 2):
            color = random.choice(hot_colors)
            particle = ExplosionParticle(
                x, y, color,
                size=random.randint(4, 10),
                speed=cfg["speed"] * random.uniform(0.8, 1.5),
                lifetime=cfg["lifetime"] * random.uniform(0.7, 1.3)
            )
            self.particles.append(particle)

        smoke_colors = [arcade.color.GRAY, arcade.color.DARK_GRAY, arcade.color.BLACK]
        for _ in range(cfg["particles"] // 3):
            color = random.choice(smoke_colors)
            particle = ExplosionParticle(
                x, y, color,
                size=random.randint(6, 15),
                speed=cfg["speed"] * random.uniform(0.3, 0.7),
                lifetime=cfg["lifetime"] * random.uniform(1.2, 2.0)
            )
            particle.gravity = -10
            self.particles.append(particle)

        for _ in range(cfg["particles"] // 4):
            particle = ExplosionParticle(
                x, y, arcade.color.WHITE,
                size=random.randint(2, 4),
                speed=cfg["speed"] * random.uniform(1.5, 2.5),
                lifetime=0.4
            )
            particle.alpha = 200
            self.particles.append(particle)

    def spawn_enemy(self):
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x, y = random.randint(0, self.SCREEN_WIDTH), -10
        elif side == "bottom":
            x, y = random.randint(0, self.SCREEN_WIDTH), self.SCREEN_HEIGHT + 10
        elif side == "left":
            x, y = -10, random.randint(0, self.SCREEN_HEIGHT)
        else:
            x, y = self.SCREEN_WIDTH + 10, random.randint(0, self.SCREEN_HEIGHT)

        enemy = Enemy(self.enemy_texture)
        enemy.center_x = x
        enemy.center_y = y
        enemy.angle = self._calculate_angle_to_player(x, y)
        self.enemies.append(enemy)

    def _calculate_angle_to_player(self, x, y):
        """Вспомогательный метод: угол от точки (x,y) к игроку"""
        dx = self.player.center_x - x
        dy = self.player.center_y - y
        return math.degrees(math.atan2(dy, dx))

    def apply_damage_to_player(self, enemy):
        dx = enemy.center_x - self.player.center_x
        dy = enemy.center_y - self.player.center_y
        angle_from_player = math.degrees(math.atan2(dy, dx))

        visual_angle = self.player.angle - 270
        diff = (angle_from_player - visual_angle + 180) % 360 - 180

        if - 45 <= diff < 45:
            shield_idx = 0

        elif 45 <= diff <= 135:
            shield_idx = 1

        elif 135 <= diff < -90:
            shield_idx = 2
        else:
            shield_idx = 3

        if self.shields[shield_idx] > 0:
            self.shields[shield_idx] = max(0, self.shields[shield_idx] - 25)
        else:
            self.player_hp -= 20
            if self.player_hp <= 0:
                self.spawn_explosion(self.player.center_x, self.player.center_y)

    def on_key_press(self, key: int, modifiers: int):
        self.keys_held.add(key)
        if key == arcade.key.KEY_1:
            self.selected_shield = 0
        elif key == arcade.key.KEY_2:
            self.selected_shield = 1
        elif key == arcade.key.KEY_3:
            self.selected_shield = 2
        elif key == arcade.key.KEY_4:
            self.selected_shield = 3
        # elif key == arcade.key.U:
        #     self.player_hp = 0
        #     self.score += 7000
        # self.shields[self.selected_shield] = max(0, self.shields[self.selected_shield] - 20)
        elif key == arcade.key.ESCAPE:
            from views.pause_view import PauseView
            pause_view = PauseView(self)
            self.window.show_view(pause_view)

    def on_key_release(self, key: int, modifiers: int):
        self.keys_held.discard(key)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.firing_queue = [-2, 5, 20, 30]
            self.fire_side_offset = 90
            self.fire_timer = 0.0

        elif button == arcade.MOUSE_BUTTON_RIGHT:
            self.firing_queue = [30, 20, 5, -2]
            self.fire_side_offset = -90
            self.fire_timer = 0.0

    def spawn_enemy_bullet(self, x, y, angle_rad):
        bullet = arcade.Sprite(self.enemy_bullet_texture)
        bullet.center_x = x + math.cos(angle_rad) * 20
        bullet.center_y = y + math.sin(angle_rad) * 20
        bullet.change_x = math.cos(angle_rad) * 250
        bullet.change_y = math.sin(angle_rad) * 250
        self.enemy_bullets.append(bullet)
