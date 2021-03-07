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

class Projectile(pygame.sprite.Sprite):
    def __init__(self, size=(10,10), pos = (10,400), color = (255,255,40), vel = (0,0)):
        super().__init__() 
        self.surf = pygame.Surface(size)
        self.surf.fill(color)
        self.rect = self.surf.get_rect(center = pos)
        
        self.pos = pos
        self.vel = 2 * vel
        # self.vel.y = P_YVEL
        self.acc = vec(0,0)
        self.representation = self.rect
        
    def move(self, **kwargs):
        self.acc = vec(0,0)
         
            
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
    def __init__(self, pygame_screen, size=(400,400), pos = (200,200), color = (128,255,40), vel = (0,0), L = 150, theta = np.pi/3):
        super().__init__() 
        self.surf = pygame.Surface(size)
        # self.surf.fill(color)
        self.surf.fill((255,255,255))
        self.pos = vec(pos)
        self.L = L
        self.theta = theta
        self.theta_dot = 0
        self.pygame_screen = pygame_screen
        
        self.circle_pos = vec(0,0)

        self.circle_pos.x = self.pos.x + self.L * np.sin(self.theta)
        self.circle_pos.y = self.pos.y + self.L * np.cos(self.theta)
        
        self.rect =  self.surf.get_rect(center = self.pos)
        self.circle = pygame.draw

        self.vel = vec(0,0)
        self.vel.x = self.L * self.theta_dot * np.cos(self.theta)
        self.vel.y = self.L * self.theta_dot * (-1) * np.sin(self.theta)
        
        self.representation = self.rect
        self.draw()
        
    def pend(self, y, t, b, c):
        theta, omega = y
        dydt = [omega, -b*omega - c*np.sin(theta)]
        return dydt

    def move(self, pressed_keys):
        self.acc = vec(0,0)
         
                
        if pressed_keys[pygame.K_LEFT]:
            self.theta_dot -= ACC
        if pressed_keys[pygame.K_RIGHT]:
            self.theta_dot += ACC     
            
        y = np.asarray( [self.theta, self.theta_dot] )
        
        dydt =  self.pend( y, 0, 0, 1e-3)
        
        dydt = np.asarray(dydt)
        
        delta_t = 1
        
        y += dydt *  delta_t # Euler update
        
        # self.acc.x += self.vel.x * (-1) * FRIC
        # self.vel += self.acc
        # self.pos += self.vel + 0.5 * self.acc
        
        # if self.pos.x > WIDTH:
        #     self.pos.x = 0
        # if self.pos.x < 0:
        #     self.pos.x = WIDTH
     
        self.theta = y[0]
        self.theta_dot = y[1]
        self.circle_pos.x = self.pos.x + self.L * np.sin(self.theta)
        self.circle_pos.y = self.pos.y + self.L * np.cos(self.theta)
        
        self.vel.x = self.L * self.theta_dot * np.cos(self.theta)
        self.vel.y = self.L * self.theta_dot * (-1) * np.sin(self.theta)
        
        
    def draw(self):
      pygame.draw.line(self.pygame_screen, (255,255,255), self.rect.center,
                       (int(self.circle_pos.x),int(self.circle_pos.y)),1)
      pygame.draw.circle(self.pygame_screen, (128, 40, 50), 
                         (int(self.circle_pos.x),int(self.circle_pos.y)), 10)

      # self.pygame_screen.blit(self.surf, self.circle)

     
class PygView(object):
 
 
    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
        """
        pygame.init()
        pygame.display.set_caption("Press Left/Right to control the pendulum, SPACE to shoot, ESC to quit")
        self.width = width
        self.height = height
        #self.height = width // 4
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        self.pendulum = Pendulum(self.screen)
        self.all_sprites = pygame.sprite.Group()
        # self.all_sprites.add(self.pendulum)
        self.projectile_no = 0
        self.projectile_no_max = 100
        self.projectiles = []


 
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
 
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            
            # event handling (key press)
            pressed_keys = pygame.key.get_pressed()
            
            # launch projectile if SPACE is pressed
            # TODO: destroy projectiles
            
            if pressed_keys[pygame.K_SPACE] and self.projectile_no < self.projectile_no_max:
              self.projectile_no += 1
              new_projectile = Projectile(pos = self.pendulum.circle_pos.xy, vel = self.pendulum.vel.xy)
              self.all_sprites.add(new_projectile)
              self.projectiles.append(new_projectile)
            
            # move the pendulum and the projectiles (physics)
            
            self.pendulum.move(pressed_keys)
            
            for proj in self.projectiles:
              proj.move()
            
            # draw all entities (pendulum, projectiles)
            
            for entity in self.all_sprites:
              self.screen.blit(entity.surf, entity.representation)
 
            self.pendulum.draw()
            self.draw_text("Ammo:{}".format(self.projectile_no_max - self.projectile_no), pos = (self.width - 200, 15))

        pygame.quit()
 
 
    def draw_text(self, text, pos = None):
        """Center text in window
        """
        fw, fh = self.font.size(text) # fw: font width,  fh: font height
        surface = self.font.render(text, True, (0, 255, 0))
        if pos == None:
          pos = ((self.width - fw) // 2, (self.height - fh) // 2)
        # // makes integer division in python3
        self.screen.blit(surface, pos )
 
####
 
if __name__ == '__main__':
 
    # call with width of window and fps
    PygView(WIDTH, 400, fps=60).run()