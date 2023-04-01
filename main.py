import pygame
import sys
import os

pygame.init()
clock = pygame.time.Clock()
FPS = 120

pygame.display.set_caption('Pygame Window')

WINDOW_SIZE = (1980, 1080)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface((990/2, 540/2), pygame.SRCALPHA)  # все что происходит на display увеличивается до WINDOW_SIZE

start_x = 500
start_y = 250

def read_txt(path):
    with open(path, "r") as file:
        rows = file.read().split('\n')
        m = [t.split(',') for t in rows]
    return m


MAP = read_txt(os.getcwd()+'/gamemap.txt')
tile_0 = pygame.image.load(os.getcwd() + '/tiles/tile_0.png')
tile_1 = pygame.image.load(os.getcwd() + '/tiles/tile_1.png')
tile_2 = pygame.image.load(os.getcwd() + '/tiles/tile_2.png')
tile_3 = pygame.image.load(os.getcwd() + '/tiles/tile_3.png')
tile_4 = pygame.image.load(os.getcwd() + '/tiles/tile_4.png')
tile_5 = pygame.image.load(os.getcwd() + '/tiles/tile_5.png')
tile_6 = pygame.image.load(os.getcwd() + '/tiles/tile_6.png')
tile_7 = pygame.image.load(os.getcwd() + '/tiles/tile_7.png')
tile_8 = pygame.image.load(os.getcwd() + '/tiles/tile_8.png')
door = pygame.image.load(os.getcwd() + '/tiles/door.png')
door_rect = pygame.Rect(0, 0, 64, 80)


def draw_map():
    global door_rect
    tiles = []
    y = 0
    for row in MAP:
        x = 0
        for tile in row:
            if tile == '1':
                display.blit(tile_0, (x * 16 - scroll[0], y * 16 - scroll[1]))
            elif tile == '2':
                display.blit(tile_1, (x * 16 - scroll[0], y * 16 - scroll[1]))
            elif tile == '3':
                display.blit(tile_2, (x * 16 - scroll[0], y * 16 - scroll[1]))
            elif tile == '4':
                display.blit(tile_3, (x * 16 - scroll[0], y * 16 - scroll[1]))
            elif tile == '5':
                display.blit(tile_4, (x * 16 - scroll[0], y * 16 - scroll[1]))
            elif tile == '6':
                display.blit(tile_5, (x * 16 - scroll[0], y * 16 - scroll[1]))
            elif tile == '7':
                display.blit(tile_6, (x * 16 - scroll[0], y * 16 - scroll[1]))
            elif tile == '8':
                display.blit(tile_7, (x * 16 - scroll[0], y * 16 - scroll[1]))
            elif tile == '9':
                display.blit(tile_8, (x * 16 - scroll[0], y * 16 - scroll[1]))
            elif tile == '-1':
                display.blit(door, (x * 16 - scroll[0], y * 16 - scroll[1]))
                door_rect = pygame.Rect(x * 16, y * 16, 64, 80)
            if tile != '0' and tile != '5' and tile != '-1':
                tiles.append(pygame.Rect(x * 16, y * 16, 16, 16))
            x += 1
        y += 1
    return tiles


player_img = pygame.image.load(os.getcwd()+'/player_animation/idle/idle_0.png')


class Player:
    def __init__(self, img, x, y):
        self.img = img
        self.rect = pygame.Rect(x, y, self.img.get_width(), self.img.get_height())

        self.move_left = False
        self.move_right = False
        self.move_val = 2

        self.y_momentum = 0
        self.jump_height = -7
        self.air_timer = 0

        self.dash_mode = False
        self.dash_shadow = [(start_x, start_y), (start_x, start_y), (start_x, start_y), (start_x, start_y)]
        self.img_copy_list = [self.img, self.img, self.img, self.img]

        self.collision_type = {"left": False, 'right': False, "top": False, 'bottom': False}

        self.animation_frames = {}
        self.animation_db = {"run": self.load_animation(os.getcwd()+'/player_animation/run', [7, 14, 7, 14]),
                             "idle": self.load_animation(os.getcwd()+'/player_animation/idle', [40, 40])}

        self.action = 'idle'
        self.flip = False
        self.frame = 0

    def load_animation(self, path, duration):
        animation_frame_data = []
        img_name = os.listdir(path)
        for frame in range(len(duration)):
            animation_image = pygame.image.load(path + '/' + img_name[frame])
            self.animation_frames[img_name[frame][:-4]] = animation_image.copy()
            for i in range(duration[frame]):
                animation_frame_data.append(img_name[frame][:-4])

        return animation_frame_data

    def change_action(self, new_action):
        if self.action != new_action:
            self.action = new_action
            self.frame = 0

    def get_hit_list(self, tiles):
        hit_list = []
        for tile in tiles:
            if self.rect.colliderect(tile):
                hit_list.append(tile)

        return hit_list

    def collision_check(self, tiles, movement):
        self.collision_type = {"left": False, 'right': False, "top": False, "bottom": False}
        self.rect.x += movement[0]
        hit_list = self.get_hit_list(tiles)
        for tile in hit_list:
            if movement[0] > 0:
                self.rect.right = tile.left
                self.collision_type["right"] = True
            elif movement[0] < 0:
                self.rect.left = tile.right
                self.collision_type["left"] = True
        self.rect.y += movement[1]
        hit_list = self.get_hit_list(tiles)
        for tile in hit_list:
            if movement[1] > 0:
                self.rect.bottom = tile.top
                self.collision_type["bottom"] = True
            elif movement[1] < 0:
                self.rect.top = tile.bottom
                self.collision_type["top"] = True

    def move(self, tiles):
        movement = [0, 0]
        if self.move_left:
            movement[0] = -self.move_val
        elif self.move_right:
            movement[0] = self.move_val

        self.y_momentum += 0.2
        if self.y_momentum > 5:
            self.y_momentum = 5
        movement[1] = self.y_momentum

        if movement[0] > 0:
            self.change_action("run")
            self.flip = False

        elif movement[0] < 0:
            self.change_action('run')
            self.flip = True

        if movement[0] == 0:
            self.change_action('idle')

        if movement[1] < 0:
            self.img = pygame.image.load(os.getcwd() +  '/player_animation/jump/jump_0.png')
        elif movement[1] > 2 and not self.collision_type['bottom']:
            self.img = pygame.image.load(os.getcwd() + '/player_animation/jump/jump_1.png')

        self.collision_check(tiles, movement)
        if self.collision_type['bottom']:
            self.y_momentum = 0
            self.air_timer = 0
        else:
            self.air_timer += 1

        if self.collision_type['top']:
            self.y_momentum = 0

        if self.rect.colliderect(door_rect):
            print('lol')

    def dash(self):
        if self.move_val > 2:
            self.move_val -= 0.3
            for i in range(4):
                display.blit(pygame.transform.flip(self.img_copy_list[i], self.flip, False), (self.dash_shadow[i][0] - scroll[0], self.dash_shadow[i][1] - scroll[1]))

        if self.dash_mode:
            self.move_val = 10
            self.dash_mode = False

    def update_dash_shadow(self):
        self.dash_shadow[0] = self.dash_shadow[1]
        self.dash_shadow[1] = self.dash_shadow[2]
        self.dash_shadow[2] = self.dash_shadow[3]
        self.dash_shadow[3] = (self.rect.x, self.rect.y)

        img_copy = self.img.copy()
        n = 0
        for i in range(50, 201, 50):
            img_copy.set_alpha(i)
            self.img_copy_list[n] = img_copy
            img_copy = self.img.copy()
            n += 1


    def draw(self):
        display.blit(pygame.transform.flip(self.img, self.flip, False), (self.rect.x - scroll[0], self.rect.y - scroll[1]))


player = Player(player_img, start_x, start_y)

true_scroll = [0, 0]
cam_x_speed = 30
cam_y_speed = 20

while True:

    true_scroll[0] += (player.rect.x - true_scroll[0] - display.get_width()/2 - player.img.get_width()/2)/cam_x_speed
    true_scroll[1] += (player.rect.y - true_scroll[1] - display.get_height()/2 - player.img.get_height()/2-10)/cam_y_speed

    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    display.fill((15, 58, 172))

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_d:
                player.move_right = True
            if event.key == pygame.K_a:
                player.move_left = True
            if event.key == pygame.K_SPACE and player.air_timer < 6:
                player.y_momentum += player.jump_height
            if event.key == pygame.K_k:
                player.dash_mode = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                player.move_right = False
            if event.key == pygame.K_a:
                player.move_left = False

    tiles = draw_map()

    player.frame += 1
    if player.frame >= len(player.animation_db[player.action]):
        player.frame = 0

    player_img_id = player.animation_db[player.action][player.frame]
    player.img = player.animation_frames[player_img_id]

    player.update_dash_shadow()
    player.dash()
    player.move(tiles)
    player.draw()

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    clock.tick(FPS)
