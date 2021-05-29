# required libraries
from abc import *
from sourceFiles import *
from coordinate_class import Coordinate
import random
import pygame
# dimensions for display
DISPLAY_WIDTH = 1080
DISPLAY_HEIGHT = 720
# middle positions of display
MID_WIDTH = DISPLAY_WIDTH / 2
MID_HEIGHT = DISPLAY_HEIGHT / 2
# font
pygame.font.init()
FONT = pygame.font.Font("freesansbold.ttf", 30)
# color RGB values
WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
# display screen
SCREEN = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
# clock and tick rates
CLOCK = pygame.time.Clock()
FPS = 800
pygame.display.set_caption("Elementals")


# a game class to include and display data
class Game:
    def __init__(self):
        # game initializations
        pygame.init()
        pygame.mixer.init()
        # background image
        self.background = BACKGROUND
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        # surface to display text
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        # Menu objects
        self.main_menu = MainMenu(self)
        self.option_menu = Options(self)
        self.ship_selection = ShipSelection(self)
        self.instructions = Instructions(self)
        self.level = Level(self)
        self.high_scores = HighScores(self)
        self.credits = Credits(self)
        # current state
        self.score = 0
        self.state = "Main Menu"
        # for filing
        self.filing = Files(self)

    # function to display score on screen
    def display_score(self):
        score = FONT.render(f"SCORE: {self.score}", True, (255, 255, 255))
        SCREEN.blit(score, (30, 30))

    # function to decide which screen to display
    def current_display(self):
        MENU_TRACK.play(-1)
        if self.state == "Main Menu":
            FINALE_TRACK.stop()
            LEVEL_TRACK.stop()
            MENU_TRACK.play(-1)
            self.main_menu.display_main_menu()
        elif self.state == "Options":
            self.option_menu.display_main_menu()
        elif self.state == "Instructions":
            self.instructions.display_main_menu()
        elif self.state == "Ship Selection":
            self.ship_selection.display_main_menu()
        elif self.state == "High Scores":
            self.high_scores.display_main_menu()
        elif self.state == "Game":
            MENU_TRACK.stop()
            user = ship_creation(self.ship_selection.get_state())
            self.playing = True
            self.game_loop(user)
            self.filing.write_data(str(self.score))
            LOSE_TRACK.stop()
        elif self.state == "Credits":
            FINALE_TRACK.play()
            self.credits.display_main_menu()

    # function to set the game to starting point
    def reset_settings(self):
        self.level.lost = False
        self.score = 0
        self.level.lives = 5
        self.level.level = 0

    # function which hold the whole game mechanics
    def game_loop(self, user):
        LEVEL_TRACK.play(-1)
        LEVEL_TRACK.set_volume(75)
        self.reset_settings()
        while self.playing:
            CLOCK.tick(FPS)
            self.level.draw_window(user)
            self.level.check_end_game(user)
            if self.level.level == 0:
                self.level.spawn_enemies(6, 5, ENEMY_SHIP1, ENEMY_BULLET1, False, 10)
            elif self.level.level == 1:
                self.level.spawn_enemies(6, 10, ENEMY_SHIP2, ENEMY_BULLET2, False, 10)
            elif self.level.level == 2:
                self.level.spawn_enemies(6, 15, ENEMY_SHIP3, ENEMY_BULLET3, False, 10)
            elif self.level.level == 3:
                self.level.spawn_enemies(6, 20, ENEMY_SHIP4, ENEMY_BULLET4, False, 10)
            elif self.level.level == 4:
                self.level.spawn_enemies(1, 40, BOSS_SHIP, BOSS_BULLET, True, 1000, 10)
            elif self.level.level == 5:
                self.level.spawn_enemies(0, 0, ENEMY_SHIP1, ENEMY_BULLET1, False, 10)
                LEVEL_TRACK.stop()
                FINALE_TRACK.play(-1)
                FINALE_TRACK.set_volume(100)
            elif self.level.level == 6:
                self.level.win = True
            self.level.enemy_mechanics(user)
            Player.move(user)
            Player.check_bounds(user)

    # to check the incoming events and set the respective key to true so actions can be taken later
    def check_events(self):
        for event in pygame.event.get():
            # game quit mechanics
            if event.type == pygame.QUIT:
                self.running = False
                self.playing = False
                self.main_menu.show_menu = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.START_KEY = True
                elif event.key == pygame.K_UP:
                    self.UP_KEY = True
                elif event.key == pygame.K_DOWN:
                    self.DOWN_KEY = True
                elif event.key == pygame.K_ESCAPE or pygame.K_BACKSPACE:
                    self.BACK_KEY = True

    # reset the keys set to True so only the required action is performed
    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    # draw text over screen
    def display_text(self, text, size, x, y):
        # add a font with varying size
        font = pygame.font.SysFont("Comic Sans MS", size)
        # creates an object to render
        text_display = font.render(text, True, WHITE_COLOR)
        # transforming into a rectangle to fix coordinates
        text_rect = text_display.get_rect()
        text_rect.center = (x, y)
        # display text with blit(text, (x,y)positions)
        self.display.blit(text_display, text_rect)


class Level:
    def __init__(self, game):
        self.game = game
        self.level = 0
        self. enemies = []
        self.lives = 5
        self.lost, self.win = False, False
        self.lost_count = 0

    # function to display score, level number and missile count
    def display_data(self, user):
        score = FONT.render(f"LIVES: {self.lives}", True, (255, 255, 255))
        SCREEN.blit(score, (30, 70))
        level = FONT.render(f"LEVEL: {self.level}", True, (0, 255, 255))
        SCREEN.blit(level, (940, 80))
        limit = FONT.render(f"MISSILE COUNT: {6 - user.limit}", True, (0, 255, 0))
        SCREEN.blit(limit, (800, 30))

    # function to draw window on screen
    def draw_window(self, user):
        if self.lost:
            SCREEN.blit(LOST_BG, (-400, -150))
            LEVEL_TRACK.stop()
            FINALE_TRACK.stop()
            LOSE_TRACK.play()
        elif self.win:
            self.game.state = "Credits"
            self.game.playing = False
        else:
            SCREEN.blit(BACKGROUND, (0, 0))
            self.game.display_score()
            self.display_data(user)
            user.health_bar()
            for enemy in self.enemies:
                enemy.draw_ship()
                enemy.boss_bar()
            user.draw_ship()
        pygame.display.update()

    # function to decide if to end the game
    def check_end_game(self, user):
        if self.lives <= 0 or user.health <= 0:
            self.lost = True
            self.lost_count += 1
        if self.lost:
            if self.lost_count > FPS * 3:
                self.game.playing = False
                self.game.state = "Main Menu"

    # function to spawn boss and enemies
    def spawn_enemies(self, count, damage, ship_img, bullet_img, boss=False, health=10, y=0):
        if len(self.enemies) == 0:
            self.level += 1
            if boss:
                for i in range(count):
                    enemy = Enemy(random.randint(0, 1080), y, 1, 0.1, damage, ship_img, bullet_img, boss, health)
                    self.enemies.append(enemy)
            else:
                for i in range(count):
                    enemy = Enemy(random.randint(0, 1081), random.randint(-700, -100), 0.25, 0.25, damage, ship_img, bullet_img, boss, health)
                    self.enemies.append(enemy)

    # function to control enemy movements
    def enemy_mechanics(self, user):
        for enemy in self.enemies:
            user.boss_fight = enemy.block
            enemy.move()
            enemy.move_bullets(1.6, user)
            if random.randrange(0, 600) == 1:
                enemy.shoot(None)
            if collide(user, enemy):
                if enemy.block:
                    user.receive_damage(100)
                else:
                    user.receive_damage(20)
                    self.lives -= 1
                    self.game.score -= 5
                    self.enemies.remove(enemy)
            elif enemy.get_y() > 720:
                self.lives -= 1
                self.game.score -= 5
                self.enemies.remove(enemy)
            if 0 > self.level > 4:
                user.move_bullets(-1, self.enemies)
            else:
                user.move_bullets(-2, self.enemies)


class Files:
    def __init__(self, game):
        self.game = game

    # static function to read data from files
    @staticmethod
    def read_data():
        read = open("Scores.txt", "r")
        score_list = read.read().splitlines()
        return score_list

    # static function to write data to files
    @staticmethod
    def write_data(score):
        write = open("Scores.txt", "a")
        write.seek(0)
        write.write(score)
        write.write("\n")
        write.close()


# Menu parent class
class Menu:
    def __init__(self, game):
        self.game = game
        self._show_menu = True
        # a pointer to show the current option
        # pygame.Rect(left, top, width, height)
        self.pointer = pygame.Rect(0, 0, 30, 30)
        # pointer offset for correct positioning
        self._offset = -100

    # draw a pointer to mark the current position
    def display_pointer(self):
        # due to pygame.Rect the x and y coordinates were assigned
        self.game.display_text("|=>", 25, self.pointer.x, self.pointer.y)

    def display_menu(self):
        # blit the black screen
        SCREEN.blit(self.game.display, (0, 0))
        # update screen after function call
        pygame.display.update()
        # reset keys after use
        self.game.reset_keys()

    @abstractmethod
    def display_main_menu(self):
        pass

    def move_pointer(self):
        pass

    def check_input(self):
        pass


# child class Main menu
class MainMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        # state variable to move between options
        self.__state = "Start"
        # positions for text to be displayed
        self.__start_x, self.__start_y = MID_WIDTH, MID_HEIGHT + 30
        self.__options_x, self.__options_y = MID_WIDTH, MID_HEIGHT + 60
        self.__exit_x, self.__exit_y = MID_WIDTH, MID_HEIGHT + 90
        # pointer's mid position from the top
        self.pointer.midtop = (self.__start_x + self._offset, self.__start_y)

    # display the main menu
    def display_main_menu(self):
        self._show_menu = True
        while self._show_menu:
            # check which key is turned into True
            self.game.check_events()
            # check which move to make depending on the event
            self.check_input()
            # display background behind menu
            self.game.display.blit(BACKGROUND, (0, 0))
            # main menu list
            self.game.display_text("Main Menu", 30, MID_WIDTH, MID_HEIGHT - 50)
            self.game.display_text("Start", 30, self.__start_x, self.__start_y)
            self.game.display_text("Options", 30, self.__options_x, self.__options_y)
            self.game.display_text("Exit", 30, self.__exit_x, self.__exit_y)
            # display the pointer
            self.display_pointer()
            # display the menu
            self.display_menu()

    # function to move the pointer depending on the calls
    def move_pointer(self):
        # mechanics for pointer going down
        if self.game.DOWN_KEY:
            if self.__state == "Start":
                self.pointer.midtop = (self.__options_x + self._offset, self.__options_y)
                self.__state = "Options"
            elif self.__state == "Options":
                self.pointer.midtop = (self.__exit_x + self._offset, self.__exit_y)
                self.__state = "Exit"
            elif self.__state == "Exit":
                self.pointer.midtop = (self.__start_x + self._offset, self.__start_y)
                self.__state = "Start"
        # mechanics for pointer going up
        elif self.game.UP_KEY:
            if self.__state == "Start":
                self.pointer.midtop = (self.__exit_x + self._offset, self.__exit_y)
                self.__state = "Exit"
            elif self.__state == "Options":
                self.pointer.midtop = (self.__start_x + self._offset, self.__start_y)
                self.__state = "Start"
            elif self.__state == "Exit":
                self.pointer.midtop = (self.__options_x + self._offset, self.__options_y)
                self.__state = "Options"

    # take actions depending on which option is entered
    def check_input(self):
        self.move_pointer()
        if self.game.START_KEY:
            # goto ship selection screen
            if self.__state == "Start":
                self._show_menu = False
                self.game.state = "Ship Selection"
            # goto options
            elif self.__state == "Options":
                self._show_menu = False
                self.game.state = "Options"
            # exit the game
            elif self.__state == "Exit":
                exit(0)
            self._show_menu = False


# options menu
class Options(Menu):
    def __init__(self, game):
        super().__init__(game)
        # state variable to move between options
        self.__state = "Controls"
        # positions for options
        self.__controls_x, self.__controls_y = MID_WIDTH, MID_HEIGHT + 30
        self.__high_x, self.__high_y = MID_WIDTH, MID_HEIGHT + 60

    # display the menu
    def display_main_menu(self):
        self.pointer.midtop = (self.__controls_x + self._offset, self.__controls_y)
        self._show_menu = True
        while self._show_menu:
            # select events
            self.game.check_events()
            # check where to move pointer depending on the input
            self.check_input()
            # display background
            self.game.display.blit(SETTINGS_BG, (0, 0))
            # options list
            self.game.display_text("Options", 30, MID_WIDTH, MID_HEIGHT - 50)
            self.game.display_text("Controls", 30, self.__controls_x, self.__controls_y)
            self.game.display_text("High Scores", 30, self.__high_x, self.__high_y)
            # display the pointer
            self.display_pointer()
            # display the menu
            self.display_menu()

    # move pointer among options
    def move_pointer(self):
        if self.game.UP_KEY or self.game.DOWN_KEY:
            if self.__state == "Controls":
                self.pointer.midtop = (self.__high_x + self._offset, self.__high_y)
                self.__state = "High Scores"
            elif self.__state == "High Scores":
                self.pointer.midtop = (self.__controls_x + self._offset, self.__controls_y)
                self.__state = "Controls"

    # take actions wrt inputs
    def check_input(self):
        self.move_pointer()
        # if escape pressed then return to the main menu
        if self.game.BACK_KEY:
            self._show_menu = False
            # call main menu here
            self.game.state = "Main Menu"
        # go to the selected option
        elif self.game.START_KEY:
            if self.__state == "Controls":
                # call options here
                self.game.state = "Instructions"
                self._show_menu = False
            elif self.__state == "High Scores":
                # call high scores here
                self.game.state = "High Scores"
                self._show_menu = False


# ship selection screen
class ShipSelection(Menu):
    def __init__(self, game):
        super().__init__(game)
        # initial state
        self.__state = "Air"
        # positions for options
        self.__air_x, self.__air_y = MID_WIDTH, MID_HEIGHT + 20
        self.__water_x, self.__water_y = MID_WIDTH, MID_HEIGHT + 70
        self.__fire_x, self.__fire_y = MID_WIDTH, MID_HEIGHT + 120
        self.__earth_x, self.__earth_y = MID_WIDTH, MID_HEIGHT + 170

    # display menu
    def display_main_menu(self):
        self.pointer.midtop = (self.__air_x + self._offset, self.__air_y)
        self._show_menu = True
        while self._show_menu:
            # check events and set required to true
            self.game.check_events()
            # check which part to start
            self.check_input()
            # background for screen
            self.game.display.blit(SELECTION_SCREEN_BG, (0, 0))
            # list of options
            self.game.display_text("Select your ship", 30, MID_WIDTH, MID_HEIGHT - 50)
            self.game.display_text("Air", 30, self.__air_x, self.__air_y)
            self.game.display_text("Water", 30, self.__water_x, self.__water_y)
            self.game.display_text("Fire", 30, self.__fire_x, self.__fire_y)
            self.game.display_text("Earth", 30, self.__earth_x, self.__earth_y)
            # display pointer
            self.display_pointer()
            # display menu
            self.display_menu()

    # getter for state
    def get_state(self):
        return self.__state

    # mechanics for pointer
    def move_pointer(self):
        # mechanics for going down
        if self.game.DOWN_KEY:
            if self.__state == "Air":
                self.pointer.midtop = (self.__water_x + self._offset, self.__water_y)
                self.__state = "Water"
            elif self.__state == "Water":
                self.pointer.midtop = (self.__fire_x + self._offset, self.__fire_y)
                self.__state = "Fire"
            elif self.__state == "Fire":
                self.pointer.midtop = (self.__earth_x + self._offset, self.__earth_y)
                self.__state = "Earth"
            elif self.__state == "Earth":
                self.pointer.midtop = (self.__air_x + self._offset, self.__air_y)
                self.__state = "Air"
        # mechanics for going up
        elif self.game.UP_KEY:
            if self.__state == "Air":
                self.pointer.midtop = (self.__earth_x + self._offset, self.__earth_y)
                self.__state = "Earth"
            elif self.__state == "Water":
                self.pointer.midtop = (self.__air_x + self._offset, self.__air_y)
                self.__state = "Air"
            elif self.__state == "Fire":
                self.pointer.midtop = (self.__water_x + self._offset, self.__water_y)
                self.__state = "Water"
            elif self.__state == "Earth":
                self.pointer.midtop = (self.__fire_x + self._offset, self.__fire_y)
                self.__state = "Fire"

    # check and select a Ship
    def check_input(self):
        self.move_pointer()
        if self.game.START_KEY:
            self.game.state = "Game"
            self._show_menu = False
        elif self.game.BACK_KEY:
            self.game.state = "Main Menu"
            self._show_menu = False


class Instructions(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.__line1_x, self.__line1_y = 380, 20
        self.__line2_x, self.__line2_y = 500, 150
        self.__line3_x, self.__line3_y = 490, 180
        self.__line4_x, self.__line4_y = 400, 220
        self.__line5_x, self.__line5_y = 225, 260
        self.__line6_x, self.__line6_y = 330, 300
        self.__line6_1x, self.__line6_1y = 250, 330
        self.__line7_x, self.__line7_y = 305, 370
        self.__line7_1x, self.__line7_1y = 250, 400
        self.__line8_x, self.__line8_y = 397, 440
        self.__line9_x, self.__line9_y = 360, 480
        self.__line10_x, self.__line10_y = 225, 520

    # function to display menu on screen
    def display_main_menu(self):
        self._show_menu = True
        while self._show_menu:
            self.game.check_events()
            self.check_input()
            self.game.display.blit(INSTRUCTIONS_BG, (0, 0))
            self.game.display_text("This Game has been developed using Python in Pycharm Community Edition 20.1", 20,
                                   self.__line1_x, self.__line1_y)
            self.game.display_text("GAME CONTROL KEYS", 40, self.__line2_x, self.__line2_y)
            self.game.display_text("=======================================", 30, self.__line3_x, self.__line3_y)
            self.game.display_text("- Use Arrow keys as perspective to move up , down , left and right .", 25,
                                   self.__line4_x, self.__line4_y)
            self.game.display_text("- Use Space Bar to shoot the bullet .", 25, self.__line5_x, self.__line5_y)
            self.game.display_text("- This Game is based on Avatar type , and has 4 modes ", 25, self.__line6_x,
                                   self.__line6_y)
            self.game.display_text("i.e EARTH , AIR , FIRE and WATER .", 25, self.__line6_1x, self.__line6_1y)
            self.game.display_text("- Each levels has its own function and difficulties ,", 25, self.__line7_x,
                                   self.__line7_y)
            self.game.display_text(" you have to kill all bots to clear level.", 25, self.__line7_1x, self.__line7_1y)
            self.game.display_text("- On collision with bot or bots' bullet, player ship will lose health . ", 25,
                                   self.__line8_x, self.__line8_y)
            self.game.display_text("- You have to kill the boss as well in the end to win the game", 25, self.__line9_x,
                                   self.__line9_y)
            self.game.display_text("- Use Z to use special ability.(6 Limit) ", 25, self.__line10_x, self.__line10_y)
            self.display_menu()

    # function to check user input
    def check_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
        if self.game.BACK_KEY:
            self.game.state = "Options"
            self._show_menu = False


class HighScores(Menu):
    def __init__(self, game):
        super().__init__(game)

    # function to display menu on screen
    def display_main_menu(self):
        self._show_menu = True
        while self._show_menu:
            self.game.check_events()
            self.check_input()
            self.game.display.blit(HIGH_BG, (-400, 0))
            scores = self.game.filing.read_data()
            self.game.display_text("High Scores ", 30, 520, 30)
            for i in range(len(scores)):
                self.game.display_text("Elemenol: ", 30, 200, 80 * (i + 1))
                self.game.display_text(scores[i], 30, 900, 80 * (i + 1))
            self.display_menu()

    # function to check user input
    def check_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
        if self.game.BACK_KEY:
            self.game.state = "Options"
            self._show_menu = False


class Credits(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.__line1_x, self.__line1_y = MID_WIDTH - 40, 250
        self.__line2_x, self.__line2_y = 500, 350
        self.__line3_x, self.__line3_y = 200, 450
        self.__line4_x, self.__line4_y = 210, 500
        self.__line5_x, self.__line5_y = 210, 550
        self.__line6_x, self.__line6_y = 210, 600

    # function to display menu on screen
    def display_main_menu(self):
        self._show_menu = True
        while self._show_menu:
            self.game.check_events()
            self.check_input()
            self.game.display.blit(CREDITS_BG, (0, 0))
            self.game.display_text("CONGRATULATIONS!!! ", 50, self.__line1_x, self.__line1_y)
            self.game.display_text("You have successfully completed the game ", 40, self.__line2_x, self.__line2_y)
            self.game.display_text("Made by:  ", 20, self.__line3_x, self.__line3_y)
            self.game.display_text("-> Wahaj Javed ", 20, self.__line4_x, self.__line4_y)
            self.game.display_text("-> Muhammad Zunique  ", 20, self.__line5_x, self.__line5_y)
            self.game.display_text("-> Uneeb Ahmed", 20, self.__line6_x, self.__line6_y)
            self.display_menu()

    # function to check user input
    def check_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
        if self.game.START_KEY:
            self.game.state = "Main Menu"
            self._show_menu = False


# bullet class
class Bullet(Coordinate):
    def __init__(self, x, y, img, damage):
        super().__init__(x, y, 0, 0)
        self.bullet_img = img
        self.mask = pygame.mask.from_surface(self.bullet_img)
        self.damage = damage

    # function to draw bullet on screen
    def draw_bullet(self):
        SCREEN.blit(self.bullet_img, (self.get_x(), self.get_y()))

    # function to handle movement of bullet
    def move(self, direction):
        self.set_dy(direction)
        self.set_y(self.get_y() + self.get_dy())

    # function to check if bullet is off screen
    def off_screen(self):
        return not (DISPLAY_HEIGHT >= self.get_y() >= 0)

    # function to check for collisions
    def is_collision(self, obj):
        return collide(self, obj)


# Ship parent class
class Ship(Coordinate):
    # constant fixed cool down
    COUNTDOWN = 70

    def __init__(self, x, y, dx, dy, health=100):
        super().__init__(x, y, dx, dy)
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = []
        self.__coolDown = 0

    # getter for cool down
    def get_cool_down(self):
        return self.__coolDown

    # function to draw the ship
    def draw_ship(self):
        SCREEN.blit(self.ship_img, (self.get_x(), self.get_y()))
        for bullet in self.bullets:
            bullet.draw_bullet()

    # function to check cool down
    def cool_down(self):
        if self.__coolDown >= self.COUNTDOWN:
            self.__coolDown = 0
        elif self.__coolDown > 0:
            self.__coolDown += 1

    # mechanics to move the bullet and damage objects
    def move_bullets(self, vel, obj):
        self.cool_down()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen():
                self.bullets.remove(bullet)
            elif bullet.is_collision(obj):
                obj.receive_damage(bullet.damage)
                self.bullets.remove(bullet)

    # function to shoot depending on cool down
    @abstractmethod
    def shoot(self, img):
        if self.__coolDown == 0:
            bullet = Bullet(self.get_x(), self.get_y(), self.bullet_img, 10)
            self.bullets.append(bullet)
            self.__coolDown = 1


# child class Player Ship
class Player(Ship):
    def __init__(self, name, x, y, dx, dy, game, health=100):
        super().__init__(x, y, dx, dy, health)
        self.__name = name
        self.game = game
        self.__max_health = 100
        self.__health_bar_length = 350
        self.__health_ratio = self.__max_health / self.__health_bar_length
        self.__health_change_speed = 0.32
        self.__target_health = 100
        self.boss_fight = False
        self.limit = 0

    # function to decide the damage received
    def receive_damage(self, amount):
        if self.__target_health > 0:
            self.__target_health -= amount

    # function to create health bar
    def health_bar(self):
        transition_width = 0
        transition_color = (255, 0, 0)
        if self.health < self.__target_health:
            self.health += self.__health_change_speed
            transition_width = int((self.__target_health - self.health) / self.__health_ratio)
            transition_color = (0, 255, 0)
        if self.health > self.__target_health:
            self.health -= self.__health_change_speed
            transition_width = int((self.__target_health - self.health) / self.__health_ratio)
            transition_color = (255, 255, 0)
        health_bar_width = int(self.health / self.__health_ratio)
        health_bar = pygame.Rect(10, 680, health_bar_width, 25)
        transition_bar = pygame.Rect(health_bar.right, 680, transition_width, 25)
        pygame.draw.rect(SCREEN, (255, 0, 0), health_bar)
        pygame.draw.rect(SCREEN, (255, 255, 255), (10, 680, self.__health_bar_length, 25), 4)
        pygame.draw.rect(SCREEN, transition_color, transition_bar)

    # function to keep the boundaries in check
    @staticmethod
    def check_bounds(user):
        if user.get_x() <= 0:
            user.set_x(0)
        elif user.get_x() >= 1006:
            user.set_x(1006)
        if user.get_y() <= 0:
            user.set_y(0)
        elif user.get_y() >= 656:
            user.set_y(656)

    # function to keep check of movements of user
    @staticmethod
    def move(user):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    user.set_dx(-1.6)
                if event.key == pygame.K_RIGHT:
                    user.set_dx(1.6)
                if event.key == pygame.K_UP:
                    user.set_dy(-1.6)
                if event.key == pygame.K_DOWN:
                    user.set_dy(1.6)
                if event.key == pygame.K_SPACE:
                    user.shoot(None)
                    FIRE.play()
                if event.key == pygame.K_z:
                    user.shoot(1)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    user.set_dx(0)
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    user.set_dy(0)
        user.set_x(user.get_x() + user.get_dx())
        user.set_y(user.get_y() + user.get_dy())

    # function to handle the movement of ships
    def move_bullets(self, vel, objects):
        self.cool_down()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen():
                self.bullets.remove(bullet)
            else:
                for obj in objects:
                    if bullet.is_collision(obj):
                        if self.boss_fight:
                            obj.health -= bullet.damage
                            obj.receive_damage(bullet.damage)
                        else:
                            objects.remove(obj)
                        if obj.health < 0:
                            objects.remove(obj)
                        self.game.score += 10
                        self.bullets.remove(bullet)

    # function to handle bullet fires
    def shoot(self, img=None):
        if self.get_cool_down() == 0:
            if img is None:
                bullet = Bullet(self.get_x() + 18.5, self.get_y(), self.bullet_img, 10)
                self.bullets.append(bullet)
            self.__coolDown = 1


# AIR class
class Air(Player):
    def __init__(self, name, x, y, dx, dy, game, health=100):
        super().__init__(name, x, y, dx, dy, game, health)
        self.ship_img = AIR_SHIP
        self.bullet_img = AIR_BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)

    # shoot air specific missiles
    def shoot(self, img=None):
        if img is None:
            bullet = Bullet(self.get_x() + 18.5, self.get_y(), self.bullet_img, 10)
            self.bullets.append(bullet)
        elif img is not None and self.limit <= 5:
            if self.get_cool_down() == 0:
                bullet = Bullet(self.get_x() + 18.5, self.get_y(), AIR_MISSILE, 15)
                self.bullets.append(bullet)
                self.limit += 1
                MISSILE.play()
        self.__coolDown = 1


# WATER class
class Water(Player):
    def __init__(self, name, x, y, dx, dy, game, health=100):
        super().__init__(name, x, y, dx, dy, game, health)
        self.ship_img = WATER_SHIP
        self.bullet_img = WATER_BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)

    # shoot water specific missiles
    def shoot(self, img=None):
        if img is None:
            bullet = Bullet(self.get_x() + 18.5, self.get_y(), self.bullet_img, 10)
            self.bullets.append(bullet)
        elif img is not None and self.limit <= 5:
            if self.get_cool_down() == 0:
                bullet = Bullet(self.get_x() + 18.5, self.get_y(), WATER_MISSILE, 20)
                self.bullets.append(bullet)
                self.limit += 1
                MISSILE.play()
        self.__coolDown = 1


# FIRE class
class Fire(Player):
    def __init__(self, name, x, y, dx, dy, game, health=100):
        super().__init__(name, x, y, dx, dy, game, health)
        self.ship_img = FIRE_SHIP
        self.bullet_img = FIRE_BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)

    # shoot fire specific missiles
    def shoot(self, img=None):
        if img is None:
            bullet = Bullet(self.get_x() + 18.5, self.get_y(), self.bullet_img, 10)
            self.bullets.append(bullet)
        elif img is not None and self.limit <= 5:
            if self.get_cool_down() == 0:
                bullet = Bullet(self.get_x() + 18.5, self.get_y(), FIRE_MISSILE, 30)
                self.bullets.append(bullet)
                self.limit += 1
                MISSILE.play()
        self.__coolDown = 1


# EARTH class
class Earth(Player):
    def __init__(self, name, x, y, dx, dy, game, health=100):
        super().__init__(name, x, y, dx, dy, game, health)
        self.ship_img = EARTH_SHIP
        self.bullet_img = EARTH_BULLET
        self.mask = pygame.mask.from_surface(self.ship_img)

    # shoot earth specific missiles
    def shoot(self, img=None):
        if img is None:
            bullet = Bullet(self.get_x() + 18.5, self.get_y(), self.bullet_img, 10)
            self.bullets.append(bullet)
        elif img is not None and self.limit <= 5:
            if self.get_cool_down() == 0:
                bullet = Bullet(self.get_x() + 18.5, self.get_y(), EARTH_MISSILE, 40)
                self.bullets.append(bullet)
                self.limit += 1
                MISSILE.play()
        self.__coolDown = 1


# Enemy ship class
class Enemy(Ship):
    def __init__(self, x, y, dx, dy, damage, ship_img, bullet_img, block=False, health=10):
        super().__init__(x, y, dx, dy, health)
        self.ship_img = ship_img
        self.bullet_img = bullet_img
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.damage = damage
        self.block = block
        self.__max_health = 1000
        self.__health_bar_length = 350
        self.__health_ratio = self.__max_health / self.__health_bar_length
        self.__health_change_speed = 0.32
        self.__target_health = 1000
        # bullet image and damage to be added later

    # movement mechanics for enemy ship
    def move(self):
        if not self.block:
            self.set_y(self.get_y() + self.get_dy())
            if self.get_x() >= 1006:
                self.set_dx(-0.1)
        else:
            if self.get_x() >= 950:
                self.set_dx(-0.1)
        self.set_x(self.get_x() + self.get_dx())
        if self.get_x() <= 0:
            self.set_dx(0.1)

    # shooting mechanics for enemy ships
    def shoot(self, img):
        if self.get_cool_down() == 0:
            if self.block:
                bullet = Bullet(self.get_x() + 30, self.get_y(), self.bullet_img, self.damage)
                self.bullets.append(bullet)
            else:
                bullet = Bullet(self.get_x() - 17, self.get_y(), self.bullet_img, self.damage)
                self.bullets.append(bullet)
            self.__coolDown = 1

    # get damage for boss
    def receive_damage(self, amount):
        if self.__target_health > 0:
            self.__target_health -= amount

    # boss health bar
    def boss_bar(self):
        if self.block:
            transition_width = 0
            transition_color = (0, 0, 255)
            if self.health < self.__target_health:
                self.health += self.__health_change_speed
                transition_width = int((self.__target_health - self.health) / self.__health_ratio)
                transition_color = (0, 255, 0)
            if self.health > self.__target_health:
                self.health -= self.__health_change_speed
                transition_width = int((self.__target_health - self.health) / self.__health_ratio)
                transition_color = (255, 255, 0)
            health_bar_width = int(self.health / self.__health_ratio)
            health_bar = pygame.Rect(10, 130, health_bar_width, 25)
            transition_bar = pygame.Rect(health_bar.right, 680, transition_width, 25)
            pygame.draw.rect(SCREEN, (0, 0, 255), health_bar)
            pygame.draw.rect(SCREEN, (255, 255, 255), (10, 130, self.__health_bar_length, 25), 4)
            pygame.draw.rect(SCREEN, transition_color, transition_bar)


# function to check for collisions
def collide(obj1, obj2):
    offset_x = int(obj2.get_x()) - int(obj1.get_x())
    offset_y = int(obj2.get_y()) - int(obj1.get_y())
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


g = Game()


# create a ship depending on the selection
def ship_creation(state):
    if state == "Air":
        user1 = Air("Wahaj", 646, 646, 0, 0, g)
        return user1
    elif state == "Water":
        user1 = Water("Wahaj", 646, 646, 0, 0, g)
        return user1
    elif state == "Fire":
        user1 = Fire("Wahaj", 646, 646, 0, 0, g)
        return user1
    elif state == "Earth":
        user1 = Earth("Wahaj", 646, 646, 0, 0, g)
        return user1


# actual game function main()
def main():
    while g.running:
        g.current_display()


main()
