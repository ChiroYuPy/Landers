import sys

import pygame

from level import Level
from overworld import Overworld
from settings import *
from ui import UI


class Game:
    def __init__(self):

        self.restart = None
        self.saves = None
        self.pause = False

        self.font = pygame.font.Font('venv/graphics/ui/ARCADEPI.ttf', 32)
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
        self.level_bg_music = pygame.mixer.Sound('venv/audio/level_music.wav')
        self.overworld_bg_music = pygame.mixer.Sound('venv/audio/overworld_music.wav')
        self.coin_sound = pygame.mixer.Sound('venv/audio/effects/coin.wav')
        self.stomp_sound = pygame.mixer.Sound('venv/audio/effects/stomp.wav')
        self.jump_sound = pygame.mixer.Sound('venv/audio/effects/jump.wav')
        self.hit_sound = pygame.mixer.Sound('venv/audio/effects/hit.wav')
        self.update_volume()

        # Tkt fréro <3

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

    def check_game_over(self):
        if self.cur_health <= 0:
            self.cur_health = 100
            self.coins = 0
            self.max_level = 0
            self.overworld = Overworld(0, self.max_level, screen, self.create_level)
            self.status = 'overworld'
            self.level_bg_music.stop()
            self.overworld_bg_music.play(loops=-1)

    def update_volume(self):
        self.level_bg_music.set_volume(self.volume_gain * self.volume_musics * self.sound)
        self.overworld_bg_music.set_volume(self.volume_gain * self.volume_musics * self.sound)
        self.coin_sound.set_volume(self.volume_gain * self.volume_effects * self.sound)
        self.stomp_sound.set_volume(self.volume_gain * self.volume_effects * self.sound)
        self.jump_sound.set_volume(self.volume_gain * self.volume_effects * self.sound)
        self.hit_sound.set_volume(self.volume_gain * self.volume_effects * self.sound)

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
                        print('pause = True')
                        self.pause = True
                    else:
                        print('pause = False')
                        self.pause = False

                    self.start_time = current_time
        if event.type == pygame.MOUSEBUTTONDOWN and self.pause:
            if self.saves.collidepoint(event.pos):
                self.pause = False


    def timer(self):
        if not self.allow_input:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.timer_length:
                self.allow_input = True

    def draw_pause(self):
        pygame.draw.rect(self.surface, (128, 128, 128, 150), [0, 0, screen_width, screen_height])
        pygame.draw.rect(self.surface, 'grey', [screen_width * 0.5 - 245, 200, 240, 80], 5, 10)
        self.reset = pygame.draw.rect(self.surface, 'grey', [screen_width * 0.5 + 5, 200, 240, 80], 5, 10)
        self.save = pygame.draw.rect(self.surface, 'grey', [screen_width * 0.5 - 120, 290, 240, 80], 5, 10)
        self.surface.blit(self.font.render('Game Paused', True, 'black'), (screen_width * 0.5 - 125, 150))
        self.surface.blit(self.font.render('Restart', True, 'black'), (screen_width * 0.5 + 50, 225))
        self.surface.blit(self.font.render('Save', True, 'black'), (screen_width * 0.5 - 170, 225))
        self.surface.blit(self.font.render('Resume', True, 'black'), (screen_width * 0.5 - 70, 315))
        screen.blit(self.surface, (0, 0))
        return self.reset, self.save

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.ui.show_health(self.cur_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()
        self.timer()
        self.input()
        self.ui.show_if_muted(self.sound, self.volume_gain)
        if self.pause:
            self.restart, self.saves = self.draw_pause()


# Pygame setup
pygame.init()
pygame.display.set_caption('Landers - V0.2.5')
pygame_icon = pygame.image.load('venv\\graphics\\tilesTEST.png')
pygame.display.set_icon(pygame_icon)
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('#DCDDD8')
    game.run()

    pygame.display.update()
    clock.tick(60)
