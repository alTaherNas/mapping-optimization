#!/usr/bin/env python

import pygame as pg
from pygame.locals import *
import random
import sys
import numpy as np

pg.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SCREEN_RECT = pg.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

ROBOT_SPEED = 2
ROBOT_COLOR = (0, 0, 255)
ROBOT_LEN = WINDOW_WIDTH//50
ROBOT_SIZE = (ROBOT_LEN, ROBOT_LEN)
FONT_SIZE = 40
LANDMARK_RADIUS = 5
LANDMARK_COLOR =  (255, 0, 0)



class Robot:
    def __init__(self, speed, color):

        # generate random initial positions for robots
        self.x = random.randint(ROBOT_LEN, WINDOW_WIDTH - ROBOT_LEN)
        self.y = random.randint(ROBOT_LEN, WINDOW_HEIGHT - ROBOT_LEN)
        self.rect = pg.Rect((self.x - ROBOT_LEN // 2, self.y - ROBOT_LEN // 2), ROBOT_SIZE)

        self.action = [0, 0]
        self.speed = speed
        self.color = color
        self.costs = []
        # creating separate costs for each landmark
        for landmark in landmarks:
            self.costs.append(QuadraticCost())

    def communicate(self, robots):
        '''
        does weighted averaging
        '''
        n = len(robots) # number of neighbors
        for i in range(len(landmarks)):
            sm = np.zeros(2)
            for robot in robots:
                if id(robot) != id(self):
                    sm += robot.costs[i].x # equal weighted
            sm /= (n-1)

            self.costs[i].setX(0.1* self.costs[i].x + 0.9 * sm) # set the solution to weighted average
        return



    def render(self):
        self.rect.left += self.speed * self.action[0]
        self.rect.top += self.speed * self.action[1]
        self.x = self.rect.left + ROBOT_LEN // 2
        self.y = self.rect.top + ROBOT_LEN // 2

        pg.draw.rect(screen, self.color, self.rect)

    def readSensor(self):
        '''
        Range only measuerments
        '''
        # distances = []
        for i in range(len(landmarks)):
            sigma = 10 *euclideanDistance(landmarks[i], [self.x, self.y]) / WINDOW_WIDTH
            measurement = np.random.normal(landmarks[i], sigma)
            self.costs[i].update([self.x, self.y], euclideanDistance([self.x, self.y], measurement)) # updates cost

            # distances.append(measurement)


        return # distances

    def makeDecision(self, nn):
        if nn == None:
            self.action[0] = 0
            self.action[1] = 0
        elif nn == "random":
            self.action[0] = random.randint(-1, 1)
            self.action[1] = random.randint(-1, 1)
        else:
            print("Not yet implemented!")



class QuadraticCost:
    '''
    for all robots, associate a cost function for every landmark
    '''
    def __init__(self):
        self.T = 0 # number of data
        # initial state and solution that evolves with time
        self.x = np.array((np.random.uniform(0, WINDOW_WIDTH), np.random.uniform(0, WINDOW_HEIGHT)))
        self.cost = 0
        self.d = 0
        self.p = np.array((0, 0))

    def update(self, p, d):
        '''
        add newly observed data
        '''
        # p is the position of the robot at time t
        # d is the distance measured from a landmark
        self.T += 1
        self.p = p
        self.d = d
        xp = np.linalg.norm(self.p - self.x)
        self.cost = 1 / 2 * (xp - self.d) ** 2
        # gradient = (self.x - p) (1 - d / xp)
        # self.x -= 1 / self.T * (gradient)
        return

    def setX(self, y):
        self.x = y
        xp = np.linalg.norm(self.p - self.x)
        self.cost = 1 / 2 * (xp - self.d) ** 2

    def step(self):
        xp = np.linalg.norm(self.p - self.x) # update cost
        gradient = (self.x - self.p) * (1 - self.d / xp)
        self.x -= 1 / 10 * (gradient) # update x
        xp = np.linalg.norm(self.p - self.x) # update cost
        self.cost = 1 / 2 * (xp - self.d) ** 2
        pg.draw.circle(screen, (0, 0, 0), self.x, 4)
        return


def processInput(simulation):
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()
        elif not(simulation) and event.type in (KEYDOWN, KEYUP):
            if event.key in {K_UP, K_DOWN}:
                robot1.action[1] = (event.type==KEYDOWN) * ((-1) ** (event.key==K_UP))
            if event.key in {K_RIGHT, K_LEFT}:
                robot1.action[0] = (event.type==KEYDOWN) * ((-1) ** (event.key==K_LEFT))

            if event.key in {K_i, K_k}:
                robot2.action[1] = (event.type == KEYDOWN) * ((-1) ** (event.key == K_i))
            if event.key in {K_l, K_j}:
                robot2.action[0] = (event.type == KEYDOWN) * ((-1) ** (event.key == K_j))

            if event.key in {K_w, K_s}:
                robot3.action[1] = (event.type == KEYDOWN) * ((-1) ** (event.key == K_w))
            if event.key in {K_a, K_d}:
                robot3.action[0] = (event.type == KEYDOWN) * ((-1) ** (event.key == K_a))


                # for debugging purposes
            if event.key == K_8: # display 8 sensor readings
                print("robot 1")
                # print(robot1.readSensor())
                # print(robot2.readSensor())
                # display whatever

def renderLandmarks():
    for landmark in landmarks:
        pg.draw.circle(screen, LANDMARK_COLOR, landmark, LANDMARK_RADIUS)


def euclideanDistance(a, b):
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)




landmarks = [[2*WINDOW_WIDTH//3, 2*WINDOW_HEIGHT//3], [1*WINDOW_WIDTH//3, 1*WINDOW_HEIGHT//3]]
robots = []
running = True


clock = pg.time.Clock()

screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pg.SCALED) # global variable
pg.display.set_caption("Mapping")

# cost_font = pg.font.Font(None, FONT_SIZE)

robot1 = Robot(ROBOT_SPEED, ROBOT_COLOR)
robots.append(robot1)
robot2 = Robot(ROBOT_SPEED, ROBOT_COLOR)
robots.append(robot2)
robot3 = Robot(ROBOT_SPEED, ROBOT_COLOR)
robots.append(robot3)

robots = [robot1, robot2, robot3]

ticks = 0
simulation = False

while running:

    processInput(simulation)

    screen.fill('White')



    # cost += .0005
    # cost_surface = cost_font.render("Cost = %.2f" % cost, True, 'Black')
    # screen.blit(cost_surface, (0, 0))



    renderLandmarks()

    # make observation
    # robots pass their values to their neighbors (they should have a local copy of their neighbors)
    # do a weighted averaging step


    for robot in robots:
        robot.readSensor()

    for robot in robots:
        robot.communicate(robots)

    # evaluate gradient at that step

    for i in range(len(landmarks)):
        for robot in robots:
            robot.costs[i].step()

    ###################################################
    # remember to update step size
    # print stuff and debug

    robot1.render()
    # if ticks % 9 == 0:
    #     robot2.makeDecision(None)
    #     if simulation:
    #         robot1.makeDecision(None)

    robot2.render()

    robot3.render()

    for i in range(len(robots)):
        print(f'Landmark 0 is at {landmarks[0]}')
        print(f'Robot {i}')
        print(robots[i].costs[0].x)
        print(f'Landmark 1 is at {landmarks[1]}')
        print(robots[i].costs[1].x)



    ticks += 1
    pg.display.update()
    pg.image.save(screen, "screenshot.jpeg")
    clock.tick(60)


pg.quit()
sys.exit()
