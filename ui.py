import pygame

from settings import screen_width, screen_height


class UI:
    def __init__(self, surface):
        # setup
        self.display_surface = surface

        # health
        self.health_bar = pygame.image.load('venv/graphics/ui/health_bar.png').convert_alpha()
        self.health_bar_topleft = (50, 40)
        self.bar_max_width = 152
        self.bar_height = 4

        # coins
        self.coin = pygame.image.load('venv/graphics/ui/coin.png').convert_alpha()
        self.coin_rect = self.coin.get_rect(topleft=(screen_width /2 - 20, 30))

        # if muted
        self.unmuted = pygame.image.load('venv/graphics/ui/unmute.png').convert_alpha()
        self.muted = pygame.image.load('venv/graphics/ui/mute.png').convert_alpha()
        self.if_muted_rect = self.coin.get_rect(topright=(screen_width - 52, screen_height-80))

        # font
        self.font = pygame.font.Font('venv/graphics/ui/ARCADEPI.ttf', 30)

    def show_health(self, current, full, pause):
        if not pause:
            self.display_surface.blit(self.health_bar, (20, 10))
            current_health_ratio = current / full
            current_bar_width = self.bar_max_width * current_health_ratio
            health_bar_rect = pygame.Rect(self.health_bar_topleft, (current_bar_width, self.bar_height))
            pygame.draw.rect(self.display_surface, '#dc4949', health_bar_rect)

    def show_coins(self, amount, pause):
        if not pause:
            self.display_surface.blit(self.coin, self.coin_rect)
            coin_amount_surf = self.font.render(str(amount), False, '#33323d')
            coin_amount_rect = coin_amount_surf.get_rect(midleft=(self.coin_rect.right + 4, self.coin_rect.centery))
            self.display_surface.blit(coin_amount_surf, coin_amount_rect)

    def show_if_muted(self, sound, volume_gain, pause):
        if sound:
            self.display_surface.blit(self.unmuted, self.if_muted_rect)
        else:
            self.display_surface.blit(self.muted, self.if_muted_rect)