# Status: Abgeschlossen und funktioniert! :-D
# Start des Projekts: 16.08.2022
# Ende des Projekts: 25.08.2022
# Hintergrundmusik von bensound.com,
# Soundeffekte von Scratch.
import pygame
import sys
import random
import time

pygame.init()
screen = pygame.display.set_mode([1930, 1060])
pygame.display.set_caption("Weltraum Shooter")
clock = pygame.time.Clock()

pygame.mixer.music.load("./Sounds/epic.mp3")
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(0.5)

laser1 = pygame.mixer.Sound("./Sounds/laser1.wav")
pygame.mixer.Sound.set_volume(laser1, 0.5)
laser2 = pygame.mixer.Sound("./Sounds/laser2.wav")
damage = pygame.mixer.Sound("./Sounds/damage.wav")
collect = pygame.mixer.Sound("./Sounds/collect.wav")
new_highscore = pygame.mixer.Sound("./Sounds/new_highscore.wav")

class Star():
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed

    def moveDown(self):
        if self.y >= 1060:
            self.y = 0
            self.x = random.randint(0, 1930)
        self.y += self.speed

    def paint(self):
        pygame.draw.ellipse(screen, (255, 255, 255), (self.x, self.y, 5, 5))

class Heart():
    def __init__(self, speed):
        self.x = 0
        self.y = 0
        self.speed = speed

        self.alive = False
        self.heart = pygame.image.load("./Graphics/Hearts/heart.png")

    def spawn(self, atX, atY):
        self.x = atX
        self.y = atY
        self.alive = True

    def moveDown(self):
        if self.alive:
            if self.y >= 1060:
                self.alive = False
            self.y += self.speed

    def hide(self):
        self.alive = False

    def paint(self):
        if self.alive:
            screen.blit(self.heart, (self.x, self.y))

class Shot():
    def __init__(self, speed):
        self.speed = speed

        self.x = 0
        self.y = 0
        self.direction = "none"
        self.by = "none"
        self.alive = False
        self.shot = pygame.image.load("./Graphics/Shot/laser.png")

    def prepareShot(self, x, y, direction, by):
        self.x = x
        self.y = y
        self.direction = direction
        self.by = by
        self.alive = True

        if by == "player":
            pygame.mixer.Sound.play(laser2)
        else:
            pygame.mixer.Sound.play(laser1)

    def move(self):
        if self.alive:
            if self.y >= 1060 and self.direction == "bottom" or self.y <= 0 and self.direction == "top":
                self.alive = False
            if self.direction == "top":
                self.y -= self.speed
            else:
                self.y += self.speed

    def hide(self):
        self.alive = False

    def paint(self):
        if self.alive:
            screen.blit(self.shot, (self.x, self.y))

class Player():
    def __init__(self, lives, x, y):
        self.player = pygame.image.load("./Graphics/Player/player.png")
        self.lives = lives
        self.x = x
        self.y = y

    def move(self):
        self.x = pygame.mouse.get_pos()[0]
        self.y = pygame.mouse.get_pos()[1]

    def shot(self):
        for shot in shots:
            if not shot.alive:
                shot.prepareShot(self.x, self.y, "top", "player")
                break

    def damage(self):
        self.lives -= 1
        pygame.mixer.Sound.play(damage)

    def newLive(self):
        pygame.mixer.Sound.play(collect)
        if self.lives < 6:
            self.lives += 1

    def paintLives(self):
        if self.lives == 6: screen.blit(pygame.image.load("./Graphics/Player/lives/6_lives.png"), (1720, 5))
        elif self.lives == 5: screen.blit(pygame.image.load("./Graphics/Player/lives/5_lives.png"), (1720, 5))
        elif self.lives == 4: screen.blit(pygame.image.load("./Graphics/Player/lives/4_lives.png"), (1720, 5))
        elif self.lives == 3: screen.blit(pygame.image.load("./Graphics/Player/lives/3_lives.png"), (1720, 5))
        elif self.lives == 2: screen.blit(pygame.image.load("./Graphics/Player/lives/2_lives.png"), (1720, 5))
        elif self.lives == 1: screen.blit(pygame.image.load("./Graphics/Player/lives/1_lives.png"), (1720, 5))
        else:
            screen.blit(pygame.image.load("./Graphics/Player/lives/0_lives.png"), (1720, 5))
            gameOver()

    def paint(self):
        screen.blit(self.player, (self.x - 65, self.y - 65))

class Enemy():
    def __init__(self, speed, lives, type):
        self.speed = speed
        self.lives = lives
        self.type = type
        self.enemy = pygame.image.load("./Graphics/Enemys/" + self.type + ".png")

        self.x = 0
        self.y = 0
        self.ticksAfterShot = 0
        self.alive = False
        self.enemy = pygame.image.load("./Graphics/Enemys/enemy1.png")

    def spawn(self, atX, atY, lives, type):
        self.x = atX
        self.y = atY
        self.lives = lives
        self.type = type
        self.enemy = pygame.image.load("./Graphics/Enemys/" + self.type + ".png")
        self.alive = True

    def move(self):
        if self.alive:
            if self.y >= 1060:
                self.alive = False
            self.y += self.speed

    def shot(self):
        if self.ticksAfterShot > 0 and self.ticksAfterShot < 50:
            self.ticksAfterShot += 1
        else:
            self.ticksAfterShot = 0
        if self.alive and self.y > 0 and self.ticksAfterShot == 0:
            if random.randint(0, 50) == 1:
                for shot in shots:
                    if not shot.alive:
                        shot.prepareShot(self.x + 50, self.y, "bottom", "enemy")
                        self.ticksAfterShot = 1
                        break

    def damage(self):
        self.lives -= 1
        if self.lives == 0:
            self.alive = False
        if self.type == "enemy2" and self.lives == 1:
            self.enemy = pygame.image.load("./Graphics/Enemys/enemy2_broken.png")

    def paint(self):
        if self.alive:
            screen.blit(self.enemy, (self.x, self.y))

def testOfCollision(myX, myY, otherObjectName, otherX, otherY):
    if otherObjectName == "player_shot" and (((myX - otherX) > -105) and ((myX - otherX) < 5)) and ((myY - otherY) > 10):
        return True
    elif otherObjectName == "enemy_shot" and (((myX - otherX) > -105) and ((myX - otherX) < 60)) and ((myY - otherY) < 10):
        return True
    elif otherObjectName == "heart" and (((myX - otherX) > -40) and ((myX - otherX) < 100)) and ((myY - otherY) > -30) and ((myY - otherY) < 60):
        return True
    else:
        return False

def gameOver():
    screen.fill((0, 0, 0))
    screen.blit(pygame.image.load("./Graphics/Game Over/game_over_text.png"), (780, 450))
    pygame.display.update()
    time.sleep(2)
    sys.exit("--- Game Over ---\nBitte erneut starten")

player = Player(6, 0, 0)

font = pygame.font.SysFont("arial", 50)
score = 0

with open("./highscore.txt", "r+", encoding="utf-8") as file:
    highscore = file.readline()

shots = []
for i in range(10):
    shots.append(Shot(30))
hearts = []
for i in range(1):
    hearts.append(Heart(7.5))
stars = []
for i in range(10):
    stars.append(Star(random.randint(0, 1930), random.randint(0, 1060), 10))
enemys = []
for i in range(3):
    enemys.append(Enemy(10, 1, "enemy1"))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN: player.shot()

    screen.fill((0, 0, 0))
    for shot in shots:
        shot.move()
        if testOfCollision(player.x, player.y, "enemy_shot", shot.x, shot.y) and shot.by == "enemy" and shot.alive:
            player.damage()
            shot.hide()
        shot.paint()
    for heart in hearts:
        if heart.alive:
            heart.moveDown()
            if testOfCollision(player.x, player.y, "heart", heart.x, heart.y) and heart.alive:
                player.newLive()
                heart.hide()
        else:
            heart.spawn(random.randint(0, 1800), random.randint(-20000, -5000))
        heart.paint()
    for star in stars:
        star.moveDown()
        star.paint()
    for enemy in enemys:
        if enemy.alive:
            enemy.move()
            enemy.shot()
            for shot in shots:
                if testOfCollision(enemy.x, enemy.y, "player_shot", shot.x, shot.y) and shot.by == "player" and shot.alive:
                    enemy.damage()
                    if not enemy.alive and enemy.type == "enemy1":
                        score += 10
                    elif not enemy.alive and enemy.type == "enemy2":
                        score += 30
                    shot.hide()
                    if score > int(highscore):
                        with open("./highscore.txt", "w", encoding="utf-8") as file:
                            file.write(str(score))
                            highscore = score
                            pygame.mixer.Sound.play(new_highscore)
        else:
            if random.randint(0, 5) == 1:
                enemy.spawn(random.randint(0, 1800), random.randint(-2000, 0), 2, "enemy2")
            else:
                enemy.spawn(random.randint(0, 1800), random.randint(-2000, 0), 1, "enemy1")
        enemy.paint()
    player.move()
    player.paint()
    player.paintLives()

    highScoreText = font.render("Höchstpunktzahl: " + str(highscore), False, (255, 255, 255))
    highScoreTextRect = highScoreText.get_rect()
    highScoreTextRect.center = (170 + (11 * len(str(highscore))), 25)
    screen.blit(highScoreText, highScoreTextRect)

    scoreText = font.render("Punkte: " + str(score), False, (255, 255, 255))
    scoreTextRect = scoreText.get_rect()
    scoreTextRect.center = (900 + (11 * len(str(score))), 25)
    screen.blit(scoreText, scoreTextRect)

    pygame.display.update()
    clock.tick(60)
