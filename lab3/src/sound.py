import os
import pygame
from src.config import ConfigManager


class SoundManager:
    """Менеджер звуков и музыки"""
    
    def __init__(self):
        self.sounds_available = True
        self.sfx = {}
        self.current_music = None
        self.cfg = ConfigManager.load()
        try:
            pygame.mixer.init()
            print("Звуковая система инициализирована")
        except Exception as e:
            self.sounds_available = False
            print(f"Звук недоступен: {e}")
        self._try_load_sounds()
    
    def _try_load_sounds(self):
        if not self.sounds_available:
            return
        
        if not os.path.exists("assets/sounds"):
            os.makedirs("assets/sounds", exist_ok=True)
        
        paths = self.cfg.get("paths", {})
        sound_files = {
            "swap": paths.get("sfx_swap", "assets/sounds/swap.wav"),
            "match": paths.get("sfx_match", "assets/sounds/match.wav"),
            "bomb": paths.get("sfx_bomb", "assets/sounds/bomb.wav"),
            "clear": paths.get("sfx_clear", "assets/sounds/clear.wav"),
            "click": paths.get("sfx_click", "assets/sounds/click.wav"),
            "gem_click": paths.get("sfx_gem_click", "assets/sounds/gem_click.wav"),
            "win": paths.get("sfx_win", "assets/sounds/win.wav"),
            "nomoves": paths.get("sfx_nomoves", "assets/sounds/nomoves.wav")
        }
        
        for name, full_path in sound_files.items():
            if os.path.exists(full_path):
                try:
                    self.sfx[name] = pygame.mixer.Sound(full_path)
                    self.sfx[name].set_volume(0.5)
                except Exception as e:
                    print(f"Ошибка загрузки {full_path}: {e}")
    
    def play_sfx(self, name):
        if name in self.sfx:
            try:
                self.sfx[name].play()
            except:
                pass
    
    def play_menu_music(self):
        self._play_music_track("menu")
    
    def play_music(self, track="calm"):
        self._play_music_track(track)
    
    def _play_music_track(self, track_name):
        if track_name == self.current_music:
            return
        
        paths = self.cfg.get("paths", {})
        music_key = f"bgm_{track_name}"
        default_path = f"assets/sounds/bgm_{track_name}.wav"
        music_file = paths.get(music_key, default_path)
        
        if os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play(-1)
                self.current_music = track_name
            except Exception as e:
                print(f"Ошибка загрузки музыки: {e}")
        else:
            self.current_music = None
    
    def stop_music(self):
        try:
            pygame.mixer.music.fadeout(500)
            self.current_music = None
        except:
            pass
    
    def pause_music(self):
        try:
            pygame.mixer.music.pause()
        except:
            pass
    
    def resume_music(self):
        try:
            pygame.mixer.music.unpause()
        except:
            pass