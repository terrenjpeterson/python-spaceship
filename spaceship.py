# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
drag_coef = 0.02
missle_speed = 10
time = 0.5
ship_radius = 45
number_of_rocks = 10
sprites = []

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
missile_sound.rewind()
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.missile_in_flight = False
        self.fired_missile = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(ship_image, (135, 45), (90, 90), (self.pos[0], self.pos[1]), (90, 90), self.angle)                   
        else:
            canvas.draw_image(ship_image, (45, 45), (90, 90), (self.pos[0], self.pos[1]), (90, 90), self.angle)       
#       canvas.draw_circle(self.pos, self.radius, 1, "White", "White")
    
    def update(self):
        # factor in friction
        self.vel[0] *= (1 - drag_coef)
        self.vel[1] *= (1 - drag_coef)
            
        # position adjusts for current velocity
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        # get forward vector based on turning
        self.angle += (self.angle_vel / 50) * math.pi
        forward = angle_to_vector(self.angle)

        # this is executed when thrust button is down
        if self.thrust:
            self.vel[0] += forward[0]
            self.vel[1] += forward[1]
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.rewind()

        # check to see if ship has drifted from map    
        if self.pos[0] > WIDTH:
            self.pos[0] -= WIDTH
        elif self.pos[0] < 0:
            self.pos[0] += WIDTH

        if self.pos[1] > HEIGHT:
            self.pos[1] -= HEIGHT
        elif self.pos[1] < 0:
            self.pos[1] += HEIGHT
                         
    def shoot_missile(self):
        # adjust missle starting point based on ship rotation
        ship_adjust = angle_to_vector(self.angle)

        ship_adjust[0] = ship_adjust[0] * ship_radius
        ship_adjust[1] = ship_adjust[1] * ship_radius

        x_pos = my_ship.pos[0] + ship_adjust[0]
        y_pos = my_ship.pos[1] + ship_adjust[1]

        # calculate the missle velocity
        missle_vel = angle_to_vector(self.angle)

        x_vel = missle_vel[0] * missle_speed + my_ship.vel[0]
        y_vel = missle_vel[1] * missle_speed + my_ship.vel[1]

        # reset the missle direction based on the new ship position
        a_missile.change_direction(x_pos, y_pos, x_vel, y_vel, 0)
        self.missile_in_flight = True

        if self.fired_missile:
            missile_sound.play()
            fired_missle = False
        else:
            missile_sound.rewind()

# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, angle_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = angle_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
#        if sound:
#            sound.rewind()
#            sound.play()
   
    def draw(self, canvas):
#        canvas.draw_circle(self.pos, self.radius, 1, "Red", "Red")
        canvas.draw_image(self.image, self.image_center, self.image_size, (self.pos[0], self.pos[1]), self.image_size, self.angle)
        
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel
#        print "angle", self.angle, " velocity", self.angle_vel

        # check to see if the sprite has drifted from map    
        if self.pos[0] > WIDTH:
            self.pos[0] -= WIDTH
        elif self.pos[0] < 0:
            self.pos[0] += WIDTH

        if self.pos[1] > HEIGHT:
            self.pos[1] -= HEIGHT
        elif self.pos[1] < 0:
            self.pos[1] += HEIGHT        
    
    def change_direction(self, x_pos, y_pos, x_vel, y_vel, new_angle_vel):
        self.pos = [x_pos, y_pos]
        self.vel = [x_vel, y_vel] 
        self.angle_vel = new_angle_vel
#        print "new angle velocity", self.angle_vel

    def check_if_hit(self, x_pos, y_pos, rock_id):
        global score
        distance = dist(a_missile.pos, [x_pos, y_pos])
        if distance < 45:
#            print "hit rock", distance, rock_id
            my_ship.missile_in_flight = False
            sprites.pop(rock_id)
            score += 1
        return distance

def draw(canvas):
    global time
    
    # animiate background
    time += 1
    center = debris_info.get_center()
    size = debris_info.get_size()
    wtime = (time / 8) % center[0]
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, [center[0] - wtime, center[1]], [size[0] - 2 * wtime, size[1]], 
                                [WIDTH / 2 + 1.25 * wtime, HEIGHT / 2], [WIDTH - 2.5 * wtime, HEIGHT])
    canvas.draw_image(debris_image, [size[0] - wtime, center[1]], [2 * wtime, size[1]], 
                                [1.25 * wtime, HEIGHT / 2], [2.5 * wtime, HEIGHT])

    # draw ship and update
    my_ship.draw(canvas)
    my_ship.update()
    
    if my_ship.missile_in_flight:
        a_missile.draw(canvas)
        a_missile.update()

    rock_id = 0    
        
    for sp in sprites:
        if my_ship.missile_in_flight:
            x = int(sp.pos[0])
            y = int(sp.pos[1])
            sp.check_if_hit(x, y, rock_id)
        sp.update()
        sp.draw(canvas)
        rock_id += 1
        
    # print the score and number of lives remaining    
    canvas.draw_text("Lives : " + str(lives), [50, 50], 20, "White", "monospace")
    canvas.draw_text("Score : " + str(score), [650, 50], 20, "White", "monospace")
    
# timer handler that spawns a rock    
def rock_spawner():
    # for now this randomly moves the rock and changes direction
    rock_pos_x = random.randrange(0, WIDTH)
    rock_pos_y = random.randrange(0, HEIGHT)
    rock_pos = [rock_pos_x, rock_pos_y]
    rock_vel_x = random.randrange(-1, 1)
    rock_vel_y = random.randrange(-1, 1)
    rock_vel = [rock_vel_x, rock_vel_y]
    rock_ang_vel = (random.randrange(-10, 10)) / 100

    # if the maximum number of rocks exist, remove the oldest
    if len(sprites) > number_of_rocks - 1:
        sprites.pop(0)    
    sprites.append(Sprite(rock_pos, rock_vel, 0, rock_ang_vel, asteroid_image, asteroid_info))
    
# functions that handle when keys are pressed
def keydown(key):
    # key functions for when keys are pressed
    if key == simplegui.KEY_MAP['up']:
        my_ship.thrust = True
    elif key == simplegui.KEY_MAP['down']:
        my_ship.thrust = False
    elif key == simplegui.KEY_MAP['right']:
        my_ship.angle_vel += 1
    elif key == simplegui.KEY_MAP['left']:
        my_ship.angle_vel -= 1
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot_missile()
        my_ship.fired_missile = True
        
def keyup(key):
    # key functions for when keys are released
    if key == simplegui.KEY_MAP['up']:
        my_ship.thrust = False
    elif key == simplegui.KEY_MAP['right']:
        my_ship.angle_vel -= 1
    elif key == simplegui.KEY_MAP['left']:
        my_ship.angle_vel += 1
    elif key == simplegui.KEY_MAP['space']:
        my_ship.fire_missle = False
        
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
a_rock = Sprite([WIDTH / 3, HEIGHT / 3], [1, 1], 0, 0.05, asteroid_image, asteroid_info)
a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-5,5], 0, 0, missile_image, missile_info, missile_sound)
sprites.append(Sprite([WIDTH / 3, HEIGHT / 3], [1, 1], 0, 0.05, asteroid_image, asteroid_info))


# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
