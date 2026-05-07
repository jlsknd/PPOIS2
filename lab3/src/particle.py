import math
import random
import pygame


class Particle:
    """Частица для анимации в меню"""
    
    def __init__(self, x, y, color, speed, size, life):
        self.x = x
        self.y = y
        self.color = color
        self.speed_x = random.uniform(-speed, speed)
        self.speed_y = random.uniform(-speed * 2, -speed * 0.5)
        self.size = size
        self.life = life
        self.max_life = life
        self.angle = random.uniform(0, math.pi * 2)
        self.rot_speed = random.uniform(-3, 3)
    
    def update(self, dt):
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt
        self.speed_y += 0.02 * dt
        self.life -= dt
        self.angle += self.rot_speed * dt
        return self.life > 0
    
    def draw(self, surf):
        alpha = int(255 * (self.life / self.max_life))
        if alpha < 0:
            alpha = 0
        
        size = self.size * (self.life / self.max_life)
        if size < 1:
            return
        
        points = []
        for i in range(5):
            angle = self.angle + i * math.pi * 2 / 5
            outer_x = self.x + math.cos(angle) * size
            outer_y = self.y + math.sin(angle) * size
            points.append((outer_x, outer_y))
            inner_angle = angle + math.pi / 5
            inner_x = self.x + math.cos(inner_angle) * size * 0.4
            inner_y = self.y + math.sin(inner_angle) * size * 0.4
            points.append((inner_x, inner_y))
        
        if len(points) >= 3:
            surf_particle = pygame.Surface((int(size*2)+4, int(size*2)+4), pygame.SRCALPHA)
            offset_x = int(self.x - size - 2)
            offset_y = int(self.y - size - 2)
            shifted_points = [(x - offset_x, y - offset_y) for x, y in points]
            try:
                pygame.draw.polygon(surf_particle, (*self.color, alpha), shifted_points)
                surf.blit(surf_particle, (offset_x, offset_y))
            except:
                pass