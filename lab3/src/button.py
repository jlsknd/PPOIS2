import pygame


class Button:
    """Кнопка интерфейса"""
    
    def __init__(self, x, y, w, h, text, font, color=(60, 60, 90)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.color = color
        self.hovered = False
        self.anim = 0.0
    
    def draw(self, surf):
        target = 1.0 if self.hovered else 0.0
        self.anim += (target - self.anim) * 0.2
        bc = self.color
        r, g, b = int(bc[0] + 50 * self.anim), int(bc[1] + 50 * self.anim), int(bc[2] + 50 * self.anim)
        pygame.draw.rect(surf, (r, g, b), self.rect, border_radius=12)
        pygame.draw.rect(surf, (180, 180, 220), self.rect, 3, border_radius=12)
        ts = self.font.render(self.text, True, (255, 255, 255))
        surf.blit(ts, ts.get_rect(center=self.rect.center))
    
    def handle_event(self, event, mp):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(mp)
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            return True
        return False