import sys
import pygame
import pygame_widgets
import pickle
from pygame_widgets.slider import Slider
from pygame.locals import VIDEORESIZE,KEYDOWN,K_F11
from level import Level
from overworld import Overworld
from settings import *
from ui import UI


class Data:

    def save_data(data):
        with open('data/settings.cfg', 'wb') as f:
            pickle.dump(data, f)

    def load_data():
        try:
            with open('data/settings.cfg', 'rb') as f:
                data = pickle.load(f)
                return data
        except FileNotFoundError:
            return None

    def main():
        # Load data from file (if exists)
        saved_data = load_data()
        if saved_data is not None:
            # Utilisez les données chargées dans votre programme
            game.max_level = saved_data['max_level']
            game.cur_health = saved_data['cur_health']
            game.coins = saved_data['coins']
            game.sound = saved_data['sound']
            # Chargez d'autres données comme cela...

        # Le reste de votre programme principal...

        # Save data before exiting
        data_to_save = {
            'max_level': game.max_level,
            'cur_health': game.cur_health,
            'coins': game.coins,
            'sound': game.sound,
            # Sauvegardez d'autres données comme cela...
        }
        save_data(data_to_save)



class Game:

    def __init__(self):

        # pause and buttons
        self.if_sound = None
        self.volume_add = None
        self.volume_remove = None
        self.resume = None
        self.restart = None
        self.saves = None
        self.pause = False

        self.font = pygame.font.Font('venv/graphics/ui/ARCADEPI.ttf', 32)
        self.font2 = pygame.font.Font('venv/graphics/ui/ARCADEPI.ttf', 64)
        self.surface = pygame.Surface([screen_width, screen_height], pygame.SRCALPHA)

        # game attributes
        self.max_level = 0
        self.max_health = 100
        self.cur_health = self.max_health
        self.coins = 0
        self.sound = True
        self.volume_gain = 0.1
        self.volume_musics = 1
        self.volume_effects = 1

        # audio
        self.volume_gain = int(pygame_widgets.slider.Slider.getValue(slider1))/100
        self.volume_musics = int(pygame_widgets.slider.Slider.getValue(slider2))/10
        self.volume_effects = int(pygame_widgets.slider.Slider.getValue(slider3))/10
        self.music_volume_multiplicator = (self.volume_gain * self.volume_musics * self.sound)
        self.effect_volume_multiplicator = (self.volume_gain * self.volume_effects * self.sound)

        self.level_bg_music = pygame.mixer.Sound('venv/audio/level_music.wav')
        self.overworld_bg_music = pygame.mixer.Sound('venv/audio/overworld_music.wav')
        self.coin_sound = pygame.mixer.Sound('venv/audio/effects/coin.wav')
        self.stomp_sound = pygame.mixer.Sound('venv/audio/effects/stomp.wav')
        self.jump_sound = pygame.mixer.Sound('venv/audio/effects/jump.wav')
        self.hit_sound = pygame.mixer.Sound('venv/audio/effects/hit.wav')
        self.click_sound = pygame.mixer.Sound('venv/audio/effects/click.wav')
        self.update_volume()

        # overworld creation
        self.overworld = Overworld(0, self.max_level, screen, self.create_level)
        self.status = 'overworld'
        self.overworld_bg_music.play(loops=-1)

        # user interface
        self.ui = UI(screen)

        # time
        self.allow_input = True
        self.timer_length = 225
        self.start_time = pygame.time.get_ticks()

    def update_health(self, amount):
        self.cur_health += amount

    def create_level(self, current_level):
        self.level = Level(current_level, screen, self.create_overworld, self.change_coins, self.change_health,
                           self.sound, self.volume_gain, self.volume_effects, self.volume_musics,
                           self.overworld_bg_music, self.level_bg_music, self.coin_sound, self.stomp_sound,
                           self.hit_sound, self.jump_sound, self.pause)
        self.status = 'level'
        self.overworld_bg_music.stop()
        self.level_bg_music.play(loops=-1)

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
        self.status = 'overworld'
        self.level_bg_music.stop()
        self.overworld_bg_music.play(loops=-1)

    def change_health(self, amount):
        self.cur_health += amount

    def change_coins(self, count):
        self.coins += count

    def if_pause(self, value):
        self.pause = value

    def check_game_over(self):
        if self.cur_health <= 0:
            self.cur_health = 100
            self.coins = 0
            self.max_level = 0
            if self.status == 'level':
                self.overworld = Overworld(0, self.max_level, screen, self.create_level)
            self.status = 'overworld'
            self.level_bg_music.stop()
            self.overworld_bg_music.play(loops=-1)

    def update_volume(self):
        self.volume_gain = int(pygame_widgets.slider.Slider.getValue(slider1))/100
        self.volume_musics = int(pygame_widgets.slider.Slider.getValue(slider2))/10
        self.volume_effects = int(pygame_widgets.slider.Slider.getValue(slider3))/10
        self.music_volume_multiplicator = (self.volume_gain * self.volume_musics * self.sound)
        self.effect_volume_multiplicator = (self.volume_gain * self.volume_effects * self.sound)
        self.level_bg_music.set_volume(self.music_volume_multiplicator)
        self.overworld_bg_music.set_volume(self.music_volume_multiplicator)
        self.coin_sound.set_volume(self.effect_volume_multiplicator)
        self.stomp_sound.set_volume(self.effect_volume_multiplicator)
        self.jump_sound.set_volume(self.effect_volume_multiplicator)
        self.hit_sound.set_volume(self.effect_volume_multiplicator)
        self.click_sound.set_volume(self.effect_volume_multiplicator)

    def input(self):
        if not self.pause:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_p] and self.volume_gain < 1:
                self.volume_gain += 0.01
                print(self.volume_gain)
                self.update_volume()
            elif keys[pygame.K_m] and self.volume_gain > 0:
                self.volume_gain -= 0.01
                print(self.volume_gain)
                self.update_volume()
            if keys[pygame.K_z]:
                if self.sound:
                    self.sound = False
                    self.allow_input = False
                    self.update_volume()
                    self.timer()
                else:
                    self.sound = True
                    self.allow_input = False
                    self.timer()
                    self.update_volume()
            if keys[pygame.K_TAB]:
                if self.pause:
                    self.pause = False
                else:
                    self.pause = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                current_time = pygame.time.get_ticks()
                if current_time - self.start_time > self.timer_length:
                    if not self.pause:
                        self.pause = True
                    else:
                        self.pause = False

                    self.start_time = current_time


    def timer(self):
        if not self.allow_input:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.timer_length:
                self.allow_input = True

    def draw_pause(self):
        pygame.draw.rect(self.surface, (128, 128, 128, 150), [0, 0, screen_width, screen_height])
        pygame.draw.rect(self.surface, '#ffffff', [screen_width * 0.5 - 150, 380, 160, 80], 5, 10)
        self.saves = pygame.draw.rect(self.surface, '#ffffff', [screen_width * 0.5 - 245, 200, 240, 80], 5, 10)
        self.restart = pygame.draw.rect(self.surface, '#ffffff', [screen_width * 0.5 + 5, 200, 240, 80], 5, 10)
        self.resume = pygame.draw.rect(self.surface, '#ffffff', [screen_width * 0.5 - 120, 290, 240, 80], 5, 10)
        self.volume_add = pygame.draw.rect(self.surface, '#ffffff', [screen_width * 0.5 + 20, 380, 80, 80], 5, 10)
        self.volume_remove = pygame.draw.rect(self.surface, '#ffffff', [screen_width * 0.5 - 240, 380, 80, 80], 5, 10)
        self.if_sound = pygame.draw.rect(self.surface, '#ffffff', [screen_width * 0.5 + 130, 290, 115, 80], 5, 10)
        self.surface.blit(self.font2.render('+', True, '#666666'), (screen_width * 0.5 - 215, 390))
        self.surface.blit(self.font2.render('-', True, '#666666'), (screen_width * 0.5 + 45, 390))
        if event.type == pygame.MOUSEMOTION and self.pause:
            if self.saves.collidepoint(event.pos):
                self.saves = pygame.draw.rect(self.surface, '#2abd67', [screen_width * 0.5 - 245, 200, 240, 80], 10, 10)
                self.saves = pygame.draw.rect(self.surface, '#078b33', [screen_width * 0.5 - 245, 200, 240, 80], 5, 10)
                self.change_cursor(True)
            elif self.restart.collidepoint(event.pos):
                self.restart = pygame.draw.rect(self.surface, '#f0bc10', [screen_width * 0.5 + 5, 200, 240, 80], 10, 10)
                self.restart = pygame.draw.rect(self.surface, '#ee8b13', [screen_width * 0.5 + 5, 200, 240, 80], 5, 10)
                self.change_cursor(True)
            elif self.resume.collidepoint(event.pos):
                self.resume = pygame.draw.rect(self.surface, '#f4654b', [screen_width * 0.5 - 120, 290, 240, 80], 10, 10)
                self.resume = pygame.draw.rect(self.surface, '#cb3c1c', [screen_width * 0.5 - 120, 290, 240, 80], 5, 10)
                self.change_cursor(True)
            elif self.volume_add.collidepoint(event.pos):
                self.volume_add = pygame.draw.rect(self.surface, '#f4654b', [screen_width * 0.5 + 20, 380, 80, 80], 10, 10)
                self.volume_add = pygame.draw.rect(self.surface, '#cb3c1c', [screen_width * 0.5 + 20, 380, 80, 80], 5, 10)
                self.surface.blit(self.font2.render('-', True, '#f4654b'), (screen_width * 0.5 + 45, 390))
                self.change_cursor(True)
            elif self.volume_remove.collidepoint(event.pos):
                self.volume_remove = pygame.draw.rect(self.surface, '#2abd67', [screen_width * 0.5 - 240, 380, 80, 80], 10, 10)
                self.volume_remove = pygame.draw.rect(self.surface, '#078b33', [screen_width * 0.5 - 240, 380, 80, 80], 5, 10)
                self.surface.blit(self.font2.render('+', True, '#2abd67'), (screen_width * 0.5 - 215, 390))
                self.change_cursor(True)
            elif self.if_sound.collidepoint(event.pos):
                self.if_sound = pygame.draw.rect(self.surface, '#f4654b', [screen_width * 0.5 + 130, 290, 115, 80], 10, 10)
                self.if_sound = pygame.draw.rect(self.surface, '#cb3c1c', [screen_width * 0.5 + 130, 290, 115, 80], 5, 10)
                self.change_cursor(True)
            else:
                self.change_cursor(False)
        self.surface.blit(self.font.render('Game Paused', True, '#000000'), (screen_width * 0.5 - 125, 150))
        self.surface.blit(self.font.render('Restart', True, '#000000'), (screen_width * 0.5 + 50, 225))
        self.surface.blit(self.font.render('Save', True, '#000000'), (screen_width * 0.5 - 170, 225))
        self.surface.blit(self.font.render('Resume', True, '#000000'), (screen_width * 0.5 - 70, 315))
        self.surface.blit(self.font.render(str(int(self.volume_gain * 100)), True, '#df6c00'), (screen_width/2+150, screen_height/2+115))
        self.surface.blit(self.font.render(str(int(self.volume_musics * 10)), True, '#df6c00'), (screen_width/2+150, screen_height/2+155))
        self.surface.blit(self.font.render(str(int(self.volume_effects * 10)), True, '#df6c00'), (screen_width/2+150, screen_height/2+195))
        self.update_volume()
        screen.blit(self.surface, (0, 0))
        if event.type == pygame.MOUSEBUTTONDOWN and self.pause:
            if self.restart.collidepoint(event.pos):
                if self.status == 'level':
                    self.cur_health = 0
                self.pause = False
                self.click_sound.play()
            if self.saves.collidepoint(event.pos):
                self.pause = False
                self.click_sound.play()
            if self.resume.collidepoint(event.pos):
                self.pause = False
                self.click_sound.play()

        pygame_widgets.update(event)
        pygame.display.update()

        return self.restart, self.saves, self.resume

    def change_cursor(self, should_change):
        if should_change:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def run(self):

        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.check_game_over()
        self.timer()
        self.input()
        self.ui.show_if_muted(self.sound, self.volume_gain, self.pause)
        self.ui.show_health(self.cur_health, self.max_health, self.pause)
        self.ui.show_coins(self.coins, self.pause)
        if self.pause:
            self.restart, self.saves, self.resume = self.draw_pause()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Landers - V0.2.5')
    pygame_icon = pygame.image.load('venv\\graphics\\tilesTEST.png')
    pygame.display.set_icon(pygame_icon)
    screen = pygame.display.set_mode((screen_width, screen_height))
    slider1 = Slider(screen, int(screen_width/2-230), int(screen_height/2+120), 360, 20, min=0, max=100, step=1, initial=5)
    slider2 = Slider(screen, int(screen_width/2-230), int(screen_height/2+160), 360, 20, min=0, max=100, step=1, initial=5)
    slider3 = Slider(screen, int(screen_width/2-230), int(screen_height/2+200), 360, 20, min=0, max=100, step=1, initial=5)
    root = tk.Tk()
    monitor_size = [root.winfo_screenwidth(), root.winfo_screenheight()]
    clock = pygame.time.Clock()

    game = Game()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == VIDEORESIZE:
            if not fullscreen:
                screen = pygame.display.set_mode((event.w, event.h))
        if event.type == KEYDOWN:
            if event.key == K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((screen_width, screen_height))

    game.run()


    pygame.display.update()
    clock.tick(60)

