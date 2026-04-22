import random
from pygame import Vector2
from Ball import Ball
from Ring import Ring
from utils import utils
import time
from Sounds import sounds

TARGET_FPS = 60
DT = 1.0 / TARGET_FPS  # 1.0 = normal speed
accumulator = 0.0
last_time = time.perf_counter()
BALL_SIZE = 3

class Game:
    def __init__(self):
        # Start with one ball
        ballPosition = Vector2(utils.width/2,utils.height/2)
        self.balls = [Ball(self.offsetBallPos(ballPosition),BALL_SIZE,(255,255,255))]
        self.rings = [
            Ring(Vector2(utils.width / 2, utils.height / 2), 26, -1, 360, 60, 0.08, rotationSpeed=1.1),
            Ring(Vector2(utils.width / 2, utils.height / 2), 30, -1, 360, 60, 0.16, rotationSpeed=1.0),
            Ring(Vector2(utils.width / 2, utils.height / 2), 34, -1, 360, 60, 0.24, rotationSpeed=0.9),
            Ring(Vector2(utils.width / 2, utils.height / 2), 38, -1, 360, 60, 0.32, rotationSpeed=0.8),
            Ring(Vector2(utils.width / 2, utils.height / 2), 42, -1, 360, 60, 0.40, rotationSpeed=0.7),
            Ring(Vector2(utils.width / 2, utils.height / 2), 46, -1, 360, 60, 0.48, rotationSpeed=0.6),
        ]
        
        self.balls_inside_ring = set()
        
        self.balls_spawned = set()
        self.ring_center = Vector2(utils.width / 2, utils.height / 2)
        self.ring_radius = 50
        
        self.simulation_time = 0.0

    def update(self):
        MAX_STEP = 1.0 / 60.0
        time_remaining = DT
        steps = 0
        max_substeps = 20  # Safety limit to prevent infinite loops
        
        # Break large timesteps into smaller sub-steps for accuracy
        while time_remaining > 0.0001 and steps < max_substeps:
            step_size = min(time_remaining, MAX_STEP)
            utils.world.Step(step_size, 6, 2)
            time_remaining -= step_size
            steps += 1
        
        if not hasattr(self, '_time_override'):
            self.simulation_time += DT
        
        if utils.contactListener:
            for bodyA,bodyB in utils.contactListener.collisions:
                # Record sound event with simulation time
                sounds.play(current_time=self.simulation_time, sound_effect="assets/rizz_sound_effect.wav")
                break
            utils.contactListener.collisions = []
        
        self.check_ring_exit()
        
    def check_ring_exit(self):
        for ring in self.rings[:]:
            for ball in self.balls[:]:
                ball_position = ball.getPos()
                distance = ball_position.distance_to(self.ring_center)
                if distance > ring.radius * 10:
                    sounds.play(current_time=self.simulation_time, sound_effect="meow.wav")
                    if ring in self.rings:
                        utils.world.DestroyBody(ring.body)
                        self.rings.remove(ring)
                    
                
        return
    
    def check_ball_fall_through(self):
        for ball in self.balls[:]:  # Use slice to avoid modification during iteration
            if ball in self.balls_spawned:
                continue
            
            ball_pos = ball.getPos()
            distance_from_center = (ball_pos - self.ring_center).length()
            
            # Ball inside ring
            if distance_from_center < self.ring_radius:
                self.balls_inside_ring.add(ball)

            if ball in self.balls_inside_ring:
                # Check if ball has fallen completely off the bottom of the screen
                if ball_pos.y > utils.height:
                    sounds.play(current_time=self.simulation_time, sound_effect="assets/meow.wav")
                    self.balls_spawned.add(ball)
                    self.balls_inside_ring.discard(ball)
                    self.spawn_two_balls()

    def spawn_two_balls(self):
        # Spawn two balls at the center, slightly offset horizontally
        offset1 = Vector2(-5, 0)
        offset2 = Vector2(5, 0)
        new_ball1 = Ball(self.ring_center + offset1, BALL_SIZE, (255, 255, 255))
        new_ball2 = Ball(self.ring_center + offset2, BALL_SIZE, (255, 255, 255))
        self.balls.append(new_ball1)
        self.balls.append(new_ball2)

    def draw(self, surface=None):
        if surface is None:
            surface = utils.screen
        for ring in self.rings:
            ring.draw(surface)
        for ball in self.balls:
            ball.draw(surface)
    
    def offsetBallPos(self, pos:Vector2):
        yOffset = random.uniform(-5,5)
        pos.y = pos.y + yOffset
        return pos