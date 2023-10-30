import math

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

        self.weapon = None

        self.set_attachments()

    def player_input(self, key_pressed, released=False):
        if self.jumps and (key_pressed == pygame.K_SPACE or key_pressed == pygame.K_w) and not released:
            self.speed[1] = -1250
            self.jumps -= 1
        if key_pressed == pygame.K_a and not released:
            self.a_pressed = True
        elif key_pressed == pygame.K_a and released:
            self.a_pressed = False
        if key_pressed == pygame.K_d and not released:
            self.d_pressed = True
        if key_pressed == pygame.K_d and released:
            self.d_pressed = False

        if key_pressed == 1:  # LMB
            if self.weapon:
                shot = self.game.shoot_at_enemy()
                self.weapon.shoot_at(shot)

        elif key_pressed == 3: # RMB
            pickups = pygame.sprite.spritecollide(self, self.game.pickups, dokill=False)
            if pickups:
                self.pick_up_weapon(pickups[0])
            else:
                self.drop_weapon()
        if self.a_pressed or self.d_pressed:
            self.speed[0] = 300*bool(self.d_pressed) - 300*bool(self.a_pressed)

    def _movement(self):
        if self.game.game_state == 45:
            self.speed[0] = 0
        gravity_acc = self.game.gravity_acceleration
        stiffness = self.game.ground_stiffness

        if abs(self.rect.centerx - self.center[0]) > 2:
            self.center[0] = self.rect.centerx
        if abs(self.rect.centery - self.center[1]) > 2:
            self.center[1] = self.rect.centery

        self.speed[1] += gravity_acc * self.game.delta_time / 2000

        self.center[0] += self.speed[0] * self.game.delta_time / 1000
        self.center[1] += self.speed[1] * self.game.delta_time / 1000

        self.rect.center = [int(self.center[0]), int(self.center[1])]

        if self.rect.bottom >= 300:
            self.rect.bottom = 300
            self.speed[1] = 0
            self.jumps = self.max_jumps
        else:
            self.speed[1] += gravity_acc * self.game.delta_time / 2000

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > 780:
            self.rect.right = 780
        if abs(self.speed[0]) >= 1:
            if not (self.a_pressed or self.d_pressed):# and self.rect.bottom >= 300:
                minus = stiffness*self.game.delta_time / 1000
                if abs(self.speed[0]) > abs(minus):
                    self.speed[0] -= minus*self.speed[0]/abs(self.speed[0])
                else:
                    self.speed[0] = 0

    def set_attachments(self, mask: bool = True):
        self.mask = mask
        # self.weapon = weapon

    def pick_up_weapon(self, weapon):
        if self.weapon:
            self.drop_weapon()
        self.weapon = weapon
        self.game.pickups.remove(weapon)
        self.game.player_attachments.add(weapon)
        weapon.set_body(self)
        self.game.gun_pickup_sound.play()

    def drop_weapon(self):
        if self.weapon:
            self.weapon.body = None
            self.weapon.kill() # TODO: yeet it instead
            self.weapon = None

    def _animate(self):
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


class Mask(pygame.sprite.Sprite):
    def __init__(self, _player: Player):
        super().__init__()
        self.image = pygame.transform.scale(_player.game.rooster_mask, (90, 95))
        self.rect = self.image.get_rect()
        self.body = _player

    def update(self):
        if self.body.mask:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(0)
        self.rect.center = (self.body.rect.midtop[0] + 7, self.body.rect.midtop[1] + 23)


class Weapon(pygame.sprite.Sprite):
    def __init__(self, game, pos=None):
        super().__init__()
        self.game = game

        self.image = pygame.transform.scale(game.weapon, (120, 60))
        self.rect = self.image.get_rect()
        if pos:
            self.rect.midbottom = pos

        self.ammo = game.max_ammo
        self.body = None
        self.t = 0

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

            if not self.game.kill_run:
                self.game.kill_run_init_sound.play()
            self.game.kill_run = True
            self.ammo -= 1

    def update(self):
        if self.body:
            self.rect.midleft = (self.body.rect.left, self.body.rect.midleft[1] + 15)
        else:
            self.rect.bottom = 303 + 3*math.cos(self.t*math.pi/1100)
            self.t = (self.t + self.game.delta_time)%2200
