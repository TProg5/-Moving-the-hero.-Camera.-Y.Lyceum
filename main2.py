import os
import sys

import pygame

from ClassCamera import Camera


pygame.init()
size = width, height = 800, 600
screen = pygame.display.set_mode(size)

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join("data", name)
    if not os.path.isfile(fullname):
        print(f"Не найдено '{fullname}'")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):

    try:
        filepath = os.path.join("data", filename)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Ошибка: файл '{filepath}' не найден.")
        with open(filepath, "r") as mapFile:
            level_map = [line.strip() for line in mapFile]
        
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, "."), level_map))
    
    except FileNotFoundError as e:
        print(e)
        sys.exit()


clock = pygame.time.Clock()

FPS = 50


def start_screen():
    intro_text = ["Нажми на любую кнопку, чтобы продолжить"]

    fon = pygame.transform.scale(load_image("fon.jpg"), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color("black"))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {"wall": load_image("box.png"), "empty": load_image("grass.png")}
player_image = load_image("mario.png")

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, type):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.type = type
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5
        )

    def update_pos(self, coords):
        for_check = [
            i
            for i in all_sprites.sprites()
            if isinstance(i, Tile) and i.type == "grass"
        ]
        true_position, last_x, last_y = False, self.rect.x, self.rect.y
        self.rect.x = last_x + coords[0]
        self.rect.y = last_y + coords[1]

        for i in for_check:
            if pygame.sprite.collide_mask(self, i):
                true_position = True
                break

        if not true_position:
            self.rect.x = last_x
            self.rect.y = last_y


def generate_level(level):
    new_player, player_x, player_y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == ".":
                Tile("empty", x, y, "grass")
            elif level[y][x] == "#":
                Tile("wall", x, y, "box")
            elif level[y][x] == "@":
                Tile("empty", x, y, "grass")
                player_x, player_y = x, y

    new_player = Player(player_x, player_y)
    return new_player, player_x, player_y


def handle_movement(keys, player):
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.update_pos((+50, 0))
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.update_pos((-50, 0))
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.update_pos((0, +50))
    elif keys[pygame.K_UP] or keys[pygame.K_w]:
        player.update_pos((0, -50))


if __name__ == "__main__":
    start_screen()
    player, level_x, level_y = generate_level(load_level('level_new.txt'))

    camera = Camera(width, height)

    running = True
    while running:
        screen.fill((0, 0, 0))  # Очистка экрана
        keys = pygame.key.get_pressed()  # Получение состояния клавиш

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if any(keys):
                handle_movement(keys, player)

        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
            
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
