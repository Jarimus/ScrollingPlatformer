import pygame, os, sys
from math import sqrt
from time import sleep

os.chdir(os.path.dirname(os.path.abspath(__file__)))

vec = pygame.math.Vector2

class ScrollingPlatformer():

    fps = pygame.time.Clock()

    WIDTH = 800 # 40 tiles
    HEIGHT = 600 # 30 tiles
    TILE_SIZE = 20
    screen = pygame.display.set_mode( (WIDTH, HEIGHT) )

    BLACK = (0,0,0)
    GREY = (35, 35, 35)
    WHITE  = (255, 255, 255)

    all_sprites = pygame.sprite.LayeredUpdates()
    platforms = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    doors = pygame.sprite.Group()
    monsters = pygame.sprite.Group()
    traps = pygame.sprite.Group()

    coins_collected = 0
    current_level = 1
    ending_screen = False

    offset_x = 0
    offset_y = 0

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Scrolling Platformer")
    

    def run(self):

        self.load_assets()

        self.new_game()

        self.get_map()
        self.load_map()

        self.main_loop()


    def main_loop(self):
        while True:
            self.events()

            self.screen.fill(self.GREY)

            if not self.info_text_status:
                self.check_collisions()
                self.all_sprites.update()
                self.scroll_map()
                self.all_sprites.draw(self.screen)
                self.draw_UI()

            if self.info_text_status == True:
                self.info_text()

            pygame.display.flip()
            self.fps.tick(60)


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.info_text_status = False
                if self.current_level == 0:
                    self.next_map()
                elif self.ending_screen == True:
                    pygame.quit()
                    sys.exit()

    

    def check_collisions(self):
        grounded = False

        for trap in self.traps:
            if trap.rect.colliderect(self.player1.rect) and not self.player1.invulnerable:
                self.player_hit(self.player1)


        for platform in self.platforms: #Check for (1) if colliding (2) if player is above the platform (3) if not pressing DOWN (4) if player is moving downwards.
            if platform.rect.colliderect(self.player1.rect) and not self.player1.dropping:

                if self.player1.rect.bottom - 20 <= platform.rect.top:
                    self.player1.velocity.y = min(self.player1.velocity.y, 0)
                    self.player1.rect.bottom = platform.rect.top + 1
                    if self.player1.velocity.y == 0:
                        self.player1.grounded = True
                        grounded = True


        for wall in self.walls:

            if wall.rect.colliderect(self.player1.rect):

                if self.player1.rect.bottom - 20 <= wall.rect.top:
                    self.player1.velocity.y = min(self.player1.velocity.y, 0)
                    self.player1.rect.bottom = wall.rect.top + 1
                    if self.player1.velocity.y == 0:
                        self.player1.grounded = True
                        grounded = True

                elif self.player1.rect.right - 10 <= wall.rect.left:
                    #self.player1.velocity.x = min(self.player1.velocity.x, 0)
                    self.player1.rect.right = wall.rect.left - 1

                elif self.player1.rect.left + 10  >= wall.rect.right:
                    #self.player1.velocity.x = max(self.player1.velocity.x, 0)
                    self.player1.rect.left = wall.rect.right + 1
                
                elif self.player1.rect.top + 20 >= wall.rect.bottom:
                    self.player1.velocity.y = max(self.player1.velocity.y, 0)
                    self.player1.rect.top = wall.rect.bottom + 1

        for trap in self.traps:

            if trap.rect.colliderect(self.player1.rect):

                if self.player1.rect.bottom - 20 <= trap.rect.top:
                    self.player1.velocity.y = min(self.player1.velocity.y, 0)
                    self.player1.rect.bottom = trap.rect.top + 1
                    if self.player1.velocity.y == 0:
                        self.player1.grounded = True
                        grounded = True

                elif self.player1.rect.right - 10 <= trap.rect.left:
                    self.player1.velocity.x = min(self.player1.velocity.x, 0)
                    self.player1.rect.right = trap.rect.left - 1

                elif self.player1.rect.left + 10  >= trap.rect.right:
                    self.player1.velocity.x = max(self.player1.velocity.x, 0)
                    self.player1.rect.left = trap.rect.right + 1
                
                elif self.player1.rect.top + 20 >= trap.rect.bottom:
                    self.player1.velocity.y = max(self.player1.velocity.y, 0)
                    self.player1.rect.top = trap.rect.bottom + 1
        
        if not grounded:
            self.player1.grounded = False
        
        for coin in self.coins:
            if coin.rect.colliderect(self.player1.rect):
                coin.kill()
                self.coins_collected += 1
                if self.coins_collected % 10 == 0:
                    Player.lives += 1
        
        for door in self.doors:
            if door.rect.colliderect(self.player1.rect):
                self.next_map()
        
        for monster in self.monsters:
            if monster.rect.colliderect(self.player1.rect):
                if self.player1.rect.bottom < monster.rect.center[1] and self.player1.velocity.y > 0:
                    self.player1.rect.y -= 5
                    self.player1.velocity.y = -self.player1.velocity.y - 5
                    Coin(self.images["coin"], monster.rect.x + self.offset_x, monster.rect.center[1] + self.offset_y).add(self.all_sprites, self.coins)
                    monster.kill()
                elif not self.player1.invulnerable:
                    self.player_hit(self.player1)
    

    def player_hit(self, player: "Player"):
        player.invulnerable = True
        player.inv_timer = 120
        player.velocity *= -1
        Player.lives -= 1
        if Player.lives == 0 or self.current_level == 3:
            sleep(2)
            self.gameover()
        else:
            sleep(0.2)


    def new_game(self):
        self.current_level = 1
        self.info_text_status = True
    

    def next_map(self):
        self.clear_sprites()
        self.current_level += 1
        self.get_map()
        self.load_map()
        self.info_text_status = True
    

    def gameover(self):
        self.clear_sprites()
        self.current_level = 0
        Player.lives = 3
        self.coins_collected = 0
        self.info_text_status = True


    def get_map(self):
        
        if self.current_level == 1 or self.current_level == 0:
            self.offset_x, self.offset_y = 0, self.TILE_SIZE*3
            self.map = [
'X                                                                              X',
'X                                                       C                  D   X',
'X     C                                                                        X',
'X                                                      PPPP                    X',
'XXXXXPPPXXXXXXXXXXXXXXXXXX     PPPP            PPPP            PPPP    PPPPPPPPX',
'X              FF       XXX            PPPP                                    X',
'X              FF  C C   XXX                                                   X',
'X              FF         XXX                                                  X',
'X    PPP       FF  C C    XXXX                                                 X',
'XPP            FF         XXXX                                                 X',
'X     C        XX  C C    XXXX                                                 X',
'X              XX         XXX  C                                               X',
'X    PPP  PPPPPXXXXXXXXXXXXXX                             C                    X',
'X                   XXX    XXPPPPPX                                            X',
'X                                 XX                                           X',
'XPPP                             XXXX                   X    X                 X',
'X                               XXXXXX                 XX    XX                X',
'X                              XXXXXXXX               XXX    XXX               X',
'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX    XXXXXXXXX     PPPPX',
'X                                                                              X',
'X                                                                           C  X',
'X                                                                              X',
'X                                                                          PPPPX',
'X                   C                                                          X',
'X                                                                              X',
'X  1          C   PPPPP    C                                                   X',
'X                                                                          PPPPX',
'X             XX          XXX                                  C               X',
'X            XXXX   C    XXXXX                                           C     X',
'X       C   XXXXXX      XXXXXXXX       X  C  X               XXXXX             X',
'X          XXXXXXXX    XXXXXXXXXX     XX     XX            XXXXXXXXXX   XXXX   X',
'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',]

        elif self.current_level == 2:
            self.offset_x, self.offset_y = 0, 0
            self.map = [
'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
'X  1        F                                                                                                                                                X',
'X           F                                                                                                                                                X',
'X           F                                                          V                                                                                     X',
'X           F              C                                       V                                                                                         X',
'XXXXXX  XXXXX              V                                   V               XH          H         HX                                                      X',
'X    X  X                                                  V                   XH          H         HX                                                      X',
'X    X  X                  V                           V                           PPPPPPPPPPPPPPPP   X                                                      X',
'X    X  X               XX    XX                   V                                                  X                                                   D  X',
'X    X  X             XXXX    XXXX             V                                                      X                                                      X',
'X    X  X           XXXXXXTTTTXXXXXX                                                                  X     H       H       H       H       H       H       HX',
'X    X  X      XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
'X    X  X C                                                                                                                                                  X',
'X    X  X                                                                                                                                                    X',
'X    X  XPPP                                                                                                                                                 X',
'X    X  X                                                                                                                                                    X',
'X    X  X C                                                                                                                                                  X',
'X    X  X                                                                                                                                                    X',
'X    X  XPPP                                                                                                                                                 X',
'X    X  X                                                                                                                                                    X',
'X    X  X C                                                                                                                                                  X',
'X    X  X                              M          M       M          M            M           M         M        M        M      M       M                   X',
'X    X  XPPP                                                                                                                                                 X',
'X    X  X                                                                                                                                                    X',
'X    X  X C                                                                                                                                                  X',
'X    X  X                                                                                                                                                    X',
'X    X  XPPP                                                                                                                                                 X',
'X    X  X                                                                                                                                                    X',
'X    X  X                              C                   C                    C                     C                 C                                  C X',
'X    X  X                                                                                                                                                    X',
'X    X  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXPPPX',
'X    X  X                                                                   X        F                                                                       X',
'X    X  X                                                                   X        F                                                                   C   X',
'X    X  X                                                                   XC C C C F                                                                       X',
'X    X  X                                                                   X        F                                                                   PPPPX',
'X    X  X                                                                   XC C C C F                                                                       X',
'X    X  X                                                                   X        F                                                                       X',
'X    X  X                                                                   XXXXXXXXXX   PPPPP                                                               X',
'X    X  X                                                                                                                                                 PPPX',
'X    X  X                                                                                                                                                    X',
'X    X  X                                                                                              PPPP    PPPP   PPPP                         C         X',
'X    X  X                                                                                        M                             C                             X',
'X    X  X                                                                                                                             PPPPP   PPPPPPPPPPPPPPPX',
'X    X  X                                                                                                                    PPPPP                           X',
'X    X  X                                                                                                                                                    X',
'X    X  X                                                                                                                                                    X',
'X    X  X                                                                                                       C     PPPPP                                  X',
'X    X  X                                                                                                                                                    X',
'X    X  X                                                                                                     PPPPP                                          X',
'X    X  X                                                             C                                                                                      X',
'X    X  X                                                                                       C                                                            X',
'X    X  X                                                          PPPPPPPP                           PPPPP                                                  X',
'X    X  X                                                  C                                                                                                 X',
'X    X  X                       C                                                              PPPP                                                          X',
'X    X  X                                               PPPPPPPP              PPPPP   PPPPP                                                                  X',
'X   XX  XX                   PPPPPPPP          C                                                                                                             X',
'X  XXX  XXX                                                                                                                                                  X',
'X     M                                     PPPPPPPP                                                                                                         X',
'X                                                                                                                                            XXXXXXXXXXXXXXXXX',
'X                  PPPPPPP                                                                                                                   F C  C  C  C  C X',
'X   V M                                                                                                                                      F               X',
'X                    VVV                                                                                                                     F C  C  C  C  C X',
'X                             X   X    X    X   X   X    X    X   X   X    X    X   X   X    X    X   X   X    X    X   X   X    X    X      F               X',
'XXXXXXXXXXXXXXXXXXXXXXXXXXXTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTXXXXXXXXXXXXXXXXXXXXXX',]

        elif self.current_level == 3:
            self.offset_x, self.offset_y = 0, self.TILE_SIZE*3
            self.map = [
'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
'XM M                 X      F      X                                           X',
'X                    X      F      X                                           X',
'X                    X    C F      X                                        D  X',
'XM M                 X      F C    X                                           X',
'X                    X    PPX      X                            C              X',
'X                    X      XXXXXPPX                                  PPPPPPPPPX',
'XM M                 X      X      X             C             PPPP            X',
'X                    X      X      X                                           X',
'X                    X  XXXXX      X            PPPP                          PX',
'XM M                 X      X      X      C             PPPP                   X',
'X                    XPP    XPPXXXXX                                           X',
'X                    X      X      X     PPPP                                  X',
'XM M                 X      X      X                                          PX',
'X                    XXXXXC XC     X                                           X',
'X                    X      X      X            PPPP    PPPP                   X',
'XM M                 X    PPXXXXXPPX                            C              X',
'X                    X      X      X                                          PX',
'X                    X      X      X                           PPPP            X',
'XM M                 X  XXXXX      X                                           X',
'X                    X      X      X                                           X',
'X                    XPP    XPPXXXXX              C     PPPP                  PX',
'XM M                 X      X      X                                           X',
'X                    X      X      X             PPPP                          X',
'X                    XXXXXC X      X                                           X',
'XM M                 F      X      F      PPPP                          C C C PX',
'X        1           F    PPX      F                                           X',
'X                    F      X  C   F                                    C C C  X',
'X                    F      X      F                                           X',
'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',]

        else:
            self.ending_screen = True


    def load_map(self):
        for (row_index, row) in enumerate(self.map):
            for (col_index, cell) in enumerate(row):
                (x, y) = (col_index*self.TILE_SIZE, row_index*self.TILE_SIZE)

                if cell == "1":
                    self.player1 = Player( self.images["robot"], x, y )
                    self.player1.add(self.all_sprites)
                if cell == "X":
                    wall = Wall( self.TILE_SIZE, x, y)
                    wall.add(self.all_sprites, self.walls)
                if cell == "F":
                    wall = Wall( self.TILE_SIZE, x, y, 3)
                    wall.add(self.all_sprites)                    
                if cell == "P":
                    platform = Platform( self.TILE_SIZE, x, y)
                    platform.add(self.all_sprites, self.platforms)
                if cell == "O":
                    self.offset_x, self.offset_y = x, y
                if cell == "C":
                    coin = Coin( self.images["coin"], x, y)
                    coin.add(self.all_sprites, self.coins)
                if cell == "D":
                    door = Door( self.images["door"], x, y)
                    door.add(self.all_sprites, self.doors)
                if cell == "M":
                    monster = Monster( self.images["monster"], x, y,)
                    monster.add(self.all_sprites, self.monsters)
                if cell == "T":
                    trap = Trap( self.TILE_SIZE, x, y, vec(0, 0))
                    trap.add(self.all_sprites, self.traps)
                if cell == "V":
                    trap = Trap( self.TILE_SIZE, x, y, vec(0, -1))
                    trap.add(self.all_sprites, self.traps)
                if cell == "H":
                    trap = Trap( self.TILE_SIZE, x, y, vec(-1, 0))
                    trap.add(self.all_sprites, self.traps)


    def load_assets(self):
        self.images = {}
        for image in ["robot", "coin", "monster", "door"]:
            self.images[image] = pygame.image.load(image + ".png")
        
        self.text_ui = pygame.font.SysFont("Arial", 24, True)
        self.text_info = pygame.font.SysFont("Arial", 48)
    

    def clear_sprites(self):
        self.all_sprites.empty()
        self.walls.empty()
        self.platforms.empty()
        self.coins.empty()
        self.monsters.empty()
        self.traps.empty()


    def info_text(self):
        text = []

        if self.ending_screen == True:
            text.append(self.text_info.render("Congratulations!", True, self.WHITE))
            text.append(self.text_info.render("You finished Robot Platformer", True, self.WHITE))
            text.append(self.text_info.render(f"You collected {self.coins_collected} coins.", True, self.WHITE))
            text.append(self.text_info.render("Press Enter to quit.", True, self.WHITE))

        elif self.current_level == 0:
            text.append(self.text_info.render("You died!", True, self.WHITE))
            text.append(self.text_info.render("Press Enter to restart.", True, self.WHITE))

        elif self.current_level == 1:
            text.append(self.text_info.render("Welcome to Robot Platformer!", True, self.WHITE))
            text.append(self.text_info.render("Use arrow keys to move.", True, self.WHITE))
            text.append(self.text_info.render("Collect 10 coins for an extra life.", True, self.WHITE))
            text.append(self.text_info.render("Get to the exit to advance.", True, self.WHITE))
            text.append(self.text_info.render("press Enter to start.", True, self.WHITE))

        elif self.current_level == 2:
            text.append(self.text_info.render("Watch out for the monsters!", True, self.WHITE))
            text.append(self.text_info.render("Avoid them, or jump on them.", True, self.WHITE))
            text.append(self.text_info.render("Get to the exit to advance.", True, self.WHITE))
            text.append(self.text_info.render("press Enter to start.", True, self.WHITE))

        elif self.current_level == 3:
            text.append(self.text_info.render("Monsters!", True, self.WHITE))
            text.append(self.text_info.render("Run for your life!", True, self.WHITE))
            text.append(self.text_info.render("Get to the exit!", True, self.WHITE))
        
        for i, line in enumerate(text):
            text_rect = line.get_rect(center=(self.WIDTH/2, self.HEIGHT/4 + i*68))
            self.screen.blit(line, (text_rect))
    

    def scroll_map(self):

        #moving right
        if self.player1.rect.x > self.WIDTH*2/3 and self.player1.velocity.x > 0:
        
            self.offset_x = min( self.offset_x + self.player1.velocity.x, len(self.map[0])*self.TILE_SIZE - self.WIDTH )

            if self.offset_x < len(self.map[0])*self.TILE_SIZE - self.WIDTH:
                self.player1.rect.x -= self.player1.velocity.x

        #moving left
        if self.player1.rect.x < self.WIDTH/3 and self.player1.velocity.x < 0:
        
            self.offset_x = max( self.offset_x + self.player1.velocity.x, 0)
            
            if self.offset_x > 0:
                self.player1.rect.x -= self.player1.velocity.x

        #moving down
        if self.player1.rect.center[1] > self.HEIGHT*2/3 and self.player1.velocity.y > 0:

            self.offset_y = min( self.offset_y + self.player1.velocity.y, len(self.map)*self.TILE_SIZE - self.HEIGHT)

            if self.offset_y < len(self.map)*self.TILE_SIZE - self.HEIGHT:
                self.player1.rect.y -= self.player1.velocity.y

        #moving up
        if self.player1.rect.center[1] < self.HEIGHT/3 and self.player1.velocity.y < 0:

            self.offset_y = max( self.offset_y + self.player1.velocity.y, 0 )

            if self.offset_y > 0:
                self.player1.rect.y -= self.player1.velocity.y
    

    def draw_UI(self):
        lives_text = self.text_ui.render("Lives: ", True, self.WHITE)
        self.screen.blit(lives_text, (10, 10))

        robot_head = self.images["robot"]
        for i in range(Player.lives):
            self.screen.blit( robot_head, (80 + 40*i, 4), (0, 0, robot_head.get_width() , 35) )
        
        coins_text = self.text_ui.render(f"Coins: {self.coins_collected}", True, self.WHITE)
        self.screen.blit(coins_text, (10, 50))


class Player(pygame.sprite.Sprite):
    lives = 3

    def __init__(self, image, pos_x = 0, pos_y = 0, layer = 2):
        super().__init__()
        self.image = pygame.transform.scale_by(image, 0.75)
        self.rect = pygame.Surface.get_rect(self.image)
        self.layer = layer

        self.grounded = False
        self.dropping = False
        self.invulnerable = False
        self.inv_timer = 0

        self.position = pos_x, pos_y
        self.rect.topleft = self.position
        self.velocity = vec(0,0)
        self.acceleration = 0.25

        self.gravity = 0.75
        self.max_gravity = 10
        self.max_speed = 4
        self.friction = 0.15
        self.jump_strength = 10
    

    def update(self):
        
        #flash if invulerable
        if self.invulnerable:
            if (self.inv_timer -10) % 20 == 0:
                self.image.set_alpha(100)
            elif self.inv_timer % 20 == 0:
                self.image.set_alpha()

            self.inv_timer -= 1
            if self.inv_timer == 0:
                self.invulnerable = False
                self.image.set_alpha()



        #get keys currently pressed down
        buttons_pressed = pygame.key.get_pressed()

        #horizontal movement
        if buttons_pressed[pygame.K_LEFT]:
            self.velocity.x = max(self.velocity.x - self.acceleration, -self.max_speed)
        elif buttons_pressed[pygame.K_RIGHT]:
            self.velocity.x = min(self.velocity.x + self.acceleration, self.max_speed)
        else:
            self.velocity.x = self.velocity.x - self.friction*self.velocity.x
        
        #gravity
        if not self.grounded:
            self.velocity.y = min( self.velocity.y + self.gravity, self.max_gravity)

        #jumping
        elif buttons_pressed[pygame.K_UP] and self.grounded:
            self.velocity.y = max( self.velocity.y - self.jump_strength, - self.jump_strength )
            self.grounded = False
        
        #dropping
        if buttons_pressed[pygame.K_DOWN]:
            self.dropping = True
            self.grounded = False
        else:
            self.dropping = False

        #update position
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        #Restrict player to window
        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > game.WIDTH:
            self.rect.right = game.WIDTH

        if self.rect.y > len(game.map)*game.TILE_SIZE:
            self.rect.y = len(game.map)*game.TILE_SIZE - 5*game.TILE_SIZE
        
        if self.rect.bottom + 50 < 0:
            self.velocity.y = max( 0, self.velocity.y )
    

class Platform(pygame.sprite.Sprite):
    color = (75,50,10)

    def __init__(self, side , pos_x = 0, pos_y = 0, layer = 3):
        super().__init__()
        self.image = pygame.Surface( (side, side) )
        self.image.fill( self.color )
        self.layer = layer
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = pygame.Surface.get_rect( self.image )
        self.rect.topleft = (pos_x, pos_y)
    

    def update(self):
        self.rect.x = self.pos_x - game.offset_x
        self.rect.y = self.pos_y - game.offset_y


class Wall(pygame.sprite.Sprite):
    color = (75,75,75)

    def __init__(self, side , pos_x = 0, pos_y = 0, layer = 3):
        super().__init__()
        self.image = pygame.Surface( (side, side) )
        self.image.fill( self.color )
        self.layer = layer
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = pygame.Surface.get_rect( self.image )
        self.rect.topleft = (pos_x, pos_y)
    

    def update(self):
        self.rect.x = self.pos_x - game.offset_x
        self.rect.y = self.pos_y - game.offset_y

class Coin(pygame.sprite.Sprite):

    def __init__(self, image , pos_x = 0, pos_y = 0, layer = 0):
        super().__init__()
        self.image = pygame.transform.scale_by(image, 0.75)
        self.layer = layer
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = pygame.Surface.get_rect( self.image )
        self.rect.topleft = (pos_x, pos_y)
    

    def update(self):
        self.rect.x = self.pos_x - game.offset_x
        self.rect.y = self.pos_y - game.offset_y

class Door(pygame.sprite.Sprite):

    def __init__(self, image , pos_x = 0, pos_y = 0, layer = 0):
        super().__init__()
        self.image = pygame.transform.scale_by(image, 0.75)
        self.layer = layer
        self.position = vec( pos_x, pos_y)
        self.rect = pygame.Surface.get_rect( self.image )
        self.rect.topleft = (pos_x, pos_y)
    

    def update(self):
        self.rect.x = self.position.x - game.offset_x
        self.rect.y = self.position.y - game.offset_y

class Monster(pygame.sprite.Sprite):

    def __init__(self, image, x = 0, y = 0, layer = 2):
        super().__init__()
        self.image = pygame.transform.scale_by(image, 0.75)
        self.rect = pygame.Surface.get_rect(self.image)
        self.layer = layer

        self.aggro_range = game.HEIGHT/4
        self.position = vec(x, y)
        self.rect.topleft = self.position

        self.velocity = vec(0,0)
        self.acceleration = 0.02
        self.speed = 0
        self.max_speed = 0.75
        self.friction = 0.15
    
    def update(self):


        #check proximity
        x_dif = game.player1.rect.x - self.rect.x
        y_dif = game.player1.rect.y - self.rect.y
        distance = sqrt( x_dif**2 + y_dif**2 )

        if distance < self.aggro_range:
            if x_dif > 0:
                self.velocity.x = min(self.velocity.x + self.acceleration, self.max_speed)
            elif x_dif < 0:
                self.velocity.x = max(self.velocity.x - self.acceleration, -self.max_speed)
                    
            if y_dif > 0:
                self.velocity.y = min(self.velocity.y + self.acceleration, self.max_speed)
            elif y_dif < 0:
                self.velocity.y = max(self.velocity.y - self.acceleration, -self.max_speed)
        else:
            self.velocity = self.velocity - self.friction * self.velocity

        #update position
        if game.current_level != 3:
            self.position.x += self.velocity.x
            self.position.y += self.velocity.y

            self.rect.x = self.position.x - game.offset_x
            self.rect.y = self.position.y - game.offset_y

        elif game.current_level == 3:
            self.position.x += 0.65
            self.rect.x = self.position.x - game.offset_x


class Trap(pygame.sprite.Sprite):
    color = (255,120,0)

    def __init__(self, side , pos_x = 0, pos_y = 0, velocity= vec(0, 0), layer = 3):
        super().__init__()
        self.image = pygame.Surface([side, side])
        self.image.fill( self.color )
        self.velocity = velocity
        self.position = vec( pos_x, pos_y)
        self.rect = pygame.Rect(self.position[0], self.position[1], side, side)
    
    def update(self):
        if pygame.sprite.spritecollideany(self, game.walls.sprites()):
            self.velocity *= -1
        elif pygame.sprite.spritecollideany(self, game.platforms.sprites()):
            self.velocity *= -1

        self.position += self.velocity

        self.rect.x = self.position.x - game.offset_x
        self.rect.y = self.position.y - game.offset_y

game = ScrollingPlatformer()
game.run()