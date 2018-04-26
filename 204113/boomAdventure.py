
# Project 204113
# Sound from Martin Bersier and LittleRobotSoundFactory
# Art from Kenney.nl

import pygame
import random
from random import randint
from os import path

img_dir = path.join(path.dirname(__file__), 'img')
sound_dir = path.join(path.dirname(__file__), 'sound')

WIDTH = 500
HEIGHT =800
FPS = 60
POWERUP_TIME = 5000

#--------------COLOR---------------#
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
#----------------------------------#


#--------initialize pygame---------#
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boom Adventure")
clock = pygame.time.Clock()
#----------------------------------#

#-------------Game UI--------------#

font_name = pygame.font.match_font('Superstar X')
#fontNebulousRegular = pygame.font.match_font('Nebulous-Regular')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)
#----------------------------------#


#-------------Classes--------------#
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (51, 44))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        # timeout for powerups
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()        

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        # hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.86 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image.convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -100 or self.rect.right > WIDTH + 100:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 4

    def update(self):
        self.rect.y += self.speedy
        # kill if it moves off the bottom of the screen
        if self.rect.top > HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks() 
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
#------------------------------------#






def button(x, y, w, h):
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    pygame.draw.rect(screen, BLACK, (x, y, w, h), 1)
    if x + w > mouse_pos[0] and x < mouse_pos[0]:
        if mouse_click[0] == 1:
            return True
    if  y + h > mouse_pos[1] and y < mouse_pos[1]:
        if mouse_click[0] == 1:
            return True

def save_hg(new=None):
    hs_folder = path.join(path.dirname(__file__))
    if new is None:
        with open(path.join(hs_folder, 'sch.txt'), 'r') as f:
            try:
                highscore = int(f.read())
            except:
                highscore = 0
        return highscore
    else:
        with open(path.join(hs_folder, 'sch.txt'), 'w') as f:
            f.write(str(new))
            f.close()


def game_over_scr():
    hightscore = save_hg()
    combow = randint(0,50)
    up = score+combow
    screen.blit(background, background_rect)
    draw_text(screen, 'GAME OVER', 70, WIDTH / 2, 120)
    
    draw_text(screen, 'EXIT',30, WIDTH / 2, 530)
    draw_text(screen, 'AGAIN', 30, WIDTH / 2, 480)
    
    draw_text(screen, 'COMBO : ' + str(combow) , 35,WIDTH / 2, 345)
    
    draw_text(screen, 'YOUR SCORE  : ' + str(up)   , 35,WIDTH / 2, 390)
    
        
    if up > hightscore:
        
        hightscore = up
        draw_text(screen, 'NEW HIGH SCORE: ' + str(hightscore) , 35, WIDTH / 2, 300)
        
        save_hg(hightscore)
    else :
        draw_text(screen, 'HIGH SCORE: ' + str(hightscore),35, WIDTH / 2, 300)


     
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pos()[0] >= 200 and pygame.mouse.get_pos()[1] >= 480:
                    if pygame.mouse.get_pos()[0] <= 290 and pygame.mouse.get_pos()[1] <=520:

                        waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pos()[0] >= 210 and pygame.mouse.get_pos()[1] >= 530:
                    if pygame.mouse.get_pos()[0] <= 275 and pygame.mouse.get_pos()[1] <=565:
                        pygame.quit()
                        quit()
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

                
        pygame.display.update()
        
stars_bg_list1 = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for x in range(150)]
stars_bg_list2 = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for x in range(50)]


def show_go_screen():
    hightscore = save_hg()
    
    screen.blit(background, background_rect)
    
    draw_text(screen, "BOOM!", 91, WIDTH / 2, 200)
    draw_text(screen, "Adventure", 50, WIDTH / 2, 300)
    draw_text(screen, 'START ' , 30, WIDTH / 2, 480)
    draw_text(screen, 'EXIT', 30, (WIDTH / 2)-5, 530)
    draw_text(screen, "Move: arrow key to right/left ", 18, WIDTH / 2, 600)
    draw_text(screen, "Shoot: space bar ", 18, WIDTH / 2, 580)
    draw_text(screen, 'HIGH SCORE: ' + str(hightscore),20, WIDTH / 2, HEIGHT / 2.3 / 4)

    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pos()[0] >= 200 and pygame.mouse.get_pos()[1] >= 480:
                    if pygame.mouse.get_pos()[0] <= 290 and pygame.mouse.get_pos()[1] <=520:

                        waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pos()[0] >= 210 and pygame.mouse.get_pos()[1] >= 530:
                    if pygame.mouse.get_pos()[0] <= 275 and pygame.mouse.get_pos()[1] <=565:
                        pygame.quit()
                        quit()
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        
        pygame.display.update()


#------------Load all game graphics---------------#
background = pygame.image.load(path.join(img_dir, "mainBG.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, "playerShip.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, "laserRed07.png")).convert()

meteor_images = []
meteor_list =['meteorGrey_big1.png','meteorGrey_big2.png',
              'meteorGrey_med1.png','meteorGrey_med2.png',
              'meteorGrey_small1.png','meteorGrey_med2.png',
              'meteorGrey_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, img)).convert_alpha())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()
#---------------------------------------------------#


#-----------------Load all game sounds----------------------#
shoot_sound = pygame.mixer.Sound(path.join(sound_dir, 'Laser_Shoot28.wav'))
shield_sound = pygame.mixer.Sound(path.join(sound_dir, 'Shield6.wav'))
power_sound = pygame.mixer.Sound(path.join(sound_dir, 'Powerup10.wav'))
expl_sounds = []
for sound in ['expl3.wav', 'expl6.wav', 'Explosion7.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_dir, sound)))
player_die_sound = pygame.mixer.Sound(path.join(sound_dir, "Explosion11.wav"))
pygame.mixer.music.load(path.join(sound_dir, 'mainBG.mp3'))
pygame.mixer.music.set_volume(0.4)

pygame.mixer.music.play(loops=-1)
#------------------------------------------------------------#


#------------------------------Game loop--------------------------------#
game_over = True
running = True
while running:
    if game_over:
        pygame.mixer.music.unpause()
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            newmob()
        score = 0

    # keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update()

    # check to see if a bullet hit a mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    #check to see if a mob hit the player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    # check to see if player hit a powerup
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            shield_sound.play()
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()
            power_sound.play()

    # if the player died and the explosion has finished playing
    if player.lives == 0 and not death_explosion.alive():
        
        game_over = True
        pygame.mixer.music.pause()
        game_over_scr()
        continue

    # Draw / render
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    # *after* drawing everything, flip the display
    pygame.display.flip()
#---------------------------------------------------------------------------#


pygame.quit()
