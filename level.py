import pygame
from support import import_csv_layout, import_cut_graphics
from settings import tile_size, screen_height, screen_width
from tiles import Tile, StaticTile, Crate, Coin, Palm
from enemy import Enemy
from decoration import Sky, Water, Clouds
from player import Player
from particles import ParticleEffect
from game_data import levels


class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health, sound, volume_gain,
                volume_effects, volume_musics, overworld_bg_music, level_bg_music, coin_sound, stomp_sound, hit_sound,
                 jump_sound):
        # general setup
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None

        # audio
        self.sound = sound
        self.volume_effects = volume_effects
        self.volume_musics = volume_musics
        self.volume_gain = volume_gain
        self.overworld_bg_music = overworld_bg_music
        self.level_bg_music = level_bg_music
        self.coin_sound = coin_sound
        self.stomp_sound = stomp_sound
        self.hit_sound = hit_sound
        self.jump_sound = jump_sound

        # overworld connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

        # player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)

        # user interface
        self.change_coins = change_coins

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # explosion particle
        self.explosion_sprite = pygame.sprite.Group()

        # terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        # terrain_without_collide setup
        terrain_without_collide_layout = import_csv_layout(level_data['terrain_without_collide'])
        self.terrain_without_collide_sprites = \
        self.create_tile_group(terrain_without_collide_layout, 'terrain_without_collide')

        # grass_setup
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        # crates_setup
        crate_layout = import_csv_layout(level_data['crates'])
        self.crate_sprites = self.create_tile_group(crate_layout, 'crates')

        # coins_setup
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')

        # foreground palms
        fg_palm_layout = import_csv_layout(level_data['fg_palms'])
        self.fg_palm_sprites = self.create_tile_group(fg_palm_layout, 'fg_palms')

        # background palms
        bg_palm_layout = import_csv_layout(level_data['bg_palms'])
        self.bg_palm_sprites = self.create_tile_group(bg_palm_layout, 'bg_palms')

        # enemy
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout,'enemies')

        # constraint
        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout,'constraints')

        # decoration
        self.sky = Sky(8)
        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 40, level_width)
        self.clouds = Clouds(300, level_width, 30)

    def create_tile_group(self, layout, type):
        global sprite
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('venv/graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'terrain_without_collide':
                        terrain_without_collide_tile_list = import_cut_graphics('venv/graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_without_collide_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'grass':
                        grass_tile_list = import_cut_graphics('venv/graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'crates':
                        sprite = Crate(tile_size, x, y)

                    if type == 'coins':
                        if val == '0': sprite = Coin(tile_size, x, y, 'venv/graphics/coins/gold', 5)
                        if val == '1': sprite = Coin(tile_size, x, y, 'venv/graphics/coins/silver', 1)

                    if type == 'fg_palms':
                        if val == '0': sprite = Palm(tile_size, x, y, 'venv/graphics/terrain/palm_small',38)
                        if val == '1': sprite = Palm(tile_size, x, y, 'venv/graphics/terrain/palm_large', 70)

                    if type == 'bg_palms':
                        if val == '0': sprite = Palm(tile_size, x, y, 'venv/graphics/terrain/palm_small',38)
                        if val == '1': sprite = Palm(tile_size, x, y, 'venv/graphics/terrain/palm_large', 70)

                    if type == 'enemies':
                        sprite = Enemy(tile_size,x,y)

                    if type == 'constraints':
                        sprite = Tile(tile_size,x,y)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x,y), self.display_surface, self.create_jump_particles, change_health, self.hit_sound, self.jump_sound)
                    self.player.add(sprite)
                if val == '1':
                    hat_surface = pygame.image.load('venv/graphics/character/selector.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, hat_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy,self.constraint_sprites,False):
                enemy.reverse()

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,14)
        else:
            pos += pygame.math.Vector2(10,-14)

        jump_particle_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0.1:
            player.on_ceiling = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 16 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 3) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.create_overworld(self.current_level, 0)
        if keys[pygame.K_PLUS]:
            self.volume_gain += 0.1
            print(self.volume_gain)
            self.level_bg_music.set_volume(self.volume_gain * self.volume_musics * self.sound)
        elif keys[pygame.K_MINUS]:
            self.volume_gain -= 0.1
            print(self.volume_gain)
            self.overworld_bg_music.set_volume(self.volume_gain * self.volume_musics * self.sound)
        if keys[pygame.K_p]:
            self.sound = False

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level, 0)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite,self.goal,False):
            self.create_overworld(self.current_level, self.new_max_level)

    def check_coin_collisions(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if collided_coins:
            self.coin_sound.play()
            for coin in collided_coins:
                self.change_coins(coin.value)

    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)
        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                    self.stomp_sound.play()
                    self.player.sprite.direction.y = -12
                    explosion_sprite = ParticleEffect(enemy.rect.center, 'explosion')
                    self.explosion_sprite.add(explosion_sprite)
                    enemy.kill()
                else:
                    self.player.sprite.get_damage()


    def run(self):

        # run the entire game / level
        self.input()

        # sky
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface,self.world_shift)

        # terrains
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        # terrains_without_collide
        self.terrain_without_collide_sprites.update(self.world_shift)
        self.terrain_without_collide_sprites.draw(self.display_surface)

        # background_palms
        self.bg_palm_sprites.update(self.world_shift)
        self.bg_palm_sprites.draw(self.display_surface)

        # enemies
        self.constraint_sprites.update(self.world_shift)
        self.enemy_sprites.update(self.world_shift)
        self.enemy_sprites.draw(self.display_surface)
        self.enemy_collision_reverse()
        self.explosion_sprite.update(self.world_shift)
        self.explosion_sprite.draw(self.display_surface)

        # crates
        self.crate_sprites.update(self.world_shift)
        self.crate_sprites.draw(self.display_surface)

        # grass
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)

        # coins
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)

        # foreground_palms
        self.fg_palm_sprites.update(self.world_shift)
        self.fg_palm_sprites.draw(self.display_surface)

        # dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # player sprites
        self.player.update()
        self.horizontal_movement_collision()

        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()

        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_death()
        self.check_win()

        self.check_coin_collisions()
        self.check_enemy_collisions()

        # water
        self.water.draw(self.display_surface, self.world_shift)