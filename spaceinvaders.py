from tkinter import *
import random
import time
import pygame

pygame.mixer.init()


class Ball:
    '''creates the bullets for the user's paddle to shoot the alien'''
    def __init__(self, canvas, paddle, color, x1, y1, x2, y2):
        global BULLET_SPEED
        self.canvas = canvas
        self.paddle = paddle
        self.id = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
        self.y = BULLET_SPEED

    def getID(self):
        '''gets the ID of each of the bullets'''
        return self.id

    def kms(self):
        '''this function makes it so that the bullet will penetrate through every object in its path'''
        global NO_CHEATS
        if NO_CHEATS:
            self.canvas.delete(self.id)
            BALL_OBJ.clear()

    def draw(self):
        '''once the bullet gets to the top of the screen it will be deleted for efficiency'''
        if len(BALL_OBJ) > 0:
            self.canvas.move(self.id, 0, self.y)
        if self.isAtTop():
            self.canvas.delete(self.id)
            BALL_OBJ.clear()

    def isAtTop(self):
        '''when the bullet reaches the top of the '''
        pos = self.canvas.coords(self.id)
        if len(pos) > 0:
            return pos[1] <= 105

    def isTouchingSaucer(self):
        '''if the bulle is touching the saucer it will be deleted'''
        for item in SAUCER:
            pos = self.canvas.coords(self.id)
            item_pos = item.getPos()
            if len(item_pos) > 0 and len(pos) > 0:
                if pos[0] <= item_pos[0] + 30 and pos[0] >= item_pos[0] - 30 and pos[1] <= item_pos[1] + 15:
                    self.kms()
                    item.addPoints()
                    break

    def isTouchingBlocks(self):
        '''if the bullet is toucing the blockers the blocker will go down by 1'''
        for block in ALL_BLOCKS:
            pos = self.canvas.coords(self.id)
            block_pos = block.getPos()
            if len(block_pos) > 0 and len(pos) > 0:
                if pos[0] >= block_pos[0] and pos[0] <= block_pos[2] and pos[1] <= block_pos[1]:
                    self.kms()
                    block.subtractLives()
                    break
                if pos[2] >= block_pos[0] and pos[2] <= block_pos[2] and pos[3] <= block_pos[1]:
                    self.kms()
                    block.subtractLives()
                    break

    def updateAfterRemove(self, alien):
        '''helper method for isTouchingAlien()'''
        global ALIEN_FARTHEST_LEFT, ALIEN_FARTHEST_RIGHT, ALIEN_DEATH_MUSIC, ALL_ALIENS_NOT_DEAD
        self.canvas.delete(alien.getID())  # deleting the alien's image from the canvas
        alien.kill()  # calling the kill method to add points
        self.kms()  # deleting the bullet from the canvas
        for column in topRow.getAliens():  # deleting the item from the column it is from
            if alien in column.getAliens():
                column.getAliens().remove(alien)
            if len(column.getAliens()) == 0:
                topRow.getAliens().remove(column)

        if ALIEN_FARTHEST_LEFT.getTop() == alien and len(ALIEN_FARTHEST_LEFT.getAliens()) > 0 and ALL_ALIENS_NOT_DEAD:
            # if the leftmost column's top was destroyed and the column is not empty
            ALIEN_FARTHEST_LEFT.findHighest()  # find the next highest of the column

        if ALIEN_FARTHEST_RIGHT.getTop() == alien and len(ALIEN_FARTHEST_RIGHT.getAliens()) > 0 and ALL_ALIENS_NOT_DEAD:
            # if the rightmost column's top was destroyed and the column is not empty
            ALIEN_FARTHEST_RIGHT.findHighest()  # find the next highest of the column

        if len(ALIEN_FARTHEST_LEFT.getAliens()) == 0:  # if the leftmost column is empty
            topRow.findFarthestLeft()  # find the next leftmost column in topRow

        if len(ALIEN_FARTHEST_RIGHT.getAliens()) == 0:  # if the rightmost column is empty
            topRow.findFarthestRight()  # find the next rightmost column in topRow

        ALL_ALIENS.remove(alien)  # remove the alien from ALL_ALIENS
        pygame.mixer.music.load(ALIEN_DEATH_MUSIC)  # play death music for the alien
        pygame.mixer.music.play(0)

    def isTouchingAliens(self):
        '''if the bullet is touching an alien'''
        global ALIEN_FARTHEST_LEFT, ALIEN_FARTHEST_RIGHT, ALIEN_DEATH_MUSIC, ALL_ALIENS_NOT_DEAD
        for alien in ALL_ALIENS:  # looking at each alien in the system
            pos = self.canvas.coords(self.id)
            alien_pos = alien.getPos()
            if len(pos) > 0 and len(alien_pos) > 0:
                # if either position that is called is not nothing
                if pos[0] >= alien_pos[0] - 20 and pos[0] <= alien_pos[0] + 20 and pos[1] <= alien_pos[1] + 20 and pos[
                    1] >= alien_pos[1] - 20:
                    # if the x0, y0 of the bullet is in range of the alien
                    self.updateAfterRemove(alien)
                    break

                if pos[2] >= alien_pos[0] - 20 and pos[2] <= alien_pos[0] + 20 and pos[3] <= alien_pos[1] + 20 and pos[
                    3] >= alien_pos[1] - 20:
                    # if the x1, y1 of the bullet is in range of the alien
                    self.updateAfterRemove(alien)
                    break


class AlienBullet:
    '''A class for the bullets that will be shot by the aliens which can destory the blockers and the paddle'''
    def __init__(self, canvas, color, x1, y1, x2, y2):
        global ALIEN_BULLET_SPEED
        self.canvas = canvas
        self.paddle = paddle
        self.id = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')

        self.y = ALIEN_BULLET_SPEED
        self.canvas_height = canvas.winfo_height()
        self.canvas_width = canvas.winfo_width()

    def getID(self):
        '''gets the ID of each of the Alien bullets'''
        return self.id

    def kms(self):
        '''will delete each bullet once it is toucing the blocker or the paddle... also subtract the number of alien bullets by1'''
        global alien_bullet_counter
        self.canvas.delete(self.id)
        alien_bullet_counter -= 1

    def draw(self):
        '''makes the bullets move out from the alien... if the bullet reaches the bottom of the screen it will be deleted '''
        global alien_bullet_counter
        if len(ALIEN_BULLETS) > 0:
            self.canvas.move(self.id, 0, self.y)
        if self.isAtBottom():
            self.canvas.delete(self.id)
            alien_bullet_counter -= 1

    def isAtBottom(self):
        '''the bullet is at the bottom of the screen... used for draw above'''
        pos = self.canvas.coords(self.id)
        if len(pos) > 0:
            return pos[3] >= 630

    def isTouchingBlocks(self):
        '''if the bullet touches the block once moved it will subtract a life from the block'''
        for block in ALL_BLOCKS:
            pos = self.canvas.coords(self.id)
            block_pos = block.getPos()
            if len(block_pos) > 0 and len(pos) > 0:
                if pos[0] >= block_pos[0] and pos[0] <= block_pos[2] and pos[1] >= block_pos[1]:
                    self.kms()
                    block.subtractLives()
                    break
                if pos[2] >= block_pos[0] and pos[2] <= block_pos[2] and pos[3] >= block_pos[1]:
                    self.kms()
                    block.subtractLives()
                    break

    def isTouchingPaddle(self):
        '''if the bullet touches the block once moved it will subtract a life from the paddle... if this happens
        it will make a animation to show that it has been hit and then move the paddle to the middle if the screen'''
        global lives, lives_num, GAME_ON
        pos = self.canvas.coords(self.id)
        paddle_pos_1 = paddle.getID()
        paddle_pos_2 = paddle.getID2()
        paddle_pos_3 = paddle.getID3()
        paddle_pos_4 = paddle.getID4()
        if len(paddle_pos_1) > 0 and len(pos) > 0:
            if pos[0] >= paddle_pos_1[0] and pos[0] <= paddle_pos_1[2] and pos[1] >= paddle_pos_1[1]:
                self.kms()
                lives -= 1
                if lives == 0:
                    paddle.unBind()
                    GAME_ON = False
                else:
                    paddle.center()
                    self.canvas.itemconfigure(lives_num, text=str(lives))
            elif pos[2] >= paddle_pos_2[0] and pos[2] <= paddle_pos_2[2] and pos[3] >= paddle_pos_2[1]:
                self.kms()
                lives -= 1
                if lives == 0:
                    paddle.unBind()
                    GAME_ON = False
                else:
                    paddle.center()
                    self.canvas.itemconfigure(lives_num, text=str(lives))
            elif pos[2] >= paddle_pos_3[0] and pos[2] <= paddle_pos_3[2] and pos[3] >= paddle_pos_3[1]:
                self.kms()
                lives -= 1
                if lives == 0:
                    paddle.unBind()
                    GAME_ON = False
                else:
                    paddle.center()
                    self.canvas.itemconfigure(lives_num, text=str(lives))
            else:
                if pos[2] >= paddle_pos_4[0] and pos[2] <= paddle_pos_4[2] and pos[3] >= paddle_pos_4[1]:
                    self.kms()
                    lives -= 1
                    if lives == 0:
                        paddle.unBind()
                        GAME_ON = False
                    else:
                        paddle.center()
                        self.canvas.itemconfigure(lives_num, text=str(lives))


class Paddle:
    '''A class that makes 4 different rectangles that will move at the same time to create the shooter'''
    def __init__(self, canvas, color):
        self.canvas = canvas
        x1 = 325
        x2 = 375
        self.id = canvas.create_rectangle(x1, canvas_height - 90, x2, canvas_height - 100, fill=color, outline='')
        self.id2 = canvas.create_rectangle(x1 + 5, canvas_height - 100, x2 - 5, canvas_height - 105, fill=color,
                                           outline='')
        self.id3 = canvas.create_rectangle(x1 + 19, canvas_height - 105, x2 - 19, canvas_height - 110, fill=color,
                                           outline='')
        self.id4 = canvas.create_rectangle(x1 + 23, canvas_height - 110, x2 - 23, canvas_height - 113, fill=color,
                                           outline='')

        self.ball = None
        self.moveLeft = False
        self.moveRight = False

        self.x = 0
        self.canvas_width = canvas.winfo_width()

        #if the keys are left or right the paddle will react accordingly
        self.canvas.bind_all('<Left>', self.isLeft)
        self.canvas.bind_all('<Right>', self.isRight)
        self.canvas.bind_all('<KeyRelease-Left>', self.noLeft)
        self.canvas.bind_all('<KeyRelease-Right>', self.noRight)
        self.canvas.bind_all('<KeyPress-space>', self.shoot)


    def unBind(self):
        '''when the paddle loses all of its lives each type of movement will be disabled to eliminate any errors
        that could occur when typing your name'''
        self.canvas.unbind_all('<Left>')
        self.canvas.unbind_all('<Right>')
        self.canvas.unbind_all('<KeyRelease-Left>')
        self.canvas.unbind_all('<KeyRelease-Right>')
        self.canvas.unbind_all('<KeyPress-space>')

    def center(self):
        '''when the paddle is hit by an alien bullet it will make an animation, sound, and move back to the center'''
        global SPACE_SHIP_EXPLOSION
        pygame.mixer.music.load(SPACE_SHIP_EXPLOSION)
        pygame.mixer.music.play(0)
        for i in range(3):
            self.canvas.itemconfigure(self.id, fill='black')
            self.canvas.itemconfigure(self.id2, fill='black')
            self.canvas.itemconfigure(self.id3, fill='black')
            self.canvas.itemconfigure(self.id4, fill='black')
            master.update()
            master.update_idletasks()
            time.sleep(.25)
            self.canvas.itemconfigure(self.id, fill='red')
            self.canvas.itemconfigure(self.id2, fill='red')
            self.canvas.itemconfigure(self.id3, fill='red')
            self.canvas.itemconfigure(self.id4, fill='red')
            master.update()
            master.update_idletasks()
            time.sleep(.25)

        #deletes all of the alien bullets so that you cannot be killed once you get put back into the game
        for bullet in ALIEN_BULLETS:
            canvas.delete(bullet.getID())
            canvas.delete(bullet)
        ALIEN_BULLETS.clear()
        for bullet in BALL_OBJ:
            canvas.delete(bullet.getID())
            canvas.delete(bullet)
        BALL_OBJ.clear()
        for mystery in SAUCER:
            canvas.delete(mystery.getID())
            canvas.delete(mystery)

        pos1 = self.getID()
        pos2 = self.getID2()
        pos3 = self.getID3()
        pos4 = self.getID4()

        #moves each of the pieces of the paddle to the center
        self.canvas.move(self.id, 350 - pos1[0] - 25, 0)
        self.canvas.move(self.id2, 350 - pos2[0] + 5 - 25, 0)
        self.canvas.move(self.id3, 350 - pos3[0] + 19 - 25, 0)
        self.canvas.move(self.id4, 350 - pos4[0] + 23 - 25, 0)
        master.update()
        master.update_idletasks()
        time.sleep(.5)

    def getID(self):
        '''get the ID of the first piece of the paddle'''
        return self.canvas.coords(self.id)

    def getID2(self):
        '''gets the ID of the second piece of the paddle'''
        return self.canvas.coords(self.id2)

    def getID3(self):
        '''gets the ID of the third piece of the paddle'''
        return self.canvas.coords(self.id3)

    def getID4(self):
        '''gets the ID of the fourth piece of the paddle'''
        return self.canvas.coords(self.id4)

    def getBall(self):
        '''gets the ball of the paddle'''
        return self.ball

    def setBall(self, info):
        '''sets the ball to the proper location (on the paddle)'''
        self.ball = info

    def noRight(self, cause):
        '''can't move right'''
        self.moveRight = False

    def noLeft(self, cause):
        '''can't move left '''
        self.moveLeft = False

    def isLeft(self, cause):
        '''when the paddle is ging Left moveLeft is True'''
        self.moveLeft = True
        self.moveRight = False
        self.x = -5

    def isRight(self, cause):
        '''when the paddle is going Right moveRight is True'''
        self.moveRight = True
        self.moveLeft = False
        self.x = 5

    def touchingRightEdge(self):
        '''The position of the paddle is the farthest right'''
        pos = self.canvas.coords(self.id)
        return pos[2] >= canvas_width

    def touchingLeftEdge(self):
        '''The position of the paddle is the farthest Left'''
        pos = self.canvas.coords(self.id)
        return pos[0] <= 0

    def draw(self):
        if self.moveRight == True and not self.touchingRightEdge():
            self.canvas.move(self.id, self.x, 0)
            self.canvas.move(self.id2, self.x, 0)
            self.canvas.move(self.id3, self.x, 0)
            self.canvas.move(self.id4, self.x, 0)

        if self.moveLeft == True and not self.touchingLeftEdge():
            self.canvas.move(self.id, self.x, 0)
            self.canvas.move(self.id2, self.x, 0)
            self.canvas.move(self.id3, self.x, 0)
            self.canvas.move(self.id4, self.x, 0)

    def shoot(self, cause):
        '''will shoot the bullet out of the paddle's position and make a noise... could ave it print the
        location'''
        global BULLET_SHOOT_MUSIC
        pos = self.canvas.coords(self.id3)
        # print(pos)
        if len(BALL_OBJ) == 0:
            self.ball = Ball(self.canvas, self, 'green', pos[0] + 5, pos[1] - 17, pos[2] - 5, pos[3] - 10)
            BALL_OBJ.append(self.ball)
            pygame.mixer.music.load(BULLET_SHOOT_MUSIC)
            pygame.mixer.music.play(0)


class Alien:
    def __init__(self, canvas, x1, y1, x2, y2, pointValue, type):
        global ALIEN10_SMALL, ALIEN20_SMALL, ALIEN40_SMALL, ALIEN_SPEED_X, ALIEN_SPEED_Y
        if type == 0:
            self.id = canvas.create_image(x1 + (x2 - x1), y1 + (y2 - y1), image=ALIEN40_SMALL)
        if type == 1:
            self.id = canvas.create_image(x1 + (x2 - x1), y1 + (y2 - y1), image=ALIEN20_SMALL)
        if type == 2:
            self.id = canvas.create_image(x1 + (x2 - x1), y1 + (y2 - y1), image=ALIEN10_SMALL)
        self.pointValue = pointValue
        self.canvas = canvas
        self.movement = False
        self.bullet = None
        self.x = ALIEN_SPEED_X
        self.y = ALIEN_SPEED_Y

    def move(self):
        global ALIEN_FARTHEST_LEFT, ALIEN_FARTHEST_RIGHT, alien_shooting_odds, GAME_ON, ALIEN_SPEED_X, ALIEN_SPEED_Y
        odds = random.randint(0, alien_shooting_odds)
        if ALIEN_FARTHEST_RIGHT.getTop() != None and self.touchingRightEdge(ALIEN_FARTHEST_RIGHT.getTop()):
            self.x *= -1
            self.canvas.move(self.id, self.x, self.y)
            if self.isPast():
                GAME_ON = False
                paddle.unBind()
            self.x = -ALIEN_SPEED_X
        elif ALIEN_FARTHEST_LEFT.getTop() != None and self.touchingLeftEdge(ALIEN_FARTHEST_LEFT.getTop()):
            self.x *= -1
            self.canvas.move(self.id, self.x, self.y)
            if self.isPast():
                GAME_ON = False
                paddle.unBind()
            self.x = ALIEN_SPEED_X
        else:
            self.canvas.move(self.id, self.x, 0)
        if odds == 1:
            self.shoot()

    def touchingRightEdge(self, alien):
        pos = alien.getPos()
        if len(pos) > 0:
            return pos[0] + 20 >= canvas_width

    def touchingLeftEdge(self, alien):
        pos = alien.getPos()
        if len(pos) > 0:
            return pos[0] - 20 < 0

    def getLowest(self):
        allPos = []
        for alien in ALL_ALIENS:
            pos = alien.getPos()
            if len(pos) > 1:
                allPos.append(pos[1] + 20)
        low = allPos.index(max(allPos))
        return ALL_ALIENS[low]

    def isPast(self):
        pos = self.getLowest().getPos()
        if pos[1] + 20 >= 540:
            return True

    def getPos(self):
        return self.canvas.coords(self.id)

    def getID(self):
        return self.id

    def kill(self):
        global updateScore, TOTAL_ALIEN, ALL_ALIENS_NOT_DEAD
        updateScore(self.pointValue)
        TOTAL_ALIEN -= 1
        if TOTAL_ALIEN == 0:
            ALL_ALIENS_NOT_DEAD = False

    def shoot(self):
        global alien_bullet_counter
        global MAX_ALIEN_BULLETS
        pos = self.canvas.coords(self.id)
        if alien_bullet_counter <= MAX_ALIEN_BULLETS and len(pos) > 0:
            self.bullet = AlienBullet(self.canvas, 'white', pos[0] + 1.5, pos[1] + 20, pos[0] - 1.5, pos[1] + 35)
            alien_bullet_counter += 1
            ALIEN_BULLETS.append(self.bullet)


class AlienColumn:
    def __init__(self, canvas):
        self.top = None  # highest value in the column
        self.canvas = canvas
        self.allAliens = []  # all aliens in the column

    def reset(self):
        '''reseting the column to a default state'''
        self.top = None
        self.allAliens.clear()

    def getAliens(self):
        return self.allAliens

    def getTop(self):
        return self.top

    def getPos(self):
        '''retuns the postion of any alien'''
        if len(self.allAliens) > 0:
            return self.allAliens[0].getPos()

    def addAlien(self, alien):
        '''adds aliens to the column'''
        if len(self.allAliens) == 0:
            self.top = alien  # the first one is always the top
            self.allAliens.append(alien)
        else:
            self.allAliens.append(alien)  # every other item is added to the list

    def findHighest(self):
        '''finding the highest alien in the column'''
        if ALL_ALIENS_NOT_DEAD:
            allPos = []
            for alien in self.allAliens:  # adding all the y1 positions to the list allpos
                pos = alien.getPos()
                if len(pos) > 0:
                    allPos.append(pos[1])
            if len(allPos) > 0:
                low = allPos[0]
                for val in allPos:  # sorting through and finding the lowest value
                    if val < low:
                        low = val
                point = allPos.index(low)
                self.top = self.allAliens[point]  # setting the top to the highest alien


class AlienRow:
    def __init__(self, canvas):
        self.front = None  # left most AlienColumn
        self.back = None  # right most AlienColumn
        self.canvas = canvas
        self.allAliens = []  # all AlienColumns

    def reset(self):
        '''sets the AlienRow back to a default state'''
        self.front = None
        self.back = None
        self.allAliens.clear()

    def getAliens(self):
        return self.allAliens

    def getLeft(self):
        return self.front

    def getRight(self):
        return self.back

    def addAlien(self, column):
        '''adding aliens to the list'''
        global ALIEN_FARTHEST_LEFT, ALIEN_FARTHEST_RIGHT
        if len(self.allAliens) == 0:
            self.front = column
            ALIEN_FARTHEST_LEFT = self.front  # setting the the global to the leftmost column
            self.back = column
            self.allAliens.append(column)
        else:
            self.back = column  # setting each adding column to the back
            ALIEN_FARTHEST_RIGHT = self.back  # setting the the global to the rightmost column
            self.allAliens.append(column)

    def findFarthestLeft(self):
        '''finding the leftmost column'''
        global ALIEN_FARTHEST_LEFT, ALL_ALIENS_NOT_DEAD
        if ALL_ALIENS_NOT_DEAD:
            allPos = []
            for alien in self.allAliens:  # adding all the positions of the columns to the list
                pos = alien.getPos()
                if len(pos) > 1:
                    allPos.append(pos[0] - 20)
            if len(allPos) > 0:  # sorting through and finding the lowest value to find the highest alien
                low = allPos[0]
                for val in allPos:
                    if val < low:
                        low = val
                point = allPos.index(low)
                self.front = self.allAliens[point]
                ALIEN_FARTHEST_LEFT = self.front  # setting the the global to the leftmost column
                ALIEN_FARTHEST_LEFT.findHighest()  # setting the top of the column

    def findFarthestRight(self):
        '''finding the rightmost column'''
        global ALIEN_FARTHEST_RIGHT, ALL_ALIENS_NOT_DEAD
        if ALL_ALIENS_NOT_DEAD:
            allPos = []
            for alien in self.allAliens:  # adding all the positions of the columns to the list
                pos = alien.getPos()
                if len(pos) > 1:
                    allPos.append(pos[0] + 20)
            if len(allPos) > 0:
                high = allPos[0]
                for val in allPos:  # sorting through and finding the highest value to find the lowest alien
                    if val > high:
                        high = val
                high = allPos.index(high)
                self.back = self.allAliens[high]
                ALIEN_FARTHEST_RIGHT = self.back  # setting the the global to the rightmost column
                ALIEN_FARTHEST_RIGHT.findHighest()  # setting the top of the column


class Mystery:
    def __init__(self, canvas):
        global ALIEN_SAUCER_SMALL, ALIEN_SAUCER_MUSIC, MYSTERY_SPEED
        self.canvas = canvas
        self.leftRight = random.randint(0, 1)
        self.possiblePoints = [150, 200, 300]
        if self.leftRight == 0:
            self.id = canvas.create_image(-40, 130, image=ALIEN_SAUCER_SMALL)
            self.x = MYSTERY_SPEED
            pygame.mixer.music.load(ALIEN_SAUCER_MUSIC)
            pygame.mixer.music.play(0)
        elif self.leftRight == 1:
            self.id = canvas.create_image(740, 130, image=ALIEN_SAUCER_SMALL)
            self.x = -MYSTERY_SPEED
            pygame.mixer.music.load(ALIEN_SAUCER_MUSIC)
            pygame.mixer.music.play(0)
        else:
            canvas.delete(self)

    def getID(self):
        return self.id

    def move(self):
        self.canvas.move(self.id, self.x, 0)
        pos = self.canvas.coords(self.id)
        if len(pos) > 0:
            if self.leftRight == 0 and pos[0] > 740:
                self.canvas.delete(self.id)
                SAUCER.remove(self)
            if self.leftRight == 1 and pos[0] < -40:
                self.canvas.delete(self.id)
                SAUCER.remove(self)

    def getPos(self):
        return self.canvas.coords(self.id)

    def addPoints(self):
        global ALIEN_SAUCER_DEATH
        global updateScore
        updateScore(self.possiblePoints[random.randint(0, 2)])
        self.canvas.delete(self.id)
        pygame.mixer.music.load(ALIEN_SAUCER_DEATH)
        pygame.mixer.music.play(0)
        SAUCER.clear()


class Blockers:
    def __init__(self, canvas, x1, y1, x2, y2):
        self.canvas = canvas
        self.lives = 4
        self.id = canvas.create_rectangle(x1, y1, x2, y2, outline='', fill='dark green')
        self.label = canvas.create_text(x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 2, fill='white', text=self.lives,
                                        font=("Cosmic Alien", 15))

    def getPos(self):
        return self.canvas.coords(self.id)

    def getBlock(self):
        return self.id

    def subtractLives(self):
        self.lives -= 1
        if self.lives == 0:
            self.canvas.delete(self.id)
            self.canvas.delete(self.label)
        else:
            self.canvas.itemconfigure(self.label, text=self.lives)


class TextInputer:
    def __init__(self, label, x, y):
        self.string = ''
        self.text = label.create_text(x, y, fill='green', text='Enter Your Name ', font=("Cosmic Alien", 20))
        self.id = label.create_text(x, y + 30, fill='white', text=self.string, font=("Cosmic Alien", 25))

        self.label = label
        self.continueTyping = True

        self.label.bind("<a>", self.addText)
        self.label.bind("<b>", self.addText)
        self.label.bind("<c>", self.addText)
        self.label.bind("<d>", self.addText)
        self.label.bind("<e>", self.addText)
        self.label.bind("<f>", self.addText)
        self.label.bind("<g>", self.addText)
        self.label.bind("<h>", self.addText)
        self.label.bind("<i>", self.addText)
        self.label.bind("<j>", self.addText)
        self.label.bind("<k>", self.addText)
        self.label.bind("<l>", self.addText)
        self.label.bind("<m>", self.addText)
        self.label.bind("<n>", self.addText)
        self.label.bind("<o>", self.addText)
        self.label.bind("<p>", self.addText)
        self.label.bind("<q>", self.addText)
        self.label.bind("<r>", self.addText)
        self.label.bind("<s>", self.addText)
        self.label.bind("<t>", self.addText)
        self.label.bind("<u>", self.addText)
        self.label.bind("<v>", self.addText)
        self.label.bind("<w>", self.addText)
        self.label.bind("<x>", self.addText)
        self.label.bind("<y>", self.addText)
        self.label.bind("<z>", self.addText)
        self.label.bind("<Key-space>", self.addText)
        self.label.bind("<Return>", self.addText)
        self.label.bind("<BackSpace>", self.addText)

        self.label.focus_set()

    def getString(self):
        return self.string

    def removeText(self):
        self.label.delete(self.id)
        self.label.delete(self.text)

    def addText(self, event):
        global USER_NAME, USER_INPUTTING_NAME
        if event.keysym == 'Return':
            self.continueTyping = False
            USER_INPUTTING_NAME = False
            USER_NAME = self.string
        elif event.keysym == 'BackSpace':
            temp = ''
            for i in range(0, len(self.string) - 1):
                temp += self.string[i]
            self.string = temp
        else:
            if len(self.string) < 10 and self.continueTyping:
                if event.keysym == 'space':
                    self.string += ' '
                else:
                    self.string += str(event.keysym)
        # print(self.string)
        self.label.itemconfigure(self.id, text=self.string)


master = Tk()
master.title('Space Invaders')
canvas_width = 700
canvas_height = 700
canvas = Canvas(master, width=canvas_width, height=canvas_height, bg='black', bd=0, highlightthickness=0)
canvas.grid(row=0, column=0)
GAME_ON = True
TOTAL_ALIEN = 0
ALL_ALIENS_NOT_DEAD = True
GAME_SCORE = 0
NO_CHEATS = True  # for non-penetrating bullets use True
lives = 3  # default is 3
POINTS_10 = 10  # points for bottom 2 aliens
POINTS_20 = 20  # points for upper 2 aliens
POINTS_40 = 40  # points for medium aliens
MAX_ALIEN_BULLETS = 6  # default is 3
alien_bullet_counter = 0
alien_shooting_odds = 1000  # default is 4000
ALIEN_SPEED_X = .5  # default is .5
ALIEN_SPEED_Y = 20  # default is 20
ALIEN_BULLET_SPEED = 5  # default is 5
BULLET_SPEED = -12  # default is -12
MYSTERY_SPEED = 2
WAVE = 1
topRow = AlienRow(canvas)
BALL_OBJ = []
ALL_ALIENS = []
ALL_BLOCKS = []
ALIEN_FARTHEST_LEFT = None
ALIEN_FARTHEST_RIGHT = None
SAUCER = []
ALIEN_BULLETS = []


BACKGROUND = PhotoImage(file="images/ring.gif")
ALIEN10_SMALL = PhotoImage(
    file="images/small.gif")
ALIEN20_SMALL = PhotoImage(file="images/20small.gif")
ALIEN40_SMALL = PhotoImage(file="images/40small.gif")
ALIEN_SAUCER_LARGE = PhotoImage(file="images/mysteryphoto.gif")
ALIEN_SAUCER_DEATH = 'sounds/mysterykilled .wav'
ALIEN_SAUCER_SMALL = PhotoImage(file="images/mysteryfinal.gif")
ALIEN_SAUCER_MUSIC = 'sounds/mysteryenteredcopy.wav'
ALIEN_DEATH_MUSIC = 'sounds/shipexplosion.wav'
BULLET_SHOOT_MUSIC = 'sounds/playershoot.wav'
SPACE_SHIP_EXPLOSION = 'sounds/shipexplosion.wav'

canvas.pack()
paddle = Paddle(canvas, 'red')

pygame.mixer.music.load(ALIEN_SAUCER_MUSIC)
pygame.mixer.music.play(0)
canvas.pack()

top_border_line = canvas.create_line(0, canvas_height - 74, canvas_width, canvas_height - 74, fill='green', width=4)
bottom_border_line = canvas.create_line(0, 105, canvas_width, 105, fill='green', width=4)

title_text = canvas.create_text(360, 30, fill='green', text="SPACE INVADERS", font=("Cosmic Alien", 30))
authors_text = canvas.create_text(360, 50, fill='white', text="Teddy Lazar, Josh Dresner, Viraj Lunani",
                                  font=("Cosmic Alien", 10))
score_text = canvas.create_text(80, 80, fill='white', text="score", font=("Cosmic Alien", 20))
score_num_text = canvas.create_text(160, 80, fill='green', text=str(GAME_SCORE), font=("Cosmic Alien", 20))
lives_text = canvas.create_text(350, 80, fill='white', text="lives  ", font=("Cosmic Alien", 20))
lives_num = canvas.create_text(390, 80, fill='green', text=str(lives), font=("Cosmic Alien", 20))


def spawnAliens():
    global ALIEN_FARTHEST_RIGHT, ALIEN_FARTHEST_LEFT, TOTAL_ALIEN, POINTS_10, POINTS_20, POINTS_40
    points = 0
    type = 0
    for x in range(10, 510, 50):
        column = AlienColumn(canvas)
        for y in range(120, 360, 50):
            if y == 120:
                type = 0
                points = POINTS_40
            if y == 170 or y == 220:
                type = 1
                points = POINTS_20
            if y == 270 or y == 320:
                type = 2
                points = POINTS_10
            temp_alien = Alien(canvas, x, y, x + 40, y + 40, points, type)
            TOTAL_ALIEN += 1
            ALL_ALIENS.append(temp_alien)
            column.addAlien(temp_alien)
        topRow.addAlien(column)
    master.update_idletasks()
    master.update()


def spawnBlocks(x):
    num = x
    for y in range(500, 560, 20):
        for x in range(num, num + 80, 20):
            if y == 540:
                if x == num or x == num + 60:
                    ALL_BLOCKS.append(Blockers(canvas, x, y, x + 20, y + 20))
            else:
                ALL_BLOCKS.append(Blockers(canvas, x, y, x + 20, y + 20))
    master.update_idletasks()
    master.update()


def updateScore(num):
    global GAME_SCORE
    GAME_SCORE += num
    canvas.itemconfigure(score_num_text, text=GAME_SCORE)


def acceleration():
    global ALIEN_SPEED_X, ALIEN_SPEED_Y, MAX_ALIEN_BULLETS, alien_shooting_odds, TOTAL_ALIEN, WAVE, MYSTERY_SPEED
    timer = round(time.clock(), 1)
    if timer > 0 and timer % 3.0 == 0:
        ALIEN_SPEED_X += .02
    MYSTERY_SPEED = ALIEN_SPEED_X + 2


def nextWave():
    global lives, ALIEN_FARTHEST_RIGHT, ALIEN_FARTHEST_LEFT, ALL_ALIENS_NOT_DEAD, ALIEN_SPEED_X, WAVE, MYSTERY_SPEED
    global MAX_ALIEN_BULLETS, alien_shooting_odds
    for bullet in ALIEN_BULLETS:
        canvas.delete(bullet.getID())
        canvas.delete(bullet)
    ALIEN_BULLETS.clear()
    for bullet in BALL_OBJ:
        canvas.delete(bullet.getID())
        canvas.delete(bullet)
    BALL_OBJ.clear()
    ALIEN_FARTHEST_LEFT = None
    ALIEN_FARTHEST_RIGHT = None
    ALL_ALIENS.clear()
    for mystery in SAUCER:
        canvas.delete(mystery.getID())
        canvas.delete(mystery)
    SAUCER.clear()
    topRow.reset()
    master.update_idletasks()
    master.update()
    lives += 1
    WAVE += 1
    ALIEN_SPEED_X = .5
    ALIEN_SPEED_X += WAVE / 100 + WAVE / 100
    MYSTERY_SPEED = ALIEN_SPEED_X + 1.5
    if WAVE % 3 == 0:
        MAX_ALIEN_BULLETS += 1
    if WAVE <= 5:
        alien_shooting_odds -= 150
    spawnAliens()
    canvas.itemconfig(lives_num, text=lives)
    ALL_ALIENS_NOT_DEAD = True
    time.sleep(1)


spawnBlocks(50)
spawnBlocks(220)
spawnBlocks(390)
spawnBlocks(560)
spawnAliens()

while GAME_ON:
    if ALL_ALIENS_NOT_DEAD is False:
        nextWave()
    else:
        timer = int(time.clock()) / 2
        time10 = int(time.clock())
        paddle.draw()
        acceleration()
        if time10 % 10 == 0 and len(SAUCER) == 0 and time10 >= 5:
            SAUCER.append(Mystery(canvas))
        for item in SAUCER:
            item.move()
        for bullet in ALIEN_BULLETS:
            bullet.draw()
            bullet.isTouchingBlocks()
            bullet.isTouchingPaddle()
        for ball in BALL_OBJ:
            ball.draw()
            ball.isTouchingBlocks()
            if ALL_ALIENS_NOT_DEAD:
                ball.isTouchingAliens()
            ball.isTouchingSaucer()
        if timer % 0.5 == 0:
            for alien in ALL_ALIENS:
                if ALL_ALIENS_NOT_DEAD and TOTAL_ALIEN > 0 and alien != None:
                    alien.move()
    master.update_idletasks()
    master.update()
    time.sleep(.01)

print('OoPs!?! U tOoK An L SoN :/')
for i in canvas.find_all():
    if i != title_text:
        canvas.delete(i)
        master.update_idletasks()
        master.update()

canvas_pos = canvas.coords(title_text)
while canvas_pos[1] < 175:
    canvas.move(title_text, 0, 3)
    master.update_idletasks()
    master.update()
    canvas_pos = canvas.coords(title_text)
game_over_text = canvas.create_text(350, 225, fill='white', text="GAME OVER", font=("Cosmic Alien", 20))
EnterName = TextInputer(canvas, 350, 300)

USER_NAME = ''
USER_NAME_10 = ''
USER_INPUTTING_NAME = True
while USER_INPUTTING_NAME:
    canvas.pack()
    master.update_idletasks()
    master.update()
print(USER_NAME + ' ' + str(GAME_SCORE))
EnterName.removeText()
title_pos = canvas.coords(title_text)
while title_pos[1] > 100:
    canvas.move(title_text, 0, -3)
    canvas.move(game_over_text, 0, -3)
    master.update_idletasks()
    master.update()
    title_pos = canvas.coords(title_text)

canvas.create_line(200, 200, 200, 520, fill='green', width=4)
canvas.create_line(500, 200, 500, 520, fill='green', width=4)
canvas.create_line(200, 200, 500, 200, fill='green', width=4)
canvas.create_line(200, 520, 500, 520, fill='green', width=4)

score_board_score = []
score_board_names = []
with open('HighScore.txt', 'r') as my_file:
    count = 0
    for line in my_file:
        if count == 0:
            score_board_score = eval(line)
        else:
            score_board_names = eval(line)
        count += 1
    USER_NAME_10 = USER_NAME
    while len(USER_NAME_10) < 10:
        USER_NAME_10 += ' '
    score_board_score.append(GAME_SCORE)
    score_board_names.append(USER_NAME_10)


def writeData(sorted_score_board):
    scores = []
    names = []
    for i in range(0, len(sorted_score_board), 2):
        scores.append(sorted_score_board[i])
        names.append(sorted_score_board[i + 1])
    with open("HighScore.txt", "w") as f:
        f.write(str(scores))
        f.write("\n")
        f.write(str(names))


def sorter(scores, names):
    name_with_score = []
    n = max(scores) + 1
    while n > 0:
        for i in range(len(scores)):
            if scores[i] == n:
                name_with_score.append(scores[i])
                name_with_score.append(names[i])
                scores[i] = -1
        n = n - 1
    return name_with_score


sorted_score_board = sorter(score_board_score, score_board_names)
count = 0
del_key = None
if len(sorted_score_board) > 10:
    for i in range(0, len(sorted_score_board), 2):
        if count == 10:
            del sorted_score_board[21]
            del sorted_score_board[20]
        count += 1

x = 220
for i in range(0, len(sorted_score_board), 2):
    canvas.create_text(280, x, fill='white', text=sorted_score_board[i + 1], font=("Cosmic Alien", 20))
    canvas.create_text(440, x, fill='green', text=sorted_score_board[i], font=("Cosmic Alien", 20))
    x = x + 30
    master.update_idletasks()
    master.update()

canvas.create_text(300, 550, fill='white', text='User Name:   ', font=("Cosmic Alien", 20))
canvas.create_text(450, 550, fill='green', text=USER_NAME, font=("Cosmic Alien", 20))

canvas.create_text(300, 580, fill='white', text='User Score:  ', font=("Cosmic Alien", 20))
canvas.create_text(430, 580, fill='green', text=GAME_SCORE, font=("Cosmic Alien", 20))

master.update_idletasks()
master.update()

writeData(sorted_score_board)

show_leader_board = True


def onKeyPress(event):
    global show_leader_board
    show_leader_board = False


canvas.bind("<Return>", onKeyPress)
x = 2
exit_text = canvas.create_text(350, 650, fill='green', text='Click Enter to Exit', font=("Cosmic Alien", 20))
colors = ['green yellow', 'medium sea green', 'lawn green', 'lime green', 'sea green', 'forest green',
          'dark olive green',
          'chartreuse', 'medium spring green', 'yellow green', 'pale green', 'green']
while show_leader_board:
    exit_text_pos = canvas.coords(exit_text)
    if exit_text_pos[0] >= 550:
        x *= -1
        canvas.itemconfigure(exit_text, fill=colors[random.randint(0, len(colors) - 1)])
        canvas.move(exit_text, x, 0)
    if exit_text_pos[0] <= 150:
        canvas.itemconfigure(exit_text, fill=colors[random.randint(0, len(colors) - 1)])
        x *= -1
        canvas.move(exit_text, x, 0)
    canvas.move(exit_text, x, 0)
    master.update_idletasks()
    master.update()

exit()
