import pygame
import os
import random
import Sounds


pygame.font.init()

# Load images
WIDTH, HEIGHT = 950, 750

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fuse Space")

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets/sprites", "background.png")),
                            (WIDTH, HEIGHT))



RED_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets/sprites", "nave_vermelha.png")), (60, 50))
GREEN_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets/sprites", "nave_verde.png")), (60, 50))
BLUE_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets/sprites", "nave_azul.png")), (60, 50))

# Player
PLAYER_SPACE_SHIP = pygame.image.load(os.path.join("assets/sprites", "nave.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets/sprites", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets/sprites", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets/sprites", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets/sprites", "pixel_laser_yellow.png"))


# Game Over
GAME_OVER = pygame.transform.scale(pygame.image.load(os.path.join("assets/sprites", "Game-Over.png")), (300, 200))

pygame.mixer.init()


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 20

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 25, self.y - 20, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    score = 0

    def incr_score(self):
        self.score += 10

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SPACE_SHIP
        self.ship_img = pygame.transform.scale(PLAYER_SPACE_SHIP, (50, 40))
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):

        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        pos = self.x, self.y

                        self.incr_score()

                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health),
            10))


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1



def main(self=None):
    run = True
    FPS = 60
    level = 0
    lives = 5
    Sounds.Music.play_track(self)
    main_font = pygame.font.SysFont("impact", 50)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, 0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        score_label = main_font.render(f"Score: {player.score}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (250, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            Sounds.Music.play_track(self, False)
            WIN.blit(GAME_OVER, (300, 250))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            Sounds.Sound_Fx.game_over(self)
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                                       random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()

        # Player control : Keyboard
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_SPACE]:  # shoot
            Sounds.Sound_Fx.player_fire(self)
            player.shoot()

        # Auto destruct (Only for testing)
        if keys[pygame.K_0]:
            player.health = 0

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10

                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)


def main_menu(self=None):
    title_font = pygame.font.SysFont("impact", 70)
    run = True
    while run:

        WIN.blit(BG, (0, 0))
        instructions_label = title_font.render("A/D : Move | Space: Shoot", 1, (255, 255, 255))
        title_label = title_font.render("Fuse Space", 1, (255, 255, 255))
        sub_title_label = title_font.render("Press any key to begin", 1, (255, 255, 255))
        WIN.blit(title_label, (310, 150))
        WIN.blit(sub_title_label, (WIDTH / 2 - sub_title_label.get_width() / 2, 350))
        WIN.blit(instructions_label, (125, 470))
        pygame.display.update()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()


    pygame.quit()


main_menu()
