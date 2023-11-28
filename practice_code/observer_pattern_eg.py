from abc import ABC, abstractmethod
import pygame
import random

# Observer interface
class Observer(ABC):
    abstractmethod
    def update(self, subject):
        pass

# Concrete observer class
class Rectangle(Observer):
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def update(self, subject):
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Subject class
class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.observers = []

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def attach(self, observer):
        self.observers.append(observer)

    def notify(self):
        for observer in self.observers:
            observer.update(self)

    def move(self, x, y):
        self.x = x
        self.y = y
        self.notify()

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Observer Design Pattern with Pygame")

    running = True
    clock = pygame.time.Clock()

    # Instance of our Publisher
    circle = Circle(400, 300, 50, (255, 255, 255))

    # Three instances of our subscriber/observer classes.
    rectangles = [
        Rectangle(100, 100, 50, 50, (255, 0, 0)),
        Rectangle(200, 200, 50, 50, (0, 255, 0)),
        Rectangle(300, 300, 50, 50, (0, 0, 255)),
    ]

    # Add the three rectangles as our Subsribers to the Circle class 
    for rect in rectangles:
        circle.attach(rect)

    # Start the game loop
    while running:
        # refrsh and clear the screen with black background
        screen.fill((0, 0, 0))

        # listen for any in-game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # draw the circle at its current position
        circle.draw(screen)

        # draw each of the rectangles
        for rect in rectangles:
            rect.draw(screen)

        # get the current mouse position/location
        mouse_pos = pygame.mouse.get_pos()

        # check if the mouse button is pressed
        if pygame.mouse.get_pressed()[0]:
            circle.move(*mouse_pos) # drag the circle 

        # display the screen buffer (i.e. screen contents)
        pygame.display.flip()
        # generate 60 frames per second
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
