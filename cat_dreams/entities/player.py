import pygame
import config as cfg
import os


class Player:
    def __init__(self, x: int, y: int):
        self.x = float(x)
        self.y = float(y)
        self.width = cfg.PLAYER_WIDTH
        self.height = cfg.PLAYER_HEIGHT

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.speed = cfg.PLAYER_SPEED
        self.jump_power = cfg.PLAYER_JUMP_POWER
        self.gravity = cfg.PLAYER_GRAVITY
        self.on_ground = False

        self.facing_right = True
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0.3
        self.has_weapon = False
        self.e_cooldown = 0

        sprite_path = os.path.join(cfg.ASSETS_PATH, 'sprites', 'cat_run.png')
        self.sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
        frame_height = self.sprite_sheet.get_height() // 5
        self.frames = []
        for i in range(5):
            frame = self.sprite_sheet.subsurface((0, i * frame_height, self.sprite_sheet.get_width(), frame_height))
            frame = pygame.transform.scale(frame, (self.width, self.height))
            self.frames.append(frame)
        print(f"✅ Загружено {len(self.frames)} кадров анимации.")

    def update(self, grid, cell_size, level_objects=None):
        self.vel_y += self.gravity
        self.x += self.vel_x
        self.check_collision(grid, cell_size, is_horizontal=True, objects=level_objects)

        if abs(self.vel_x) > 0.1 and self.on_ground:
            self.anim_timer += 1
            if self.anim_timer >= (1 / self.anim_speed):
                self.anim_frame = (self.anim_frame + 1) % len(self.frames)
                self.anim_timer = 0
        else:
            self.anim_timer = 0

        if self.vel_x > 0:
            self.facing_right = True
        elif self.vel_x < 0:
            self.facing_right = False

        self.y += self.vel_y
        self.on_ground = False
        self.check_collision(grid, cell_size, is_horizontal=False, objects=level_objects)
        if self.e_cooldown > 0:
            self.e_cooldown -= 1

    def check_collision(self, grid, cell_size, is_horizontal, objects=None):
        left = int(self.x // cell_size)
        right = int((self.x + self.width - 0.1) // cell_size)
        top = int(self.y // cell_size)
        bottom = int((self.y + self.height - 0.1) // cell_size)

        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    if grid[y][x] == 1:
                        if is_horizontal:
                            if self.vel_x > 0:
                                self.x = x * cell_size - self.width
                            elif self.vel_x < 0:
                                self.x = (x + 1) * cell_size
                            self.vel_x = 0
                        else:
                            if self.vel_y > 0:
                                self.y = y * cell_size - self.height
                                self.on_ground = True
                                self.vel_y = 0
                            elif self.vel_y < 0:
                                self.y = (y + 1) * cell_size
                                self.vel_y = 0

        if objects:
            for obj in objects:
                # Проверяем столкновение с прямоугольником объекта
                obj_left = obj['x'] - obj.get('width', cell_size) // 2
                obj_right = obj['x'] + obj.get('width', cell_size) // 2
                obj_top = obj['y'] - obj.get('height', cell_size) // 2
                obj_bottom = obj['y'] + obj.get('height', cell_size) // 2

                # Столкновение по осям
                collision_x = (self.x + self.width > obj_left and self.x < obj_right)
                collision_y = (self.y + self.height > obj_top and self.y < obj_bottom)

                if collision_x and collision_y:
                    if obj['type'] == 'platform':
                        # Платформа: если падаем сверху — становимся на неё
                        if not is_horizontal and self.vel_y > 0 and self.y + self.height < obj['y'] + 10:
                            self.y = obj['y'] - self.height
                            self.on_ground = True
                            self.vel_y = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power

    def move(self, dx):
        self.vel_x = dx * self.speed

    def pickup_weapon(self):
        self.has_weapon = True
        print("⚔️ Кот подобрал оружие!")

    def attack_enemy(self):
        if self.has_weapon:
            self.has_weapon = False  # оружие расходуется
            print("💥 Кот победил врага!")
            return True
        else:
            print("😿 Кот без оружия! Поражение!")
            return False

    def draw(self, screen, camera_offset=(0, 0)):
        self.anim_frame = max(0, min(self.anim_frame, len(self.frames) - 1))
        current_frame = self.frames[self.anim_frame]
        # Отражаем спрайт, если кот смотрит влево
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        rect = pygame.Rect(
            self.x - camera_offset[0],
            self.y - camera_offset[1],
            self.width, self.height
        )
        screen.blit(current_frame, rect.topleft)
