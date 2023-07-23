import pygame
from tiles import AnimatedTile
from random import randint

class Enemy(AnimatedTile):
    def __init__(self, size, x, y, pause):
        super().__init__(size,x,y,'venv/graphics/enemy/run')
        self.rect.y += size - self.image.get_size()[1]
        self.speed = randint(1,2)
        self.pause = pause

    def move(self):
        if not self.pause:
            self.rect.x += self.speed

    def reverse_image(self):
        if self.speed > 0:
            #                                 (self,image,x,y)
            self.image = pygame.transform.flip(self.image,True,False)

    def reverse(self):
        self.speed *= -1

    def update(self,shift):
        self.rect.x += shift
        self.animate()
        self.move()
        self.reverse_image()