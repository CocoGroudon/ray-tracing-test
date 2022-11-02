from dataclasses import dataclass
from random import randint
import pygame
import math
import numpy as np


@dataclass
class Wall:
    x1: int
    y1: int
    x2: int
    y2: int

    def draw(self, screen):
        pygame.draw.line(screen, (255,255,255), (self.x1, self.y1), (self.x2, self.y2))

class World:
    def __init__(self, dimensions:tuple) -> None:
        self.dimensions = dimensions
        self.walls = []
        self.set_random_walls()
        self.set_border_walls()

    def set_random_walls(self):
        for _ in range(5):
            wall = Wall(randint(0,self.dimensions[0]), randint(0,self.dimensions[1]), randint(0,self.dimensions[0]), randint(0,self.dimensions[1]))
            self.walls.append(wall)
            
    def set_border_walls(self):
        self.walls.append(Wall(0,0,0,self.dimensions[1]))
        self.walls.append(Wall(0,0,self.dimensions[0],0))
        self.walls.append(Wall(self.dimensions[0],0,self.dimensions[0],self.dimensions[1]))
        self.walls.append(Wall(0, self.dimensions[1],self.dimensions[0],self.dimensions[1]))

    def draw(self, surface:pygame.surface):
        for wall in self.walls:
            wall.draw(surface)

class Ray:
    def __init__(self, pos:tuple, angle:float) -> None:
        self.pos = pos
        self.angle = angle
        self.len = 50
    
    def get_pos_for_len(self, len):
     x, y = self.pos

     # find the end point
     endy = y + len * math.sin(math.radians(self.angle))
     endx = x + len * math.cos(math.radians(self.angle))
     return endx, endy

    def check_intersection_with_wall(self, wall:Wall):
        y1 = wall.y1
        x1 = wall.x1

        x2 = wall.x2
        y2 = wall.y2

        x3 = self.pos[0]
        y3 = self.pos[1]

        # auch sehr unschön mit len = 1000
        x4 = self.get_pos_for_len(1000)[0]
        y4 = self.get_pos_for_len(1000)[1]

        den = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
        if den == 0:
            return False
        t = ((x1-x3) * (y3-y4) - (y1-y3) * (x3-x4)) / den
        u = -((x1-x2) * (y1-y3) - (y1-y2) * (x1-x3)) / den

        if (t > 0 and t < 1 and u > 0): # falls es keinen Punkt gibt
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return x,y 
        else:
            return False

    def check_intersection_with_walls(self, walls):
        record_dis = 9999999 # sehr unschön
        record_pos = None
        for wall in walls:
            if pos := self.check_intersection_with_wall(wall):
                dist = math.dist(self.pos, pos)
                if dist < record_dis:
                    record_dis = dist
                    record_pos = pos
        return record_pos

    def get_dist_to_walls(self, walls):
        wallcollision = self.check_intersection_with_walls(walls)
        if wallcollision:
            return math.dist(self.pos, wallcollision)
        return False

    def draw(self, screen:pygame.surface):
        pygame.draw.aaline(screen, (120,120,200), self.pos, self.get_pos_for_len(self.len))

class Player:
    def __init__(self, world_ref:World, pos:tuple[int, int], FOV:int, resulution:int) -> None:
        self.world = world_ref
        self._pos = pos
        self.FOV = FOV
        self.resolution = resulution
        self._angle = 0


        self.look_ray = self.get_new_ray(self._angle)
        self.rays = []
        self.set_FOV_Rays()

    def change_angle(self, new_angle:float):
        before_angle = self._angle
        self._angle = new_angle
        self.look_ray.angle = new_angle
        for ray in self.rays:
            ray.angle += new_angle -before_angle

    def draw(self, surface:pygame.Surface):
        self.draw_rays(surface)
        pygame.draw.aaline(surface, (0,255,0), self.look_ray.pos, self.look_ray.get_pos_for_len(100)) # for the looking direction ray

    def draw_rays(self, surface:pygame.surface):
        for ray in self.rays:
            record = ray.check_intersection_with_walls(self.world.walls)
            if record:
                pygame.draw.aaline(surface, (255,0,0), ray.pos, record)

    def set_FOV_Rays(self):
        for angle in range(-self.FOV//2, self.FOV//2, self.resolution):
            self.rays.append(self.get_new_ray(angle))

    def get_new_ray(self, angle:float):
        return Ray(self._pos, angle)

    def set_pos(self, pos):
        self._pos = np.array(pos)
        self.look_ray.pos = self._pos
        for ray in self.rays:
            ray.pos = self._pos

    def get_pos(self) -> tuple:
        return tuple(self._pos)

class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((1600,900), pygame.RESIZABLE)
        self.backgroundcolor = (0, 43, 53)

        self.world = World((500,500))
        self.player = Player(self.world, pygame.mouse.get_pos(), 90, 1)


    def draw_look_ray(self, surface):
        pygame.draw.aaline(surface, (0,0,255), self.look_ray.pos, self.look_ray.get_pos_for_len(100))


    def draw2d(self, surface:pygame.surface):
        self.player.draw(surface)
        self.world.draw(surface)


    def draw3d(self, sruface:pygame.surface):
        pass

    def draw(self):
        self.screen.fill(self.backgroundcolor)
        
        self.player.set_pos(pygame.mouse.get_pos())
        self.player.change_angle(self.player._angle+1)
        
        self.draw2d(self.screen)

        
    def handle_keyinputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

    def run(self):
        self.isRunning = True
        clock = pygame.time.Clock()
        while self.isRunning:
            self.handle_keyinputs()
            self.draw()    
            pygame.display.flip()
            clock.tick(0)


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()