import math
import random

import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game

        self.jumps = 1
        self.max_jumps = 1
        self.speed = [0, 0]
        self.speed_change = [0, 0]

        self.a_pressed = False
        self.d_pressed = False  # Ну я ))))))

        self.anim_frames = [self.game.player_walk_1,
                            self.game.player_walk_2,
                            self.game.player_jump]
        self.anim_index = 0

        self.image = self.anim_frames[self.anim_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.center = [0.0, 0.0]

        self.mask = None
        self.weapon = None

    def is_airborne(self):
        return bool(self.rect.bottom < 300)

    def player_input(self, key_pressed, released=False, event_pos=None):
        if self.jumps and (key_pressed == pygame.K_SPACE or key_pressed == pygame.K_w or key_pressed == pygame.K_UP) and not released:
            self.speed[1] = -1250
            self.jumps -= 1

        if (key_pressed == pygame.K_a or key_pressed == pygame.K_LEFT) and not released:
            self.a_pressed = True
        if (key_pressed == pygame.K_d or key_pressed == pygame.K_RIGHT) and not released:
            self.d_pressed = True
        if (key_pressed == pygame.K_a or key_pressed == pygame.K_LEFT) and released:
            self.a_pressed = False
        if (key_pressed == pygame.K_d or key_pressed == pygame.K_RIGHT) and released:
            self.d_pressed = False

        if key_pressed == 1:  # LMB
            if self.weapon:
                shot = self.game.shoot_at_enemy(event_pos)
                self.weapon.shoot_at(shot)
            else:
                if self.mask.punch_status == 'ready':
                    self.mask.punch_status = 'active'
                    self.mask.punch_used = pygame.time.get_ticks()
                    self.game.swing_sound.play()

        elif key_pressed == 3: # RMB
            pickups = pygame.sprite.spritecollide(self, self.game.pickups, dokill=False)
            if pickups:
                self.pick_up_weapon(pickups[0], event_pos)
            else:
                self.drop_weapon(event_pos)

        if key_pressed == pygame.K_LSHIFT and self.mask.dash_status == 'ready' and self.is_airborne():
            self.mask.dash_status = 'active'
            self.mask.dash_used = pygame.time.get_ticks()
            _speed = self.speed[0]
            if not _speed:
                _speed = 1

            self.speed = [800 * (_speed/abs(_speed)), 0]

    def _movement(self):
        if self.game.game_state == self.game.GameState.NUKE_START:
            self.speed[0] = 0
        gravity_acc = self.game.gravity_acceleration
        stiffness = self.game.ground_stiffness

        if abs(self.rect.centerx - self.center[0]) > 2:
            self.center[0] = self.rect.centerx
        if abs(self.rect.centery - self.center[1]) > 2:
            self.center[1] = self.rect.centery

        if self.mask.dash_status != 'active':
            self.speed[1] += gravity_acc * self.game.delta_time / 2000

        self.center[0] += self.speed[0] * self.game.delta_time / 1000
        self.center[1] += self.speed[1] * self.game.delta_time / 1000

        self.rect.center = [int(self.center[0]), int(self.center[1])]

        if not self.is_airborne():
            self.rect.bottom = 300
            self.speed[1] = 0
            self.jumps = self.max_jumps
        elif self.mask.dash_status != 'active':
            self.speed[1] += gravity_acc * self.game.delta_time / 2000

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > 780:
            self.rect.right = 780

        if self.mask.dash_status == 'active':
            pass
        else:
            self.speed[0] = -375*bool(self.a_pressed) + 375*bool(self.d_pressed)

        if not self.is_airborne():
            minus = stiffness*self.game.delta_time / 1000
            if abs(self.speed[0]) > abs(minus):
                self.speed[0] -= minus*self.speed[0]/abs(self.speed[0])
            else:
                self.speed[0] = 0

    def pick_up_weapon(self, weapon, event_pos=None):
        if event_pos is not None and self.weapon:
            self.drop_weapon(event_pos)
        self.weapon = weapon
        self.game.pickups.remove(weapon)
        self.game.player_attachments.add(weapon)
        weapon.set_body(self)
        self.game.gun_pickup_sound.play()

    def drop_weapon(self, event_pos):
        if self.weapon:
            self.weapon.body = None
            speed_x = event_pos[0] - self.rect.centerx
            speed_y = event_pos[1] - self.rect.centery
            speed = pygame.math.Vector2((speed_x, speed_y))
            speed = speed.normalize()
            speed_x = speed.x * 30
            speed_y = speed.y * 30
            self.weapon.speed = [speed_x, speed_y]
            self.weapon = None
            self.game.throw_sound.play()

    def _animate(self):
        if self.game.game_state == self.game.GameState.NUKE_START:
            self.image = self.anim_frames[0]
            return
        if self.rect.bottom < 300:
            self.image = self.anim_frames[2]
        elif abs(self.speed[0]) >= 60:
            self.anim_index += 9 * self.game.delta_time / 1000
            if self.anim_index >= 2:
                self.anim_index = 0
            self.image = self.anim_frames[int(self.anim_index)]
        else:
            self.anim_index = 0
            self.image = self.anim_frames[self.anim_index]

    def update(self):
        self._movement()
        self._animate()

        # print(self.a_pressed, self.d_pressed)


class Mask(pygame.sprite.Sprite):
    def __init__(self, _player: Player, mask='rooster'):
        super().__init__()
        self.deflect = False
        self.bear_activation_time = None

        self.dash_status = 'not active'
        self.dash_used = None
        self.dash = lambda: None

        self.punch_status = 'not active'
        self.punch_used = None
        self.punch = lambda: None
        self.punch_sprite = Punch(_player)
        _player.game.player_attachments.add(self.punch_sprite)

        if mask == 'rooster':
            self.image = pygame.transform.scale(_player.game.rooster_mask, (90, 95))
        elif mask == 'bear':
            self.deflect = True
            self.image = pygame.transform.scale(_player.game.bear_mask, (90, 80))
            self.image.set_alpha(255)
        elif mask == 'zebra':
            self.image = pygame.transform.scale(_player.game.zebra_mask, (96, 90))
            self.dash_status = 'ready'
            self.dash = self.dash_process
        elif mask == 'tiger':
            self.image = pygame.transform.scale(_player.game.tiger_mask_normal, (90, 80))
            self.punch_status = 'ready'
            self.punch = self.punch_process
        elif mask == 'frog':
            self.image = pygame.transform.scale(_player.game.frog_mask, (85, 75))
            self.deflect = True

            self.dash_status = 'ready'
            self.dash = self.dash_process

            self.punch_status = 'ready'
            self.punch = self.punch_process
        else:
            self.image = pygame.surface.Surface((90, 95))
            self.image.set_alpha(0)

        self.type_ = mask
        self.rect = self.image.get_rect()
        self.body = _player
        _player.mask = self

    def deflect_ability(self):
        self.bear_activation_time = 600
        for enemy in self.body.game.enemy_group:
            self.body.game.score_add(f'{enemy.get_type()}_kill')
            enemy.mask.kill()
            enemy.kill()
            # self.body.game.kill_run = True
        ds = random.choice([self.body.game.death_sound,
                            self.body.game.death_sound_2,
                            self.body.game.death_sound_3,
                            self.body.game.death_sound_4])
        ds.play()
        self.body.game.enemy_spawn.extend([None, None])

    def dash_process(self):
        if self.dash_used is None:
            return
        _now = pygame.time.get_ticks()
        _time_spent = _now - self.dash_used
        # if _time_spent <= 700:
        #     self.body.speed[0] = 0
        if _time_spent > 250:
            self.dash_status = 'cooldown'
        if self.dash_cd() <= 0:  # _time_spent > 1300 - 500*bool(self.body.game.kill_run):
            self.dash_status = 'ready'
            self.dash_used = None

    def dash_cd(self):
        return 1300 - 500*bool(self.body.game.kills > 0) + self.dash_used - pygame.time.get_ticks()

    def punch_process(self):
        if self.punch_used is None:
            return
        _now = pygame.time.get_ticks()
        _time_spent = _now - self.punch_used

        if _time_spent < 40:
            self.punch_sprite.image = self.body.game.punch_frames[0]
        elif _time_spent < 60:
            self.punch_sprite.image = self.body.game.punch_frames[1]
        elif _time_spent < 100:
            self.punch_sprite.image = self.body.game.punch_frames[2]
        elif _time_spent < 120:
            self.punch_sprite.image = self.body.game.punch_frames[3]
        elif _time_spent < 160:
            self.punch_sprite.image = self.body.game.punch_frames[4]
        if _time_spent > 160:
            self.punch_status = 'cooldown'
            self.punch_sprite.image = self.punch_sprite.default_image
        if self.punch_cd() <= 0:
            self.punch_status = 'ready'
            self.punch_used = None

    def punch_cd(self):
        return 950 - 100*bool(self.body.game.advanced_enemies) - self.body.game.score + self.punch_used - pygame.time.get_ticks()

    def update(self):
        # print(self.dash_status)
        match self.type_:
            case 'rooster':
                self.rect.center = (self.body.rect.midtop[0] + 7, self.body.rect.midtop[1] + 23)
            case 'bear':
                self.rect.center = (self.body.rect.midtop[0], self.body.rect.midtop[1] + 23)
            case 'zebra':
                self.rect.center = (self.body.rect.center[0] + 3, self.body.rect.center[1] - 10)
            case 'tiger':
                self.rect.center = (self.body.rect.midtop[0], self.body.rect.midtop[1] + 23)
            case 'frog':
                self.rect.center = (self.body.rect.midtop[0], self.body.rect.midtop[1] + 23)
        self.dash()
        self.punch()

class Punch(pygame.sprite.Sprite):
    def __init__(self, body):
        super().__init__()

        self.default_image = pygame.surface.Surface((74, 84))
        self.default_image.set_alpha(0)
        self.image = self.default_image
        self.rect = self.image.get_rect()
        self.body = body

    def update(self):
        self.rect.midleft = self.body.rect.midright

class Weapon(pygame.sprite.Sprite):
    def __init__(self, game, pos=None):
        super().__init__()
        self.game = game

        self.og_image = pygame.transform.scale(game.weapon, (120, 60))
        self.image = self.og_image
        self.rect = self.image.get_rect()
        if pos:
            self.rect.midbottom = pos

        self.ammo = game.max_ammo
        self.body = None
        self.t = 0
        self.angle = 0

        self.speed = [0, 0]

    def set_body(self, _body):
        self.body = _body

    def shoot_at(self, shot):
        if not self.ammo:
            self.game.empty_gun_sound.play()
        elif shot:
            for enemy in shot:
                self.game.score_add(f'{enemy.get_type()}_kill')
                enemy.mask.kill()
                enemy.kill()

            self.game.gun_sound.play()
            self.game.gunshot_afterimage.append([pygame.mouse.get_pos(), 100.0])

            self.ammo -= 1

    def rotate(self):
        self.angle += -15
        self.image = pygame.transform.rotozoom(self.og_image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        if self.speed != [0, 0]:
            self.rotate()
            self.rect.center = (self.rect.centerx + self.speed[0], self.rect.centery + self.speed[1])
            if self.rect.left < -100 or self.rect.right > 900 or self.rect.top < -100 or self.rect.bottom > 500:
                self.kill()
        elif self.body:
            self.rect.center = (self.body.rect.centerx + 30, self.body.rect.centery + 15)  #(self.body.rect.left, self.body.rect.midleft[1] + 15)
        else:
            self.rect.bottom = 303 + 3*math.cos(self.t*math.pi/1100)
            self.t = (self.t + self.game.delta_time)%2200

