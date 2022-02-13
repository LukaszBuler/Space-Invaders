import pygame, sys
from player import Player
import przeszkoda
from alien import Alien, Extra
from random import choice, randint
from laser import Laser
from button import Button


class Game:
    def __init__(self):
        # Player setup
        player_sprite = Player((screen_width / 2, screen_height), screen_width, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        # Health and score setup
        self.lives = 3
        self.live_surf = pygame.image.load("images/heart.png").convert_alpha()
        self.lives_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 3 + 20)
        self.score = 0
        self.font = pygame.font.SysFont("copperplategothic", 20)

        # Przeszkoda setup
        self.shape = przeszkoda.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacle_x_positions, x_start=screen_width / 15, y_start=480)

        # Alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_setup(rows=6, cols=8)
        self.alien_direction = 1
        self.alien_lasers = pygame.sprite.Group()

        # Extra setup
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400, 800)

        # Audio
        music = pygame.mixer.Sound("music/Alien-Sky.mp3")
        music.set_volume(0.2)
        music.play(loops=-1)
        self.laser_sound = pygame.mixer.Sound("music/SpaceLaserShot.mp3")
        self.laser_sound.set_volume(0.05)
        self.explosion_sound = pygame.mixer.Sound("music/Explosion.wav")
        self.explosion_sound.set_volume(0.2)

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == "x":
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = przeszkoda.Block(self.block_size, (241, 79, 80), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols, x_distance=60, y_distance=48, x_offset=70, y_offset=100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset
                if row_index == 0:
                    alien_sprite = Alien("red", x, y)
                elif 1 <= row_index <= 2:
                    alien_sprite = Alien("purple", x, y)
                else:
                    alien_sprite = Alien("green", x, y)
                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_move_down(2)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(2)

    def alien_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites() and self.lives > 0 and flaga == 1:
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, -6, screen_height)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(["right", "left"]), screen_width))
            self.extra_spawn_time = randint(400, 800)

    def collisions_checks(self):
        # player laser
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # alien collisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion_sound.play()

                # extra collisions
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    laser.kill()
                    self.score += 500

        # alien laser
        if self.alien_lasers:
            for laser in self.alien_lasers:
                # obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # player collisions
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pass

        # aliens
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)

                if pygame.sprite.spritecollide(alien, self.player, False):
                    self.lives = 0

    def display_lives(self):
        for live in range(self.lives):
            x = self.lives_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf, (x - 10, 8))

    def display_score(self):
        score_surf = self.font.render(f"score: {self.score}", False, "white")
        score_rect = score_surf.get_rect(topleft=(10, 0))
        screen.blit(score_surf, score_rect)

    def victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render("You won!", False, "white")
            victory_rect = victory_surf.get_rect(center=(screen_width / 2, screen_height / 2))
            screen.blit(victory_surf, victory_rect)

    def lost_message(self):
        if self.lives == 0:
            lost_surf = self.font.render("You lost!", False, "white")
            lost_rect = lost_surf.get_rect(center=(screen_width / 2, screen_height / 2))
            screen.blit(lost_surf, lost_rect)

    def run(self):
        if self.lives > 0 and flaga == 1:
            self.player.update()
            self.aliens.update(self.alien_direction)
            self.alien_lasers.update()
            self.extra.update()

            self.alien_position_checker()
            self.extra_alien_timer()
            self.collisions_checks()

            self.player.draw(screen)
            self.player.sprite.lasers.draw(screen)
            self.blocks.draw(screen)
            self.aliens.draw(screen)
            self.alien_lasers.draw(screen)
            self.extra.draw(screen)
            self.display_lives()
            self.display_score()
            self.victory_message()
        else:
            self.lost_message()


class Background:
    def __init__(self):
        self.background = pygame.image.load("images/background.png").convert_alpha()
        self.background = pygame.transform.scale(self.background, (screen_width, screen_height))

    def draw(self):
        self.background.set_alpha(50)
        screen.blit(self.background, (0, 0))


if __name__ == '__main__':
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()
    background = Background()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    # Menu
    flaga = 0
    flaga1 = 0
    bg_menu = pygame.image.load("images/background-menu.png").convert_alpha()
    bg_menu = pygame.transform.scale(bg_menu, (screen_width, screen_height))
    bg_menu.set_alpha(50)

    while True:
        menu_mouse_pos = pygame.mouse.get_pos()
        menu_surf = pygame.font.SysFont("copperplategothic", 50).render("MAIN MENU", False, "white")
        menu_rect = menu_surf.get_rect(center=((screen_width / 2), 100))

        play_button = Button(image=pygame.image.load("images/menu.png"), pos=((screen_width / 2), 300),
                             text_input="PLAY", font=pygame.font.SysFont("copperplategothic", 25), base_color="#00ff99",
                             hovering_color="White")
        quit_button = Button(image=pygame.image.load("images/menu.png"), pos=((screen_width / 2), 500),
                             text_input="QUIT", font=pygame.font.SysFont("copperplategothic", 25), base_color="#ff3300",
                             hovering_color="White")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:       # Jeśli gracz zamknie okno
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.check_for_input(menu_mouse_pos):
                    flaga = 1
                    flaga1 = 1
                elif quit_button.check_for_input(menu_mouse_pos):
                    pygame.quit()
                    sys.exit()

        screen.fill((30, 30, 30))       # Rysowanie tła

        game.run()
        background.draw()

        if flaga1 == 0:
            screen.blit(bg_menu, (0, 0))
            screen.blit(menu_surf, menu_rect)
            for button in [play_button, quit_button]:
                button.change_color(menu_mouse_pos)
                button.update(screen)

        pygame.display.flip()
        clock.tick(60)      # maksymalnie 60 fps
