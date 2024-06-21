class EnemyTank2:
    def __init__(self):
        self.x = 0 * CELL_SIZE
        self.y = 4 * CELL_SIZE
        self.direction = RIGHT
        self.bullets = []
        self.shoot_interval = 60  
        self.shoot_timer = 0
        self.hits = 0

    def update(self, cells):
        if self.shoot_timer <= 0:
            self.shoot_bullet()
            self.shoot_timer = self.shoot_interval
        else:
            self.shoot_timer -= 0.3

        if random.random() < 0.05: 
            self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

        new_x = self.x
        new_y = self.y

        if self.direction == UP:
            new_y -= TANK_SPEED_2
        elif self.direction == DOWN:
            new_y += TANK_SPEED_2
        elif self.direction == LEFT:
            new_x -= TANK_SPEED_2
        elif self.direction == RIGHT:
            new_x += TANK_SPEED_2

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
        tank_sprites = [(0, 64), (16, 64), (32, 64), (48, 64)]
        pyxel.blt(self.x, self.y, 0, *tank_sprites[self.direction], TANK_SPRITE_SIZE, TANK_SPRITE_SIZE, 0) 
        for bullet in self.bullets:
            pyxel.blt(bullet.x, bullet.y, 0, 32, 80, 16, 16, 0)

    def is_destroyed(self):
        return self.hits == 1
