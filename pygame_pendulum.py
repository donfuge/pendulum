# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 21:27:38 2020

@author: fulop
"""

####

import pygame

import numpy as np
####


vec = pygame.math.Vector2
ACC = 0.5e-3
FRIC = 0.1
WIDTH = 1000
PROJ_FRIC = 0.01
G = - 0.1
P_YVEL = -10


class Enemy(pygame.sprite.Sprite):
    def __init__(self, size=(50, 50), pos=vec(10, 400), color=(0, 255, 0), vel=vec(0, 0)):
        super().__init__()
        self.surf = pygame.Surface(size)
        self.color = color
        self.surf.fill(self.color)
        self.rect = self.surf.get_rect(center=pos)
        self.health = 100.0
        self.pos = pos
        self.vel = vel
        # self.vel.y = P_YVEL
        self.acc = vec(0, 0)
        self.representation = self.rect

    def move(self, **kwargs):

        self.pos += self.vel

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos
    def hit(self, hitpoints = 1):
        self.health -= hitpoints
        if self.health >= 0:
            self.color = (0,self.health /100 * 255,0)
            self.surf.fill(self.color)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, size=(10, 10), pos=vec(10, 400), color=(255, 255, 40), vel=vec(0, 0)):
        super().__init__()
        self.surf = pygame.Surface(size)
        self.surf.fill(color)
        self.rect = self.surf.get_rect(center=pos)

        self.pos = pos
        self.vel = 1.5 * vel  # boosting the projectiles
        # self.vel.y = P_YVEL
        self.acc = vec(0, 0)
        self.representation = self.rect

    def move(self, **kwargs):
        self.acc = vec(0, 0)

        self.acc.x += self.vel.x * (-1) * PROJ_FRIC
        self.acc.y += self.vel.y * (-1) * PROJ_FRIC - G
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos


class Pendulum(pygame.sprite.Sprite):
    def __init__(self, pygame_screen, size=(20, 20), center_pos=(200, 200), color=(128, 255, 40), vel=(0, 0), L=150, theta=np.pi/3):
        super().__init__()
        self.surf = pygame.Surface(size)
        # self.surf.fill(color)
        self.surf.fill((255, 255, 255))
        self.center_pos = vec(center_pos)
        self.L = L
        self.theta = theta
        self.theta_dot = 0
        self.pygame_screen = pygame_screen

        self.circle_pos = vec(0, 0)

        self.circle_pos.x = self.center_pos.x + self.L * np.sin(self.theta)
        self.circle_pos.y = self.center_pos.y + self.L * np.cos(self.theta)

        self.rect = self.surf.get_rect(center=self.circle_pos)
        self.circle = pygame.draw

        self.vel = vec(0, 0)
        self.vel.x = self.L * self.theta_dot * np.cos(self.theta)
        self.vel.y = self.L * self.theta_dot * (-1) * np.sin(self.theta)

        self.representation = self.rect
        self.draw()

    def pend(self, y, t, b, c):
        theta, omega = y
        dydt = [omega, -b*omega - c*np.sin(theta)]
        return dydt

    def move(self, pressed_keys):
        self.acc = vec(0, 0)

        if pressed_keys[pygame.K_LEFT]:
            self.theta_dot -= np.cos(self.theta) * ACC
        if pressed_keys[pygame.K_RIGHT]:
            self.theta_dot += np.cos(self.theta) * ACC

        y = np.asarray([self.theta, self.theta_dot])

        dydt = self.pend(y, 0, 0, 1e-3)

        dydt = np.asarray(dydt)

        delta_t = 1

        y += dydt * delta_t  # Euler update

        self.theta = y[0]
        self.theta_dot = y[1]
        self.circle_pos.x = self.center_pos.x + self.L * np.sin(self.theta)
        self.circle_pos.y = self.center_pos.y + self.L * np.cos(self.theta)

        self.vel.x = self.L * self.theta_dot * np.cos(self.theta)
        self.vel.y = self.L * self.theta_dot * (-1) * np.sin(self.theta)

        self.rect = self.surf.get_rect(center = self.circle_pos)

    def draw(self):
        pygame.draw.line(self.pygame_screen, (255, 255, 255), self.center_pos,
                         (int(self.circle_pos.x), int(self.circle_pos.y)), 1)
        pygame.draw.circle(self.pygame_screen, (128, 40, 50),
                           (int(self.circle_pos.x), int(self.circle_pos.y)), 10)
        # self.pygame_screen.blit(self.surf, self.circle)


class PygView(object):

    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
        """
        pygame.init()
        pygame.display.set_caption(
            "Press Left/Right to control the pendulum, SPACE to shoot, ESC to quit")
        self.width = width
        self.height = height
        #self.height = width // 4
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.holdoff = 0.1  # holdoff time between shots
        self.last_shot = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        self.pendulum = Pendulum(self.screen)
        self.all_sprites = pygame.sprite.Group()
        # self.all_sprites.add(self.pendulum)
        self.projectile_no = 0
        self.projectile_no_max = 200
        self.projectiles = pygame.sprite.Group()

        self.enemies = pygame.sprite.Group()

    def run(self):
        """The mainloop
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0
            # self.draw_text("FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS \r theta: {:6.03}".format(
            #                 self.clock.get_fps(), " ", self.playtime, self.pendulum.theta))

            
            self.screen.blit(self.background, (0, 0))

            # spawn enemy
            if len(self.enemies) == 0:
                new_enemy = Enemy(
                    pos=vec(self.width, self.pendulum.circle_pos.y + np.random.randint(-100, 100)), vel=vec(-1, 0))
                self.enemies.add(new_enemy)
                self.all_sprites.add(new_enemy)

            # event handling (key press)
            pressed_keys = pygame.key.get_pressed()



        # launch projectile if SPACE is pressed

            if pressed_keys[pygame.K_SPACE] and self.projectile_no < self.projectile_no_max and self.playtime - self.last_shot >= self.holdoff:

                self.projectile_no += 1
                new_projectile = Projectile(
                    pos=self.pendulum.circle_pos.xy, vel=self.pendulum.vel.xy)
                self.projectiles.add(new_projectile)
                self.all_sprites.add(new_projectile)

                self.last_shot = self.playtime

            # move the pendulum and the projectiles (physics)

            self.pendulum.move(pressed_keys)

            for proj in self.projectiles:
                proj.move()

                # destroy projectiles
                if proj.pos.y >= self.height - 10:
                    self.projectiles.remove(proj)
                    self.all_sprites.remove(proj)

            for enemy in self.enemies:
                enemy.move()

                # collisions: check if enemy is hit by projectile(s)

                collided = pygame.sprite.spritecollideany(
                    enemy, self.projectiles)

                if collided:
                    enemy.hit(50)
                    self.projectiles.remove(collided)
                    self.all_sprites.remove(collided)
                if enemy.health <= 0:
                    self.all_sprites.remove(enemy)
                    self.enemies.remove(enemy)


            # draw all entities (pendulum, projectiles)

            for entity in self.all_sprites:
                self.screen.blit(entity.surf, entity.representation)

            self.pendulum.draw()
            self.draw_text("Ammo:{}".format(
                self.projectile_no_max - self.projectile_no), pos=(self.width - 200, 15))

            # collision: check if any enemies hit the pendulum
            collided = pygame.sprite.spritecollide(
                self.pendulum, self.enemies, dokill=False)

            if collided:
                self.draw_text("GAME OVER")
                pygame.time.delay(10)
                pygame.display.flip()
                pygame.event.clear()
                event = pygame.event.wait()
                running = False

            pygame.display.flip()

        pygame.quit()

    def draw_text(self, text, pos=None):
        fw, fh = self.font.size(text)  # fw: font width,  fh: font height
        surface = self.font.render(text, True, (255, 255, 255))
        if pos == None:
            pos = ((self.width - fw) // 2, (self.height - fh) // 2)
        self.screen.blit(surface, pos)

    def game_over(self):
        self.draw_text("GAME OVER")
        event = pygame.event.wait()
####


if __name__ == '__main__':

    # call with width of window and fps
    PygView(WIDTH, 400, fps=60).run()
