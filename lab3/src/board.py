import random
import pygame
from src.gem import Gem, GemType


class Board:
    """Игровое поле с кристаллами"""
    
    def __init__(self, rows=8, cols=8, cell_size=60, allow_specials=True, allow_bombs=True, spawn_bombs=False):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.allow_specials = allow_specials
        self.allow_bombs = allow_bombs
        self.spawn_bombs = spawn_bombs
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self._initialize_board()
    
    def _initialize_board(self):
        for row in range(self.rows):
            for col in range(self.cols):
                while True:
                    gtype = random.choice(list(GemType)[:6])
                    if not self._creates_match(row, col, gtype):   #если добавляемый кристалл не создает тройку с соседними, вставляем его
                        self.grid[row][col] = Gem(gtype, row, col, self.cell_size)
                        break
        if not self.has_valid_moves():   #если нет ходов, доска перезаполняетсся
            self._initialize_board()
    
    def _creates_match(self, row, col, gtype):
        if col >= 2: 
            g1, g2 = self.grid[row][col-1], self.grid[row][col-2]
            if g1 and g2 and g1.get_match_type() == gtype and g2.get_match_type() == gtype:
                return True #нельзя ставить
        if row >= 2:
            g1, g2 = self.grid[row-1][col], self.grid[row-2][col]
            if g1 and g2 and g1.get_match_type() == gtype and g2.get_match_type() == gtype:
                return True 
        return False #можно
    
    def _random_gem_type(self):
        if self.spawn_bombs and random.random() < 0.03:   #если бомбы разерешены к спавну на уровне, они выпадут с вероятностью 3%
            return GemType.BOMB
        return random.choice(list(GemType)[:6])
    
    def _would_create_match(self, r1, c1, r2, c2):
        if not self.grid[r1][c1] or not self.grid[r2][c2]:
            return False
        
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
        has_match = False
        
        for row in [r1, r2]: #если обмен затронул две строки
            for start_col in range(max(0, min(c1, c2) - 2), min(self.cols - 2, max(c1, c2) + 1)): #все возможные тройки вокруг измененных ячеечек
                g1, g2, g3 = self.grid[row][start_col], self.grid[row][start_col + 1], self.grid[row][start_col + 2]
                if g1 and g2 and g3:
                    t1, t2, t3 = g1.get_match_type(), g2.get_match_type(), g3.get_match_type()
                    if t1 is not None and t1.value < 6 and t1 == t2 == t3:
                        has_match = True
                        break
            if has_match:
                break
        
        if not has_match:
            for col in [c1, c2]:
                for start_row in range(max(0, min(r1, r2) - 2), min(self.rows - 2, max(r1, r2) + 1)):
                    g1, g2, g3 = self.grid[start_row][col], self.grid[start_row + 1][col], self.grid[start_row + 2][col]
                    if g1 and g2 and g3:
                        t1, t2, t3 = g1.get_match_type(), g2.get_match_type(), g3.get_match_type()
                        if t1 is not None and t1.value < 6 and t1 == t2 == t3:
                            has_match = True
                            break
                if has_match:
                    break  
        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
        return has_match
    
    def has_valid_moves(self):
        for row in range(self.rows): 
            for col in range(self.cols):
                if col + 1 < self.cols and self._would_create_match(row, col, row, col + 1):
                    return True
                if row + 1 < self.rows and self._would_create_match(row, col, row + 1, col):
                    return True
        return False
    
    def is_animating(self):
        for row in range(self.rows):
            for col in range(self.cols):
                gem = self.grid[row][col]
                if gem and (gem.anim_x or gem.anim_y or gem.match_anim or
                           (gem.scale_anim and not gem.scale_anim.finished)):
                    return True #есть активные анимации
        return False
    
    def can_swap(self, row1, col1, row2, col2):
        if not (0 <= row1 < self.rows and 0 <= col1 < self.cols and
                0 <= row2 < self.rows and 0 <= col2 < self.cols):
            return False #когда ячейки не в пределах доски
        return self.grid[row1][col1] and self.grid[row2][col2] and \
               abs(row1 - row2) + abs(col1 - col2) == 1 #ячейки не пусты и расстояние 1 (ну они соседи типо)
    
    def swap(self, row1, col1, row2, col2):
        if not self.can_swap(row1, col1, row2, col2):
            return False #если нельга свапнуть
        self.grid[row1][col1], self.grid[row2][col2] = self.grid[row2][col2], self.grid[row1][col1] #меняет местами кристаллы в сетке
        if self.grid[row1][col1]:
            self.grid[row1][col1].row, self.grid[row1][col1].col = row1, col1
            self.grid[row1][col1].start_move(row1, col1, 200)
        if self.grid[row2][col2]:
            self.grid[row2][col2].row, self.grid[row2][col2].col = row2, col2
            self.grid[row2][col2].start_move(row2, col2, 200)
        return True
    
    def find_matches(self):
        matches = set()    #для удаления 
        match_groups = []
        activated_specials = []
        
        for row in range(self.rows):
            col = 0
            while col < self.cols:
                gem = self.grid[row][col]
                if gem:
                    mt = gem.get_match_type()
                    if mt is not None and mt.value < 6:
                        match_len = 1
                        while col + match_len < self.cols and self.grid[row][col + match_len] and \
                              self.grid[row][col + match_len].get_match_type() == mt:
                            match_len += 1
                        if match_len >= 3:
                            for i in range(match_len):
                                g = self.grid[row][col + i]
                                if g:
                                    matches.add((row, col + i))
                                    if g.type == GemType.ROW_CLEAR:
                                        activated_specials.append(('row_clear', row, col + i))
                                    elif g.type == GemType.COL_CLEAR:
                                        activated_specials.append(('col_clear', row, col + i))
                            match_groups.append(('h', row, col, match_len, mt))
                        col += match_len
                    else:
                        col += 1
                else:
                    col += 1
        
        for col in range(self.cols):
            row = 0
            while row < self.rows:
                gem = self.grid[row][col]
                if gem:
                    mt = gem.get_match_type()
                    if mt is not None and mt.value < 6:
                        match_len = 1
                        while row + match_len < self.rows and self.grid[row + match_len][col] and \
                              self.grid[row + match_len][col].get_match_type() == mt:
                            match_len += 1
                        if match_len >= 3:
                            for i in range(match_len):
                                g = self.grid[row + i][col]
                                if g:
                                    matches.add((row + i, col))
                                    if g.type == GemType.ROW_CLEAR:
                                        activated_specials.append(('row_clear', row + i, col))
                                    elif g.type == GemType.COL_CLEAR:
                                        activated_specials.append(('col_clear', row + i, col))
                            match_groups.append(('v', row, col, match_len, mt))
                        row += match_len
                    else:
                        row += 1
                else:
                    row += 1
        return matches, match_groups, activated_specials
    
    def create_special_gem(self, gem_type, row, col, base_color=None):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if gem_type == GemType.BOMB and not self.allow_bombs:
                return
            if gem_type in [GemType.ROW_CLEAR, GemType.COL_CLEAR] and not self.allow_specials:
                return
            self.grid[row][col] = Gem(gem_type, row, col, self.cell_size, base_color)
    
    def activate_bomb(self, row, col):
        removed = set()
        for r in range(max(0, row-1), min(self.rows, row+2)):
            for c in range(max(0, col-1), min(self.cols, col+2)):
                if self.grid[r][c]:
                    removed.add((r, c))
        return removed
    
    def activate_row_clear(self, row):
        return {(row, c) for c in range(self.cols) if self.grid[row][c]}
    
    def activate_col_clear(self, col):
        return {(r, col) for r in range(self.rows) if self.grid[r][col]}
    
    def remove_gems(self, positions):
        for row, col in positions:
            if self.grid[row][col]:
                self.grid[row][col].start_match_animation()
    
    def apply_gravity(self):
        for col in range(self.cols):
            write_row = self.rows - 1
            for row in range(self.rows - 1, -1, -1):
                if self.grid[row][col] and not self.grid[row][col].is_matched:
                    if row != write_row:
                        gem = self.grid[row][col]
                        self.grid[write_row][col] = gem
                        self.grid[row][col] = None
                        gem.start_fall(write_row, 250 + abs(write_row - row) * 50)
                    write_row -= 1
                elif self.grid[row][col] and self.grid[row][col].is_matched:
                    self.grid[row][col] = None
            for row in range(write_row + 1):
                if self.grid[row][col] is None:
                    gtype = self._random_gem_type()
                    gem = Gem(gtype, row, col, self.cell_size)
                    gem.y = row - (write_row + 1)
                    gem.start_fall(row, 300 + row * 50)
                    self.grid[row][col] = gem
    
    def update(self):
        for row in range(self.rows):
            for col in range(self.cols):
                gem = self.grid[row][col]
                if gem:
                    if not gem.update() and gem.is_matched:
                        self.grid[row][col] = None
    
    def draw(self, surf, offset_x, offset_y):
        pygame.draw.rect(surf, (25, 25, 45), (offset_x-8, offset_y-8,
                        self.cols*self.cell_size+16, self.rows*self.cell_size+16), border_radius=15)
        pygame.draw.rect(surf, (35, 35, 55), (offset_x-5, offset_y-5,
                        self.cols*self.cell_size+10, self.rows*self.cell_size+10), border_radius=12)
        for row in range(self.rows):
            for col in range(self.cols):
                x, y = offset_x + col*self.cell_size, offset_y + row*self.cell_size
                c = (42, 42, 62) if (row+col) % 2 == 0 else (52, 52, 72)
                pygame.draw.rect(surf, c, (x+1, y+1, self.cell_size-2, self.cell_size-2), border_radius=3)
        for row in range(self.rows):
            for col in range(self.cols):
                gem = self.grid[row][col]
                if gem:
                    gem.draw(surf, offset_x, offset_y)