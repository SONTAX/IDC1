from pygame import *


class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + WIDTH / 2, -t + HEIGHT / 2

    l = min(0, l)
    l = max(-(camera.width - WIDTH), l)
    t = max(-(camera.height - HEIGHT), t)
    t = min(0, t)

    return Rect(l, t, w, h)


class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, width, height, speed):
        super().__init__()
        self.image = transform.scale(image.load(img), (width, height))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        pass


class Player(GameSprite):
    def __init__(self, img, x, y, width, height, speed):
        super().__init__(img, x, y, width, height, speed)
        self.on_ground = False
        self.x_change = 0
        self.y_change = 0
        self.jump = 12
        self.downforce = 0.35
        self.weapon = False
        self.ammo = 0
        self.deletion = 0
        self.d = 1

    def update(self, left, right, up):
        if self.deletion > 0:
            self.deletion -= 1

        if up:
            if self.on_ground:
                self.y_change = -self.jump
        if left:
            self.x_change = -self.speed
            self.d = -1

        if right:
            self.x_change = self.speed
            self.d = 1

        if not (left or right):
            self.x_change = 0

        if not self.on_ground:
            self.y_change += self.downforce

        self.on_ground = False
        self.rect.y += self.y_change
        self.collide(0, self.y_change)
        self.rect.x += self.x_change
        self.collide(self.x_change, 0)

    def collide(self, x_change, y_change):
        for p in platforms:
            if sprite.collide_rect(self, p):
                if x_change > 0:
                    self.rect.right = p.rect.left

                if x_change < 0:
                    self.rect.left = p.rect.right

                if y_change > 0:
                    self.rect.bottom = p.rect.top
                    self.on_ground = True
                    self.y_change = 0

                if y_change < 0:
                    self.rect.top = p.rect.bottom
                    self.y_change = 0
        for w in weapons:
            if sprite.collide_rect(self, w):
                w.kill()
                self.weapon = True
                self.ammo += 5

    def shoot(self):
        if self.weapon and self.ammo > 0 and self.deletion == 0:
            bullet = Bullet("coin.png", self.rect.centerx, self.rect.centery, 20, 20, self.d * 10)
            player_bullets.add(bullet)
            self.deletion = 10
            self.ammo -= 1


class Enemy(GameSprite):
    def __init__(self, img, x, y, width, height, speed):
        super().__init__(img, x, y, width, height, speed)
        self.distance = 400
        self.deletion = 100

    def update(self):
        if abs(self.rect.centerx - player.rect.centerx) < self.distance:
            if self.rect.centerx > player.rect.centerx:
                d = -1
            else:
                d = 1
            if self.deletion == 0:
                bullet = Bullet("coin.png", self.rect.centerx, self.rect.centery, 20, 20, d * 10)
                enemy_bullets.add(bullet)
                self.deletion = 100
        if self.deletion > 0:
            self.deletion -= 1
        if sprite.groupcollide(enemies, player_bullets, True, True):
            self.deletion = -1


class Bullet(GameSprite):
    def update(self):
        self.rect.x += self.speed
        if self.rect.x < 0 or self.rect.x > 3000:
            self.kill()


WIDTH, HEIGHT = 700, 400
window = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()

font.init()
FONT = font.SysFont('Arial', 50)

start = Rect(100, 100, 300, 70)
leave = Rect(100, 340, 300, 70)

start_text = FONT.render("Почати гру", True, (255, 255, 255))
leave_text = FONT.render("Вийти", True, (255, 255, 255))

menu_background = transform.scale(image.load("background.jpg"), (WIDTH, HEIGHT))
game_background = transform.scale(image.load("background.png"), (WIDTH, HEIGHT))

platforms = sprite.Group()
platform = GameSprite("brick.jpg", 0, 2400, 800, 200, 0)
platforms.add(platform)
platform = GameSprite("brick.jpg", 0, 400, 800, 200, 0)
platforms.add(platform)
platform = GameSprite("brick.jpg", 1200, 400, 800, 200, 0)
platforms.add(platform)
platform = GameSprite("brick.jpg", 300, 250, 100, 20, 0)
platforms.add(platform)


player = Player("sprite1.png", 10, 10, 100, 100, 7)

enemies = sprite.Group()
enemy = Enemy("sprite2.png", 300, 150, 100, 100, 0)
enemies.add(enemy)

weapons = sprite.Group()
weapon = GameSprite("treasure.png", 700, 320, 50, 50, 0)
weapons.add(weapon)

player_bullets = sprite.Group()
enemy_bullets = sprite.Group()

menu_flag = True
game_flag = False

left = False
right = False
up = False

camera = Camera(camera_configure, 5000, 5000)

while True:
    sprites = sprite.Group()
    sprites.add(player)
    sprites.add(enemies)
    sprites.add(platforms)
    sprites.add(player_bullets)
    sprites.add(enemy_bullets)
    sprites.add(weapons)
    if menu_flag:
        for e in event.get():
            if e.type == QUIT:
                quit()
                exit(0)
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                x, y = e.pos
                if start.collidepoint(x, y):
                    game_flag = True
                    info_flag = False
                    menu_flag = False
                elif leave.collidepoint(x, y):
                    quit()
                    exit(0)
        window.blit(menu_background, (0, 0))
        draw.rect(window, (0, 0, 0), start)
        window.blit(start_text, start)
        draw.rect(window, (0, 0, 0), leave)
        window.blit(leave_text, leave)
    elif game_flag:
        for e in event.get():
            if e.type == QUIT:
                quit()
                exit(0)
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True
            if e.type == KEYDOWN and e.key == K_SPACE:
                player.shoot()

            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_RIGHT:
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False

        window.blit(game_background, (0, 0))
        camera.update(player)
        player.update(left, right, up)
        enemy.update()
        player_bullets.update()
        enemy_bullets.update()
        if sprite.spritecollide(player, enemy_bullets, True) or \
                player.rect.y > 2600 or sprite.spritecollide(player, enemies, True):
            game_flag = False
            text = FONT.render("GAME OVER", True, (255, 50, 50))
        for s in sprites:
            window.blit(s.image, camera.apply(s))
    else:
        for e in event.get():
            if e.type == QUIT:
                quit()
                exit(0)
        window.fill((0, 0, 0))
        window.blit(text, (20, 20))

    clock.tick(60)
    display.update()
