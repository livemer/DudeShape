import pygame
from pygame.locals import *

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500
TANK_SIZE = 50
BULLET_SIZE = 35
TANK_SPEED = 5
BULLET_SPEED = 10
COOLDOWN = 5  # задержка между выстрелами (мс)
RESPAWN_TIME = 2000  # время возрождения (мс)
DAMAGE = 20  # урон от пули
MAX_HEALTH = 100  # максимальное здоровье танка

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Загрузка изображений (замените на свои или используйте фигуры)
try:
    tank_image = pygame.image.load('tank.png').convert_alpha()
    tank_image = pygame.transform.scale(tank_image, (TANK_SIZE, TANK_SIZE))
    bullet_image = pygame.image.load('image.png').convert_alpha()
    bullet_image = pygame.transform.scale(bullet_image, (BULLET_SIZE, BULLET_SIZE))
except FileNotFoundError or pygame.error:
    print("Изображения не найдены. Используются фигуры.")
    tank_image = pygame.Surface((TANK_SIZE, TANK_SIZE))
    tank_image.fill((0, 255, 0))  # Зеленый танк
    bullet_image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
    bullet_image.fill((255, 0, 0))  # Красная пуля

# Поворот изображений танка для разных направлений
tank_images = {}
for angle in [0, 90, 180, 270]:
    rotated = pygame.transform.rotate(tank_image, angle)
    tank_images[angle] = rotated

# Класс танка
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, controls):
        super().__init__()
        self.original_image = tank_images[0]
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = 0  # 0: вверх, 90: вправо, 180: вниз, 270: влево
        self.speed = TANK_SPEED
        self.health = MAX_HEALTH
        self.score = 0
        self.alive = True
        self.last_shot_time = 0
        self.respawn_time = 0
        self.controls = controls  # Клавиши управления

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > COOLDOWN:
            self.last_shot_time = current_time
            # Определение начальной позиции пули в зависимости от направления
            if self.direction == 0:  # вверх
                bullet_x = self.rect.centerx
                bullet_y = self.rect.top
            elif self.direction == 90:  # вправо
                bullet_x = self.rect.right
                bullet_y = self.rect.centery
            elif self.direction == 180:  # вниз
                bullet_x = self.rect.centerx
                bullet_y = self.rect.bottom
            elif self.direction == 270:  # влево
                bullet_x = self.rect.left
                bullet_y = self.rect.centery
            bullet = Bullet(bullet_x, bullet_y, self.direction, self)
            all_sprites.add(bullet)
            bullet_group.add(bullet)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            self.remove(active_tanks)
            self.respawn_time = pygame.time.get_ticks() + RESPAWN_TIME

    def respawn(self):
        self.health = MAX_HEALTH
        self.alive = True
        # Начальная позиция
        if self.controls == 'wasd':
            self.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT - 100)
        else:
            self.rect.center = (SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT - 100)
        self.add(active_tanks)

    def update(self):
        if not self.alive:
            if pygame.time.get_ticks() >= self.respawn_time:
                self.respawn()
            return
        keys = pygame.key.get_pressed()
        if self.controls == 'wasd':
            if keys[K_w]:
                self.direction = 0
                self.rect.y -= self.speed
            elif keys[K_s]:
                self.direction = 180
                self.rect.y += self.speed
            elif keys[K_a]:
                self.direction = 270
                self.rect.x -= self.speed
            elif keys[K_d]:
                self.direction = 90
                self.rect.x += self.speed
            if keys[K_SPACE]:
                self.shoot()
        elif self.controls == 'arrows':
            if keys[K_UP]:
                self.direction = 0
                self.rect.y -= self.speed
            elif keys[K_DOWN]:
                self.direction = 180
                self.rect.y += self.speed
            elif keys[K_LEFT]:
                self.direction = 270
                self.rect.x -= self.speed
            elif keys[K_RIGHT]:
                self.direction = 90
                self.rect.x += self.speed
            if keys[K_RETURN]:
                self.shoot()
        # Ограничение движения рамками экрана
        self.rect.clamp_ip(screen.get_rect())
        # Обновление изображения в зависимости от направления
        if self.direction == 90 or self.direction == 270:
            self.image = pygame.transform.flip(tank_images[self.direction], True, False)
        else:
            self.image = tank_images[self.direction]

# Класс пули
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner):
        super().__init__()
        self.image = pygame.transform.rotate(bullet_image, direction)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = BULLET_SPEED
        self.owner = owner

    def update(self):
        if self.direction == 0:
            self.rect.y -= self.speed
        elif self.direction == 90:
            self.rect.x += self.speed
        elif self.direction == 180:
            self.rect.y += self.speed
        elif self.direction == 270:
            self.rect.x -= self.speed
        # Удаление пули, если она вышла за экран
        if not screen.get_rect().contains(self.rect):
            self.kill()

# Создание групп спрайтов
all_sprites = pygame.sprite.Group()
tank_group = pygame.sprite.Group()
active_tanks = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

# Создание игроков
player1 = Tank(SCREEN_WIDTH // 4, SCREEN_HEIGHT - 100, 'wasd')
player2 = Tank(SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT - 100, 'arrows')
all_sprites.add(player1, player2)
tank_group.add(player1, player2)
active_tanks.add(player1, player2)

# Основной цикл игры
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # Обновление всех спрайтов
    all_sprites.update()

    # Проверка столкновений
    for bullet in bullet_group:
        hits = pygame.sprite.spritecollide(bullet, active_tanks, False)
        for hit in hits:
            if hit != bullet.owner:
                hit.take_damage(DAMAGE)
                if hit.health <= 0:
                    bullet.owner.score += 1
                bullet.kill()

    # Отрисовка
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Отображение счета
    font = pygame.font.Font(None, 36)
    player1_score_text = font.render(f"Игрок 1: {player1.score}", True, BLACK)
    player2_score_text = font.render(f"Игрок 2: {player2.score}", True, BLACK)
    screen.blit(player1_score_text, (10, 10))
    screen.blit(player2_score_text, (SCREEN_WIDTH - 150, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()