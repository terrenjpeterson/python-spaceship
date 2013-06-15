# program template for Spaceship
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 0
drag_coef = 0.03
missle_speed = 10
time = 0.5
ship_radius = 45
number_of_rocks = 10
points_to_bonus = 500
rock_group = []
missile_group = []
explosion_group = []

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        self.target_size = [radius * 2, radius * 2]
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size
    
    def get_target_size(self):
        return self.target_size

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
asteroid_info = ImageInfo([45, 45], [90, 90], 45)
asteroid_info_medium = ImageInfo([45, 45], [90, 90], 30)
asteroid_info_small = ImageInfo([45, 45], [90, 90], 15)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blend.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [64, 64], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_blue.png")

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

        missile_group.append(Sprite([x_pos, y_pos], [x_vel, y_vel], 0, 0, missile_image, missile_info, missile_sound))
        self.missile_in_flight = True

        if self.fired_missile:
            missile_sound.play()
            fired_missle = False
        else:
            missile_sound.rewind()
            
    def ship_crash(self):
        global lives
        # reduce number of lives by 1
        lives -= 1
        explosion_sound.play()
        explosion_group.append(Sprite(my_ship.pos, [0, 0], 0, 0, explosion_image, explosion_info))
        # reset ship to middle of the screen
        my_ship.pos[0] = WIDTH / 2
        my_ship.pos[1] = HEIGHT / 2
        # remove all the rocks from the screen
        num_rocks = len(rock_group)
        while num_rocks > 0:
            rock_group.pop()
            num_rocks -= 1


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
        self.target_size = info.get_target_size()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
#        if sound:
#            sound.rewind()
#            sound.play()
   
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, (self.pos[0], self.pos[1]), self.target_size, self.angle)
        
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel
        self.age += 1
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
    
    def check_if_hit(self, rock_x, rock_y, rock_id, missile_x, missile_y):
        global score, lives, points_to_bonus
        distance = dist([missile_x, missile_y], [rock_x, rock_y])
        if distance < (self.radius):
        # if missile hits the rock, destroy it and increment score
            missile_group.pop(0)
            explosion_group.append(Sprite([rock_x, rock_y], [0, 0], 0, 0, explosion_image, explosion_info))
            rock_group.pop(rock_id)
            # check if rock was large, if so split into two
            if self.radius == asteroid_info.radius:
                # collision with large asteroid
                new_rock_vel_x = random.randrange(-2, 2)
                new_rock_vel_y = random.randrange(1, 2)
                rock_group.append(Sprite([rock_x, rock_y], [new_rock_vel_x, new_rock_vel_y], 0, -.1, asteroid_image, asteroid_info_medium))
                rock_group.append(Sprite([rock_x, rock_y], [new_rock_vel_x, -new_rock_vel_y], 0, .1, asteroid_image, asteroid_info_medium))
                score += 10
                points_to_bonus -= 10
            elif self.radius == asteroid_info_medium.radius:
                # collision with medium asteroid
                new_rock_vel_x = random.randrange(-4, 4)
                new_rock_vel_y = random.randrange(1, 4)
                rock_group.append(Sprite([rock_x, rock_y], [new_rock_vel_x, new_rock_vel_y], 0, -.1, asteroid_image, asteroid_info_small))
                rock_group.append(Sprite([rock_x, rock_y], [new_rock_vel_x, -new_rock_vel_y], 0, .1, asteroid_image, asteroid_info_small))
                score += 25
                points_to_bonus -= 25
            else:
                # collision with small asteroid
                score += 50
                points_to_bonus -= 50
            if points_to_bonus < 0:
            # check if bonus level has been met
                lives += 1
                points_to_bonus += 500
            explosion_sound.rewind()
            explosion_sound.play()
        return distance

    def check_if_crash(self, rock_x, rock_y, rock_id):
        global lives
        # calculate distance between ship and current rock
        distance = dist(my_ship.pos, [rock_x, rock_y])
        if distance < (self.radius + my_ship.radius):
#            print self.radius, distance, my_ship.radius
        # if ship crashes into the rock, destroy it and reduce the number of lives
            rock_group.pop(rock_id)
            my_ship.ship_crash()
        return distance
    
def draw(canvas):
    global time, lives
    
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

    # draw spash image if game is not in action (no lives exist)    
    if lives == 0:
        canvas.draw_image(splash_image, (200, 150), (400, 300), (WIDTH / 2, 175), (400, 300))
        canvas.draw_text("Begin with three lives", [25, 375], 20, "White", "monospace")
        canvas.draw_image(ship_image, [45, 45], [90, 90], [100, 450], [90, 90], 4.75)
        canvas.draw_image(ship_image, [45, 45], [90, 90], [175, 450], [90, 90], 4.75)
        canvas.draw_image(ship_image, [45, 45], [90, 90], [250, 450], [90, 90], 4.75)
        canvas.draw_text("Bonus life every 500 points", [25, 550], 20, "White", "monospace")
        canvas.draw_text("Score by exploding rocks", [425, 375], 20, "White", "monospace")
        canvas.draw_text("Large - 10 points", [400, 425], 20, "White", "monospace")
        canvas.draw_text("Medium - 25 points", [400, 500], 20, "White", "monospace")      
        canvas.draw_text("Small - 50 points", [400, 550], 20, "White", "monospace")      
        canvas.draw_image(asteroid_image, [45, 45], [90, 90], [700, 425], [90, 90])
        canvas.draw_image(asteroid_image, [45, 45], [90, 90], [700, 500], [50, 50])
        canvas.draw_image(asteroid_image, [45, 45], [90, 90], [700, 550], [30, 30])
        soundtrack.play()
        
    # draw ship and update
    if lives > 0:
        my_ship.draw(canvas)
        my_ship.update()
    
    if len(missile_group) > 0:
    # update missiles
        missile_num = 0
        for m in missile_group:
            m.update()
            m.draw(canvas)
            missile_x = m.pos[0]
            missile_y = m.pos[1]
            if m.age > m.lifespan:
                missile_group.pop(missile_num)
            missile_num += 1

    rock_id = 0            
    for sp in rock_group:
        rock_x = int(sp.pos[0])
        rock_y = int(sp.pos[1])
        if len(missile_group) > 0:
        # for each missile, check if hit rock
            sp.check_if_hit(rock_x, rock_y, rock_id, missile_x, missile_y)
        sp.update()
        sp.draw(canvas)
        # check if ship crashed into rock
        sp.check_if_crash(rock_x, rock_y, rock_id)
        rock_id += 1

    if len(explosion_group) > 0:
    # if any explosions exist, animate them
        explosion_id = 0
        for ex in explosion_group:
            ex.update()
            ex.draw(canvas)
            frame_x = ex.age * ex.image_center[1]
            frame_y = ex.image_center[1]
            if ex.age > ex.lifespan:
                explosion_group.pop(explosion_id)
            else:    
                ex.image_center = [frame_x, frame_y]
            explosion_id += 1
    
    # print the score and number of lives remaining    
    canvas.draw_text("Lives : " + str(lives), [50, 50], 20, "White", "monospace")
    canvas.draw_text("Score : " + str(score), [650, 50], 20, "White", "monospace")
    
# timer handler that spawns a rock    
def rock_spawner():
    # this creates a large rock instance with random position, velocity, and spin
    rock_pos_x = random.randrange(0, WIDTH)
    rock_pos_y = random.randrange(0, HEIGHT)
    rock_pos = [rock_pos_x, rock_pos_y]
    rock_vel_x = random.randrange(-1, 1)
    rock_vel_y = random.randrange(-1, 1)
    rock_vel = [rock_vel_x, rock_vel_y]
    rock_ang_vel = (random.randrange(-10, 10)) / 100

    # check if rock will spawn too close to ship
    distance = dist(my_ship.pos, [rock_pos_x, rock_pos_y])
    if distance < 100:
        pass
#        print "too close to spawn"
    # as long as the maximum number has not been exceeded, add the rock to the group
    elif len(rock_group) < number_of_rocks - 1 and lives > 0:
        rock_group.append(Sprite(rock_pos, rock_vel, 0, rock_ang_vel, asteroid_image, asteroid_info))
    
# functions that handle when keys are pressed
def keydown(key):
    global lives
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
        if lives > 0:
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
        my_ship.fired_missle = False
        
def mouseclick(position):
    global lives, score, points_to_bonus
    if lives == 0:
        lives = 2
        score = 0
        points_to_bonus = 500
        
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship in the middle of the screen
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(mouseclick)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
