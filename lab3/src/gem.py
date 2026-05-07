import math
import random
from enum import Enum
import pygame
from src.easing import Easing
from src.animation import Animation


class GemType(Enum):
    RED = 0
    BLUE = 1
    GREEN = 2
    PURPLE = 3
    YELLOW = 4
    ORANGE = 5
    BOMB = 6
    ROW_CLEAR = 7
    COL_CLEAR = 8


class Gem:
    """Кристалл игрового поля"""
    
    BASE_COLORS = {
        GemType.RED: (220, 50, 50), GemType.BLUE: (50, 100, 220),
        GemType.GREEN: (50, 180, 50), GemType.PURPLE: (150, 50, 180),
        GemType.YELLOW: (220, 180, 50), GemType.ORANGE: (220, 130, 50),
    }
    
    COLORS = {
        GemType.RED: (220, 50, 50), GemType.BLUE: (50, 100, 220),
        GemType.GREEN: (50, 180, 50), GemType.PURPLE: (150, 50, 180),
        GemType.YELLOW: (220, 180, 50), GemType.ORANGE: (220, 130, 50),
        GemType.BOMB: (35, 35, 45), GemType.ROW_CLEAR: (200, 200, 200),
        GemType.COL_CLEAR: (200, 200, 200),
    }
    
    FRAME_COLORS = {GemType.ROW_CLEAR: (255, 215, 0), GemType.COL_CLEAR: (255, 105, 180)}
    CLEAR_COLORS = [GemType.RED, GemType.BLUE, GemType.GREEN, GemType.PURPLE]
    
    def __init__(self, gtype, row, col, cell_size, base_color=None):
        self.type = gtype #тип
        self.row = row #позиция строка
        self.col = col #позиция столбец
        self.cell_size = cell_size #размер 
        
        if gtype in [GemType.ROW_CLEAR, GemType.COL_CLEAR]:
            self.base_color = base_color if base_color else random.choice(self.CLEAR_COLORS)
        else:
            self.base_color = gtype #если не очиститель
        
        self.x = float(col) #координаты
        self.y = float(row)
        self.anim_x = None #анимации перемещения
        self.anim_y = None
        self.scale = 0.0  #начало кристалла
        self.is_matched = False  #кристалл удаляется
        self.match_anim = None #анимация исчезновения
        self.scale_anim = Animation(0.0, 1.0, 300 + row * 50, Easing.ease_out_bounce) 
    
    def get_match_type(self):
        if self.type in [GemType.ROW_CLEAR, GemType.COL_CLEAR]:
            return self.base_color
        return self.type  #вовзрат цвета для поиска совпадений
    
    def get_display_color(self):
        if self.type in [GemType.ROW_CLEAR, GemType.COL_CLEAR]:
            return self.BASE_COLORS.get(self.base_color, (200, 200, 200))
        return self.COLORS.get(self.type, (200, 200, 200)) #возврат цвета для отрисовки
    
    def start_move(self, new_row, new_col, duration=200):  #перемещение к новой позиции
        self.anim_x = Animation(self.x, float(new_col), duration, Easing.ease_out_cubic)
        self.anim_y = Animation(self.y, float(new_row), duration, Easing.ease_out_cubic)
        self.row = new_row
        self.col = new_col
    
    def start_fall(self, new_row, duration=300): #падение вертикально
        self.anim_y = Animation(self.y, float(new_row), duration, Easing.ease_in_out_quad)
        self.row = new_row
    
    def start_match_animation(self): #кристалл удаляется за 250мс
        self.match_anim = Animation(1.0, 0.0, 250, Easing.ease_out_cubic)
        self.is_matched = True
    
    def update(self): #новый кадр
        if self.scale_anim and not self.scale_anim.finished:
            self.scale = self.scale_anim.update() #обновляем масштаб если анимация появления есть и не завершена
        if self.anim_x:
            self.x = self.anim_x.update() #обновляет горизонтальное перемещение
            if self.anim_x.finished:
                self.anim_x = None #завершает анимацию
        if self.anim_y:
            self.y = self.anim_y.update() #то же самое вертикально
            if self.anim_y.finished:
                self.anim_y = None
        if self.match_anim:
            self.scale = self.match_anim.update() #обновляет масштаб через анимацию удаления
            if self.match_anim.finished:
                return False  #когда анимация удаления закончилась
        return True #кристалл активен - опять апдейтим
    
    def draw(self, surf, offset_x, offset_y):
        if self.scale <= 0.01:
            return
        px = int(offset_x + self.x * self.cell_size + self.cell_size // 2) #х-координата центра кристалла
        py = int(offset_y + self.y * self.cell_size + self.cell_size // 2) #то же но у
        size = int(self.cell_size * 0.85 * self.scale) #сам размер
        if size < 5: #меньше 5пик не рисуем
            return
        
        if self.type == GemType.BOMB:  #спец метод отрисовки бомбы
            self._draw_bomb(surf, px, py, size)
        elif self.type in [GemType.ROW_CLEAR, GemType.COL_CLEAR]: #удаление р/с
            self._draw_clear_gem(surf, px, py, size)
        else:
            self._draw_normal_gem(surf, px, py, size) #остальное кристалл с бликом
    
    def _draw_bomb(self, surf, px, py, size):
        pulse = 1.0 + 0.06 * math.sin(pygame.time.get_ticks() / 200) #пульсация бомбы
        bomb_size = int(size * pulse)
        pygame.draw.circle(surf, (25, 25, 35), (px, py), bomb_size // 2)
        pygame.draw.circle(surf, (50, 50, 60), (px, py), bomb_size // 2 - 3)
        for i in range(8): #шипы для бомбы
            angle = i * math.pi / 4
            outer_r = bomb_size // 2 + 1 #конец шипа
            mid_r = bomb_size // 3 #начало
            pygame.draw.line(surf, (220, 70, 70), #линия от внутренней точки до внешней
                           (px + int(math.cos(angle) * mid_r), py + int(math.sin(angle) * mid_r)),
                           (px + int(math.cos(angle) * outer_r), py + int(math.sin(angle) * outer_r)), 2)
        fire_color = (255, 160, 40) if pygame.time.get_ticks() % 300 < 150 else (255, 80, 20) #тут цикл четных нечетных остатков и в зависимости от этого цвет меняется
        pygame.draw.circle(surf, fire_color, (px, py), bomb_size // 5) #сам огонек
    
    def _draw_clear_gem(self, surf, px, py, size):
        color = self.get_display_color()
        frame_color = self.FRAME_COLORS[self.type]
        points = [(px, py - size//2), (px + size//2, py), (px, py + size//2), (px - size//2, py)] #4 точки ромба
        pygame.draw.polygon(surf, color, points) #заливка цветом 
        pygame.draw.polygon(surf, (255, 255, 255), points, 3) #белая обводка 
        pygame.draw.polygon(surf, frame_color, points, 5) #рамка
        if self.type == GemType.ROW_CLEAR:
            pygame.draw.line(surf, (255, 255, 255), (px - size//2 + 10, py), (px + size//2 - 10, py), 4) #горизонтальная линия через центр
            for dx in [-1, 1]: #наконечник -1 левый, 1 правый
                tip_x = px + dx * (size//2 - 8)
                pygame.draw.polygon(surf, (255, 255, 255), [(tip_x, py), (tip_x - dx*12, py-7), (tip_x - dx*12, py+7)])
        else:
            pygame.draw.line(surf, (255, 255, 255), (px, py - size//2 + 10), (px, py + size//2 - 10), 4) #вертикальная линия
            for dy in [-1, 1]:
                tip_y = py + dy * (size//2 - 8)
                pygame.draw.polygon(surf, (255, 255, 255), [(px, tip_y), (px-7, tip_y - dy*12), (px+7, tip_y - dy*12)])
    
    def _draw_normal_gem(self, surf, px, py, size): #обычный кристаллик
        color = self.COLORS.get(self.type, (200, 200, 200))
        points = [(px, py - size//2), (px + size//2, py), (px, py + size//2), (px - size//2, py)] #4 точки ромба
        pygame.draw.polygon(surf, color, points) 
        pygame.draw.polygon(surf, (255, 255, 255), points, 3) #белый ободок
        light_color = tuple(min(255, c + 70) for c in color) #белый блик
        hl = [(px, py - size//2 + 6), (px + size//5, py - size//8), (px, py + size//4), (px - size//5, py - size//8)] #точки для блика
        pygame.draw.polygon(surf, light_color, hl) #сам блик