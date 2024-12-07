from tkinter import constants
import turtle, random, time
#Options I used
# 5, 6


#TODO write documentaion
#TODO implement sprite class
#TODO implement vectors
#TODO give snake eyes
#TODO enemy snake

#notes:
#move objects dont regen objects for games

BOARD_WIDTH = 600
TILE_WIDTH = 30
STARTPOS = (105, 315)
STRETCH_FACTOR = TILE_WIDTH/20

if BOARD_WIDTH % TILE_WIDTH != 0 :
    print("tiles must fit in board evenly")
    exit()

def check_collide(point, collider) -> bool:
    """ point is a tuple (2d vec)
        collider is multipurpose as snake class or collider
        multiplurpose func a bit messy so
        TODO make collider a class attrib and implement sprite class
    """
    if isinstance(collider, Snake):
        ishit = False
        if len(collider.segments)<1:
            return False
        for i in collider.segments[:-1]:
            # default turtle size is 20X20 px
            dimensions = i.shapesize()
            pos = i.pos()
            topx= pos[0]-(20*dimensions[0])//2
            topy= pos[1]-(20*dimensions[1])//2
            bottomx= pos[0]+(20*dimensions[0])//2
            bottomy= pos[1]+(20*dimensions[1])//2
            ishit = (ishit or 
                           check_collide(point, (topx, topy, bottomx, bottomy)))
        return ishit
    if isinstance(collider, tuple):
        if len(collider) != 4 :
            raise ValueError("Collider data is has incorrect dimension count")
        if collider[0] < point[0] < collider[2] and collider[1] < point[1] < collider[3]:
            return True
        else:
            return False



class Game():
    def __init__(self):
        #Setup 700x700 pixel window
        turtle.setup(700, 700)
        #Bottom left of screen is (-40, -40), top right is (640, 640)
        turtle.setworldcoordinates(-40, -40, 640, 640)
        cv = turtle.getcanvas()
        cv.adjustScrolls()


        self.highscore = 0
        self.score = 0
        self.gameover = False
        #since reset game resets most turtle settings, they should be defined 
        #in this method instead
        self.reset_game()

        #These lines must always be at the BOTTOM of __init__
        turtle.listen()
        # turtle.exitonclick()
        turtle.mainloop()
    def quit(self):
        turtle.bye()
        exit()
    def retry(self):
        if self.gameover:
            self.reset_game()

    def reset_game(self):
        self.gameover = True#stop gameloop temporarily
        self.highscore = max(self.score, self.highscore)
        screen = turtle.Screen()
        screen.clearscreen()
        turtle.tracer(0, 0)

        #Ensure turtle is running as fast as possible
        turtle.hideturtle()
        turtle.delay(0)
        turtle.speed(0)

        self.draw_board()

        self.score = 0
        self.gameover = False
        self.draw_score()

        self.player = Snake(STARTPOS,"green")
        self.apple = Apple()

        #bind keymaps again since turtle is reset
        turtle.onkeypress(self.player.go_down, 'Down')
        turtle.onkeypress(self.player.go_up, 'Up')
        turtle.onkeypress(self.player.go_left, 'Left')
        turtle.onkeypress(self.player.go_right, 'Right')
        turtle.onkeypress(self.retry, 'space')
        turtle.onkeypress(self.quit, 'q')


        self.gameover = False#start gameloop again
        self.gameloop()

    def draw_board(self):
        turtle.goto(0,0)
        #Draw the board as a square from (0,0) to (600,600)
        old_col = turtle.color()
        for _ in range(4):
            turtle.forward(BOARD_WIDTH)
            turtle.left(90)
        turtle.penup()
        turtle.goto(0,BOARD_WIDTH)
        turtle.color("#d1d1d1")
        for i in range(BOARD_WIDTH//TILE_WIDTH-1):
            turtle.goto(TILE_WIDTH*(i+1), 0)
            turtle.left(90)
            turtle.pendown()
            turtle.forward(BOARD_WIDTH)
            turtle.right(90)
            turtle.penup()
        turtle.goto(0,0)
        turtle.right(90)
        for i in range(BOARD_WIDTH//TILE_WIDTH-1):
            turtle.goto(0, TILE_WIDTH*(i+1))
            turtle.left(90)
            turtle.pendown()
            turtle.forward(BOARD_WIDTH)
            turtle.right(90)
            turtle.penup()
        turtle.color(old_col[0],old_col[1])

    def draw_score(self):
        turtle.goto(0,BOARD_WIDTH)
        turtle.setheading(0)
        turtle.color("white")
        turtle.begin_fill()
        turtle.forward(BOARD_WIDTH)
        turtle.left(90)
        turtle.forward(40)
        turtle.left(90)
        turtle.forward(BOARD_WIDTH)
        turtle.end_fill()
        turtle.color("black")

        turtle.goto(BOARD_WIDTH//4, BOARD_WIDTH+13)
        turtle.write(f"Score: {self.score}", True,font=('Arial', 18, 'normal'))
        turtle.goto(BOARD_WIDTH//4*2, BOARD_WIDTH+13)
        turtle.write(f"High Score: {self.highscore}", True,font=('Arial', 18, 'normal'))


    def gameloop(self):
        if not self.gameover:
            turtle.ontimer(self.gameloop, 200)
            if self.player.move(self.apple):
                self.apple.newpos(self.player.get_fullpos())
                self.score +=1
                self.draw_score()

            self.player.has_collided = (check_collide(self.player.get_pos(), self.player) 
                                        or not check_collide(self.player.get_pos(), (0,0,BOARD_WIDTH, BOARD_WIDTH)))
            if self.player.has_collided:
                self.gameover = True
            turtle.update()
            self.player.reset_mlock()
        else:
            turtle.goto(BOARD_WIDTH//4,BOARD_WIDTH//2)
            self.player.segments[-1].color("red")
            turtle.update()
            turtle.write("Game Over (space to retry, q to quit)", True,font=('Arial', 18, 'normal'))


class Snake():
    def __init__(self, pos,color):
        self.x = pos[0]
        self.y = pos[1]
        self.vx = TILE_WIDTH
        self.vy = 0
        self.color = color
        self.vel = self.vx
        self.segments = []
        self.grow()
        self.has_collided = False
        self.mlock = False # prevent player from hitting multiple keys per frame
        self.mbuffer = self.mbuf_nop
    def grow(self):
        head = turtle.Turtle()
        head.speed(0)
        head.penup()
        head.setpos(self.x, self.y)
        head.color(self.color)
        head.shape("square")
        head.shapesize(STRETCH_FACTOR,STRETCH_FACTOR)
        self.segments.append(head)
    def get_pos(self):
        return (self.x, self.y)
    def get_fullpos(self):
        pos_list = []
        for i in self.segments:
            pos_list.append(i.pos())
        return pos_list


    def move(self,apple):
        self.x += self.vx
        self.y += self.vy
        self.grow()
        if (self.x, self.y) == apple.get_pos():
            return True
        else:
            self.segments[0].hideturtle() # I guess hideturtle isnt in destructor
            self.segments.pop(0)
            return False

    # mlock prevents multiple direction changes on one frame.
    # mbuffer is stores lost input to make it feel more responsive
    # mbuffer is a call stack one wide since nobody can press that fast
    def go_down(self):
        if self.vy:
            return
        if not self.mlock:
            self.vx = 0
            self.vy = -self.vel
            self.mlock = True
        else:
            self.mbuffer = self.go_down
    def go_up(self):
        if self.vy:
            return
        if not self.mlock:
            self.vx = 0
            self.vy = self.vel
            self.mlock = True
        else:
            self.mbuffer = self.go_up
    def go_left(self):
        if self.vx:
            return
        if not self.mlock:
            self.vx = -self.vel
            self.vy = 0
            self.mlock = True
        else:
            self.mbuffer = self.go_left
    def go_right(self):
        if self.vx:
            return
        if not self.mlock:
            self.vx = self.vel
            self.vy = 0
            self.mlock = True
        else:
            self.mbuffer = self.go_right

    def reset_mlock(self):
        self.mlock = False
        self.mbuffer()
        self.mbuffer = self.mbuf_nop

    def mbuf_nop(self):
        pass

    def set_vel(self, vel):
        self.vel = vel
    def __del__(self):
        for i in self.segments:
            i.hideturtle()

class Apple():
    def __init__(self):
        # self.x = 15+30*random.randint(0,19)
        # self.y = 15+30*random.randint(0,19)
        self.x = 15+30*10
        self.y = 15+30*10
        self.drawer = turtle.Turtle()
        self.drawer.shape("circle")
        self.drawer.color("red")
        self.drawer.shapesize(STRETCH_FACTOR,STRETCH_FACTOR)
        self.drawer.penup()
        self.drawer.setpos(self.x, self.y)
    def newpos(self,blacklist):
        self.x = 15+30*random.randint(0,19)
        self.y = 15+30*random.randint(0,19)
        while (self.x,self.y) in blacklist:
            self.x = 15+30*random.randint(0,19)
            self.y = 15+30*random.randint(0,19)
        self.drawer.setpos(self.x, self.y)
    def get_pos(self):
        return (self.x, self.y)
    # def __del__(self):
    #     self.drawer.hideturtle()
    #     print("deleted Apple obj")



if __name__ == '__main__':
    Game()
