import pygame
import sys
import random
from pygame.locals import *

FPS = 30
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
REVEAL_SPEED = 8
BOX_SIZE = 40
GAP_SIZE = 10
BOARD_WIDTH = 10
BOARD_HEIGHT = 7
X_MARGIN = int((WINDOW_WIDTH-(BOARD_WIDTH*(BOX_SIZE+GAP_SIZE)))/2)
Y_MARGIN = int((WINDOW_HEIGHT-(BOARD_HEIGHT*(BOX_SIZE+GAP_SIZE)))/2)

assert (BOARD_WIDTH*BOARD_HEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches'

GRAY = (100, 100, 100)
NAVY_BLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

BGCOLOR = NAVY_BLUE
LIGHT_BGCOLOR = GRAY
BOX_COLOR = WHITE
HIGHLIGHT_COLOR = BLUE

DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALL_COLORS = (RED, GREEN, BLUE, CYAN, YELLOW, ORANGE, PURPLE)
ALL_SHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)

assert len(ALL_COLORS)*len(ALL_SHAPES)*2 >= BOARD_WIDTH * \
    BOARD_HEIGHT, 'Board is too small for the number of shapes/colors defined.'


def main():
    global DISPLAY_SURF, FPS_CLOCK
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Memory Game')
    mousex = 0
    mousey = 0
    firstSelection = None
    mainBoard = getRandomizeBoard()
    revealedBoxes = generateRevealedBoxesData(False)
    DISPLAY_SURF.fill(BGCOLOR)
    startGameAnimation(mainBoard)

    while True:
        mouseClicked = False
        DISPLAY_SURF.fill(BGCOLOR)
        drawBoard(mainBoard, revealedBoxes)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True
        boxx, boxy = getBoxAndPixel(mousex, mousey)
        if boxx != None and boxy != None:
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealedBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True
                if firstSelection == None:
                    firstSelection = (boxx, boxy)
                else:
                    icon1shape, icon1color = getShapeAndColor(
                        mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(
                        mainBoard, boxx, boxy)
                    if icon1shape != icon2shape or icon1color != icon2color:
                        pygame.time.wait(1000)
                        coveredBoxesAnimation(
                            mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]
                                      ][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif hasWon(revealedBoxes):
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)
                        revealedBoxes = generateRevealedBoxesData(False)
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)
                        startGameAnimation(mainBoard)
                    firstSelection = None
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def hasWon(revealedBoxes):
    for i in revealedBoxes:
        if False in i:
            return False
    return True


def getBoxAndPixel(x, y):
    for boxx in range(BOARD_WIDTH):
        for boxy in range(BOARD_HEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def drawHighlightBox(boxx, boxy):
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAY_SURF, HIGHLIGHT_COLOR,
                     (left-5, top-5, BOX_SIZE+10, BOX_SIZE+10))


def getRandomizeBoard():
    icons = []
    for color in ALL_COLORS:
        for shape in ALL_SHAPES:
            icons.append((shape, color))
    random.shuffle(icons)

    numIconUsed = int(BOARD_WIDTH*BOARD_HEIGHT/2)
    icons = icons[:numIconUsed]*2
    random.shuffle(icons)

    board = []
    for x in range(BOARD_WIDTH):
        column = []
        for y in range(BOARD_HEIGHT):
            column.append(icons[0])
            del icons[0]
        board.append(column)
    return board


def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARD_WIDTH):
        revealedBoxes.append([val]*BOARD_HEIGHT)
    return revealedBoxes


def drawBoard(board, revealed):
    for boxx in range(BOARD_WIDTH):
        for boxy in range(BOARD_HEIGHT):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                pygame.draw.rect(DISPLAY_SURF, BOX_COLOR,
                                 (left, top, BOX_SIZE, BOX_SIZE))
            else:
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)


def leftTopCoordsOfBox(boxx, boxy):
    left = boxx*(BOX_SIZE+GAP_SIZE)+X_MARGIN
    top = boxy*(BOX_SIZE+GAP_SIZE)+Y_MARGIN
    return (left, top)


def getShapeAndColor(board, boxx, boxy):
    return board[boxx][boxy][0], board[boxx][boxy][1]


def drawIcon(shape, color, boxx, boxy):
    quarter = int(BOX_SIZE*0.25)
    half = int(BOX_SIZE*0.5)
    left, top = leftTopCoordsOfBox(boxx, boxy)
    if shape == DONUT:
        pygame.draw.circle(DISPLAY_SURF, color, (left+half, top+half), half-5)
        pygame.draw.circle(DISPLAY_SURF, BGCOLOR,
                           (left+half, top+half), quarter-5)
    elif shape == SQUARE:
        pygame.draw.rect(DISPLAY_SURF, color, (left+quarter,
                                               top+quarter, BOX_SIZE-half, BOX_SIZE-half))
    elif shape == DIAMOND:
        pygame.draw.polygon(DISPLAY_SURF, color, ((
            left+half, top), (left+BOX_SIZE-1, top+half), (left+half, top+BOX_SIZE-1), (left, top+half)))
    elif shape == LINES:
        for i in range(0, BOX_SIZE, 4):
            pygame.draw.line(DISPLAY_SURF, color, (left, top+i), (left+i, top))
            pygame.draw.line(DISPLAY_SURF, color, (left+i,
                                                   top+BOX_SIZE-1), (left+BOX_SIZE-1, top+i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAY_SURF, color,
                            (left, top+quarter, BOX_SIZE, half))


def startGameAnimation(board):
    boxes = []
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            boxes.append((x, y))
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)
    coveredBoxes = generateRevealedBoxesData(False)
    drawBoard(board, coveredBoxes)

    for boxGroup in boxGroups:
        revealedBoxesAnimation(board, boxGroup)
        coveredBoxesAnimation(board, boxGroup)


def splitIntoGroupsOf(groupSize, theList):
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i+groupSize])
    return result


def revealedBoxesAnimation(board, boxesToReveal):
    for coverage in range(BOX_SIZE, (-REVEAL_SPEED)-1, -REVEAL_SPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coveredBoxesAnimation(board, boxesToCover):
    for coverage in range(0, BOX_SIZE+REVEAL_SPEED, REVEAL_SPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoxCovers(board, boxes, coverage):
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAY_SURF, BGCOLOR,
                         (left, top, BOX_SIZE, BOX_SIZE))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0:
            pygame.draw.rect(DISPLAY_SURF, BOX_COLOR,
                             (left, top, coverage, BOX_SIZE))
    pygame.display.update()
    FPS_CLOCK.tick(FPS)


def gameWonAnimation(board):
    coveredBoxs = generateRevealedBoxesData(True)
    color1 = LIGHT_BGCOLOR
    color2 = BGCOLOR
    for i in range(13):
        color1, color2 = color2, color1
        DISPLAY_SURF.fill(color1)
        drawBoard(board, coveredBoxs)
        pygame.display.update()
        pygame.time.wait(300)


if __name__ == '__main__':
    main()
