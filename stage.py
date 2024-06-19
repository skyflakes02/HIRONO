import pyxel
import random

SCREEN_WIDTH = 415
SCREEN_HEIGHT = 250
TANK_SPEED = 2
BULLET_SPEED = 4
TANK_SPRITE_SIZE = 16
CELL_SIZE = 16
EXPLOSION_DURATION = 10

UP, RIGHT, DOWN, LEFT = 0, 1, 2, 3

EMPTY, BRICK, STONE, WATER, SEMI_CRACKED_BRICK, CRACKED_BRICK, FOREST, HOME, MIRROR_NE, MIRROR_SE, POWER_UP = range(11)

class Cell:
    def __init__(self, x, y, cell_type):
        self.x = x
        self.y = y
        self.cell_type = cell_type
        self.hits = 0
        self.exists = True

    def draw(self):
        if not self.exists:
            return
        elif self.cell_type == EMPTY:
            pyxel.blt(self.x, self.y, 0,48, 32, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == BRICK:
            pyxel.blt(self.x, self.y, 0, 0, 16, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == STONE:
            pyxel.blt(self.x, self.y, 0, 48, 16, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == WATER:
            pyxel.blt(self.x, self.y, 0, 0, 32, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == SEMI_CRACKED_BRICK:
            pyxel.blt(self.x, self.y, 0, 16, 16, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == CRACKED_BRICK:
            pyxel.blt(self.x, self.y, 0, 32, 16, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == FOREST:
            pyxel.blt(self.x, self.y, 0, 16, 32, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == HOME:
            pyxel.blt(self.x, self.y, 0, 32, 32, CELL_SIZE, CELL_SIZE, 0)
        elif self.cell_type == MIRROR_NE:
            pyxel.line(self.x + CELL_SIZE, self.y, self.x, self.y + CELL_SIZE, 4)
        elif self.cell_type == MIRROR_SE:
            pyxel.line(self.x, self.y, self.x + CELL_SIZE, self.y + CELL_SIZE, 4)
        elif self.cell_type == POWER_UP:
            pyxel.blt(self.x, self.y, 0, 0, 80, CELL_SIZE, CELL_SIZE, 0)

class Bullet:
    def __init__(self, x, y, direction, is_enemy=False):
        self.x = x
        self.y = y
        self.direction = direction
        self.exists = True
        self.is_enemy = is_enemy

    def update(self):
        if self.direction == UP:
            self.y -= BULLET_SPEED
        elif self.direction == DOWN:
            self.y += BULLET_SPEED
        elif self.direction == LEFT:
            self.x -= BULLET_SPEED
        elif self.direction == RIGHT:
            self.x += BULLET_SPEED

    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT)

class EnemyTank:
    def __init__(self):
        self.x = 21 * CELL_SIZE
        self.y = 1 * CELL_SIZE
        self.direction = DOWN
        self.bullets = []
        self.shoot_interval = 60  
        self.shoot_timer = 0
        self.hits = 0
        self.tank_type = 1

    def update(self, cells):
        if self.shoot_timer <= 0:
            self.shoot_bullet()
            self.shoot_timer = self.shoot_interval
        else:
            self.shoot_timer -= 3

        if random.random() < 0.05: 
            self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

        new_x = self.x
        new_y = self.y

        if self.direction == UP:
            new_y -= TANK_SPEED
        elif self.direction == DOWN:
            new_y += TANK_SPEED
        elif self.direction == LEFT:
            new_x -= TANK_SPEED
        elif self.direction == RIGHT:
            new_x += TANK_SPEED

        if not self.is_collision_with_cells(new_x, new_y, cells):
            self.x = new_x
            self.y = new_y

        self.x = max(0, min(self.x, SCREEN_WIDTH - TANK_SPRITE_SIZE))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - TANK_SPRITE_SIZE))

    def is_collision_with_cells(self, x, y, cells):
        for cell in cells:
            if cell.exists and cell.cell_type in {BRICK, SEMI_CRACKED_BRICK, CRACKED_BRICK, STONE, WATER, HOME, MIRROR_NE, MIRROR_SE}:
                if (x < cell.x + CELL_SIZE and
                    x + TANK_SPRITE_SIZE > cell.x and
                    y < cell.y + CELL_SIZE and
                    y + TANK_SPRITE_SIZE > cell.y):
                    return True
        return False

    def shoot_bullet(self):
        bullet_x = self.x + TANK_SPRITE_SIZE // 2 - 2
        bullet_y = self.y + TANK_SPRITE_SIZE // 2 - 2
        bullet = Bullet(bullet_x, bullet_y, self.direction, is_enemy=True)
        self.bullets.append(bullet)
        pyxel.play(0, 1)

    def draw(self):
        if self.tank_type == 1:
            tank_sprites = [(0, 48), (16, 48), (32, 48), (48, 48)]

        elif self.tank_type == 2:
            tank_sprites = [(0, 64), (16, 64), (32, 64), (48, 64)]
        pyxel.blt(self.x, self.y, 0, *tank_sprites[self.direction], TANK_SPRITE_SIZE, TANK_SPRITE_SIZE, 0) 
        for bullet in self.bullets:
            pyxel.rect(bullet.x, bullet.y, 2, 2, 8)

    def is_destroyed(self):
        return self.hits == 1