'''
Created on Jun 19, 2017

@author: andrew
'''

import random

from lib.graphics import *
import math


Y_VALUE = 250 # keep everything along horizontal
X_MIN = 0
X_MAX = 500

PROGRAM_SPEED = 1/20 # 20 tps

class Program:
    def move_random(self, max_move_dist):
        a = round(max_move_dist/(20*3))
        a = min(50, a)
        #a = 0
        self.robot.move(random.randint(-a, a))

p = Program()

class Robot(Circle):
    """A naive object with a few helper methods."""
    def __init__(self, pos):
        center = Point(pos, Y_VALUE)
        super().__init__(center, 7)
        self.setOutline('green')
        self.draw(p.win)
        self.reverse = False
        
    def getPos(self): # controller input
        return self.getCenter().x
    
    def move(self, dx): # controller output
        if self.reverse: dx = -dx
        super().move(dx, 0)
        
class Controller:
    """This object should take input from the Robot and minimise delta."""
    def __init__(self, robot):
        self.robot = robot
        self.weight = 0 # how output affects input
        self.learn_rate = 0.05
        self.last_output = None
    
    def get_delta(self):
        """Returns a positive number if the robot is to the right of the target."""
        return self.robot.getPos() - p.target
    
    def move_robot(self):
        if abs(self.weight) < 0.01: # haven't moved yet. let's try something
            self.output(random.randint(-10, 10) or 1)
        else:
            self.move_robot_smart()
        
    def move_robot_smart(self): # controller output
        self.output(self.weight * self.get_delta())
        
    def learn(self, before, after):
        self.weight += -self.learn_rate * (self.last_output * (after - before) * PROGRAM_SPEED)
        self.weight = max(-0.5, min(0.5, self.weight))
        
    def output(self, out):
        self.last_output = out
        self.robot.move(out)

def init():
    p.win = GraphWin("1D Point", X_MAX, 2*Y_VALUE, autoflush=False) #500x500 window
    p.target = random.randint(X_MIN, X_MAX)
    
    p.robot = Robot(random.randint(X_MIN, X_MAX))
    p.cont = Controller(p.robot)
    
    p.tc = Circle(Point(p.target, Y_VALUE), 5) # put target somewhere random
    p.tc.draw(p.win)
    
    p.weight_display = Text(Point(50, 10), "Weight: None")
    p.delta_display = Text(Point(50, 20), "Delta: ")
    p.weight_display.draw(p.win)
    p.delta_display.draw(p.win)
    
    p.win.getMouse()

def loop(iteration):
    before = p.cont.get_delta()
    p.cont.move_robot()
    if iteration > 3: # give it 3 cycles to learn
        p.move_random(iteration)
    after = p.cont.get_delta()
    p.cont.learn(before, after)
    
    p.weight_display.setText("Weight: " + str(p.cont.weight))
    p.delta_display.setText("Delta: " + str(p.cont.get_delta()))
    
    time.sleep(PROGRAM_SPEED)
    a = p.win.checkMouse()
    k = p.win.checkKey()
    if a:
        p.tc.move(a.x - p.target, 0)
        p.target = a.x
    if k == 'r':
        p.robot.reverse = not p.robot.reverse
    if k == 'q':
        p.cont.weight = 0
    update()
    return True

if __name__ == '__main__':
    init()
    iteration = 0
    while loop(iteration):
        iteration += 1