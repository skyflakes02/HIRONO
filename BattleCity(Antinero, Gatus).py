import pyxel
import random
from stage import Cell, Bullet, EnemyTank

UP, RIGHT, DOWN, LEFT = 0, 1, 2, 3

EMPTY, BRICK, STONE, WATER, SEMI_CRACKED_BRICK, CRACKED_BRICK, FOREST, HOME, MIRROR_NE, MIRROR_SE, POWER_UP = range(11)
    
class BattleCity:
    def __init__(self):
        pyxel.init(415, 250, title="Battle City")
        pyxel.load("battlecity.pyxres")
        self.tank_x = 4 * 16
        self.tank_y = 15 * 16
        self.tank_direction = UP
        self.player_bullets = []
        self.enemy_tank = EnemyTank()
        self.enemy_tank.hits = 0
        self.enemy_tank_count = 0  
        self.cells = self.create_cells()
        self.create_corner_mirrors()
        self.game_over = False
        self.game_won = False
        self.player_lives = 2  
        self.shoot_interval = 15  
        self.shoot_timer = 0
        self.power_up_active = False
    #
        pyxel.sound(0).set("a2", "t", "7", "n", 3)  # Player shooting sound
        pyxel.sound(1).set("c3", "t", "6", "f", 5)  # Enemy shooting
        pyxel.sound(2).set("e2g2c3", "t", "7", "n",2)  # Game over sound
        pyxel.sound(3).set("c2", "t", "7", "n", 3)  # Bullet hitting a target
        pyxel.sound(4).set("f2a2c3f3", "t", "7", "n", 2)  # Game won sound

        pyxel.run(self.update, self.draw)
    
    def create_cells(self):
        cells = []
        home_created = False
        mirror_cells_placed = False 
        power_up_count = 0
        
        for y in range(10, 250, 16):
            for x in range(0, 415, 16):
                cell_type = EMPTY

                #if x == 0 and y == 250 - 16:
                    #cell_type = EMPTY

                #elif x == 415 - 16 and y == 0:
                    #cell_type = EMPTY

                if not home_created:
                    cell_type = HOME
                    home_created = True

                elif not mirror_cells_placed and (x == 16 or x == 415 - 2 * 16) and (y == 16 or y == 250 - 2 * 16):
                    cell_type = MIRROR_NE if x == 16 and y == 16 else MIRROR_SE
                    mirror_cells_placed = True 

                elif random.random() < 0.1 and power_up_count < 2: 
                    cell_type = POWER_UP
                    power_up_count += 1

                elif self.tank_x == max(0, min(self.tank_x, 415 - 16)) and self.tank_y == max(0, min(self.tank_y, 250 - 16)):
                    cell_type = EMPTY
                
                elif self.is_mirror_position(x, y):
                    cell_type = EMPTY

                elif random.random() < 0.7: 
                    cell_type = EMPTY

                else:
                    cell_type = random.choice([BRICK, STONE, WATER, FOREST])

                cells.append(Cell(x, y, cell_type))

        return cells
    
    def draw_explosion(self, x, y):
        pyxel.blt(x, y, 0, 16, 80, 16, 16, 0)
    
    def is_tank_position(self, x, y):
        tank_positions = [
            (4 * 16, 15 * 16),  # Player tank starting position
            (21 * 16, 1 * 16)   # Enemy tank starting position
        ]
        for pos in tank_positions:
            if x == pos[0] and y == pos[1]:
                return True
        return False

    def is_mirror_position(self, x, y):
        mirror_positions = [
            (16, 16),               # MIRROR_NE position
            (415 - 2 * 16, 16),     # MIRROR_SE position
            (16, 250 - 2 * 16),     # MIRROR_SE position
            (415 - 2 * 16, 250 - 2 * 16)  # MIRROR_NE position
        ]
        for pos in mirror_positions:
            if x == pos[0] and y == pos[1]:
                return True
        return False

    def create_corner_mirrors(self):
        self.cells.append(Cell(16, 16, MIRROR_NE))    
        self.cells.append(Cell(415 - 2 * 16, 16, MIRROR_SE))  
        self.cells.append(Cell(16, 250 - 2 * 16, MIRROR_SE))  
        self.cells.append(Cell(415 - 2 * 16, 250 - 2 * 16, MIRROR_NE))

    def is_position_valid(self, x, y, cells):
        for cell in cells:
            if cell.x == x and cell.y == y:
                return False
        return True

    def update(self):
        new_tank_x = self.tank_x 
        new_tank_y = self.tank_y

        if self.power_up_active:
            self.player_lives += 1

        if pyxel.btn(pyxel.KEY_W):
            new_tank_y -= 2 
            self.tank_direction = UP
        elif pyxel.btn(pyxel.KEY_UP):
            new_tank_y -= 2 
            self.tank_direction = UP
        elif pyxel.btn(pyxel.KEY_S):
            new_tank_y += 2 
            self.tank_direction = DOWN
        elif pyxel.btn(pyxel.KEY_DOWN):
            new_tank_y += 2 
            self.tank_direction = DOWN
        elif pyxel.btn(pyxel.KEY_A):
            new_tank_x -= 2 
            self.tank_direction = LEFT
        elif pyxel.btn(pyxel.KEY_LEFT):
            new_tank_x -= 2 
            self.tank_direction = LEFT
        elif pyxel.btn(pyxel.KEY_D):
            new_tank_x += 2 
            self.tank_direction = RIGHT
        elif pyxel.btn(pyxel.KEY_RIGHT):
            new_tank_x += 2 
            self.tank_direction = RIGHT
                
        if not self.is_collision_with_cells(new_tank_x, new_tank_y):
            self.tank_x = new_tank_x
            self.tank_y = new_tank_y

        if pyxel.btn(pyxel.KEY_SPACE):
            if self.shoot_timer <= 0:
                self.shoot_bullet()
                self.shoot_timer = self.shoot_interval
        if self.shoot_timer > 0:
            self.shoot_timer -= 3

        self.tank_x = max(0, min(self.tank_x, 415 - 16))
        self.tank_y = max(0, min(self.tank_y, 250 - 16))

        for bullet in self.player_bullets:
            if (bullet.x + 2 >= self.enemy_tank.x and bullet.x <= self.enemy_tank.x + 16 and 
                bullet.y + 2 >= self.enemy_tank.y and bullet.y <= self.enemy_tank.y + 16):
                self.enemy_tank.hits += 1
                bullet.exists = False
                pyxel.play(0, 3)
                if self.enemy_tank.is_destroyed():
                    self.enemy_tank_count += 1
                    if self.enemy_tank_count < 3: 
                        self.enemy_tank = EnemyTank()
                    else:
                        self.game_won = True
                        pyxel.play(0, 4)

        for bullet in self.player_bullets:
            bullet.update()

        self.handle_bullet_collision()

        self.player_bullets = [bullet for bullet in self.player_bullets if bullet.exists and not bullet.is_off_screen()]

        self.enemy_tank.update(self.cells)

        for bullet in self.enemy_tank.bullets:
            bullet.update()

        for bullet in self.enemy_tank.bullets:
            if (bullet.x + 2 >= self.tank_x and bullet.x <= self.tank_x + 16 and 
                bullet.y + 2 >= self.tank_y and bullet.y <= self.tank_y + 16):
                self.player_lives -= 1
                if self.player_lives <= 0:
                    self.game_over = True
                    pyxel.play(0, 2)
                else:
                    self.tank_x = 4 * 16
                    self.tank_y = 15 * 16
                    self.tank_direction = UP

        self.enemy_tank.bullets = [bullet for bullet in self.enemy_tank.bullets if bullet.exists and not bullet.is_off_screen()]

        if pyxel.btn(pyxel.KEY_N):
            self.reset_game()

        if self.game_over or self.game_won:
            if pyxel.btn(pyxel.KEY_Q):
                pyxel.quit()
            pyxel.stop()
        else:
            pyxel.playm(0, loop=True)

    def is_collision_with_cells(self, x, y):
        for cell in self.cells:
            if cell.exists and cell.cell_type in {BRICK, STONE, WATER, SEMI_CRACKED_BRICK, CRACKED_BRICK, HOME, MIRROR_NE, MIRROR_SE}:
                if (x < cell.x + 16 and
                    x + 16 > cell.x and
                    y < cell.y + 16 and
                    y + 16 > cell.y):
                    if cell.cell_type == POWER_UP:
                        cell.cell_type = EMPTY
                    return True
        return False

    def update_bullets(self):
        for bullet in self.player_bullets:
            bullet.update()
            if bullet.is_off_screen():
                bullet.exists = False

        for bullet in self.player_bullets:
            if bullet.exploding:
                bullet.explosion_timer += 1
                if bullet.explosion_timer > 10:
                    self.player_bullets.remove(bullet)
                continue

            if bullet.direction == UP:
                bullet.y -= 2
            elif bullet.direction == DOWN:
                bullet.y += 2
            elif bullet.direction == LEFT:
                bullet.x -= 2
            elif bullet.direction == RIGHT:
                bullet.x += 2

            if bullet.x < 0 or bullet.x > 415 or bullet.y < 0 or bullet.y > 250:
                self.player_bullets.remove(bullet)
                continue
            
            cell_x = bullet.x // 16
            cell_y = bullet.y // 16
            if self.cells[cell_y][cell_x] == 1:  # Assume 1 represents bricks
                self.cells[cell_y][cell_x] = 0
                self.start_explosion(bullet)
            elif self.cells[cell_y][cell_x] == 4:  # Mirror cell
                if bullet.direction == UP:
                    bullet.direction = DOWN
                elif bullet.direction == DOWN:
                    bullet.direction = UP
                elif bullet.direction == LEFT:
                    bullet.direction = RIGHT
                elif bullet.direction == RIGHT:
                    bullet.direction = LEFT

            if self.enemy_tank.x <= bullet.x <= self.enemy_tank.x + 16 and self.enemy_tank.y <= bullet.y <= self.enemy_tank.y + 16:
                self.enemy_tank.hits += 1
                self.start_explosion(bullet)
                if self.enemy_tank.hits >= 3:
                    self.enemy_tank_count += 1
                    if self.enemy_tank_count >= 10:
                        self.game_won = True
                    else:
                        self.enemy_tank = EnemyTank()
                pyxel.play(1, 3)


        self.player_bullets = [bullet for bullet in self.player_bullets if bullet.exists]

        for bullet in self.enemy_tank.bullets:
            bullet.update()
            if bullet.is_off_screen():
                bullet.exists = False

        self.enemy_tank.bullets = [bullet for bullet in self.enemy_tank.bullets if bullet.exists]

    def start_explosion(self, bullet):
        bullet.exploding = True
        bullet.explosion_timer = 0
        pyxel.play(2, 2)

    def update_enemy_tank(self):
        self.enemy_tank.update(self.cells)

    def check_collisions(self):
        for bullet in self.player_bullets:
            if not bullet.exists:
                continue

            for cell in self.cells:
                if cell.exists and cell.cell_type in {BRICK, SEMI_CRACKED_BRICK, CRACKED_BRICK, STONE, HOME}:
                    if (bullet.x < cell.x + 16 and
                        bullet.x + 2 > cell.x and
                        bullet.y < cell.y + 16 and
                        bullet.y + 2 > cell.y):
                        bullet.exists = False
                        cell.hits += 1
                        pyxel.play(0, 3)
                        if cell.cell_type == BRICK and cell.hits == 1:
                            cell.cell_type = SEMI_CRACKED_BRICK
                        elif cell.cell_type == BRICK and cell.hits == 2:
                            cell.cell_type = CRACKED_BRICK
                        elif cell.cell_type == SEMI_CRACKED_BRICK and cell.hits == 1:
                            cell.cell_type = CRACKED_BRICK
                        elif cell.cell_type == CRACKED_BRICK and  cell.hits == 1:
                            cell.exists = False
                        elif cell.cell_type == STONE and cell.hits == 2:
                            cell.exists = False
                        elif cell.cell_type == POWER_UP:
                            cell.exists = False
                        elif cell.cell_type == HOME:
                            cell.exists = False
                            self.game_over = True
                        break

            if (bullet.x < self.enemy_tank.x + 16 and
                bullet.x + 2 > self.enemy_tank.x and
                bullet.y < self.enemy_tank.y + 16 and
                bullet.y + 2 > self.enemy_tank.y):
                bullet.exists = False
                self.enemy_tank.hits += 1
                pyxel.play(0, 3)
                if self.enemy_tank.is_destroyed():
                    self.enemy_tank_count += 1
                    if self.enemy_tank_count == 1:
                        self.enemy_tank = EnemyTank() 
                        self.enemy_tank.tank_type += 1
                        
                    else:
                        self.game_won = True

        for bullet in self.enemy_tank.bullets:
            if not bullet.exists:
                continue

            if (bullet.x < self.tank_x + 16 and
                bullet.x + 2 > self.tank_x and
                bullet.y < self.tank_y + 16 and
                bullet.y + 2 > self.tank_y):
                bullet.exists = False
                self.player_lives -= 1
                pyxel.play(0, 3)
                if self.player_lives == 0:
                    self.game_over = True

    def handle_bullet_collision(self):
        for bullet in self.player_bullets:
            for cell in self.cells:
                if cell.exists:
                    if (bullet.x + 2 >= cell.x and bullet.x <= cell.x + 16 and 
                        bullet.y + 2 >= cell.y and bullet.y <= cell.y + 16):
                        if cell.cell_type == BRICK:
                            cell.cell_type = SEMI_CRACKED_BRICK
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == SEMI_CRACKED_BRICK:
                            cell.cell_type = CRACKED_BRICK
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == CRACKED_BRICK:
                            cell.exists = False
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == STONE:
                            bullet.exists = False
                        elif cell.cell_type == HOME:
                            cell.exists = False
                            bullet.exists = False
                            self.game_over = True
                            pyxel.play(0, 2)
                        elif cell.cell_type == MIRROR_NE:
                            if bullet.direction == UP:
                                bullet.direction = RIGHT
                            elif bullet.direction == DOWN:
                                bullet.direction = LEFT
                            elif bullet.direction == LEFT:
                                bullet.direction = DOWN
                            elif bullet.direction == RIGHT:
                                bullet.direction = UP
                        elif cell.cell_type == MIRROR_SE:
                            if bullet.direction == UP:
                                bullet.direction = LEFT
                            elif bullet.direction == DOWN:
                                bullet.direction = RIGHT
                            elif bullet.direction == LEFT:
                                bullet.direction = UP
                            elif bullet.direction == RIGHT:
                                bullet.direction = DOWN

        for bullet in self.enemy_tank.bullets:
            for cell in self.cells:
                if cell.exists:
                    if (bullet.x + 2 >= cell.x and bullet.x <= cell.x + 16 and 
                        bullet.y + 2 >= cell.y and bullet.y <= cell.y + 16):
                        if cell.cell_type == BRICK:
                            cell.cell_type = SEMI_CRACKED_BRICK
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == SEMI_CRACKED_BRICK:
                            cell.cell_type = CRACKED_BRICK
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == CRACKED_BRICK:
                            cell.exists = False
                            bullet.exists = False
                            pyxel.play(0, 3)
                        elif cell.cell_type == STONE:
                            bullet.exists = False
                        elif cell.cell_type == HOME:
                            cell.exists = False
                            bullet.exists = False
                            self.game_over = True
                            pyxel.play(0, 2)
                        elif cell.cell_type == MIRROR_NE:
                            if bullet.direction == UP:
                                bullet.direction = RIGHT
                            elif bullet.direction == DOWN:
                                bullet.direction = LEFT
                            elif bullet.direction == LEFT:
                                bullet.direction = DOWN
                            elif bullet.direction == RIGHT:
                                bullet.direction = UP
                        elif cell.cell_type == MIRROR_SE:
                            if bullet.direction == UP:
                                bullet.direction = LEFT
                            elif bullet.direction == DOWN:
                                bullet.direction = RIGHT
                            elif bullet.direction == LEFT:
                                bullet.direction = UP
                            elif bullet.direction == RIGHT:
                                bullet.direction = DOWN

    def shoot_bullet(self):
        bullet_x = self.tank_x + 16 // 2 - 2
        bullet_y = self.tank_y + 16 // 2 - 2
        if self.tank_direction == UP:
            bullet_y = self.tank_y
        elif self.tank_direction == DOWN:
            bullet_y = self.tank_y + 16
        elif self.tank_direction == LEFT:
            bullet_x = self.tank_x
        elif self.tank_direction == RIGHT:
            bullet_x = self.tank_x + 16

        bullet = Bullet(bullet_x, bullet_y, self.tank_direction)
        self.player_bullets.append(bullet)
        pyxel.play(0, 0)


    def draw(self):
        pyxel.cls(0)

        for cell in self.cells:
            cell.draw()

        self.enemy_tank.draw()

        pyxel.blt(self.tank_x, self.tank_y, 0, 0, 0, 16, 16, 0)
        for bullet in self.player_bullets:
            for bullet in self.player_bullets:
                pyxel.circ(bullet.x, bullet.y, 2, 12)

            for bullet in self.enemy_tank.bullets:
                pyxel.circ(bullet.x, bullet.y, 2, 4)

        pyxel.text(5, 2, f"LIVES: {self.player_lives}", 8)
        pyxel.text(65, 2, f"KILLS: {self.enemy_tank_count}", 8)

        if self.game_over:
            pyxel.cls(0)
            pyxel.text(185, 95, "GAME OVER", pyxel.frame_count % 16)
            pyxel.text(165, 165, "PRESS 'N' TO RESTART", pyxel.frame_count % 16)
            pyxel.text(170, 180, "PRESS 'Q' TO QUIT", pyxel.frame_count % 16)
            pyxel.play(2, 2)
        elif self.game_won:
            pyxel.cls(0)
            pyxel.text(185, 95, "YOU WON!", pyxel.frame_count % 16)
            pyxel.text(165, 165, "PRESS 'N' TO RESTART", pyxel.frame_count % 16)
            pyxel.text(170, 180, "PRESS 'Q' TO QUIT", pyxel.frame_count % 16)
            pyxel.play(2, 4)

    def reset_game(self):
        self.tank_x = 4 * 16
        self.tank_y = 15 * 16
        self.enemy_tank.x = 21 * 16
        self.enemy_tank.y = 1 * 16
        self.tank_direction = UP
        self.enemy_tank_direction = DOWN
        self.player_bullets = []
        self.enemy_tank = EnemyTank()
        self.enemy_tank.hits = 0
        self.enemy_tank_count = 0
        self.power_up_active = False

        for cell in self.cells:
            if cell.cell_type != MIRROR_NE and cell.cell_type != MIRROR_SE:
                cell.exists = True
                if cell.cell_type == HOME:
                    cell.hits = 0
                elif cell.cell_type in {SEMI_CRACKED_BRICK, CRACKED_BRICK}:
                    cell.cell_type = BRICK
                    
            self.game_over = False
            self.game_won = False
            self.player_lives = 2
            self.shoot_timer = 0

BattleCity()

