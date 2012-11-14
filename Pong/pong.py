#!/usr/bin/env python

"""
Pygame Tutorial 3
Pong: Step 3 - The Polish

Written by Collin "Keeyai" Green

Version 1.0.0 - 2010-12-26

Modifications for Analogue input control by Chris Fane
For more information see http://Rasathus.blogspot.co.uk

"""

try:
    import sys 
    import os
    import math
    import random
    import time

    from threading import Thread

    import pygame
    from pygame.locals import *
    
    from pigredients.ics import mcp3008 as mcp3008

except ImportError, err:
    print "%s Failed to Load Module: %s" % (__file__, err)
    sys.exit(1)

paddle_count = 0

class Paddle(pygame.sprite.Sprite):
    """A paddle sprite. Subclasses the pygame sprite class.
    Handles its own position so it will not go off the screen."""

    def __init__(self, xy):
    
        global paddle_count
        
        # initialize the pygame sprite part
        pygame.sprite.Sprite.__init__(self)
        # set image and rect
        self.image = pygame.image.load(os.path.join('images','pong_paddle.gif'))
        self.rect = self.image.get_rect()

        self.spi_address = paddle_count
        paddle_count = paddle_count + 1
        
        # set position
        self.rect.centerx, self.rect.centery = xy

        # the movement speed of our paddle
        self.movementspeed = 5

        # the current velocity of the paddle -- can only move in Y direction
        self.velocity = 0

    def up(self):
        """Increases the vertical velocity"""
        if self.velocity >= 0:
            #print "Old Velocity Up : %s" % self.velocity 
            self.velocity -= self.movementspeed
            #print "New Velocity Up : %s" % self.velocity

    def down(self):
        """Decreases the vertical velocity"""
        if self.velocity <= 0:
            #print "Old Velocity Up : %s" % self.velocity 
            self.velocity += self.movementspeed
            #print "New Velocity Up : %s" % self.velocity

    def zero(self):
        """Zero the vertical velocity"""
        #print "Zero'd"
        #print "Old Velocity Up : %s" % self.velocity 
        self.velocity = 0
        #print "New Velocity Up : %s" % self.velocity

    def move(self, dy):
        """Move the paddle in the y direction. Don't go out the top or bottom"""
        if self.rect.bottom + dy > 400:
            self.rect.bottom = 400
        elif self.rect.top + dy < 0:
            self.rect.top = 0
        else:
            self.rect.y += dy

    def update(self):
        """Called to update the sprite. Do this every frame. Handles
        moving the sprite by its velocity"""
        self.move(self.velocity)




class ControlListner(object):
    
    def __init__(self):
        # Using standard addresses so no need for any params.
        self.adc = mcp3008.MCP3008()
        self.event_id = pygame.USEREVENT+1
        self.control_state = {}
        for i in range(paddle_count):
            self.control_state[i] = self.adc.read_input(i) 
    
    def check_interfaces(self):
        for i in range(paddle_count):
            cur_val = self.adc.read_input(i)
            #print "cur_val : %s previous_state : %s" % ( cur_val, self.control_state[i]) 
            new_event = pygame.event.Event(self.event_id, current_pos = cur_val, previous_pos = self.control_state[i],  paddle_num = i) 
            pygame.event.post(new_event)
            self.control_state[i] = cur_val
            
            """
            if cur_val > self.control_state[i]+3:
                #print "New is greater than previous"
                #print "Adding event"
                new_event = pygame.event.Event(self.event_id, current_pos = cur_val, previous_pos = self.control_state[i],  paddle_num = i) 
                pygame.event.post(new_event)
            elif cur_val < self.control_state[i]-3:
                #print "New is less than previous"
                #print "Adding event"
                new_event = pygame.event.Event(self.event_id, current_pos = cur_val,  previous_pos = self.control_state[i], paddle_num = i) 
                pygame.event.post(new_event)
            self.control_state[i] = cur_val
            """

class Ball(pygame.sprite.Sprite):
    """A ball sprite. Subclasses the pygame sprite class."""

    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images','pong_ball.gif'))
        self.rect = self.image.get_rect()

        self.rect.centerx, self.rect.centery = xy
        self.maxspeed = 10
        self.servespeed = 5
        self.velx = 0
        self.vely = 0

    def reset(self):
        """Put the ball back in the middle and stop it from moving"""
        self.rect.centerx, self.rect.centery = 400, 200
        self.velx = 0
        self.vely = 0

    def serve(self):
        angle = random.randint(-45, 45)

        # if close to zero, adjust again
        if abs(angle) < 5 or abs(angle-180) < 5:
            angle = random.randint(10,20)

        # pick a side with a random call
        if random.random() > .5:
            angle += 180

        # do the trig to get the x and y components
        x = math.cos(math.radians(angle))
        y = math.sin(math.radians(angle))

        self.velx = self.servespeed * x
        self.vely = self.servespeed * y


class Score(pygame.sprite.Sprite):
    """A sprite for the score."""

    def __init__(self, xy):
        pygame.sprite.Sprite.__init__(self)

        self.xy = xy    # save xy -- will center our rect on it when we change the score

        self.font = pygame.font.Font(None, 50)  # load the default font, size 50

        self.leftscore = 0
        self.rightscore = 0
        self.reRender()

    def update(self):
        pass

    def left(self):
        """Adds a point to the left side score."""
        self.leftscore += 1
        self.reRender()

    def right(self):
        """Adds a point to the right side score."""
        self.rightscore += 1
        self.reRender()

    def reset(self):
        """Resets the scores to zero."""
        self.leftscore = 0
        self.rightscore = 0
        self.reRender()

    def reRender(self):
        """Updates the score. Renders a new image and re-centers at the initial coordinates."""
        self.image = self.font.render("%d     %d"%(self.leftscore, self.rightscore), True, (0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = self.xy


class Game(object):
    """Our game object! This is a fairly simple object that handles the
    initialization of pygame and sets up our game to run."""

    def __init__(self):
        """Called when the the Game object is initialized. Initializes
        pygame and sets up our pygame window and other pygame tools
        that we will need for more complicated tutorials."""

        # load and set up pygame
        pygame.init()

        # create our window
        self.window = pygame.display.set_mode((800, 400))

        # clock for ticking
        self.clock = pygame.time.Clock()

        # set the window title
        pygame.display.set_caption("Pygame Tutorial 3 - Pong")

        # tell pygame to only pay attention to certain events
        # we want to know if the user hits the X on the window, and we
        # want keys so we can close the window with the esc key
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

        # make background -- all white, with black line down the middle
        self.background = pygame.Surface((800,400))
        self.background.fill((255,255,255))
        # draw the line vertically down the center
        pygame.draw.line(self.background, (0,0,0), (400,0), (400,400), 2)
        self.window.blit(self.background, (0,0))
        # flip the display so the background is on there
        pygame.display.flip()

        # a sprite rendering group for our ball and paddles
        self.sprites = pygame.sprite.RenderUpdates()

        # create our paddles and add to sprite group
        self.leftpaddle = Paddle((50,200))
        self.sprites.add(self.leftpaddle)
        self.rightpaddle = Paddle((750,200))
        self.sprites.add(self.rightpaddle)

        # create ball
        self.ball = Ball((400,200))
        self.sprites.add(self.ball)

        # score image
        self.scoreImage = Score((400, 50))
        self.sprites.add(self.scoreImage)

        # create sounds
        self.pingsound = pygame.mixer.Sound(os.path.join('sound', 'ping.wav'))
        self.pongsound = pygame.mixer.Sound(os.path.join('sound', 'pong.wav'))
        
        # run up control interfaces reader.
        self.control_listner = ControlListner()
        

    def run(self):
        """Runs the game. Contains the game loop that computes and renders
        each frame."""

        print 'Starting Event Loop'

        running = True
        # run until something tells us to stop
        while running:

            # tick pygame clock
            # you can limit the fps by passing the desired frames per seccond to tick()
            self.clock.tick(60)

            # Update our control interfaces.
            self.control_listner.check_interfaces()
            
            # handle pygame events -- if user closes game, stop running
            running = self.handleEvents()

            # update the title bar with our frames per second
            pygame.display.set_caption('Pygame Tutorial 3 - Pong   %d fps' % self.clock.get_fps())

            # handle ball -- all our ball management here
            self.manageBall()

            # update our sprites
            for sprite in self.sprites:
                sprite.update()

            # render our sprites
            self.sprites.clear(self.window, self.background)    # clears the window where the sprites currently are, using the background
            dirty = self.sprites.draw(self.window)              # calculates the 'dirty' rectangles that need to be redrawn

            # blit the dirty areas of the screen
            pygame.display.update(dirty)                        # updates just the 'dirty' areas

        print 'Quitting. Thanks for playing'

    def handleEvents(self):
        """Poll for PyGame events and behave accordingly. Return false to stop
        the event loop and end the game."""

        # poll for pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == pygame.USEREVENT+1:
                # will be using 0.390625 a lot, 400/1023 = 0.390625
                if event.paddle_num == 0:
                    # Right paddle
                    #print "Right - Current Pos : %s Mapped Pos : %s Paddle Pos : %s" % (event.current_pos, (event.current_pos * 0.390625), self.rightpaddle.rect.y)
                    if (event.current_pos * 0.390625) > self.rightpaddle.rect.y +10:
                        self.rightpaddle.down()
                    elif (event.current_pos * 0.390625) < self.rightpaddle.rect.y -10:
                        self.rightpaddle.up()
                    else:
                        self.rightpaddle.zero()
                else:
                    # Left paddle
                    #print "Left - Current Pos : %s Mapped Pos : %s Paddle Pos : %s" % (event.current_pos, (event.current_pos * 0.390625), self.leftpaddle.rect.y)
                    if (event.current_pos * 0.390625) > self.leftpaddle.rect.y +10:
                        self.leftpaddle.down()
                    elif (event.current_pos * 0.390625) < self.leftpaddle.rect.y -10:
                        self.leftpaddle.up()
                    else:
                        self.leftpaddle.zero() 
                    
            # handle user input
            elif event.type == KEYDOWN:
                # if the user presses escape, quit the event loop.
                if event.key == K_ESCAPE:
                    return False

                # paddle control
                if event.key == K_w:
                    self.leftpaddle.up()
                if event.key == K_s:
                    self.leftpaddle.down()

                if event.key == K_UP:
                    self.rightpaddle.up()
                if event.key == K_DOWN:
                    self.rightpaddle.down()

                # serve with space if the ball isn't moving
                if event.key == K_SPACE:
                    if self.ball.velx == 0 and self.ball.vely == 0:
                        self.ball.serve()

            elif event.type == KEYUP:
                # paddle control
                if event.key == K_w:
                    self.leftpaddle.down()
                if event.key == K_s:
                    self.leftpaddle.up()

                if event.key == K_UP:
                    self.rightpaddle.down()
                if event.key == K_DOWN:
                    self.rightpaddle.up()

        return True

    def manageBall(self):
        """This basically runs the game. Moves the ball and handles
        wall and paddle collisions."""

        # move the ball according to its velocity
        self.ball.rect.x += self.ball.velx
        self.ball.rect.y += self.ball.vely

        # check if ball is off the top
        if self.ball.rect.top < 0:
            self.ball.rect.top = 1

            # reverse Y velocity so it 'bounces'
            self.ball.vely *= -1

            # play the pong sound
            self.pongsound.play()

        # check if ball is off the bottom
        elif self.ball.rect.bottom > 400:
            self.ball.rect.bottom = 399

            # reverse Y velocity so it 'bounces'
            self.ball.vely *= -1

            # play the ping sound
            self.pongsound.play()

        # check if the ball hits the left side -- point for right!
        if self.ball.rect.left < 0:
            # keep score
            self.scoreImage.right()

            # reset ball
            self.ball.reset()
            return

        # check if the ball hits the right side -- point for left!
        elif self.ball.rect.right > 800:
            #keep score
            self.scoreImage.left()

            # reset ball
            self.ball.reset()
            return

        # check for collisions with the paddles using pygames collision functions
        collided = pygame.sprite.spritecollide(self.ball, [self.leftpaddle, self.rightpaddle], dokill=False)

        # if the ball hit a paddle, it will be in the collided list
        if len(collided) > 0:
            hitpaddle = collided[0]

            # reverse the x velocity on the ball
            self.ball.velx *= -1

            # need to make sure the ball is no longer in the paddle -- going to move it again manually
            self.ball.rect.x += self.ball.velx

            # give a little of the paddle's velocity to the ball
            self.ball.vely += hitpaddle.velocity/3.0

            # play the ping sound
            self.pingsound.play()

# create a game and run it
if __name__ == '__main__':
    game = Game()
    game.run()
