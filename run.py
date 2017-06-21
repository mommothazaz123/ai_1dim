'''
Created on Jun 19, 2017

@author: andrew
'''

import math
import random

from lib.graphics import *


Y_VALUE = 250  # keep everything along horizontal
X_MIN = 0
X_MAX = 500

PROGRAM_SPEED = 1 / 20  # 20 tps

class Program:
    def move_random(self, max_move_dist):
        a = round(max_move_dist / (20 * 3))
        a = min(50, a)
        #a = 0
        r = random.randint(-a, a)/100
        self.last_random = r
        self.robot.move(r)

p = Program()

class Robot(Circle):
    """A naive object with a few helper methods."""
    def __init__(self, pos):
        center = Point(pos, Y_VALUE)
        super().__init__(center, 7)
        self.setOutline('green')
        self.draw(p.win)
        self.reverse = False
        
    def getPos(self):  # controller input
        return self.getCenter().x
    
    def move(self, dx):  # controller output
        if self.reverse: dx = -dx
        super().move(dx, 0)
        
class Controller:
    """This object should take input from the Robot and minimise delta."""
    def __init__(self, robot):
        self.robot = robot
        self.weight = 0  # how output affects input
        self.learn_rate = 0.001
        self.learn_rate_rate = 0.001
        self.last_output = None
        self.last_lr_output = 0
    
    def get_delta(self):
        """Returns a positive number if the robot is to the right of the target."""
        return self.robot.getPos() - p.target
    
    def move_robot(self, a=False):
        if a or abs(self.weight) < 0.001:  # haven't moved yet. let's try something
            self.output(random.randint(-100, 100) or 1)
        else:
            self.move_robot_smart()
        
    def move_robot_smart(self):  # controller output
        self.output(self.weight * self.get_delta())
        
    def learn(self, before, after):
        delta = abs(after) - abs(before) # neg = closer
        print("Delta: " + str(delta))
        print("Last output: " + str(-abs(self.last_output)))
        a = -self.learn_rate * (-abs(self.last_output) * delta * PROGRAM_SPEED)
        print("Changing weight by: " + str(a))
        self.weight += a
        self.weight = max(-20.1, min(20.1, self.weight))
        
    def change_learn(self):
        out = random.randint(-5, 5) * self.get_delta() / 10000
        self.last_lr_output += out
        self.learn_rate += out
        self.learn_rate = max(0, min(0.5, self.learn_rate))
        
    def learn_to_learn(self, before, after):
        delta = abs(after) - abs(before)
        if delta == 0: delta += 0.01
        self.learn_rate = (self.learn_rate - self.last_lr_output) + -self.learn_rate_rate * (self.last_lr_output * delta * (PROGRAM_SPEED*10))
        self.learn_rate = max(0, min(0.5, self.learn_rate))
        self.last_lr_output = 0
        
    def output(self, out):
        self.last_output = out
        out = out/10
        self.robot.move(out)

def init():
    p.win = GraphWin("1D Point", X_MAX, 2 * Y_VALUE, autoflush=False)  # 500x500 window
    p.graphwin = GraphWin("Data", 500, 500, autoflush=False)
    p.target = random.randint(X_MIN, X_MAX)
    
    p.robot = Robot(random.randint(X_MIN, X_MAX))
    p.cont = Controller(p.robot)
    
    p.before_ten = 0
    
    p.tc = Circle(Point(p.target, Y_VALUE), 5)  # put target somewhere random
    p.tc.draw(p.win)
    
    p.weight_display = Text(Point(50, 10), "Weight: None")
    p.delta_display = Text(Point(50, 20), "Delta: ")
    p.weight_display.draw(p.win)
    p.delta_display.draw(p.win)
    
    zero = Line(Point(0, 250), Point(500, 250))
    zero.draw(p.graphwin)
    
    p.win.getMouse()

def update_graphs():
    X_VALUE_COLOR = 'green'
    OUTPUT_COLOR = 'red'
    RANDOM_COLOR = 'blue'
    LR_COLOR = 'purple'
    colors = (X_VALUE_COLOR, OUTPUT_COLOR, RANDOM_COLOR, LR_COLOR)
    p.last_points = getattr(p, 'last_points', None) or [[], [], [], []]  # [[x], [o], [r], [lr]]
    p.datalines = getattr(p, 'datalines', None) or []
    for t in p.last_points:
        for po in t:
            po.move(-1, 0)
    for l in p.datalines:
        l.move(-1, 0)
    p.last_points[0].append(Point(500, 250 - (p.robot.getPos() - p.target)))
    p.last_points[1].append(Point(500, 250 - p.cont.last_output))
    p.last_points[2].append(Point(500, 250 - getattr(p, 'last_random', 0)))
    p.last_points[3].append(Point(500, 500 - (p.cont.learn_rate * 100)))
    for i, t in enumerate(p.last_points):
        if len(t) > 1:
            li = Line(t[-2], t[-1])
            li.setFill(colors[i])
            li.draw(p.graphwin)
            p.datalines.append(li)

def loop(iteration):
    before = p.cont.get_delta()
    p.cont.move_robot()
    if iteration > 10:  # give it 3 cycles to learn
        p.move_random(iteration)
    after = p.cont.get_delta()
    print(before, after)
    p.cont.learn(before, after)
    
    #p.cont.change_learn()
    print(p.cont.learn_rate)
    
    if iteration % 10:
        p.cont.learn_to_learn(p.before_ten, after)
        p.before_ten = p.cont.get_delta()
        
    
    p.weight_display.setText("Weight: " + str(p.cont.weight))
    p.delta_display.setText("Delta: " + str(p.cont.get_delta()))
    
    update_graphs()
    
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
