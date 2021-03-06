from pygame.key import start_text_input
from pygame.locals import K_RIGHT, K_SPACE, KEYDOWN, KEYUP, K_LEFT, K_ESCAPE
from pygame import Color, Vector2
from src.entities.shield import Shield
from src.entities.enemy import Enemy
from src.constants import BLACK, ENEMY_OFFSET, ENEMY_SPEED, EXTRA_ENEMIES_PER_LEVEL, EXTRA_ENEMY_SPEED_PER_LEVEL, INITIAL_NUM_ENEMIES, MAX_PER_ROW, SCREEN_H, SCREEN_W, WHITE, NUMBER_OF_SHIELDS
from src.entities.player import Player
import random
import pygame

class Game:

    entities: "list"

    def __init__(self):
        self.restart_game()

    def restart_game(self):
        print('Start a new game.')
        self.entities = []
        self.player = Player()  # object
        self.entities.append(self.player)
        self.num_active_enemies = 0
        self.level = 0
        self.start_next_level()

    def start_next_level(self):
        print(f"Start level {self.level}")
        self.generate_enemies()
        self.generate_shield()
        self.level += 1

    def generate_enemies(self):
        extra_enemies = self.level * EXTRA_ENEMIES_PER_LEVEL
        extra_enemy_speed = self.level * EXTRA_ENEMY_SPEED_PER_LEVEL
        total_enemy_count = extra_enemies + INITIAL_NUM_ENEMIES

        self.num_active_enemies = total_enemy_count
        curr_enemy_speed = extra_enemy_speed + ENEMY_SPEED

        col_gap = SCREEN_W // MAX_PER_ROW
        col, row = 0, 0
        colors = ['green', 'blue', 'red', 'pink', 'yellow']
        for _ in range(total_enemy_count):
            enemy_corrds = Vector2(ENEMY_OFFSET+(col*col_gap), ENEMY_OFFSET+row*col_gap)
            color_idx = random.randint(0, len(colors)-1)
            new_enemy = Enemy(enemy_corrds, curr_enemy_speed, f"res/enemy-{colors[color_idx]}.png")
            self.entities.append(new_enemy)
            col += 1
            if col >= MAX_PER_ROW:
                col = 0
                row += 1


    def generate_shield(self):
        n = NUMBER_OF_SHIELDS + 1
        for i in range(1, n):
            self.entities.append(Shield(i*SCREEN_W/n, 350))

    def handle_input(self, events):
        for event in events:
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    self.player.move_left()
                elif event.key == K_RIGHT:
                    self.player.move_right()
                elif event.key == K_SPACE:
                    if self.player.expired:
                        self.restart_game()
                    else:
                        self.player.shoot()
                elif event.key == K_ESCAPE:
                    print("Game exited")
                    pygame.quit()
                    exit()
                    
            if event.type == KEYUP:
                if event.key == K_LEFT and self.player.move_direction < 0:
                    self.player.stop_moving()
                if event.key == K_RIGHT and self.player.move_direction > 0:
                    self.player.stop_moving()

    def update(self,delta):
        for i in range(len(self.entities) - 1, -1, -1):
            obj = self.entities[i]
            # delete the enemy that has been shot
            if obj.expired:
                if isinstance(obj, Enemy):
                    self.num_active_enemies -= 1
                del self.entities[i]

            # Execute entity logic
            obj.tick(delta, self.entities)
            obj.move(delta)

            Enemy.random_enemy_shoot(self.entities, self.num_active_enemies, delta, NUM_ENEMIES_SHOOT=1)

            if self.num_active_enemies == 0:
                self.start_next_level()

    def render_text(self, display, font, text: str, color: Color, position: Vector2):
        surface = font.render(text, True, color)
        display.blit(surface, position)

    def render(self, display, font):
        display.fill(BLACK)
        self.render_text(display, font, "Space Invaders", WHITE, (SCREEN_W//2-70,25))
        if not self.player.expired:
            # loop through each entity and render it
            for o in self.entities:
                o.render(display)
            self.render_text(display, font, f"Level: {self.level}", WHITE, (50,50))                
            self.render_text(display, font, f"health: {self.player.health}", WHITE, (SCREEN_W-150,50))
        else:
            # player is killed
            self.render_text(display, font, "Game Over. Press SPACE to start again!", WHITE, (SCREEN_W//2-200, SCREEN_H//2-50))
            self.render_text(display, font, f"Score: {self.level}", WHITE, (SCREEN_W//2-50, SCREEN_H//2+50))
            