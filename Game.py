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
        self.balls = [Ball(Vector2(utils.width/2,utils.height/2),BALL_SIZE,(255,255,255))]
        self.rings = [
            Ring(Vector2(utils.width / 2, utils.height / 2), 50, -1, 360, rotationSpeed=1.1),
            Ring(Vector2(utils.width / 2, utils.height / 2), 30, -1, 360, rotationSpeed=1.0),
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
                #sounds.play(current_time=self.simulation_time)
                break
            utils.contactListener.collisions = []
        
        self.check_ball_fall_through()

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
                    sounds.play(current_time=self.simulation_time)
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