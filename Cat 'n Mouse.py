import pygame
import os
from PIL import Image
import random
import math

################################### Pygame setup ###################################
pygame.init()
screen = pygame.display.set_mode((1080, 720), )
clock = pygame.time.Clock()
running = True
dt = 0

####################################################################################





#################################### Get assets ####################################
_image_library = {}
def get_image(path):
    global _image_library
    path = "Assets/" + path
    image = _image_library.get(path)
    if image == None:
        canonicalized_path = path.replace('/', os.sep)
        image = pygame.image.load(canonicalized_path)
        _image_library[path] = image
    return image

_sound_library = {}
def play_sound(path, volume=1.0, loops=0):
    global _sound_library
    path = "Assets/" + path
    sound = _sound_library.get(path)
    if sound == None:
        canonicalized_path = path.replace('/', os.sep)
        sound = pygame.mixer.Sound(canonicalized_path)
        sound.set_volume(volume)
        _sound_library[path] = sound
    channel = sound.play(loops)
    return channel

'''_music_library = {}
def play_music(path, number_of_repeats):
    global _music_library
    path = "Assets/" + path
    music = _music_library.get(path)
    if music == None:
        canonicalized_path = path.replace('/', os.sep)
        music = pygame.mixer.music.load(canonicalized_path)
        _music_library[path] = music
    channel = pygame.mixer.music.play(number_of_repeats)
    return channel'''

#####################################################################################





##################################### Variables #####################################
event_number = 0
font = pygame.font.Font(None, 72)

#####################################################################################





##################################### Funktions #####################################
def get_mid_screen():
    return pygame.Vector2(pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2))

def teleport_from_mouse(distance):
    mouse_pos = pygame.mouse.get_pos()
    max_attempts=1000
    for _ in range(max_attempts):
        pos = pygame.Vector2(
            random.randint(0, screen.get_width()),
            random.randint(0, screen.get_height())
        )
        if pos.distance_to(mouse_pos) >= distance:
            return pos
    # fallback 
    return pygame.Vector2(
        random.randint(0, screen.get_width()),
        random.randint(0, screen.get_height())
    )

def turn_to(who_pos, where):
    new_direction = pygame.Vector2(where - who_pos)
    new_direction = new_direction.normalize() if new_direction.length_squared() else new_direction
    return new_direction

def random_direction():
    return pygame.Vector2(random.randint(-1, 1), random.randint(-1, 1))

#####################################################################################





################################## handle buttons ##################################
def handle_mouse(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        close_button.click(event)
    if event.type == pygame.MOUSEBUTTONUP:
        close_button.unclick(event)

#####################################################################################





###################################### Classes ######################################
class Music():
    def __init__(self, calm, activ):
        self.calm = calm
        self.activ = activ
        self.ch1 = None
        self.ch2 = None
        self.ch1_volume = 1
        self.ch2_volume = 0
        self.activ_ch = 1

    def update(self, dt):
        if self.ch1 != None:
            if self.activ_ch == 1:
                self.ch1_volume = min(self.ch1_volume + dt, 1)
                self.ch2_volume = max(self.ch2_volume - dt, 0)
            elif self.activ_ch == 2:
                self.ch1_volume = max(self.ch1_volume - dt, 0)
                self.ch2_volume = min(self.ch2_volume + dt, 1)
            else:
                print("Music class self.activ_ch error")
            self.ch1.set_volume(self.ch1_volume)
            self.ch2.set_volume(self.ch2_volume)

    def play(self):
        self.ch1 = play_sound(self.calm, 0.9, -1)
        self.ch2 = play_sound(self.activ, 0.9, -1)

    def switch(self):
        self.activ_ch = max((self.activ_ch+1)%3, 1)

music = Music("Battle.ogg", "Battle dirty.ogg")




class Animation:
    def __init__(self, frames, frame_duration=0.5):
        self.frames = frames
        self.frame_duration = frame_duration  # frames per second
        self.current_frame = 0
        self.timer = 0

    def get_frame(self, dt):
        if len(self.frames) == 1:
            return self.frames[0]
        self.timer += dt

        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames) 
        return self.frames[self.current_frame]

    def get_random_frame(self, dt):
        if len(self.frames) == 1:
            return self.frames[0]
        self.timer += dt

        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame = random.randint(0, len(self.frames)-1)
        return self.frames[self.current_frame]


class Dialogue:
    def __init__(self, lines, line_duration=5, looping_line=None):
        self.lines = lines
        self.line_duration = line_duration  # lines per second
        self.current_line = 0
        self.timer = 0
        self.looping_line = looping_line  #If he said all the lines, which one should he loop
        if self.looping_line == None:
            self.looping_line = len(self.lines)-1

    def get_line(self, dt, random=False):
        if self.line_duration == -1:
            return self.lines[self.current_line].split('\n')
        else:
            if len(self.lines) == 1:
                self.timer += dt
                if self.timer >= self.line_duration:
                    mouse.state = "WAITARROW"
                return self.lines[0].split('\n')
            self.timer += dt
    
            if self.timer >= self.line_duration:
                self.timer = 0
                if random:
                    self.set_random_line()
                else:
                    self.current_line = (self.current_line + 1)
                    if self.current_line > len(self.lines)-1:
                        self.current_line = self.looping_line
                        mouse.state = "WAITARROW"
            return self.lines[self.current_line].split('\n')

    def set_random_line(self):
        self.current_line = random.randint(self.looping_line, len(self.lines)-1)


class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = get_image(filename)

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet,(0,0),(x, y, w, h))
        return sprite

class Progress_bar:
    def __init__(self, max_hp, size=500, pos=get_mid_screen(), color="white", low_hp_percent=-1):
        self.max_hp = max_hp
        self.hp = max_hp
        self.low_hp_percent = low_hp_percent
        self.pos = pos
        self.size = size
        self.color = color

    def update(self, current_hp):
        self.hp = current_hp
        self.draw()

    def draw(self):
        bar_surface = pygame.Surface((self.pos.x + self.size, 40), pygame.SRCALPHA)

        pygame.draw.rect(bar_surface, (22,22,66, 100), pygame.Rect(0, 0, self.size, 40))    #background

        percent = (self.hp / self.max_hp)


        color_with_alpha = pygame.Color(self.color)
        if self.low_hp_percent < percent:
            color_with_alpha.a = 200 
        else:
            color_with_alpha.a = 100
        pygame.draw.rect(bar_surface, (color_with_alpha), pygame.Rect(0, 0, self.size*percent, 40))

        screen.blit(bar_surface, (self.pos.x - (self.size//2), self.pos.y))

#####################################################################################




####################################### Mouse #######################################
class Mouse:
    def __init__(self, name):
        self.pos = pygame.mouse.get_pos()
        self.direction = 0
        self.speed = 640
        self.state = "default"
        self.max_hp = 4
        self.hp = self.max_hp
        self.glitch_chance = 0 #per second
        self.uncorrupt_timer = 0
        self.name = name #important to find sprites
        self.spritesheet = Spritesheet(name + ".png")
        self.sprites = {
            "4": {
                "default" : Animation([self.spritesheet.get_sprite(0,0,32,32)]),
                "corruptet": Animation([self.spritesheet.get_sprite(0,0,32,32), self.spritesheet.get_sprite(0,32,32,32), self.spritesheet.get_sprite(0,64,32,32), self.spritesheet.get_sprite(0,96,32,32), self.spritesheet.get_sprite(0,128,32,32), self.spritesheet.get_sprite(0,160,32,32)], 0.1),
                "glitching": Animation([self.spritesheet.get_sprite(0,32,32,32), self.spritesheet.get_sprite(0,64,32,32)], 0.1)
            },
            "3": {
                "default" : Animation([self.spritesheet.get_sprite(32,0,32,32)]),
                "corruptet": Animation([self.spritesheet.get_sprite(32,0,32,32), self.spritesheet.get_sprite(32,32,32,32), self.spritesheet.get_sprite(32,64,32,32), self.spritesheet.get_sprite(32,96,32,32), self.spritesheet.get_sprite(32,128,32,32), self.spritesheet.get_sprite(32,160,32,32)], 0.1),
                "glitching": Animation([self.spritesheet.get_sprite(32,32,32,32), self.spritesheet.get_sprite(32,64,32,32)], 0.1)
            } ,
            "2": {
                "default" : Animation([self.spritesheet.get_sprite(64,0,32,32)]),
                "corruptet": Animation([self.spritesheet.get_sprite(64,0,32,32), self.spritesheet.get_sprite(64,32,32,32), self.spritesheet.get_sprite(64,64,32,32), self.spritesheet.get_sprite(64,96,32,32), self.spritesheet.get_sprite(64,128,32,32), self.spritesheet.get_sprite(64,160,32,32)], 0.1),
                "glitching": Animation([self.spritesheet.get_sprite(64,32,32,32), self.spritesheet.get_sprite(64,64,32,32)], 0.1)
            } ,
            "1": {
                "default" : Animation([self.spritesheet.get_sprite(96,0,32,32)]),
                "corruptet": Animation([self.spritesheet.get_sprite(96,0,32,32), self.spritesheet.get_sprite(96,32,32,32), self.spritesheet.get_sprite(96,64,32,32), self.spritesheet.get_sprite(96,96,32,32), self.spritesheet.get_sprite(96,128,32,32), self.spritesheet.get_sprite(96,160,32,32)], 0.1),
                "glitching": Animation([self.spritesheet.get_sprite(96,32,32,32), self.spritesheet.get_sprite(96,64,32,32)], 0.1)
            } 
        }

    def update(self, dt):
        self.pos = pygame.mouse.get_pos()
        if self.state == "WAITARROW":
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
        else:
            if self.state == "glitching":
                cursor_surface = self.sprites[str(self.hp)][self.state].get_frame(dt).convert_alpha()
            else:
                cursor_surface = self.sprites[str(self.hp)][self.state].get_random_frame(dt).convert_alpha()
            cursor = pygame.cursors.Cursor((9, 4), cursor_surface)
            pygame.mouse.set_cursor(cursor)
        
        self.states_logic(dt)

    def states_logic(self, dt):
        self.glitch_chance = max(self.glitch_chance - dt*0.01, 0)
        if self.state == "default":
            chance_per_second = self.glitch_chance
            chance_this_frame = 1 - math.exp(-chance_per_second * dt)
            if self.hp < self.max_hp and random.random() < chance_this_frame:
                self.state = "glitching"

        if self.state == "glitching":
            chance_per_second = (3 - self.glitch_chance)
            chance_this_frame = 1 - math.exp(-chance_per_second * dt)
            if random.random() < chance_this_frame:
                self.state = "default"
            else:
                chance_per_second = self.glitch_chance * 2.5
                chance_this_frame = 1 - math.exp(-chance_per_second * dt)
                if random.random() < chance_this_frame:
                    self.glitch_move(dt)
            


        elif self.state == "corruptet":
            self.move(dt)
            if 1 + (random.random()*2.5) + self.glitch_chance*2 <= self.uncorrupt_timer:
                self.uncorrupt_timer = 0
                self.state = "default"
            else:
                self.uncorrupt_timer += dt

                mouse_vec = pygame.Vector2(self.pos)
                if mouse_vec.distance_to(cat.pos) < 700 and cat.state == "chase":   #if cat is near the mouse, uncorrupt timer go faster
                    self.uncorrupt_timer += dt*2

    def corrupt(self):
        play_sound("Hurt.wav", 0.5)
        if self.hp > 1:
            mouse.hp -= 1
        else:
            self.glitch_chance += 0.2
        self.glitch_chance += 0.11
        self.state = "corruptet"
        self.uncorrupt_timer = 0

    def move(self, dt):
        self.direction = -turn_to(self.pos, close_button.pos)
        new_mouse_pos = self.pos + ((self.direction + random_direction()*2) * self.speed * dt)
        mouse_x, mouse_y = new_mouse_pos
        mouse_x = max(0, min(mouse_x, screen.get_width()))
        mouse_y = max(0, min(mouse_y, screen.get_height()))
        pygame.mouse.set_pos([mouse_x, mouse_y])

    def glitch_move(self, dt):
        new_mouse_pos = self.pos + ((random_direction()) * self.speed * min(self.glitch_chance,2) * random.random() * dt)
        mouse_x, mouse_y = new_mouse_pos
        mouse_x = max(0, min(mouse_x, screen.get_width()))
        mouse_y = max(0, min(mouse_y, screen.get_height()))
        pygame.mouse.set_pos([mouse_x, mouse_y])

mouse = Mouse("Mouse")

#####################################################################################



######################################## Cat ########################################
class Cat:
    def __init__(self, name, pos):
        self.pos = pos
        self.direction = 0
        self.speed = 700
        self.stamina = 100
        self.stamina_regen = 4 #per second
        self.stamina_cost = 17
        self.stamina_bar = Progress_bar(max_hp=self.stamina, size=500, pos=pygame.Vector2(270, 20), color="white", low_hp_percent=self.stamina_cost*0.01)
        self.max_hp = 15
        self.hp = self.max_hp
        self.hp_bar = Progress_bar(max_hp=self.max_hp, size=500, pos=pygame.Vector2(270, 80), color="red")
        self.state = "chase"
        self.damage_state = "default"
        self.damage_animation_timer = 0
        self.hitbox_radius = 20
        self.transparency = 255
        self.name = name #important to find sprites
        self.spritesheet = Spritesheet(name + ".png")
        self.sprites = {
            "chase": {
                "default": Animation([self.spritesheet.get_sprite(0,0,64,46)]),
                "damage": Animation([self.spritesheet.get_sprite(0,46,64,46), self.spritesheet.get_sprite(0,92,64,46), self.spritesheet.get_sprite(0,138,64,46)], 0.1),
            },
            "laugh": {
                "default": Animation([self.spritesheet.get_sprite(64,0,64,46), self.spritesheet.get_sprite(128,0,64,46)], 0.1),
                "damage": Animation([self.spritesheet.get_sprite(64,46,64,46), self.spritesheet.get_sprite(64,92,64,46), self.spritesheet.get_sprite(64,138,64,46), self.spritesheet.get_sprite(128,46,64,46), self.spritesheet.get_sprite(128,92,64,46), self.spritesheet.get_sprite(128,138,64,46)], 0.1),
            },

        }
        self.dialogue_lines = {
            "1": Dialogue(["Don't leave me yet.", "Just let me finish installing all my \nvirus files on your PC...", "Did I say virus? \nI meant all the game files!"], 5, 2),
            "2": Dialogue(["No.", "Don't click that button."], 2, 1),
            "3": Dialogue(["Stop that.", "You're really bothering me by trying to close me", "Bypassing antiviruses is quite difficult these days, you know?", "God, why does no one appreciate my efforts?"], 5, 3),
            "4": Dialogue(["Stop that!", "You won't be able to play the game if you don't stop closing me!", "You won't be able to play the game if you don't stop closing me!", "You won't be able to play the game if you don't stop closing me!", "Oh, wait, you... You actually listened to me?", "Well, thank you?", "...", "Wellp, so you don't get bored and close me again,\nI'll tell you a little story...", "„Once upon a time, there was a little white mouse.", "She was very afraid of the cat.", "But the the cat was actually nice! =)", "Yet, the mouse wanted to lock the cat in a cage, run an antivirus scan on him, and throw him in the trash can.", "But when the mouse tried to do that, sh̴e̴ rea̷l̷ly̸ d̵idn̴’̵t like̵ w̶hat̴ ha̸p̵pen̵e̴d next̷...", "Then, another mouse stumbled upon this cat.", "She was afraid of him too, and began to plot something mischievous.", "However, the cat noticed this, and decided to warn her what would happen if she tried to do anything to him.", "He told a little story about what had happened some time ago:"], 5, 8),
            "5": Dialogue(["Okay, if that's what you want, then close me. If you can =)", "Ha-ha!", "Too slow!", "I could do this all day", "self.dialogue_lines[Taunt_4].get_line(dt)", "It's right hier!", "You missed!"], -1, 1),
            "7": Dialogue(["No, you can't do this to me!", "N̴o,̨ ͟you c̛an't́ ̧d̶o̴ ̡this ̷t̴o m͏e!", "Stop it!", "St̨o͠p̀ i̸t̡!", "Don't click that button.", "Do̵n'̵t̸ c̴li̷c̵k th̴a̶t̸ bu̵t̵t̴on̵.", "01000101 01110010 01110010 01101111 01110010", "Error", "Traceback (most recent call last):\n line 416, in <module>\ncurrent_lines = self.dialogue_lines[Pain_5].get_line(dt)\nNameError: name 'self' is not defined",], 0.5, 0),
        }
        self.eyes_sprite = get_image('Eyes.png')

    def update(self, surface, dt):
        self.states_logic()
        self.draw(surface)
        self.stamina = min(self.stamina + dt * self.stamina_regen, 100)
        if self.stamina < 100:
            self.stamina_bar.pos=pygame.Vector2(270, 10)
            self.stamina_bar.update(self.stamina)
        if self.hp < self.max_hp:
            self.hp_bar.pos=pygame.Vector2(270, 60)
            self.hp_bar.update(self.hp)
        if self.damage_state == "damage":
            self.damage_animation_timer += dt
            if self.damage_animation_timer >= (self.max_hp-self.hp)*0.1:
                self.damage_animation_timer = 0
                self.damage_state = "default"


    def talk(self, event_number, surface):
        try:
            if event_number == 7:
                random = True
            else:
                random = False
            current_lines = self.dialogue_lines[str(event_number)].get_line(dt, random)
            y = get_mid_screen().y
            for line in current_lines:
                text_surface = font.render(line, True, (0, 128, 0))
                surface.blit(text_surface, (get_mid_screen().x - text_surface.get_width()//2, y - text_surface.get_height()//2))
                y += text_surface.get_height()
        except:
            pass

    def draw(self, surface):
        if self.damage_state == "default":
            sprite = self.sprites[self.state][self.damage_state].get_frame(dt)
        else:
            sprite = self.sprites[self.state][self.damage_state].get_random_frame(dt)

        if random.random()*(self.max_hp-self.hp) >= 10:
            sprite = self.sprites[self.state]["damage"].get_random_frame(dt)

        sprite.set_alpha(self.transparency)
        rect_pos = sprite.get_rect()
        rect_pos.center = self.pos

        surface.blit(sprite, (rect_pos))
        self.draw_eyes()

    def draw_eyes(self):
        rect_eyes_pos = self.eyes_sprite.get_rect()
        rect_eyes_pos.center = self.pos + self.direction*4
        screen.blit(self.eyes_sprite, (rect_eyes_pos))

    ################################## Logic ##################################
    def damage(self):
        self.hp -= 1
        if self.hp == 5:
            self.special_hit()
        self.damage_state = "damage"
        play_sound("Cat Hurt.wav")
        self.stamina = 0
        if self.hp % 4 == 0:
            self.speed += 50

    def special_hit(self):
        music.switch()

    def catch(self):
        self.state = "laugh"
        play_sound("laugh.mp3")
        mouse.corrupt()

    def fade_away(self, dt):
        delay = 0.05
        self.transparency -= 20 * dt/delay
        self.transparency = max(0, self.transparency)

    def appear(self, dt):
        delay = 0.1
        self.transparency += 20 * dt/delay
        self.transparency = min(255, self.transparency)

    def states_logic(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.state == "laugh":
            if self.transparency == 0:
                self.pos = teleport_from_mouse(700)
                self.state = "chase"
            else:
                self.fade_away(dt)

        elif self.state == "chase":
            if self.pos.distance_to(mouse_pos) < self.hitbox_radius:
                self.catch()

            if self.transparency == 255:
                pass
            else:
                self.appear(dt)
            self.move(dt)

        self.direction = turn_to(self.pos, mouse_pos)


    def move(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        mid_screen = get_mid_screen()

        self.direction = turn_to(self.pos, mid_screen)
        self.pos += self.speed/4 * self.direction * dt
    
        if self.hp > 5:
            modifier = 1
        else: 
            modifier = 1 + (6-self.hp)*0.19
        self.direction = turn_to(self.pos, mouse_pos)
        self.pos += self.speed*modifier * self.direction * dt

        if self.stamina > self.stamina_cost:
            modifier = 0.4
        else: 
            modifier = 0.5
        self.direction = turn_to(self.pos, close_button.pos)
        self.pos += self.speed*modifier * self.direction * dt
    
        if self.pos.distance_to(mouse_pos) > 40:
            modifier = 0.7
        else: 
            modifier = 0.3
        for dot in dots:
            self.direction = turn_to(self.pos, dot.pos)
            self.pos -= self.speed*modifier * self.direction * dt 


        self.pos.x = max(0, min(self.pos.x, screen.get_width()))
        self.pos.y = max(0, min(self.pos.y, screen.get_height()))

#####################################################################################
        
cat = Cat("Friend", teleport_from_mouse(700))





class Button:
    def __init__(self, name, pos):
        self.width = 45
        self.height = 29
        self.pos = pos
        self.pos.x = max(0, min(self.pos.x, screen.get_width() - self.width))
        self.pos.y = max(0, min(self.pos.y, screen.get_height() - self.height))
        self.name = name #important to find sprites
        self.timer = 0.0
        self.state = "default"
        self.was_presset = False
        self.spritesheet = Spritesheet(name + ".png")
        self.sprites = {
            "default": Animation([self.spritesheet.get_sprite(0,0,45,29)]), 
            "hover": Animation([self.spritesheet.get_sprite(45,0,45,29)]),
            "pressed": Animation([self.spritesheet.get_sprite(90,0,45,29)])
        }

    def update(self, surface, event_number, dt):
        self.states_logic(event_number, dt)
        self.draw(surface)
        
    def draw(self, surface):
        sprite = self.sprites[self.state].get_frame(dt)
        surface.blit(sprite, (self.pos))

    def states_logic(self, event_number, dt):
        self.pos.x = max(0, min(self.pos.x, screen.get_width() - self.width))
        self.pos.y = max(0, min(self.pos.y, screen.get_height() - self.height))
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        if rect.collidepoint(mouse_pos):
            if mouse.state == "WAITARROW":
                mouse.state = "default"
            if self.state == "default":
                self.state = "hover"
                if self.was_presset:
                    self.state = "pressed"
            self.teleport_if_can(event_number, dt)

        else:
            self.state = "default"

    def teleport_if_can(self, event_number, dt):
        if cat.stamina > cat.stamina_cost and event_number >= 6:
                self.pos = teleport_from_mouse(700)
                cat.stamina -= cat.stamina_cost

        elif event_number == 5:
            self.timer += dt
            if self.timer > 0.18:
                self.timer = 0.0
                self.pos = teleport_from_mouse(300)
                cat.dialogue_lines[str(event_number)].set_random_line()

    def click(self, event):
        rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        if event.button == 1 and rect.collidepoint(event.pos):
            self.state = "pressed"
            self.was_presset = True

    def unclick(self, event):
        rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        if event.button == 1 and self.was_presset:
            self.was_presset = False
            if rect.collidepoint(event.pos):
                self.state = "hover"
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                self.pos = teleport_from_mouse(700)
                if event_number >= 6:
                    cat.damage()
            



close_button = Button("close_button", teleport_from_mouse(700))




class Dot():
    def __init__(self, pos, speed):
        self.pos = pos
        self.direction = 0
        self.speed = speed

    def draw(self, surface):
        pygame.draw.circle(surface, "white", self.pos, 1)

    def move(self, dt):
        self.pos += self.speed * self.direction * dt
        if random.randint(1, 38) == 1:
            self.direction = turn_to(self.pos, cat.pos)
            self.direction.rotate_ip(random.randint(-50, 50))
        self.pos.x = max(0, min(self.pos.x, screen.get_width()))
        self.pos.y = max(0, min(self.pos.y, screen.get_height()))

dots = [Dot(pygame.mouse.get_pos(), cat.speed*2), Dot(pygame.mouse.get_pos(), cat.speed*2)]

for dot in dots:
    dot.direction = turn_to(dot.pos, cat.pos)
    dot.direction.rotate_ip(random.randint(-50, 50))




###############################################################################################################################
loading_speed = 20
loading_bar = Progress_bar(max_hp=1000, size=950, pos=pygame.Vector2(get_mid_screen().x, screen.get_height()-120))
loading_bar.hp = 0

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mouse.state = "default"
            if event_number != 6 or cat.hp <= 1:
                event_number += 1
                if event_number == 3:
                    screen = pygame.display.set_mode((1080, 720), pygame.NOFRAME)
                    close_button.pos = pygame.Vector2(300, 500)
                elif event_number == 6:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    cat.pos = teleport_from_mouse(700)
                    music.play()
                elif event_number == 8:
                    running = False
            
        handle_mouse(event)


    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")
    cat.talk(event_number, screen)
    if event_number == 0:
        screen.blit(get_image("Smich2.png"), (0, 0))

        ####################################
        #I really should fix this mess, but I want to finish it before April Fools' Day, and this part works fine as it is
        loading_bar.hp += loading_speed * dt
        if loading_bar.hp >= 900 and loading_bar.hp - loading_speed * dt < 900:
            loading_bar.hp = 900
        if loading_bar.hp < 900:
            if random.random()*500 < loading_speed:
                loading_speed = random.random()*700
        elif loading_bar.hp < 903:
            loading_speed = 0.5
        else:
            loading_speed = 0
            mouse.state = "WAITARROW"
        loading_bar.update(loading_bar.hp)
        ####################################

    elif event_number >= 3:
        if event_number >= 6:
            cat.update(screen, dt)
        close_button.update(screen, event_number, dt)
    
    mouse.update(dt)
    music.update(dt)

    for dot in dots:
        dot.move(dt)
        
    

    #debug
    #for dot in dots:
    #    dot.draw(screen)
    #pygame.draw.circle(screen, "red", cat.pos, cat.hitbox_radius)


    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
