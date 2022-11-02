from dataclasses import dataclass
from random import randint
import pygame
import math
import numpy as np

def translate(oneMin, oneMay, Value, resultMin, resultMax):
    return (Value - oneMin) / (oneMay - oneMin) * (resultMax - resultMin) + resultMin

def draw_borders(surface:pygame.Surface, color:pygame.color, thickness:int)-> None:
    dimensions = surface.get_width(), surface.get_height()
    pygame.draw.line(surface, color, (0,0),(0,dimensions[1]-1), thickness)
    pygame.draw.line(surface, color, (0,0),(dimensions[0]-1,0), thickness)
    pygame.draw.line(surface, color, (dimensions[0]-1,0),(dimensions[0]-1,dimensions[1]-1), thickness)
    pygame.draw.line(surface, color, (0,dimensions[1]-1),(dimensions[0]-1,dimensions[1]-1), thickness)

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
        self.walls.append(Wall(0,0,0,self.dimensions[1]-1))
        self.walls.append(Wall(0,0,self.dimensions[0]-1,0))
        self.walls.append(Wall(self.dimensions[0]-1,0,self.dimensions[0]-1,self.dimensions[1]-1))
        self.walls.append(Wall(0, self.dimensions[1]-1,self.dimensions[0]-1,self.dimensions[1]-1))

    def draw(self, surface:pygame.Surface):
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

    def draw(self, screen:pygame.Surface):
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

    def move_left_right(self, left_right:int):
        endx = self._pos[0] + left_right * math.cos(math.radians(self._angle+90))
        endy = self._pos[1] + left_right * math.sin(math.radians(self._angle+90))
        self.set_pos((endx, endy))
        
    def move_front_back(self, front_back:int):
        endx = self._pos[0] + front_back * math.cos(math.radians(self._angle+180))
        endy = self._pos[1] + front_back * math.sin(math.radians(self._angle+180))
        self.set_pos((endx, endy))

    def change_angle(self, new_angle:float):
        before_angle = self._angle
        self._angle = new_angle
        self.look_ray.angle = new_angle
        for ray in self.rays:
            ray.angle += new_angle -before_angle

    def set_FOV_Rays(self):
        for angle in range(round(-self.FOV/2*self.resolution), round(self.FOV/2*self.resolution)):
            angle = angle / self.resolution
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

        self.world_size = (500, 500)
        self.world = World(self.world_size)
        self.player = Player(self.world, (10,10), 90, 10)
        self.surface_2d = pygame.Surface(self.world_size, flags=pygame.SRCALPHA)
        self.surface_3d = pygame.Surface((900,600), flags=pygame.SRCALPHA)

    def draw_vertical_line(self, surface:pygame.Surface, height:float, x:float, color:pygame.color, thickness:int):
        height *= 50
        top = (surface.get_height()-height)/2
        bottom = (surface.get_height()+height)/2
        pygame.draw.line(surface, color, (x, top), (x, bottom), math.floor(thickness))
        
    def draw_rays(self, surface:pygame.Surface):
        i = 0
        rays_amount = self.player.rays
        for ray in self.player.rays:
            i += 255/len(rays_amount)
            record = ray.check_intersection_with_walls(self.world.walls)
            if record:
                pygame.draw.aaline(surface, (i,i,i), ray.pos, record)        
        pygame.draw.aaline(surface, (0,255,0), self.player.look_ray.pos, self.player.look_ray.get_pos_for_len(100)) # for the looking direction ray

    def draw2d(self, surface:pygame.Surface):
        # surface.fill((0,0,0,0))
        surface.fill((0,30,50))
        self.draw_rays(self.surface_2d)
        self.world.draw(self.surface_2d)

    def draw3d(self, surface:pygame.Surface):
        # surface.fill((0,0,0,0))
        surface.fill((0,30,50))
        amount_rays = len(self.player.rays)
        step = self.surface_3d.get_width()/amount_rays
        i=0
        for index, ray in enumerate(self.player.rays):
            i += 255/len(self.player.rays)
            if (dist := ray.get_dist_to_walls(self.world.walls)) == 0: return
            line_height = translate(0, max(self.world_size)*2, 1/dist*100, 0, self.size[1])
            x_pos = index*step
            self.draw_vertical_line(surface, line_height, x_pos, (i,i,i), step)

    def draw(self):
        self.size = self.screen.get_width(), self.screen.get_height()
        self.screen.fill(self.backgroundcolor)
        
        
        mouse_pos_x = pygame.mouse.get_pos()[0] / self.size[0] * self.world_size[0]
        mouse_pos_y= pygame.mouse.get_pos()[1] / self.size[1] * self.world_size[1]
        self.mouse_pos = mouse_pos_x, mouse_pos_y
        
        # self.player.set_pos(self.mouse_pos)
        self.player.change_angle(self.player._angle+1)
        
        
        self.draw3d(self.surface_3d)
        draw_borders(self.surface_3d, (255,255,255), 1)
        self.screen.blit(self.surface_3d, (0,0))
        
        self.draw2d(self.surface_2d)
        self.screen.blit(self.surface_2d, (self.size[0]-self.world_size[0], 0))
      
    def handle_keyinputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isRunning = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_a:
                    self.player.move_left_right(-10)
                elif event.key == pygame.K_d:
                    self.player.move_left_right(+10)
                elif event.key == pygame.K_w:
                    self.player.move_front_back(-10)
                elif event.key == pygame.K_s:
                    self.player.move_front_back(+10)


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