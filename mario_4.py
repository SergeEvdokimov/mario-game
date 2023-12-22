import pygame
import os
import sys


class SpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def shift(self, vector):
        global max_y, max_x
        if vector == "up":
            min_y = min([elem.y for elem in self])
            for sprite in self:
                if sprite.y == cell_height * max_y:
                    sprite.y = min_y - cell_height
            max_y -= 1
        elif vector == "down":
            min_y = min([elem.y for elem in self])
            for sprite in self:
                if sprite.y == min_y:
                    sprite.y = (max_y + 1) * cell_height
            max_y += 1
        elif vector == "left":
            min_x = min([elem.x for elem in self])
            for sprite in self:
                if sprite.x == cell_width * max_x:
                    sprite.x = min_x - cell_width
            max_x -= 1
        elif vector == "right":
            min_x = min([elem.x for elem in self])
            for sprite in self:
                if sprite.x == min_x:
                    sprite.x = (max_x + 1) * cell_width
            max_x += 1


class Cell(pygame.sprite.Sprite):
    def __init__(self, cell_type, x, y):
        super().__init__(sprite_group)
        self.image = cell_images[cell_type]
        self.rect = self.image.get_rect().move(cell_width * x, cell_height * y)
        self.x, self.y = self.rect.x, self.rect.y

    def set_pos(self, x, y):
        self.x, self.y = x, y


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(hero_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(cell_width * x + 15, cell_height * y + 5)
        self.pos = (x, y)

    def move(self, x, y):
        camera.dx -= cell_width * (x - self.pos[0])
        camera.dy -= cell_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.x + self.dx
        obj.rect.y = obj.y + self.dy

    def update(self):
        self.dx = 0
        self.dy = 0


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


def intro():
    intro_text = ["Перемещение героя", "", "", "на торе"]
    fon = pygame.transform.scale(fon_image, screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_y = 50

    for line in intro_text:
        text = font.render(line, 1, 'black')
        rect = text.get_rect()
        text_y += 10
        rect.topleft = (10, text_y)
        text_y += rect.height
        screen.blit(text, rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(50)


def load_level(filename):
    text_map = open(os.path.join('data', filename), 'r')
    level_map = list(map(str.strip, text_map))
    max_width = max(map(len, level_map))
    for i in list(map(lambda line: list(line.ljust(max_width, '.')), level_map)):
        print(i)
    return list(map(lambda line: list(line.ljust(max_width, '.')), level_map))


def new_level(level):
    new_player, x, y = [None] * 3
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Cell('empty', x, y)
            elif level[y][x] == '#':
                Cell('wall', x, y)
            elif level[y][x] == '@':
                Cell('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
    return new_player, x, y


lvl_name = input('Введите имя файла: ')
try:
    map_level = load_level(lvl_name)
except Exception:
    print('Не удаётся загрузить', lvl_name)
    sys.exit()

pygame.init()
pygame.display.set_caption('Перемещение героя. Новый уровень')
screen_size = 500, 500
screen = pygame.display.set_mode(screen_size)

cell_images = {'empty': load_image('grass.png'), 'wall': load_image('box.png')}
player_image = load_image('mar.png')
fon_image = load_image('fon.jpg')
cell_width, cell_height = 50, 50

player = None
running = True
clock = pygame.time.Clock()
sprite_group, hero_group = SpriteGroup(), SpriteGroup()
intro()
camera = Camera()
hero, max_x, max_y = new_level(map_level)
camera.update()
field_x, field_y = max_x, max_y
print(field_x, field_y)


def calibration(hero_x, hero_y):
    if hero_x < 0:
        hero_x += field_x + 1
        for i in range(field_x):
            sprite_group.shift("right")
    elif hero_x > field_x:
        hero_x -= field_x
        for i in range(field_x):
            sprite_group.shift("left")
    if hero_y < 0:
        hero_y += field_y + 1
        for i in range(field_y):
            sprite_group.shift("down")
    elif hero_y > field_y:
        hero_y -= field_y
        for i in range(field_y):
            sprite_group.shift("up")
    return hero_x, hero_y


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            x_hero, y_hero = hero.pos
            if event.key == pygame.K_UP:
                if map_level[y_hero % field_y - 1][x_hero] == ".":
                    x_hero, y_hero = calibration(x_hero, y_hero)
                    y_hero -= 1
                    sprite_group.shift("up")
                    hero.move(x_hero, y_hero)
            elif event.key == pygame.K_DOWN:
                if map_level[y_hero % field_y + 1][x_hero] == ".":
                    x_hero, y_hero = calibration(x_hero, y_hero)
                    y_hero += 1
                    sprite_group.shift("down")
                    hero.move(x_hero, y_hero)
            elif event.key == pygame.K_RIGHT:
                if map_level[y_hero][x_hero % field_x + 1] == ".":
                    x_hero, y_hero = calibration(x_hero, y_hero)
                    x_hero += 1
                    sprite_group.shift("right")
                    hero.move(x_hero, y_hero)
            elif event.key == pygame.K_LEFT:
                if map_level[y_hero][x_hero % field_x - 1] == ".":
                    x_hero, y_hero = calibration(x_hero, y_hero)
                    x_hero -= 1
                    sprite_group.shift("left")
                    hero.move(x_hero, y_hero)

    screen.fill('black')
    sprite_group.draw(screen)
    hero_group.draw(screen)
    clock.tick(50)
    pygame.display.flip()
pygame.quit()
