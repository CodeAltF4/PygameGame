import pygame
import configparser
import time
import random


#initializing the configparser
config = configparser.ConfigParser()
config.read("config.ini")

#initializing game
(numpass, numfail) = pygame.init()
print(f"Successfull inits: {numpass}, Unsuccessfull inits: {numfail}")


#window
displayw = int(config["WINDOW"]["display_width"])
displayh = int(config["WINDOW"]["display_height"])
displaycolor = tuple(map(int, config["WINDOW"]["display_color"].split(", "))) #turns 100, 100, 100 into (100, 100, 100)
root = pygame.display.set_mode((displayw, displayh))

#load sprites
player_sprite = pygame.image.load(str(config["PLAYER"]["player_sprite"])).convert_alpha()
playershot_sprite = pygame.image.load(str(config["PLAYERSHOT"]["playershot_sprite"]))
rock_sprite = pygame.image.load(str(config["ROCK"]["rock_sprite"]))

player_health_sprite = pygame.transform.scale(pygame.image.load(str(config["DISPLAY"]["health_sprite"])), (25, 25))

extra_life_sprite = pygame.transform.scale(pygame.image.load(str(config["POWERUP"]["extra_life_sprite"])), (25, 25))
                                  
#clock
clock = pygame.time.Clock()
fps = 60
target_fps = 60

class MainRun(object):
    def __init__(self):
        self.main()
        
    def main(self):
        #time for independant framerate
        prev_time = time.time()        
        
        #game loop
        running = True
        while running:
            #independant framerate to make movement the same speed independant from the framerate
            now = time.time()
            dt = now-prev_time
            prev_time = now
            
            root.fill(displaycolor)
            
            #Event handling
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                #window boundaries
                if (player.ypos - player.yspeed) > 0:
                    player.ypos -= player.yspeed * dt * target_fps
                
            if keys[pygame.K_a]:
                #window boundaries
                if (player.xpos - player.xspeed) > 0:
                    player.xpos -= player.xspeed * dt * target_fps
                
            if keys[pygame.K_s]:
                #window boundaries
                if (player.ypos + player.ysize + player.yspeed) < displayh:
                    player.ypos += player.yspeed * dt * target_fps
                
            if keys[pygame.K_d]:
                #window boundaries
                if (player.xpos + player.xsize + player.xspeed) < displayw:
                    player.xpos += player.xspeed * dt * target_fps
            
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            
                if event.type == pygame.KEYDOWN:
                    #player shoot
                    if event.key == pygame.K_SPACE:
                        if len(player_shot.bullets) < 5:
                            player_shot.bullets.append([player.xpos+(player.xsize/2)-(playershot_sprite.get_width()/2),
                                                        player.ypos,
                                                        playershot_sprite.get_width(),
                                                        playershot_sprite.get_height()])
            
            #moving and generating the space rocks
            if random.randint(0, 100) == 0:
                spacerock.generate_rock_data()
                
            
            #generating a extra life
            if len(player.health) < 3:
                if random.randint(0, 400) == 0:
                    extra_life.generate_data()
                    
                
            #moving objects
            player_shot.move(dt)
            spacerock.move(dt)
            extra_life.move_life(dt)
            
            #detecting collisions
            for rock in spacerock.rocks:
                #rock and spaceship
                collision.collision_detect_rock_ship(rock)
                
                for bullet in player_shot.bullets:
                    #rock and bullet
                    collision.collision_detect_rock_shot(rock, bullet)
                    
                    for life in extra_life.extra_life_list:
                        #bullet and extra life
                        collision.collision_detect_extralife_shot(bullet, life)
            
            #drawing objects
            spacerock.draw()
            extra_life.draw()
            player_shot.draw()
            player.draw()
            
            #rendering player lives and points
            player.display_lives()
            player.display_points()
            
            pygame.display.update()
            clock.tick(fps)
            
            #if player has 0 lives game is lost
            if len(player.health) <= 0:
                print("Game over")
                self.game_over_menu()
    
    
    def game_over_menu(self):       
        #game loop
        running = True
        while running:
            root.fill(displaycolor)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.__init__()  
                        player_shot.__init__()
                        spacerock.__init__()                      
                        self.main()
            
            font1 = pygame.font.Font(None, 50)
            font2 = pygame.font.Font(None, 30)
            font3 = pygame.font.Font(None, 20)
                        
            string1 = "Game over"
            string2 = str(f"You got {player.score} points!")
            string3 = "Press space to restart"
            
            string1_width, string1_height = font1.size(string1)
            string2_width, string2_height = font2.size(string2)
            string3_width, string3_height = font3.size(string3)
            
            text1 = font1.render(string1, 1, (255, 255, 255))
            text2 = font2.render(string2, 1, (255, 255, 255))
            text3 = font3.render(string3, 1, (255, 255, 255))
            
            root.blit(text1, ((displayw/2)-(string1_width/2), (displayh/2)-string1_height))
            root.blit(text2, ((displayw/2)-(string2_width/2), (displayh/2)+string2_height))
            root.blit(text3, ((displayw/2)-(string3_width/2), displayh-(string3_height*2)))
            
            pygame.display.update()
            clock.tick(fps)
    
    
    def start_game():
        pass
            

class Player(object):
    def __init__(self):
        self.xsize = player_sprite.get_width()
        self.ysize = player_sprite.get_height()
        self.xpos = displayw/2 - self.xsize/2
        self.ypos = displayh/2 - self.ysize/2
        self.xspeed = int(config["PLAYER"]["player_xspeed"])
        self.yspeed = int(config["PLAYER"]["player_yspeed"])
        self.health = [[5, displayh-player_health_sprite.get_height()-5],
                       [40, displayh-player_health_sprite.get_height()-5],
                       [75, displayh-player_health_sprite.get_height()-5]]
        self.score = 0
        self.font = pygame.font.Font(None, 30)
        
        
    def display_lives(self):
        for life in self.health:
            root.blit(player_health_sprite, (life[0], life[1]))
        
        
    def display_points(self):
        text = self.font.render(str(self.score), 1, (255, 255, 255))
        root.blit(text, (10,10))
    
        
    def draw(self):
        root.blit(player_sprite, (self.xpos, self.ypos))
        
        
class Shot(object):
    def __init__(self):
        self.speed = int(config["PLAYERSHOT"]["shot_speed"])
        self.bullets = []
        
        
    def move(self, dt):
        #moving the bullets
        for b in range(len(self.bullets)):
            self.bullets[b][1] -= self.speed * dt * target_fps
            
        #checking if bullet hits the top
        for bullet in self.bullets[:]:
            if bullet[1] < 0:
                self.bullets.remove(bullet)        
        
        
    def draw(self):
        #rendering the bullets
        for bullet in self.bullets:
            root.blit(playershot_sprite, (bullet[0], bullet[1]))
            
            
class Rock(object):
    def __init__(self):
        self.rocks = []
        self.speedmin = int(config["ROCK"]["rock_speedmin"])
        self.speedmax = int(config["ROCK"]["rock_speedmax"])
        
    
    def generate_rock_data(self):
        #RNG space rock generator
        #generates a size for the rock
        xsize = random.randint(30, 50)
        ysize = random.randint(20, 50)
        
        #generate a random x position
        xpos = random.randint(0, displayw-xsize)
        ypos = 0-ysize
        
        #generates the speed of the rock
        speed = random.randint(self.speedmin, self.speedmax)
        
        self.rocks.append([xpos, ypos, xsize, ysize, speed])
    
    
    def move(self, dt):
        #moving the rocks
        for r in range(len(self.rocks)):
            self.rocks[r][1] += self.rocks[r][4] * dt * target_fps
            
        #checking if rocks have hit the bottom of the window
        for rock in self.rocks[:]:
            if rock[1] > displayh-rock[3]:
                self.rocks.remove(rock)
                #remove 1 life
                del player.health[-1]
                
    
    def draw(self):
        for rock in self.rocks:
            root.blit(pygame.transform.scale(rock_sprite, (rock[2], rock[3])), (rock[0], rock[1]))
            
     
class ExtraLife(object):
    def __init__(self):
        self.life_speedmin = int(config["POWERUP"]["life_speedmin"])
        self.life_speedmax = int(config["POWERUP"]["life_speedmax"])
        
        self.extra_life_list = []
    
    def generate_data(self):
        #generate x and y position and speed
        xpos = random.randint(0, displayw-extra_life_sprite.get_width())
        ypos = 0-extra_life_sprite.get_height()
        speed = random.randint(self.life_speedmin, self.life_speedmax)
        
        self.extra_life_list.append([xpos, ypos, speed])
    
    
    def move_life(self, dt):
        #moving the lifes
        for l in range(len(self.extra_life_list)):
            self.extra_life_list[l][1] += self.extra_life_list[l][2] * dt * target_fps
            
        #checking if powerups have hit the bottom of the window
        for life in self.extra_life_list[:]:
            if life[1] > displayh-extra_life_sprite.get_height():
                self.extra_life_list.remove(life)
                
    
    def draw(self):
        for life in self.extra_life_list:
            root.blit(extra_life_sprite, (life[0], life[1]))

    
class Collision_detection(object):
    def collision_detect_extralife_shot(self, shot, life):
        if pygame.Rect(shot[0], shot[1], shot[2], shot[3]).colliderect(
            pygame.Rect(life[0], life[1], extra_life_sprite.get_width(), extra_life_sprite.get_height())):
            
            #add 1 life
            if len(player.health) == 1:
                player.health.append([40, displayh-player_health_sprite.get_height()-5])
            elif len(player.health) == 2:
                player.health.append([75, displayh-player_health_sprite.get_height()-5])
                
            extra_life.extra_life_list.remove(life)
                
        
    def collision_detect_rock_ship(self, rock):
        #collision detection
        if pygame.Rect(rock[0], rock[1], rock[2], rock[3]).colliderect(
            pygame.Rect(player.xpos, player.ypos, player.xsize, player.ysize)):
            
            spacerock.rocks.remove(rock)
            
            #delete last element in health list
            del player.health[-1]
            
            print("chrashed ship")
            
            
    def collision_detect_rock_shot(self, rock, shot):
        #collision detection
        if pygame.Rect(rock[0], rock[1], rock[2], rock[3]).colliderect(
            pygame.Rect(shot[0], shot[1], shot[2], shot[3])):
            
            spacerock.rocks.remove(rock)
            player_shot.bullets.remove(shot)
            print("Shot hit rock")
            #add points
            player.score += 1


if __name__ == "__main__":
    #initializing objects
    player = Player()
    player_shot = Shot()
    spacerock = Rock()
    extra_life = ExtraLife()
    collision = Collision_detection()
    MainRun()