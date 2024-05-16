"""
1. 方块的构造
2. 方块的变形
4. 碰撞检测
5. 消行处理
6. 绘制
"""

import turtle
import random
import time


SHAPE_SIZE = 4
SHAPE = {
    "L": [[0, 1, 0, 0],
          [0, 1, 0, 0],
          [0, 1, 1, 0],
          [0, 0, 0, 0]],

    "J": [[0, 0, 1, 0],
          [0, 0, 1, 0],
          [0, 1, 1, 0],
          [0, 0, 0, 0]],

    "I": [[0, 1, 0, 0],
          [0, 1, 0, 0],
          [0, 1, 0, 0],
          [0, 1, 0, 0]],

    "O": [[0, 0, 0, 0],
          [0, 1, 1, 0],
          [0, 1, 1, 0],
          [0, 0, 0, 0]],

    "Z": [[0, 0, 0, 0],
          [1, 1, 0, 0],
          [0, 1, 1, 0],
          [0, 0, 0, 0]],

    "S": [[0, 0, 0, 0],
          [0, 1, 1, 0],
          [1, 1, 0, 0],
          [0, 0, 0, 0]],

    "T": [[0, 0, 0, 0],
          [1, 1, 1, 0],
          [0, 1, 0, 0],
          [0, 0, 0, 0]],
}

SHAPE_COLOR = {
    "L": "red",
    "J": "green",
    "I": "blue",
    "O": "grey",
    "Z": "cyan",
    "S": "yellow",
    "T": "pink"
}


def draw_square(pen, x, y, color):
    pen.penup()
    pen.goto(x, y)
    pen.pendown()
    pen.fillcolor(color)
    pen.begin_fill()
    for _ in range(4):
        pen.fd(Block.size)
        pen.left(90)
    pen.end_fill()


class Block(turtle.Turtle):
    size = 15
    def __init__(self, x, y):
        super().__init__()
        self.ht()
        s = random.choice(list(SHAPE.keys()))
        self.shape = SHAPE[s]
        self.x = x
        self.y = y
        self.color = SHAPE_COLOR[s]
        self.falling = True

    def draw(self, offset=0):
        self.clear()
        for y in range(SHAPE_SIZE):
            for x in range(SHAPE_SIZE):
                if self.shape[y][x] == 1:
                    draw_square(self, \
                        (self.x + x) * Block.size, \
                        -(self.y + y + offset) * Block.size, \
                        self.color)


class Tetris(turtle.Turtle):
    width = 10
    height = 22
    def __init__(self):
        super().__init__()
        self.ht()
        self.array = [[1] + [0] * self.width + [1] for _ in range(self.height)]
        self.array.append([1] * (self.width + 2))

        self.current_block = Block(self.width // 2, 0)
        self.next_block = Block(self.width // 2, 0)
        self.score = 0
        self.fall_freq = self.calculate_level_fallfreq()
        self.pause = False
        self.gameover = False

        turtle.onkeypress(self._left, "Left")
        turtle.onkeypress(self._right, "Right")
        turtle.onkeypress(self.rotate, "space")
        turtle.onkey(self._downr, "Down")
        turtle.onkeypress(self._down, "Down")
        turtle.onkey(self._pause, "p")
        turtle.listen()

    def _pause(self):
        self.pause = False if self.pause else True

    def _left(self):
        if not self.pause:
            self.current_block.x -= 1
            if self.collide():
                self.current_block.x += 1

    def _right(self):
        if not self.pause:
            self.current_block.x += 1
            if self.collide():
                self.current_block.x -= 1

    def _down(self):
        self.fall_freq = 0.01
    def _downr(self):
        self.fall_freq = self.calculate_level_fallfreq()

    def rotate(self):
        shape = []
        for t in zip(*self.current_block.shape[::-1]):
            shape.append(list(t))
        
        shape_pre = self.current_block.shape.copy()
        self.current_block.shape = shape
        if self.collide():
            self.current_block.shape = shape_pre

    def fall(self):
        # 下落状态： y增加 -> 如果没有碰撞 -> 下落
        #           y增加 -> 有碰撞 -> 停止、更新array -> 出现新的block
        # 这里的更新array交个tetris实例检查处理
        self.current_block.y += 1
        if self.collide():
            self.current_block.y -= 1
            self.current_block.falling = False

    def collide(self):
        # 下落碰撞、左右碰撞、旋转碰撞
        for y in range(SHAPE_SIZE):
            for x in range(SHAPE_SIZE):
                try:
                    if self.current_block.shape[y][x] == \
                            self.array[self.current_block.y + y][self.current_block.x + x] == 1:
                        return True
                except IndexError:
                    continue


    def update(self):
        # 当前块停止下落时，修改array为标记后的
        self.fall()
        if not self.current_block.falling:
            for y in range(SHAPE_SIZE):
                for x in range(SHAPE_SIZE):
                    if self.current_block.shape[y][x] == 1:
                        self.array[self.current_block.y + y][self.current_block.x + x] = 1
            self.current_block = self.next_block
            self.next_block = Block(self.width // 2, 0)
            self.eline()
            self.draw() # 优化，当落定某个方块时才重新绘制背景
            if self.collide():
                self.gameover = True

    def draw(self):
        self.clear()
        self.pencolor("lightgrey")
        for y in range(self.height):
            for x in range(1, self.width + 1):
                if self.array[y][x] == 1:
                    bgcolor = "grey"
                else:
                    bgcolor = "snow"
                draw_square(self, x * Block.size, -y * Block.size, bgcolor)

    def eline(self):
        # 消行处理
        for y in range(self.height):
            if all(self.array[y]):
                self.array.remove(self.array[y])
                self.array.insert(0, [1] + [0] * self.width + [1])
                self.score += 1

    def calculate_level_fallfreq(self):
        self.level = int(self.score / 10) + 1
        return 0.27 - (self.level * 0.01)

class Score(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.penup()
        self.ht()

    def draw(self, carry=""):
        self.clear()
        self.goto(0, Block.size)
        msg = f"score: {tetris.score} level: {tetris.level}"
        msg += " " + carry
        self.write(msg)


if __name__ == "__main__":
    turtle.tracer(False)
    turtle.title("俄罗斯方块(p键暂停游戏，空格键变形)")
    tetris = Tetris()
    tetris.draw()
    now = time.time()
    score = Score()


    while True:
        if time.time() - now > tetris.fall_freq and not tetris.pause:
            tetris.update()
            score.draw()
            now = time.time()
            tetris.next_block.draw(offset=-4)
        if not tetris.pause:
            tetris.current_block.draw()
        if tetris.pause: 
            score.draw("pause")
        if tetris.gameover:
            score.draw("gameover")
            break
            
        turtle.update()
turtle.done()

