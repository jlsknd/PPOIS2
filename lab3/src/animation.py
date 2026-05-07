import pygame
from src.easing import Easing


class Animation:
    """Класс для плавных анимаций значений"""
    
    def __init__(self, start_val, end_val, duration, easing=None):
        self.start_val = start_val #начальное значение
        self.end_val = end_val #конечное
        self.duration = max(duration, 1) #длительность анимации
        self.easing = easing if easing else Easing.ease_out_cubic #плавность
        self.start_time = pygame.time.get_ticks() #запоминает время создания анимации в мс
        self.finished = False
    
    def update(self):
        if self.finished:
            return self.end_val #вернем если анимация завершена
        elapsed = pygame.time.get_ticks() - self.start_time #сколько мс прошло
        t = min(elapsed / self.duration, 1.0) #доля прошедшего времени
        if t >= 1.0: #если прошло более 100% времени, анимация завершена
            self.finished = True
            return self.end_val
        return self.start_val + (self.end_val - self.start_val) * self.easing(t) #интерполяция