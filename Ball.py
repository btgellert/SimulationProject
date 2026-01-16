import pygame
from pygame import Vector2
from utils import utils

class Ball:
    def __init__(self,pos,radius,color):
        self.color = color
        self.radius = radius
        self.circle_body = utils.world.CreateDynamicBody(position=(utils.from_Pos((pos.x, pos.y))))
        self.circle_shape = self.circle_body.CreateCircleFixture(radius=self.radius, density=1, friction=0.0, restitution=1.0)
        self.circle_body.userData = self

    def draw(self, surface=None):
        # Draw the ball. If surface is None, uses utils.screen
        if surface is None:
            surface = utils.screen
        for fixture in self.circle_body.fixtures:
            self.draw_circle(fixture.shape, self.circle_body, fixture, surface)

    def draw_circle(self, circle, body, fixture, surface=None):
        # Draw a circle. If surface is None, uses utils.screen
        if surface is None:
            surface = utils.screen
        position = utils.to_Pos(body.transform * circle.pos)
        pygame.draw.circle(surface, self.color, [int(x) for x in position], int(circle.radius * utils.PPM))

    def getPos(self):
        p = utils.to_Pos(self.circle_body.position)
        return Vector2(p[0],p[1])

