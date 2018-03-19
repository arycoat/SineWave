
import gym
from gym.utils import seeding
import numpy as np
import time
import math
import pygame
import threading

class mover(object):
    def __init__(self):
        # The Mover tracks position, velocity, and acceleration 
        self.velocity = 0
        self.position = 0
        # The Mover's maximum speed
        self.speed = 2
        self.magnitude = 3
        
    def update(self):
        self.velocity = self.magnitude * math.sin((1/4)*(2*math.pi) + self.speed * time.time())
        self.position += self.velocity
        #print (self.position)
        threading.Timer(1/60,self.update).start()
        
    def state(self):
        return (self.position, self.velocity)
        
class SineWave(gym.Env):
    
    def __init__(self):
        
        pygame.init()
        # Set the window title
        pygame.display.set_caption("Sine Wave")
        
        self.background_color = pygame.Color(0, 0, 0, 0)
        self.width = 640
        self.height = 480
        
        # Make a screen to see
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill(self.background_color)

        # Make a surface to draw on
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(self.background_color)

        length = 500
        self.history = np.zeros(length)
        self.mover = mover()
        
        self.seed()
        self.viewer = None
        self.state = None
        self.clock = pygame.time.Clock()
        
        threading.Timer(1/60,self.mover.update).start()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
    
    def reset(self):
        self.state = np.zeros(2)
        self.done = False
        self.steps_beyond_done = None
        return np.array(self.state)
    
    def step(self, action):
        y0, y0_dot = self.state
        
        y1, dy = self.mover.state()
        
        self.history = np.concatenate([[y1], self.history[:self.history.size-1]])
        
        #force = self.force_mag if action==1 else -self.force_mag
        #costheta = math.cos(theta)
        #sintheta = math.sin(theta)
        #temp = (force + self.polemass_length * theta_dot * theta_dot * sintheta) / self.total_mass
        #thetaacc = (self.gravity * sintheta - costheta* temp) / (self.length * (4.0/3.0 - self.masspole * costheta * costheta / self.total_mass))
        #xacc  = temp - self.polemass_length * thetaacc * costheta / self.total_mass
        
        #x  = x + self.tau * x_dot
        #x_dot = x_dot + self.tau * xacc
        #theta = theta + self.tau * theta_dot
        #theta_dot = theta_dot + self.tau * thetaacc
        
        self.state = (y1, dy)
        #done =  x < -self.x_threshold \
        #        or x > self.x_threshold \
        #        or theta < -self.theta_threshold_radians \
        #        or theta > self.theta_threshold_radians

        if not self.done:
            reward = 1.0
        elif self.steps_beyond_done is None:
            # Pole just fell!
            self.steps_beyond_done = 0
            reward = 1.0
        else:
            if self.steps_beyond_done == 0:
                logger.warn("You are calling 'step()' even though this environment has already returned done = True. You should always call 'reset()' once you receive 'done = True' -- any further steps are undefined behavior.")
            self.steps_beyond_done += 1
            reward = 0.0

        return np.array(self.state), reward, self.done, {}
    
    def render(self, mode='human'):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
                print ("Done")
                break

        # Redraw the background
        self.surface.fill(self.background_color)

        y = self.history[0]
        pos = (600, int(self.height/2 + y))
        pygame.draw.circle(self.surface, (255, 255, 255), pos, 2) # WHITE

        # Update sine wave
        for x in range(0, self.history.size):
            self.surface.set_at((600-x, int(self.height/2) + int(self.history[x])), pygame.Color(255, 255, 0, 0))

        # Put the surface we draw on, onto the screen
        self.screen.blit(self.surface, (0, 0))

        # Show it.
        pygame.display.flip()
        pygame.time.Clock().tick(60)
        
    def close(self):
        pygame.quit()