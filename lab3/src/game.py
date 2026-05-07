import math
import random
import os
import json
from enum import Enum
import pygame

from src.config import ConfigManager
from src.board import Board
from src.gem import GemType
from src.sound import SoundManager
from src.button import Button
from src.particle import Particle


class GameState(Enum):
    MENU = 0
    MODE_SELECT = 1
    LEVEL_SELECT = 2
    PLAYING = 3
    GAME_OVER = 4
    LEADERBOARD = 5
    HELP = 6
    INPUT_NAME = 7
    NO_MOVES = 8
    PAUSED = 9
    LEADERBOARD_MENU = 10


class MenuGem:
    """Декоративный кристалл для меню"""

    COLORS = [
        (220, 50, 50),
        (50, 100, 220),
        (50, 180, 50),
        (150, 50, 180),
        (220, 180, 50),
        (220, 130, 50),
    ]

    def __init__(self, x, y, size, fall_speed):
        self.x = x
        self.y = y
        self.size = size
        self.fall_speed = fall_speed
        self.color = random.choice(self.COLORS)
        self.angle = random.uniform(0, math.pi * 2)
        self.rot_speed = random.uniform(-0.02, 0.02)
        self.glow_alpha = random.uniform(0.3, 0.8)
        self.glow_dir = 0.02
        self.trail = []

    def update(self, dt, screen_height):
        self.y += self.fall_speed * dt
        self.angle += self.rot_speed * dt
        self.glow_alpha += self.glow_dir
        if self.glow_alpha > 0.9 or self.glow_alpha < 0.3:   #если свечение слишком яркое или слишком тусклое меняем направление на противоположное
            self.glow_dir *= -1

        if random.random() < 0.3:  #новая частица следа в текущей позиции с вероятностью 30%
            self.trail.append([self.x, self.y, 255])

        for t in self.trail:
            t[2] -= 8 * dt #прозрачность теряется
        self.trail = [t for t in self.trail if t[2] > 0] #удаляет частицы с прозрачностью меньше и =0

        return self.y < screen_height + 50

    def draw(self, surf): #отрисовка на экране
        sz = self.size
        ca, sa = math.cos(self.angle), math.sin(self.angle) #кос и син текущего угла поворота

        for t in self.trail:   #рисуем след
            alpha = int(t[2])
            trail_sz = sz * (alpha / 255) * 0.7  #частицы следа меньше основного кристалла
            trail_pts = [
                (t[0] + int(-trail_sz * sa), t[1] + int(-trail_sz * ca)),
                (t[0] + int(trail_sz * ca), t[1] + int(-trail_sz * sa)),
                (t[0] + int(trail_sz * sa), t[1] + int(trail_sz * ca)),
                (t[0] + int(-trail_sz * ca), t[1] + int(trail_sz * sa)),  #4 точкки ромба для частицы следа с учетом поврота
            ]
            if len(trail_pts) >= 3:
                trail_surf = pygame.Surface((sz * 3, sz * 3), pygame.SRCALPHA) #создаем временную прозрачную оверхность для отрисовки частицы
                shifted = [
                    (px - self.x + sz * 1.5, py - self.y + sz * 1.5) 
                    for px, py in trail_pts
                ]
                pygame.draw.polygon(trail_surf, (*self.color, alpha), shifted)
                surf.blit(trail_surf, (self.x - sz * 1.5, self.y - sz * 1.5)) #полупрозраченый ромб на временной поверхности переносим на экран

        glow_sz = sz + 6
        glow_pts = [
            (self.x + int(-glow_sz * sa), self.y + int(-glow_sz * ca)),
            (self.x + int(glow_sz * ca), self.y + int(-glow_sz * sa)),    #4 точки ромба большего размера 
            (self.x + int(glow_sz * sa), self.y + int(glow_sz * ca)),
            (self.x + int(-glow_sz * ca), self.y + int(glow_sz * sa)),
        ]
        glow_alpha = int(100 * self.glow_alpha) #прозрачность 30-90/255
        glow_surf = pygame.Surface((sz * 5, sz * 5), pygame.SRCALPHA)
        shifted = [
            (px - self.x + sz * 2.5, py - self.y + sz * 2.5) for px, py in glow_pts
        ]
        pygame.draw.polygon(glow_surf, (*self.color, glow_alpha), shifted)
        surf.blit(glow_surf, (self.x - sz * 2.5, self.y - sz * 2.5))

        pts = [
            (self.x + int(-sz * sa), self.y + int(-sz * ca)),
            (self.x + int(sz * ca), self.y + int(-sz * sa)),
            (self.x + int(sz * sa), self.y + int(sz * ca)),
            (self.x + int(-sz * ca), self.y + int(sz * sa)), #сам кристалл
        ]
        pygame.draw.polygon(surf, self.color, pts) #заоитый цветоом ромб
        pygame.draw.polygon(surf, (255, 255, 255), pts, 2) #обводка

        light = tuple(min(255, c + 80) for c in self.color) #блик
        hl = [
            (self.x, self.y - sz + 5),
            (self.x + sz // 3, self.y - sz // 3),
            (self.x, self.y + sz // 3),   #по 4 точкам
            (self.x - sz // 3, self.y - sz // 3),
        ]
        pygame.draw.polygon(surf, light, hl) #рисуем


class Game:
    """Основной класс игры Jewel Quest"""

    def __init__(self):
        pygame.init()
        self.cfg = ConfigManager.load()
        self.width, self.height = (
            self.cfg["display"]["width"],
            self.cfg["display"]["height"],
        )
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.cfg["display"]["title"])
        self.clock = pygame.time.Clock() #часы для контроля фпс
        self.leaderboard_type = "scores"  
        self.font = pygame.font.SysFont("Arial", 24, bold=True) #об текст
        self.big_font = pygame.font.SysFont("Arial", 32, bold=True) #заголовкм
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True) #большой заголовок
        self.small_font = pygame.font.SysFont("Arial", 18) #подсказки
        self.combo_font = pygame.font.SysFont("Arial", 20, bold=True) #комбо

        self.snd = SoundManager()
        self.state = GameState.MENU
        self.board = None
        self.score = 0
        self.time_left = 60
        self.mode = None
        self.level = 0
        self.selected_gem = None
        self.input_text = ""
        self.game_time = 0
        self.tense_music_played = False
        self.combo_count = 0
        self.goal_score = 2500
        self.resume_button = None
        self.menu_button = None

        #очерредь анимаций
        self.pending_actions = []
        self.action_timer = 0

        self.menu_gems = []
        self.menu_particles = []
        self.menu_bg_stars = []
        self._init_menu_bg_stars()

        self.buttons = []
        self.mode_buttons = []
        self.level_buttons = []
        self._create_buttons()

        self.snd.play_menu_music()

    def _init_menu_bg_stars(self):
        self.menu_bg_stars = []
        for _ in range(60):
            star = {
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "size": random.uniform(1, 3),
                "brightness": random.uniform(0.3, 1.0),
                "twinkle_speed": random.uniform(0.5, 2.0),
                "phase": random.uniform(0, math.pi * 2),
            }
            self.menu_bg_stars.append(star)

    def _spawn_menu_gem(self):
        x = random.randint(30, self.width - 30)
        y = random.randint(-150, -30)
        size = random.uniform(8, 20)
        speed = random.uniform(0.03, 0.08)
        self.menu_gems.append(MenuGem(x, y, size, speed))

    def _spawn_menu_particle(self):
        x = random.randint(50, self.width - 50)
        y = random.randint(self.height - 50, self.height + 20)
        colors = [
            (255, 255, 200),
            (200, 220, 255),
            (255, 200, 220),
            (200, 255, 200),
            (255, 220, 180),
        ]
        color = random.choice(colors)
        speed = random.uniform(0.5, 2)
        size = random.uniform(3, 8)
        life = random.uniform(1500, 4000)
        self.menu_particles.append(Particle(x, y, color, speed, size, life))

    def _update_menu_animation(self, dt):
        for gem in self.menu_gems[:]:
            if not gem.update(dt, self.height):
                self.menu_gems.remove(gem)

        if len(self.menu_gems) < 15 and random.random() < 0.04:
            self._spawn_menu_gem()

        self.menu_particles = [p for p in self.menu_particles if p.life > 0]
        for p in self.menu_particles:
            p.update(dt)

        if len(self.menu_particles) < 25 and random.random() < 0.1:
            self._spawn_menu_particle()

    def _create_buttons(self):
        cx = self.width // 2

        self.buttons = [
            Button(cx - 150, 240, 300, 60, "Начать игру", self.font),
            Button(cx - 150, 320, 300, 60, "Таблица рекордов", self.font),
            Button(cx - 150, 400, 300, 60, "Справка", self.font),
            Button(cx - 150, 480, 300, 60, "Выход", self.font),
        ]

        self.mode_buttons = [
            Button(cx - 170, 200, 340, 60, "Режим на время (60 сек)", self.font),
            Button(cx - 170, 290, 340, 60, "Режим на очки", self.font),
            Button(cx - 100, 400, 200, 60, "Назад", self.font),
        ]

        self.level_buttons = [
            Button(cx - 180, 100, 360, 60, "Уровень 1", self.font),
            Button(cx - 180, 180, 360, 60, "Уровень 2", self.font),
            Button(cx - 180, 260, 360, 60, "Уровень 3", self.font),
            Button(cx - 100, 360, 200, 60, "Назад", self.font),
        ]

    def _add_pending_action(self, action, delay):
        """Добавляет действие в очередь с задержкой"""
        self.pending_actions.append(
            {"action": action, "time": pygame.time.get_ticks() + delay}
        )

    def _show_leaderboard(self, lb_type):
        """Переключает тип таблицы рекордов"""
        self.leaderboard_type = lb_type
        self.state = GameState.LEADERBOARD

    def _process_pending_actions(self):
        """Обрабатывает очередь отложенных действий"""
        current_time = pygame.time.get_ticks()
        to_process = []

        for item in self.pending_actions[:]:
            if current_time >= item["time"]:
                to_process.append(item["action"])
                self.pending_actions.remove(item)

        for action in to_process:
            action()

    def run(self): #крутится пока игрок не закроет окно
        running = True #игра работает
        while running:
            dt = self.clock.tick(60) #фпс 60 кадров в секунду
            mp = pygame.mouse.get_pos() #позиция курсора
            for ev in pygame.event.get():  #накопившиеся события
                if ev.type == pygame.QUIT:  #закрытие окна
                    running = False #цикл завершился
                self._handle_events(ev, mp)   #событие в обработчик
            self._update(dt)
            self._render()    #рисует текущий кадр
            pygame.display.flip()   
        pygame.quit()
        import sys

        sys.exit()

    def _handle_events(self, ev, mp):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_p:      #нажата клавиша и именно Р
            if self.state == GameState.PLAYING:
                self.state = GameState.PAUSED  #ставим на паузу и вырбаем музыку
                self.snd.pause_music()
                self.snd.play_sfx("click") #звук клика
                return
            elif self.state == GameState.PAUSED:   #если на паузе вернемся в игру и вернем у
                self.state = GameState.PLAYING
                self.snd.resume_music()
                self.snd.play_sfx("click")
                return

        if self.state == GameState.MENU: #клики по кнопкам
            self._handle_menu_events(ev, mp)
        elif self.state == GameState.LEADERBOARD_MENU: #выбор таблицы рекордов
            self._handle_leaderboard_menu_events(ev, mp)
        elif self.state == GameState.MODE_SELECT: #режим игры
            self._handle_mode_select_events(ev, mp)
        elif self.state == GameState.LEVEL_SELECT: #выбор уровня
            self._handle_level_select_events(ev, mp)
        elif self.state == GameState.PLAYING: #игровой процесс клики по кристаллам
            self._handle_playing(ev, mp)
        elif self.state == GameState.PAUSED:   #прожолжить выйти там
            self._handle_paused_events(ev, mp)
        elif self.state == GameState.GAME_OVER: #игра окончена
            self._handle_game_over_events(ev)
        elif self.state == GameState.NO_MOVES: #нет ходов
            self._handle_no_moves_events(ev)
        elif self.state == GameState.INPUT_NAME: #введите имя
            self._handle_input_name_events(ev)
        elif self.state in [GameState.LEADERBOARD, GameState.HELP]: #просмотр таблицы рекордов или справки
            self._handle_info_events(ev)

    def _handle_leaderboard_menu_events(self, ev, mp):
        """Обработка меню выбора таблицы рекордов"""
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.snd.play_sfx("click")
            self.state = GameState.MENU
            self.snd.play_menu_music()
            return

        if ev.type == pygame.MOUSEBUTTONDOWN:
            # рекорды по очкам
            if hasattr(self, "lb_scores_btn") and self.lb_scores_btn.collidepoint(mp):
                self.snd.play_sfx("click")
                self._show_leaderboard("scores")
            # кнопка "рекорды по времени"
            elif hasattr(self, "lb_time_btn") and self.lb_time_btn.collidepoint(mp):
                self.snd.play_sfx("click")
                self._show_leaderboard("time")
            # кнопка "назад"
            elif hasattr(self, "lb_back_btn") and self.lb_back_btn.collidepoint(mp):
                self.snd.play_sfx("click")
                self.state = GameState.MENU
                self.snd.play_menu_music()

    def _handle_menu_events(self, ev, mp):
        for b in self.buttons:
            if b.handle_event(ev, mp):
                self.snd.play_sfx("click")
                if "Начать" in b.text:
                    self.state = GameState.MODE_SELECT
                elif "рекорд" in b.text:
                    self.state = GameState.LEADERBOARD_MENU  
                elif "Справка" in b.text:
                    self.state = GameState.HELP
                elif "Выход" in b.text:
                    pygame.quit()
                    import sys

                    sys.exit()

    def _handle_mode_select_events(self, ev, mp):
        for b in self.mode_buttons:
            if b.handle_event(ev, mp):
                self.snd.play_sfx("click")
                if "время" in b.text:
                    self.start_time_mode()
                elif "очки" in b.text:
                    self.state = GameState.LEVEL_SELECT
                elif "Назад" in b.text:
                    self.state = GameState.MENU
                    self.snd.play_menu_music()

    def _handle_level_select_events(self, ev, mp):
        for b in self.level_buttons:
            if b.handle_event(ev, mp):
                self.snd.play_sfx("click")
                if "Уровень 1" == b.text:
                    self.start_points_mode(1)
                elif "Уровень 2" == b.text:
                    self.start_points_mode(2)
                elif "Уровень 3" == b.text:
                    self.start_points_mode(3)
                elif "Назад" == b.text:
                    self.state = GameState.MODE_SELECT

    def _handle_paused_events(self, ev, mp):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_p or ev.key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
                self.snd.resume_music()
                self.snd.play_sfx("click")
            elif ev.key == pygame.K_q:
                self.state = GameState.MENU
                self.snd.stop_music()
                self.snd.play_menu_music()
                self.snd.play_sfx("click")
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if self.resume_button and self.resume_button.rect.collidepoint(mp):
                self.state = GameState.PLAYING
                self.snd.resume_music()
                self.snd.play_sfx("click")
            if self.menu_button and self.menu_button.rect.collidepoint(mp):
                self.state = GameState.MENU
                self.snd.stop_music()
                self.snd.play_menu_music()
                self.snd.play_sfx("click")

    def _handle_game_over_events(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN or (
            ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN
        ):
            self.snd.play_sfx("click")
            if self.mode == "time":
                self.leaderboard_type = "time"  
                self.state = GameState.INPUT_NAME
            else:
                self.leaderboard_type = "scores"  
                self.state = GameState.INPUT_NAME

    def _handle_no_moves_events(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN or (
            ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN
        ):
            self.snd.play_sfx("click")
            if self.mode == "time":
                self.leaderboard_type = "time"  
                self.state = GameState.INPUT_NAME
            else:
                self.leaderboard_type = "scores"  
                self.state = GameState.INPUT_NAME

    def _handle_input_name_events(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                self.snd.play_sfx("click")
                self._save_score()
                self.state = GameState.LEADERBOARD
            elif ev.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif len(ev.unicode) == 1 and len(self.input_text) < 20:
                self.input_text += ev.unicode

    def _handle_info_events(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN or (
            ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE
        ):
            self.snd.play_sfx("click")
            self.state = GameState.MENU
            self.snd.play_menu_music()

    def _handle_playing(self, ev, mp):
        # не обрабатываем клики если есть активные действия
        if self.pending_actions:
            return

        ox = self.cfg["grid"]["offset_x"]
        oy = self.cfg["grid"]["offset_y"]
        cs = self.cfg["grid"]["cell_size"]

        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.selected_gem = None
            self.snd.play_sfx("click")

        if ev.type == pygame.MOUSEBUTTONDOWN:
            if ox <= mp[0] < ox + cs * 8 and oy <= mp[1] < oy + cs * 8:
                self.snd.play_sfx("gem_click")
                c = (mp[0] - ox) // cs
                r = (mp[1] - oy) // cs
                if 0 <= r < 8 and 0 <= c < 8:
                    if self.selected_gem is None:
                        self.selected_gem = (r, c)
                    else:
                        r1, c1 = self.selected_gem
                        if (r, c) == (r1, c1):
                            self.selected_gem = None
                        elif self.board.can_swap(r1, c1, r, c):
                            self._perform_swap(r1, c1, r, c)
                            self.selected_gem = None

    def _perform_swap(self, r1, c1, r2, c2):
        g1, g2 = self.board.grid[r1][c1], self.board.grid[r2][c2]
        if not self.board.swap(r1, c1, r2, c2):
            return

        self.snd.play_sfx("swap")

        def check_result():
            all_removed = set()
            bomb_combo = False
            mega_combo = False

            if g1 and g2:
                # бомба и удал ряда - 3 ряда
                if (g1.type == GemType.BOMB and g2.type == GemType.ROW_CLEAR) or (
                    g2.type == GemType.BOMB and g1.type == GemType.ROW_CLEAR
                ):
                    bomb_row = r2 if g1.type == GemType.BOMB else r1
                    for dr in [-1, 0, 1]:
                        row_to_clear = bomb_row + dr
                        if 0 <= row_to_clear < self.board.rows:
                            all_removed.update(
                                self.board.activate_row_clear(row_to_clear)
                            )
                    bomb_combo = True

                # бомба и удал столбца
                elif (g1.type == GemType.BOMB and g2.type == GemType.COL_CLEAR) or (
                    g2.type == GemType.BOMB and g1.type == GemType.COL_CLEAR
                ):
                    bomb_col = c2 if g1.type == GemType.BOMB else c1
                    for dc in [-1, 0, 1]:
                        col_to_clear = bomb_col + dc
                        if 0 <= col_to_clear < self.board.cols:
                            all_removed.update(
                                self.board.activate_col_clear(col_to_clear)
                            )
                    bomb_combo = True

                # бомба * бомба 5*5
                elif g1.type == GemType.BOMB and g2.type == GemType.BOMB:
                    center_r, center_c = r2, c2
                    for r in range(
                        max(0, center_r - 2), min(self.board.rows, center_r + 3)
                    ):
                        for c in range(
                            max(0, center_c - 2), min(self.board.cols, center_c + 3)
                        ):
                            if self.board.grid[r][c]:
                                all_removed.add((r, c))
                    mega_combo = True

                # удаление ряда*столбца-крест
                elif (
                    g1.type == GemType.ROW_CLEAR and g2.type == GemType.COL_CLEAR
                ) or (g2.type == GemType.ROW_CLEAR and g1.type == GemType.COL_CLEAR):
                    if g1.type == GemType.ROW_CLEAR:
                        all_removed.update(self.board.activate_row_clear(r1))
                        all_removed.update(self.board.activate_col_clear(c2))
                    else:
                        all_removed.update(self.board.activate_row_clear(r2))
                        all_removed.update(self.board.activate_col_clear(c1))
                    mega_combo = True

                else:
                    # просто бомба
                    if g1.type == GemType.BOMB:
                        all_removed.update(self.board.activate_bomb(r2, c2))
                        bomb_combo = True
                    if g2.type == GemType.BOMB:
                        all_removed.update(self.board.activate_bomb(r1, c1))
                        bomb_combo = True

            # было комбо
            if all_removed:
                # проверяем цепную реакцию до удаления
                chain = self._activate_specials_in_blast(all_removed)
                if chain:
                    all_removed.update(chain)

                if mega_combo:
                    self.snd.play_sfx("bomb")
                    self.score += len(all_removed) * self.cfg["scoring"]["mega_combo"]
                elif bomb_combo:
                    self.snd.play_sfx("bomb")
                    self.score += len(all_removed) * self.cfg["scoring"]["bomb_clear_combo"] 

                self.board.remove_gems(all_removed)
                self._add_pending_action(lambda: self._after_remove(), 300)
                return

            # простые совпадения
            m, mg, sp = self.board.find_matches()
            if m or sp:
                if sp:
                    # вызов _process_specials, который теперь проверяет цепочку
                    self._process_specials(sp, m)
                    # _process_specials сам удаляет через remove_gems
                if m:
                    self._process_matches(m, mg, [])
                self._check_no_moves()
            else:
                self.board.swap(r1, c1, r2, c2)

        self._add_pending_action(check_result, 200)

    def _process_matches(self, matches, match_groups, activated_specials):
        if not matches and not activated_specials:
            self.combo_count = 0
            return

        if activated_specials:
            self._process_specials(activated_specials, matches)

        self.snd.play_sfx("match")
        self.combo_count += 1
        self.score += len(matches) * self.cfg["scoring"]["match_per_gem"]  #10 за кристалл
        self.score += self.combo_count * self.cfg["scoring"]["combo_bonus"]  #+5 за каждое комбо

        for direction, row, col, length, gem_type in match_groups:
            if length >= 5 and self.board.allow_bombs:
                if direction == "h":
                    self.board.create_special_gem(GemType.BOMB, row, col + length // 2)
                    matches.discard((row, col + length // 2))
                else:
                    self.board.create_special_gem(GemType.BOMB, row + length // 2, col)
                    matches.discard((row + length // 2, col))
            elif length == 4 and self.board.allow_specials:
                if direction == "h":
                    self.board.create_special_gem(
                        GemType.ROW_CLEAR, row, col + length // 2, gem_type
                    )
                    matches.discard((row, col + length // 2))
                else:
                    self.board.create_special_gem(
                        GemType.COL_CLEAR, row + length // 2, col, gem_type
                    )
                    matches.discard((row + length // 2, col))

        if matches:
            self.board.remove_gems(matches)

        # добавим гравитацию в очередь (250 мс после удаления)
        self._add_pending_action(lambda: self._apply_gravity_and_check(), 250)

    def _activate_specials_in_blast(self, removed_positions):
        """Активирует ВСЕ спецкристаллы в зоне взрыва ДО их удаления"""
        already_processed = set()
        extra_removed = set()

        # очередь позиций для проверки
        to_check = list(removed_positions)

        while to_check:
            row, col = to_check.pop(0) #первый эл ищ списка

            if (row, col) in already_processed:
                continue

            if not (0 <= row < self.board.rows and 0 <= col < self.board.cols):
                continue

            already_processed.add((row, col))

            gem = self.board.grid[row][col]
            if gem is None:
                continue

            # проверка до удаления
            if gem.is_matched:
                continue

            if gem.type == GemType.BOMB:
                # бомба взрывается
                bomb_removed = self.board.activate_bomb(row, col)
                for pos in bomb_removed:
                    if pos not in already_processed:
                        extra_removed.add(pos)
                        to_check.append(pos)  #в очередь на проверку

            elif gem.type == GemType.ROW_CLEAR:
                # удаляет ряд
                row_removed = self.board.activate_row_clear(row)
                for pos in row_removed:
                    if pos not in already_processed:
                        extra_removed.add(pos)
                        to_check.append(pos)  # в очередь

            elif gem.type == GemType.COL_CLEAR:
                #  удаляет столбец
                col_removed = self.board.activate_col_clear(col)
                for pos in col_removed:
                    if pos not in already_processed:
                        extra_removed.add(pos)
                        to_check.append(pos)  # в очередь

        return extra_removed

    def _after_remove(self):
        """Вызывается после анимации удаления"""
        self.board.apply_gravity()

        def check_new_matches():
            new_m, new_mg, new_sp = self.board.find_matches()
            if new_m or new_sp:
                if new_sp:
                    self._process_specials(new_sp, new_m)
                self._process_matches(new_m, new_mg, new_sp)
            self._check_no_moves()

        self._add_pending_action(check_new_matches, 600)

    def _check_no_moves(self):
        def check():
            if not self.board.has_valid_moves():
                self.state = GameState.NO_MOVES
                self.snd.stop_music()
                self.snd.play_sfx("nomoves")

        self._add_pending_action(check, 100)

    def _process_specials(self, sp, matches):
        """Собирает всё что нужно удалить, проверяет цепную реакцию, удаляет"""
        spec_rem = set()

        for t, r, c in sp:
            if t == "row_clear":
                rem = self.board.activate_row_clear(r)
                spec_rem.update(rem)
                self.score += len(rem) * self.cfg["scoring"]["clear_per_gem"]  
            else:
                rem = self.board.activate_col_clear(c)
                spec_rem.update(rem)
                self.score += len(rem) * self.cfg["scoring"]["clear_per_gem"] 

        if spec_rem:
            self.snd.play_sfx("clear")

            # проверяем цепную реакцию
            chain = self._activate_specials_in_blast(spec_rem)
            if chain:
                new_chain = chain - spec_rem - matches
                if new_chain:
                    spec_rem.update(new_chain)
                    self.snd.play_sfx("bomb")
                    self.score += len(new_chain) * self.cfg["scoring"]["bomb_per_gem"]

            # удаляем всё вместе
            all_to_remove = matches.union(spec_rem)
            self.board.remove_gems(all_to_remove)

    def _apply_gravity_and_check(self):
        """Применяет гравитацию и проверяет новые совпадения"""
        self.board.apply_gravity()

        def check_after_gravity():
            nm, ng, ns = self.board.find_matches()
            if nm or ns:
                self._process_matches(nm, ng, ns)
            else:
                self.combo_count = 0
            self._check_no_moves()

        self._add_pending_action(check_after_gravity, 600)

    def _update(self, dt):
        # всегда обрабатываем очередь действий
        self._process_pending_actions()

        if self.state == GameState.PAUSED:
            return
        if self.state == GameState.MENU:
            self._update_menu_animation(dt)
        elif self.state == GameState.PLAYING:
            self.game_time += dt
            if self.mode == "time":
                self.time_left = max(0, 60 - self.game_time / 1000)
                if self.time_left <= 15 and not self.tense_music_played:
                    self.snd.play_music("tense")
                    self.tense_music_played = True
                if self.time_left <= 0 and not self.pending_actions:
                    self._end_game()
                    return
            elif self.mode == "points":
                if self.score >= self.goal_score and not self.pending_actions:
                    self._end_game()
                    return

            if self.board:
                self.board.update()

            if (
                self.board
                and not self.board.is_animating()
                and not self.board.has_valid_moves()
                and not self.pending_actions
            ):
                self.state = GameState.NO_MOVES
                self.snd.stop_music()
                self.snd.play_sfx("nomoves")

    def _end_game(self):
        self.state = GameState.GAME_OVER
        self.snd.stop_music()
        self.snd.play_sfx("win")

    def _render(self):
        self.screen.fill((15, 15, 30))
        renderers = {
            GameState.MENU: self._render_menu,
            GameState.MODE_SELECT: self._render_mode_select,
            GameState.LEVEL_SELECT: self._render_level_select,
            GameState.PLAYING: self._render_game,
            GameState.PAUSED: self._render_paused,
            GameState.GAME_OVER: self._render_game_over,
            GameState.NO_MOVES: self._render_no_moves,
            GameState.INPUT_NAME: self._render_input_name,
            GameState.LEADERBOARD: self._render_leaderboard,
            GameState.LEADERBOARD_MENU: self._render_leaderboard_menu,  # Новое
            GameState.HELP: self._render_help,
        }
        if self.state in renderers:
            renderers[self.state]()

    def _render_menu(self):
        t = pygame.time.get_ticks()

        for star in self.menu_bg_stars:
            twinkle = (
                math.sin(t / 1000 * star["twinkle_speed"] + star["phase"]) * 0.5 + 0.5
            )
            alpha = int(star["brightness"] * twinkle * 200)
            color = (180, 200, 255, alpha)
            star_surf = pygame.Surface(
                (star["size"] * 4, star["size"] * 4), pygame.SRCALPHA
            )
            pygame.draw.circle(
                star_surf, color, (star["size"] * 2, star["size"] * 2), star["size"]
            )
            self.screen.blit(
                star_surf, (star["x"] - star["size"] * 2, star["y"] - star["size"] * 2)
            )

        for gem in self.menu_gems:
            gem.draw(self.screen)

        for p in self.menu_particles:
            p.draw(self.screen)

        pulse = 1.0 + 0.04 * math.sin(t / 700)
        title_size = int(52 * pulse)
        tf = pygame.font.SysFont("Arial", title_size, bold=True)

        title = tf.render("Jewel Quest", True, (150, 220, 255))
        title_shadow = tf.render("Jewel Quest", True, (20, 40, 80))
        tx = self.width // 2 - title.get_width() // 2
        ty = 60 - title.get_height() // 2
        self.screen.blit(title_shadow, (tx + 4, ty + 4))
        self.screen.blit(title, (tx, ty))

        sub = self.small_font.render(
            "Собирай кристаллы | Ставь рекорды | Побеждай!", True, (180, 200, 220)
        )
        self.screen.blit(sub, (self.width // 2 - sub.get_width() // 2, 130))

        line_y = 165
        pygame.draw.line(
            self.screen,
            (60, 80, 120),
            (self.width // 2 - 200, line_y),
            (self.width // 2 + 200, line_y),
            2,
        )

        for b in self.buttons:
            b.draw(self.screen)

        ver = self.small_font.render("v666h3lp", True, (100, 100, 140))
        self.screen.blit(
            ver, (self.width // 2 - ver.get_width() // 2, self.height - 30)
        )

    def _render_mode_select(self):
        t = self.big_font.render("Выберите режим игры", True, (255, 255, 255))
        self.screen.blit(t, (self.width // 2 - t.get_width() // 2, 100))
        for b in self.mode_buttons:
            b.draw(self.screen)

    def _render_level_select(self):
        t = self.big_font.render("Выберите уровень сложности", True, (255, 255, 255))
        self.screen.blit(t, (self.width // 2 - t.get_width() // 2, 30))
        descs = [
            ("Все усилители", "Цель: 3000 очков"),
            ("Усилители без бомб", "Цель: 3500 очков"),
            ("Без усилителей", "Цель: 5000 очков"),
        ]
        for i, b in enumerate(self.level_buttons):
            if i < 3:
                b.draw(self.screen)
                d = self.small_font.render(descs[i][0], True, (200, 200, 220))
                g = self.small_font.render(descs[i][1], True, (150, 200, 150))
                self.screen.blit(d, (b.rect.right + 20, b.rect.centery - 14))
                self.screen.blit(g, (b.rect.right + 20, b.rect.centery + 8))
            else:
                b.draw(self.screen)

    def _render_game(self):
        ox = self.cfg["grid"]["offset_x"]
        oy = self.cfg["grid"]["offset_y"]
        cs = self.cfg["grid"]["cell_size"]

        # верхняя панель
        panel_height = 75
        pygame.draw.rect(
            self.screen,
            (35, 35, 55),
            (10, 10, self.width - 20, panel_height),
            border_radius=12,
        )

        # очкі - слева сверху
        self.screen.blit(
            self.font.render(f"Очки: {self.score}", True, (255, 255, 100)), (30, 20)
        )

        if self.mode == "time":
            tc = (255, 60, 60) if self.time_left <= 15 else (100, 255, 100)
            self.screen.blit(
                self.font.render(f"Время: {int(self.time_left)}с", True, tc),
                (self.width - 250, 20),
            )
        else:
            self.screen.blit(
                self.font.render(f"Цель: {self.goal_score}", True, (200, 200, 200)),
                (self.width - 250, 20),
            )

            level_names = {
                1: "Уровень 1 (Лёгкий)",
                2: "Уровень 2 (Средний)",
                3: "Уровень 3 (Сложный)",
            }
            level_text = self.small_font.render(
                level_names.get(self.level, ""), True, (200, 200, 255)
            )
            self.screen.blit(level_text, (30, 50))

            elapsed = self.game_time / 1000
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            time_text = self.small_font.render(
                f"Время: {mins}:{secs:02d}", True, (180, 220, 180)
            )
            self.screen.blit(time_text, (self.width - 250, 50))

        # кобо - над игровым полем
        if self.combo_count > 1:
            combo_text = self.combo_font.render(
                f"КОМБО x{self.combo_count}!", True, (255, 200, 50)
            )
            combo_y = oy - 40 
            cb = pygame.Rect(
                self.width // 2 - combo_text.get_width() // 2 - 15,
                combo_y,
                combo_text.get_width() + 30,
                28,
            )
            pygame.draw.rect(self.screen, (40, 30, 20), cb, border_radius=8)
            pygame.draw.rect(self.screen, (255, 180, 50), cb, 2, border_radius=8)
            self.screen.blit(
                combo_text, (self.width // 2 - combo_text.get_width() // 2, combo_y + 2)
            )

        # игровое поле
        if self.board:
            self.board.draw(self.screen, ox, oy)

        # подсветка выбранного кристалла
        if self.selected_gem:
            r, c = self.selected_gem
            x, y = ox + c * cs, oy + r * cs
            pulse = 3 + 3 * math.sin(pygame.time.get_ticks() / 150)
            pygame.draw.rect(
                self.screen, (255, 255, 100), (x + 2, y + 2, cs - 4, cs - 4), 4
            )
            pygame.draw.rect(
                self.screen,
                (255, 200, 50),
                (
                    x - int(pulse),
                    y - int(pulse),
                    cs + int(pulse * 2),
                    cs + int(pulse * 2),
                ),
                2,
            )

        # подсказка про паузу
        pause_hint = self.small_font.render("P - пауза", True, (120, 120, 150))
        self.screen.blit(
            pause_hint, (self.width - pause_hint.get_width() - 15, self.height - 25)
        )

    def _render_paused(self):
        self._render_game()

        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        pulse = 1.0 + 0.05 * math.sin(pygame.time.get_ticks() / 500)
        scaled_font = pygame.font.SysFont("Arial", int(40 * pulse), bold=True)
        pause_text = scaled_font.render("ПАУЗА", True, (255, 255, 255))
        self.screen.blit(
            pause_text,
            (self.width // 2 - pause_text.get_width() // 2, self.height // 2 - 120),
        )

        y_offset = self.height // 2 - 30
        info_texts = [
            ("P / ESC - продолжить", (200, 200, 200)),
            ("Q - выйти в меню", (200, 150, 150)),
        ]

        for text, color in info_texts:
            rendered = self.font.render(text, True, color)
            self.screen.blit(
                rendered, (self.width // 2 - rendered.get_width() // 2, y_offset)
            )
            y_offset += 35

        score_text = self.font.render(
            f"Текущий счет: {self.score}", True, (255, 255, 150)
        )
        self.screen.blit(
            score_text, (self.width // 2 - score_text.get_width() // 2, y_offset + 10)
        )

        resume_btn = pygame.Rect(self.width // 2 - 110, y_offset + 60, 220, 50)
        self.resume_button = type("obj", (object,), {"rect": resume_btn})()
        resume_hover = resume_btn.collidepoint(pygame.mouse.get_pos())
        resume_color = (80, 140, 80) if resume_hover else (60, 100, 60)
        pygame.draw.rect(self.screen, resume_color, resume_btn, border_radius=12)
        pygame.draw.rect(self.screen, (120, 200, 120), resume_btn, 3, border_radius=12)
        resume_text = self.font.render("Продолжить", True, (255, 255, 255))
        self.screen.blit(
            resume_text, (self.width // 2 - resume_text.get_width() // 2, y_offset + 72)
        )

        menu_btn = pygame.Rect(self.width // 2 - 110, y_offset + 125, 220, 50)
        self.menu_button = type("obj", (object,), {"rect": menu_btn})()
        menu_hover = menu_btn.collidepoint(pygame.mouse.get_pos())
        menu_color = (140, 70, 70) if menu_hover else (100, 50, 50)
        pygame.draw.rect(self.screen, menu_color, menu_btn, border_radius=12)
        pygame.draw.rect(self.screen, (200, 120, 120), menu_btn, 3, border_radius=12)
        menu_text = self.font.render("В меню", True, (255, 255, 255))
        self.screen.blit(
            menu_text, (self.width // 2 - menu_text.get_width() // 2, y_offset + 137)
        )

    def _render_game_over(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        self.screen.blit(
            self.big_font.render("Игра окончена!", True, (255, 100, 100)),
            (self.width // 2 - 120, self.height // 2 - 100),
        )
        self.screen.blit(
            self.font.render(f"Счет: {self.score}", True, (255, 255, 255)),
            (self.width // 2 - 60, self.height // 2 - 40),
        )

        # для режима очков показываем время прохождения
        if self.mode == "points":
            elapsed = self.game_time / 1000
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            time_text = self.font.render(
                f"Время: {mins}:{secs:02d}", True, (200, 200, 255)
            )
            self.screen.blit(
                time_text,
                (self.width // 2 - time_text.get_width() // 2, self.height // 2),
            )

        self.screen.blit(
            self.small_font.render(
                "Enter или клик - продолжить", True, (150, 150, 150)
            ),
            (self.width // 2 - 120, self.height // 2 + 50),
        )

    def _render_no_moves(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        sad_face = self.emoji_font.render(":(", True, (255, 200, 100))
        self.screen.blit(
            sad_face,
            (self.width // 2 - sad_face.get_width() // 2, self.height // 2 - 110),
        )

        msg = self.big_font.render("Ходов нет!", True, (255, 130, 130))
        self.screen.blit(
            msg, (self.width // 2 - msg.get_width() // 2, self.height // 2 - 30)
        )

        msg2 = self.font.render("Игра окончена.", True, (255, 180, 180))
        self.screen.blit(
            msg2, (self.width // 2 - msg2.get_width() // 2, self.height // 2 + 15)
        )

        score_text = self.font.render(f"Счет: {self.score}", True, (255, 255, 150))
        self.screen.blit(
            score_text,
            (self.width // 2 - score_text.get_width() // 2, self.height // 2 + 60),
        )

        hint = self.small_font.render(
            "Enter или клик - продолжить", True, (150, 150, 150)
        )
        self.screen.blit(
            hint, (self.width // 2 - hint.get_width() // 2, self.height // 2 + 100)
        )

    def _render_input_name(self):
        self.screen.blit(
            self.big_font.render("Новый рекорд!", True, (255, 215, 0)),
            (self.width // 2 - 120, self.height // 2 - 130),
        )
        self.screen.blit(
            self.font.render(f"Очки: {self.score}", True, (255, 255, 255)),
            (self.width // 2 - 50, self.height // 2 - 70),
        )
        self.screen.blit(
            self.font.render("Введите имя:", True, (200, 200, 200)),
            (self.width // 2 - 70, self.height // 2 - 20),
        )

        ir = pygame.Rect(self.width // 2 - 150, self.height // 2 + 10, 300, 50)
        pygame.draw.rect(self.screen, (40, 40, 60), ir, border_radius=8)
        pygame.draw.rect(self.screen, (100, 180, 255), ir, 2, border_radius=8)

        cur = "_" if int(pygame.time.get_ticks() / 500) % 2 == 0 else " "
        self.screen.blit(
            self.font.render(self.input_text + cur, True, (255, 255, 255)),
            (self.width // 2 - 140, self.height // 2 + 22),
        )
        self.screen.blit(
            self.small_font.render("Enter - сохранить", True, (150, 150, 150)),
            (self.width // 2 - 70, self.height // 2 + 80),
        )

    def _render_leaderboard(self):
        """Отрисовка таблицы рекордов (два вида)"""
        if self.leaderboard_type == "scores":
            self._render_scores_leaderboard()
        else:
            self._render_time_leaderboard()

    def _render_scores_leaderboard(self):
        """Таблица рекордов по очкам (режим очков) - сортировка по времени"""
        self.screen.blit(
            self.big_font.render("Рекорды по очкам", True, (255, 215, 0)),
            (self.width // 2 - 150, 30),
        )

        lb = self._load_leaderboard()
        # фильтр и сортировка по времени
        scores_lb = [e for e in lb if e.get("mode") == "points"]
        scores_lb.sort(key=lambda x: x.get("time_seconds", 9999))

        if not scores_lb:
            self.screen.blit(
                self.font.render("Пока нет рекордов", True, (150, 150, 150)),
                (self.width // 2 - 100, 250),
            )
        else:
            headers = ["№", "Имя", "Очки", "Уровень", "Время"]
            col_widths = [50, 200, 100, 100, 100]
            x_start = self.width // 2 - 275

            # заголовки
            x = x_start
            for header, width in zip(headers, col_widths):
                color = (255, 255, 100)
                text = self.font.render(header, True, color)
                if header == "Имя":
                    text_rect = text.get_rect(midleft=(x + 10, 110))
                else:
                    text_rect = text.get_rect(center=(x + width // 2, 110))
                self.screen.blit(text, text_rect)
                x += width

            pygame.draw.line(
                self.screen,
                (100, 100, 150),
                (x_start, 135),
                (x_start + sum(col_widths), 135),
                2,
            )

            for i, entry in enumerate(scores_lb[:10]):
                y = 150 + i * 38

                if i % 2 == 0:
                    row_rect = pygame.Rect(x_start - 5, y - 3, sum(col_widths) + 10, 35)
                    pygame.draw.rect(
                        self.screen, (30, 30, 50), row_rect, border_radius=5
                    )

                # топ-3
                if i == 0:
                    clr = (255, 215, 0)
                elif i == 1:
                    clr = (192, 192, 192)
                elif i == 2:
                    clr = (205, 127, 50)
                else:
                    clr = (220, 220, 220)

                name = entry.get("name", "Игрок")[:14]
                score = str(entry.get("score", 0))
                level_num = entry.get("level", "?")
                level = f"Ур.{level_num}"
                time_str = entry.get("time", "-")

                # №
                num_text = self.small_font.render(str(i + 1), True, clr)
                num_rect = num_text.get_rect(
                    center=(x_start + col_widths[0] // 2, y + 15)
                )
                self.screen.blit(num_text, num_rect)

                # имя
                name_text = self.small_font.render(name, True, clr)
                self.screen.blit(name_text, (x_start + col_widths[0] + 10, y + 8))

                # очки
                score_text = self.small_font.render(score, True, clr)
                score_rect = score_text.get_rect(
                    center=(
                        x_start + col_widths[0] + col_widths[1] + col_widths[2] // 2,
                        y + 15,
                    )
                )
                self.screen.blit(score_text, score_rect)

                # ур
                level_text = self.small_font.render(level, True, clr)
                level_rect = level_text.get_rect(
                    center=(
                        x_start
                        + col_widths[0]
                        + col_widths[1]
                        + col_widths[2]
                        + col_widths[3] // 2,
                        y + 15,
                    )
                )
                self.screen.blit(level_text, level_rect)

                # время
                time_text = self.small_font.render(time_str, True, clr)
                time_rect = time_text.get_rect(
                    center=(x_start + sum(col_widths) - col_widths[4] // 2, y + 15)
                )
                self.screen.blit(time_text, time_rect)

        self._draw_leaderboard_buttons()

    def _render_time_leaderboard(self):
        """Таблица рекордов по времени (режим на время) - сортировка по очкам"""
        self.screen.blit(
            self.big_font.render("Рекорды по времени", True, (100, 200, 255)),
            (self.width // 2 - 170, 30),
        )

        lb = self._load_leaderboard()
        time_lb = [e for e in lb if e.get("mode") == "time"]
        time_lb.sort(key=lambda x: -x.get("score", 0))

        if not time_lb:
            self.screen.blit(
                self.font.render("Пока нет рекордов", True, (150, 150, 150)),
                (self.width // 2 - 100, 250),
            )
        else:
            headers = ["№", "Имя", "Очки"]
            col_widths = [60, 340, 150]
            x_start = self.width // 2 - 275

            x = x_start
            for header, width in zip(headers, col_widths):
                color = (255, 255, 100)
                text = self.font.render(header, True, color)
                if header == "Имя":
                    text_rect = text.get_rect(midleft=(x + 10, 110))
                else:
                    text_rect = text.get_rect(center=(x + width // 2, 110))
                self.screen.blit(text, text_rect)
                x += width

            pygame.draw.line(
                self.screen,
                (100, 100, 150),
                (x_start, 135),
                (x_start + sum(col_widths), 135),
                2,
            )

            for i, entry in enumerate(time_lb[:10]):
                y = 150 + i * 38

                if i % 2 == 0:
                    row_rect = pygame.Rect(x_start - 5, y - 3, sum(col_widths) + 10, 35)
                    pygame.draw.rect(
                        self.screen, (30, 30, 50), row_rect, border_radius=5
                    )

                if i == 0:
                    clr = (255, 215, 0)
                elif i == 1:
                    clr = (192, 192, 192)
                elif i == 2:
                    clr = (205, 127, 50)
                else:
                    clr = (220, 220, 220)

                name = entry.get("name", "Игрок")[:22]
                score = str(entry.get("score", 0))

                num_text = self.small_font.render(str(i + 1), True, clr)
                num_rect = num_text.get_rect(
                    center=(x_start + col_widths[0] // 2, y + 15)
                )
                self.screen.blit(num_text, num_rect)

                name_text = self.small_font.render(name, True, clr)
                self.screen.blit(name_text, (x_start + col_widths[0] + 10, y + 8))

                score_text = self.small_font.render(score, True, clr)
                score_rect = score_text.get_rect(
                    center=(
                        x_start + col_widths[0] + col_widths[1] + col_widths[2] // 2,
                        y + 15,
                    )
                )
                self.screen.blit(score_text, score_rect)

        self._draw_leaderboard_buttons()

    def _draw_leaderboard_buttons(self):
        """Рисует возврат"""
        # кнопка "Назад"
        back_btn = pygame.Rect(self.width // 2 - 50, self.height - 25, 100, 25)
        self.lb_back_btn = back_btn
        back_text = self.small_font.render("ESC - назад", True, (150, 150, 150))
        self.screen.blit(back_text, back_text.get_rect(center=back_btn.center))

    def _render_leaderboard_menu(self):
        """Меню выбора таблицы рекордов"""
        self.screen.blit(
            self.big_font.render("Таблица рекордов", True, (255, 215, 0)),
            (self.width // 2 - 150, 80),
        )

        self.screen.blit(
            self.font.render("Выберите тип рекордов:", True, (200, 200, 200)),
            (self.width // 2 - 130, 180),
        )

        # кнопка "рекорды по очкам"
        scores_btn = pygame.Rect(self.width // 2 - 180, 250, 360, 70)
        self.lb_scores_btn = scores_btn
        scores_hover = scores_btn.collidepoint(pygame.mouse.get_pos())
        scores_color = (60, 100, 60) if scores_hover else (40, 70, 40)
        pygame.draw.rect(self.screen, scores_color, scores_btn, border_radius=15)
        pygame.draw.rect(self.screen, (120, 180, 120), scores_btn, 3, border_radius=15)

        scores_title = self.font.render("По очкам", True, (255, 255, 255))
        scores_desc = self.small_font.render(
            "Рекорды режима на очки (уровни)", True, (200, 220, 200)
        )
        self.screen.blit(
            scores_title, (self.width // 2 - scores_title.get_width() // 2, 258)
        )
        self.screen.blit(
            scores_desc, (self.width // 2 - scores_desc.get_width() // 2, 290)
        )

        # кнопка "рекорды по времени"
        time_btn = pygame.Rect(self.width // 2 - 180, 350, 360, 70)
        self.lb_time_btn = time_btn
        time_hover = time_btn.collidepoint(pygame.mouse.get_pos())
        time_color = (60, 60, 120) if time_hover else (40, 40, 80)
        pygame.draw.rect(self.screen, time_color, time_btn, border_radius=15)
        pygame.draw.rect(self.screen, (120, 120, 200), time_btn, 3, border_radius=15)

        time_title = self.font.render("По времени", True, (255, 255, 255))
        time_desc = self.small_font.render(
            "Рекорды режима на время (60 сек)", True, (200, 200, 240)
        )
        self.screen.blit(
            time_title, (self.width // 2 - time_title.get_width() // 2, 358)
        )
        self.screen.blit(time_desc, (self.width // 2 - time_desc.get_width() // 2, 390))

        #назад
        back_btn = pygame.Rect(self.width // 2 - 50, self.height - 50, 100, 30)
        self.lb_back_btn = back_btn
        back_text = self.small_font.render("ESC - назад", True, (150, 150, 150))
        self.screen.blit(back_text, back_text.get_rect(center=back_btn.center))

    def _render_help(self):
        self.screen.blit(
            self.big_font.render("Правила игры", True, (100, 200, 255)),
            (self.width // 2 - 100, 25),
        )

        rules = [
            (
                "ОСНОВЫ",
                [
                    "3+ одинаковых в ряд - совпадение",
                    "4 в ряд - очиститель ряда/столбца",
                    "5+ в ряд - БОМБА",
                ],
            ),
            (
                "СПЕЦКРИСТАЛЛЫ",
                [
                    "Бомба (темная с шипами): взрыв 3x3 при обмене",
                    "Удаление ряда: ЗОЛОТАЯ рамка + гор. стрелка",
                    "Удаление столбца: РОЗОВАЯ рамка + верт. стрелка",
                    "Удаления активируются с 2+ кристаллами своего цвета",
                ],
            ),
            (
                "КОМБО",
                [
                    "Бомба + Бомба = взрыв 5x5!",
                    "Бомба + Удаление ряда = 3 ряда!",
                    "Бомба + Удаление столбца = 3 столбца!",
                    "Удаление ряда + Удаление столбца = КРЕСТ!",
                    "Если бомба задевает другие спецкристаллы - они тоже активируются (цепная реакция)",
                ],
            ),
            (
                "УРОВНИ",
                [
                    "Ур.1 (легкий): все усилители используются, цель 3000",
                    "Ур.2(средний): усилители без бомб, цель 3500",
                    "Ур.3(сложный): без усилителей, цель 5000",
                ],
            ),
            (
                "УПРАВЛЕНИЕ",
                ["P - пауза", "ESC - снять выделение", "Q - выход в меню (из паузы)"],
            ),
        ]

        y = 80
        for sec, items in rules:
            self.screen.blit(self.font.render(sec, True, (255, 255, 100)), (40, y))
            y += 30
            for it in items:
                self.screen.blit(
                    self.small_font.render("• " + it, True, (200, 200, 220)), (60, y)
                )
                y += 22
            y += 10

        self.screen.blit(
            self.small_font.render("ESC или клик - назад", True, (150, 150, 150)),
            (self.width // 2 - 80, self.height - 35),
        )

    def start_time_mode(self):
        self.mode = "time"
        self.score = 0
        self.time_left = 60
        self.game_time = 0
        self.tense_music_played = False
        self.combo_count = 0
        self.pending_actions = []
        self.board = Board(
            8,
            8,
            self.cfg["grid"]["cell_size"],
            allow_specials=True,
            allow_bombs=True,
            spawn_bombs=True,
        )
        self.selected_gem = None
        self.state = GameState.PLAYING
        self.snd.play_music("calm")

    def start_points_mode(self, level):
        self.mode = "points"
        self.score = 0
        self.level = level
        self.game_time = 0
        self.combo_count = 0
        self.pending_actions = []
        goals = {1: 3000, 2: 3500, 3: 5000}
        self.goal_score = goals.get(level, 2500)

        if level == 1:
            self.board = Board(
                8,
                8,
                self.cfg["grid"]["cell_size"],
                allow_specials=True,
                allow_bombs=True,
                spawn_bombs=True,
            )
        elif level == 2:
            self.board = Board(
                8,
                8,
                self.cfg["grid"]["cell_size"],
                allow_specials=True,
                allow_bombs=False,
                spawn_bombs=False,
            )
        else:
            self.board = Board(
                8,
                8,
                self.cfg["grid"]["cell_size"],
                allow_specials=False,
                allow_bombs=False,
                spawn_bombs=False,
            )

        self.selected_gem = None
        self.state = GameState.PLAYING
        self.snd.play_music("calm")

    def _load_leaderboard(self):
        if not os.path.exists("leaderboard.json"):
            return []
        try:
            with open("leaderboard.json", "r", encoding="utf-8") as f:
                d = json.load(f)
            # делим на два списка
            scores_lb = [e for e in d if e.get("mode") == "points"]
            time_lb = [e for e in d if e.get("mode") == "time"]

            # сортировка по времени
            scores_lb.sort(key=lambda x: x.get("time_seconds", 9999))

            # по очкам
            time_lb.sort(key=lambda x: -x.get("score", 0))

            # объединяем обратно
            return scores_lb + time_lb
        except:
            return []

    def _save_score(self):
        name = self.input_text.strip() or "Игрок"
        lb = self._load_leaderboard()

        # форматируем время
        elapsed = self.game_time / 1000
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        time_str = f"{mins}:{secs:02d}"
        time_seconds = int(elapsed)

        entry = {
            "name": name,
            "score": self.score,
            "mode": self.mode,
            "time": time_str,
            "time_seconds": time_seconds,
        }

        if self.mode == "points":
            entry["level"] = self.level

        lb.append(entry)

        # сортировка
        scores_lb = [e for e in lb if e.get("mode") == "points"]
        time_lb = [e for e in lb if e.get("mode") == "time"]

        # по времени
        scores_lb.sort(key=lambda x: x.get("time_seconds", 9999))

        #по очкам
        time_lb.sort(key=lambda x: -x.get("score", 0))

        # оставим топ 10 
        scores_lb = scores_lb[:10]
        time_lb = time_lb[:10]

        # Объединяем
        lb = scores_lb + time_lb

        try:
            with open("leaderboard.json", "w", encoding="utf-8") as f:
                json.dump(lb, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
        self.input_text = ""
