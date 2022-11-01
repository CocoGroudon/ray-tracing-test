from dataclasses import dataclass
from random import randint
import pygame
import math


@dataclass
class Wall:
    x1: int
    y1: int
    x2: int
    y2: int

    def draw(self, screen):
        pygame.draw.line(screen, (255,255,255), (self.x1, self.y1), (self.x2, self.y2))

class Ray:
    def __init__(self, pos, angle) -> None:
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

    def draw(self, screen:pygame.display):
        pygame.draw.aaline(screen, (120,120,200), self.pos, self.get_pos_for_len(self.len))




class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((1600,900), pygame.RESIZABLE)
        self.backgroundcolor = (0, 43, 53)
        self.player_pos = [300, 200]

        self.walls =[]
        for i in range(5):
            wall = Wall(randint(0,self.screen.get_width()), randint(0,self.screen.get_height()), randint(0,self.screen.get_width()), randint(0,self.screen.get_height()))
            self.walls.append(wall)

        self.rays = []
        for i in range(360):
            self.rays.append(Ray(self.player_pos, i))

    def draw(self):
        self.screen.fill(self.backgroundcolor)
        self.player_pos[0], self.player_pos[1] = pygame.mouse.get_pos()
        for ray in self.rays:
            record = ray.check_intersection_with_walls(self.walls)
            if record:
                pygame.draw.aaline(self.screen, (255,0,0), ray.pos, record)
            # ray.draw(self.screen)
        for wall in self.walls:
            wall.draw(self.screen)
        # pygame.draw.circle(self.screen, (0,255,255), self.player_pos, 5)
        
    def handle_keyinputs(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f11:
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