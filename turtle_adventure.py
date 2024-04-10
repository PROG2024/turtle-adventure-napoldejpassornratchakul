"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random
import math



class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )


# TODO
# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.

class Enemy_walk_random(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.enemy_id = None
        self.__state = self.moving_right
        self.__state_height = self.moving_down
        self.speed = random.randint(6,10)

    def create(self) -> None:
        self.enemy_id1  = self.canvas.create_oval(0,0,0,0, fill = self.color)



    def update(self) -> None:
        self.x += 1
        self.y += 1
        self.__state()
        self.__state_height()
        if self.hits_player():
            self.game.game_over_lose()


    def move_to(self,x,y):
        self.x = x
        self.y = y

    def moving_right(self):
        self.move_to(self.x + self.speed, self.y)
        if self.x > self.canvas.winfo_width():
            self.__state = self.moving_left

    def moving_left(self):
        self.move_to(self.x - self.speed, self.y)
        if self.x < 0:
            self.__state = self.moving_right

    def moving_up(self):
        self.move_to(self.x, self.y + self.speed)
        if self.y > self.canvas.winfo_height():
            self.__state_height = self.moving_down


    def moving_down(self):
        self.move_to(self.x , self.y - self.speed)
        if self.y < 0:
            self.__state_height = self.moving_up




    def render(self) -> None:
        self.canvas.coords(self.enemy_id1,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)




    def delete(self) -> None:
        pass



class Chasing_Enemy(Enemy):
        def __init__(self,
                     game: "TurtleAdventureGame",
                     size: int,
                     color: str):
            super().__init__(game, size, color)
            self.enemy_id = None

        def create(self) -> None:
            self.enemy_id1  = self.canvas.create_oval(0,0,0,0, fill = self.color)


        def chasing_to_player(self):
            direction_x = self.game.player.x - self.x
            direction_y = self.game.player.y - self. y
            mag =  (direction_x ** 2 + direction_y ** 2) ** 0.5
            if mag != 0:
                direction_x /= mag
                direction_y /= mag
            self.x += direction_x * 1.2
            self.y += direction_y * 1.2



        def update(self) -> None:
            self.chasing_to_player()
            if self.hits_player():
                self.game.game_over_lose()

        def render(self):
            self.canvas.coords(self.enemy_id1,
                               self.x - self.size / 2,
                               self.y - self.size / 2,
                               self.x + self.size / 2,
                               self.y + self.size / 2)

        def delete(self):
            pass

class FencingEnemy(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: int):
        super().__init__(game, size, color)
        self.enemy_id = None
        self.__state = self.moving_right
        self.speed= speed

    def create(self) -> None:
        self.enemy_id1 = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def move_to(self,x,y):
        self.x = x
        self.y = y


    def moving_right(self):
        if self.x < self.game.home.x + (self.game.home.size / 2):
            self.move_to(self.x + self.speed ,self.y)
        else:
            self.__state = self.moving_down

    def moving_down(self):
        if self.y < self.game.home.y + (self.game.home.size / 2):
            self.move_to(self.x , self.y + self.speed)
        else:
            self.__state = self.moving_left

    def moving_left(self):
        if self.x > self.game.home.x - (self.game.home.size / 2):
            self.move_to(self.x - self.speed, self.y)
        else:
            self.__state = self.moving_up


    def moving_up(self):
        if self.y > self.game.home.y - (self.game.home.size / 2):
            self.move_to(self.x , self.y - self.speed)
        else:
            self.__state = self.moving_right




    def update(self):
        self.__state()
        if self.hits_player():
            self.game.game_over_lose()




    def render(self):
        self.canvas.coords(self.enemy_id1,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self):
        pass

class Stealth_Circle(Enemy):
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.enemy_id = None
        self.speed = random.randint(6, 10)
        self.detection = 100
        self.detected = False


    def create(self) -> None:
        self.enemy_id1 = self.canvas.create_oval(0, 0, 0, 0, fill=self.color,outline="white")


    def is_near_by(self):
        distance = ((self.game.player.x - self.x) ** 2 + ((self.game.player.y - self.y) ** 2)) ** 0.5
        return distance < self.detection


    def update(self):
        if self.is_near_by() and not self.detected:
            self.detected = True
            self.canvas.itemconfig(self.enemy_id1, fill = "red")
        if self.detected and not self.is_near_by():
            self.detected = False
            self.canvas.itemconfig(self.enemy_id1,fill = "white")
        if self.hits_player():
            self.game.game_over_lose()

    def delete(self):
        pass


    def render(self):
        self.canvas.coords(self.enemy_id1,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)





# TODO
# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.__game.after(1000, self.create_random_enemy)
        self.__game.after(1500,self.create_chasing_enemy)
        self.__game.after(3000,self.create_stealth_circle)
        self.__game.after(3500,self.create_fencing_enemy)



    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def position(self,object):
        object.x, object.y = random.randint(200,600),random.randint(100,500)

    def position_fencing(self,object):
        object.x, object.y = (
        (self.game.home.x - self.game.home.size / 2), (self.game.home.y - self.game.home.size / 2))


    def create_random_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        for i in range(5):
            enemy_random1 = Enemy_walk_random(self.__game, 20, "Blue")
            self.position(enemy_random1)
            self.__game.add_element(enemy_random1)

    def create_chasing_enemy(self):
        for i in range(4):
                chasing_enemy = Chasing_Enemy(self.__game,20,"red")
                self.position(chasing_enemy)
                self.__game.add_element(chasing_enemy)

    def create_fencing_enemy(self):
        for i in range(3):
            if i == 0:
                fencing_enemy = FencingEnemy(self.__game, 10,"yellow", 1)
                fencing_enemy.x, fencing_enemy.y = (
                (self.game.home.x - self.game.home.size / 2), (self.game.home.y - self.game.home.size / 2))
                self.__game.add_element(fencing_enemy)
            elif i == 1:
                fencing_enemy = FencingEnemy(self.__game, 10, "yellow", 3)
                fencing_enemy.x, fencing_enemy.y = (
                (self.game.home.x - self.game.home.size / 2), (self.game.home.y - self.game.home.size / 2))
                self.__game.add_element(fencing_enemy)
            elif i == 2:
                fencing_enemy = FencingEnemy(self.__game, 10, "yellow", 4)
                fencing_enemy.x, fencing_enemy.y = (
                (self.game.home.x - self.game.home.size / 2), (self.game.home.y - self.game.home.size / 2))

                self.__game.add_element(fencing_enemy)

    def create_stealth_circle(self):
        for i in range(5):
            stealth_circle1 = Stealth_Circle(self.__game, 50, "white")
            self.__game.add_element(stealth_circle1)
            self.position(stealth_circle1)






class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
