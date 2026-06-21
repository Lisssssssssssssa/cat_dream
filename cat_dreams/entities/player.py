import os
import pygame
import config as cfg


class Player:
    """
    Представляет игрока. Управляет физикой, анимацией,
    состоянием и отрисовкой персонажа.
    """
    def __init__(self, x: int, y: int):
        """
        Инициализация игрока.
        Args:
            x: Начальная координата X.
            y: Начальная координата Y.
        """
        # Позиция и физические параметры
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

        # Анимация и направление
        self.facing_right = True
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.3  # Кадров в секунду

        # Состояние игры
        self.has_weapon = False
        self.e_cooldown = 0

        # Загрузка спрайт-листа
        sprite_path = os.path.join(cfg.ASSETS_PATH, 'sprites', 'cat_run.png')
        self.sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
        frame_height = self.sprite_sheet.get_height() // 5
        self.frames = []

        for i in range(5):
            frame = self.sprite_sheet.subsurface(
                (0, i * frame_height, self.sprite_sheet.get_width(), frame_height)
            )
            frame = pygame.transform.scale(frame, (self.width, self.height))
            self.frames.append(frame)

    def update(self, grid: list[list[int]], cell_size: int, level_objects: list[dict] | None = None) -> None:
        """
        Обновление состояния игрока на один кадр.
        Args:
            grid: Двумерная сетка уровня (1 - стена, 0 - пол).
            cell_size: Размер клетки сетки в пикселях.
            level_objects: Список объектов уровня для проверки коллизий.
        """
        # Применение гравитации и горизонтального движения
        self.vel_y += self.gravity
        self.x += self.vel_x

        # Проверка горизонтальных коллизий
        self.check_collision(grid, cell_size, is_horizontal=True, objects=level_objects)

        # Логика анимации
        self._update_animation()

        # Определение направления взгляда
        if abs(self.vel_x) > 0.1:
            self.facing_right = self.vel_x > 0

        # Вертикальное движение
        self.y += self.vel_y
        self.on_ground = False

        # Проверка вертикальных коллизий
        self.check_collision(grid, cell_size, is_horizontal=False, objects=level_objects)

        # Обновление кулдауна взаимодействия
        if self.e_cooldown > 0:
            self.e_cooldown -= 1

    def _update_animation(self) -> None:
        """Обновляет текущий кадр анимации при движении."""
        if abs(self.vel_x) > 0.1 and self.on_ground:
            self.anim_timer += 1
            threshold = 1.0 / self.anim_speed
            if self.anim_timer >= threshold:
                self.anim_frame = (self.anim_frame + 1) % len(self.frames)
                self.anim_timer = 0.0
        else:
            self.anim_timer = 0.0

    def check_collision(
            self,
            grid: list[list[int]],
            cell_size: int,
            is_horizontal: bool,
            objects: list[dict] | None = None
    ) -> None:
        """
        Проверяет и разрешает столкновения со стенами и объектами.

        Args:
            grid: Сетка уровня.
            cell_size: Размер клетки.
            is_horizontal: Если True, проверяются боковые стены. 
                           Если False, проверяется пол/потолок.
            objects: Объекты уровня (платформы, лестницы и т.д.).
        """
        # Коллизии с сеткой (стены)
        left = int(self.x // cell_size)
        right = int((self.x + self.width - 0.1) // cell_size)
        top = int(self.y // cell_size)
        bottom = int((self.y + self.height - 0.1) // cell_size)

        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0

        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                if 0 <= y < rows and 0 <= x < cols and grid[y][x] == 1:
                    self._resolve_grid_collision(x, y, cell_size, is_horizontal)

        # Коллизии с объектами
        if objects:
            for obj in objects:
                if obj['type'] == 'platform':
                    self._resolve_platform_collision(obj, is_horizontal)

    def _resolve_grid_collision(self, gx: int, gy: int, cell_size: int, is_horizontal: bool) -> None:
        """Разрешает столкновение с клеткой сетки."""
        if is_horizontal:
            if self.vel_x > 0:
                self.x = gx * cell_size - self.width
            elif self.vel_x < 0:
                self.x = (gx + 1) * cell_size
            self.vel_x = 0.0
        else:
            if self.vel_y > 0:
                self.y = gy * cell_size - self.height
                self.on_ground = True
                self.vel_y = 0.0
            elif self.vel_y < 0:
                self.y = (gy + 1) * cell_size
                self.vel_y = 0.0

    def _resolve_platform_collision(self, obj: dict, is_horizontal: bool) -> None:
        """
        Разрешает столкновение с платформой (только сверху вниз).

        Args:
            obj: Словарь объекта платформы.
            is_horizontal: Флаг оси проверки (для платформ всегда False).
        """
        if is_horizontal:
            return

        # Вычисление границ AABB платформы (DRY)
        half_w = obj.get('width', 32) // 2
        half_h = obj.get('height', 32) // 2

        p_left = obj['x'] - half_w
        p_right = obj['x'] + half_w
        p_top = obj['y'] - half_h
        p_bottom = obj['y'] + half_h

        # Проверка пересечения прямоугольников
        if (self.x + self.width > p_left and self.x < p_right and
                self.y + self.height > p_top and self.y < p_bottom):

            # Приземление на платформу только если падаем сверху
            tolerance = 10  # Допуск в пикселях для "прилипания" к платформе
            if self.vel_y > 0 and (self.y + self.height - self.vel_y) <= p_top + tolerance:
                self.y = p_top - self.height
                self.on_ground = True
                self.vel_y = 0.0

    def jump(self) -> None:
        """Выполняет прыжок, если игрок находится на земле."""
        if self.on_ground:
            self.vel_y = self.jump_power

    def move(self, dx: int) -> None:
        """
        Устанавливает горизонтальную скорость.
        Args:
            dx: Направление (-1 влево, 0 стоп, 1 вправо).
        """
        self.vel_x = dx * self.speed

    def pickup_weapon(self) -> None:
        """Подбирает оружие."""
        self.has_weapon = True

    def attack_enemy(self) -> bool:
        """
        Атакует врага. Расходует оружие.
        Returns:
            True если атака успешна, False если нет оружия.
        """
        if self.has_weapon:
            self.has_weapon = False
            return True
        return False

    def draw(self, screen: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """
        Отрисовывает текущего кадра анимации игрока.
        Args:
            screen: Поверхность экрана Pygame.
            camera_offset: Смещение камеры (dx, dy).
        """
        # Защита от выхода за границы списка кадров
        safe_frame = max(0, min(self.anim_frame, len(self.frames) - 1))
        current_frame = self.frames[safe_frame]

        # Отражение спрайта по горизонтали
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)

        rect = pygame.Rect(
            self.x - camera_offset[0],
            self.y - camera_offset[1],
            self.width,
            self.height
        )
        screen.blit(current_frame, rect.topleft)
