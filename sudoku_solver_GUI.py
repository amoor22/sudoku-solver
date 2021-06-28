import pygame
from board_generator import generate
from threading import Thread
from time import sleep

pygame.init()

# 1 - 3 (1 easiest and 3 hardest)
difficulty = int(input("Please enter the difficulty (1 - 3): "))
board = generate(difficulty)

screen_width, screen_height = 450, 450
win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Sudoko Solver')

clock = pygame.time.Clock()

font_temp = pygame.font.SysFont('Comic Sans MS', 18)
font_main = pygame.font.SysFont('Comic Sans MS', 30)
backtracking_speed = 10

currently_edited = None


class block:
    def __init__(self):
        self.x = None
        self.y = None
        self.row = None
        self.col = None
        self.color = (255, 255, 255)
        self.width = screen_width // 9
        self.border = 1
        self.border_color = (128, 128, 128)
        self.draw_width = self.width - (self.border * 2)
        self.temp_text = ""
        self.text = ""
        self.tracking = False
        self.backtracking = False
        self.editing = False

    def draw(self, win, x, y, row, col):
        self.x, self.y, self.row, self.col = x, y, row, col
        if board[self.row][self.col] != 0:
            self.text = str(board[self.row][self.col])
        # border
        pygame.draw.rect(win, self.border_color, (self.x, self.y, self.width, self.width))
        # box
        pygame.draw.rect(win, self.color,
                         (self.x + self.border, self.y + self.border, self.draw_width, self.draw_width))
        if self.editing:
            pygame.draw.rect(win, self.border_color, (self.x, self.y, self.width, self.width))
        if self.tracking:
            pygame.draw.rect(win, (0, 255, 0), (self.x, self.y, self.width, self.width))
        if self.backtracking:
            pygame.draw.rect(win, (255, 0, 0), (self.x, self.y, self.width, self.width))

        if self.text != "":
            text_surface = font_main.render(self.text, False, (0, 0, 0))
            win.blit(text_surface, (self.x + ((self.width // 2) - text_surface.get_width() // 2),
                                    self.y + ((self.width // 2) - text_surface.get_height() // 2)))
        elif self.temp_text != "":
            text_surface = font_temp.render(self.temp_text, False, (50, 50, 50))
            win.blit(text_surface, (self.x + (self.border * 2) + 2, self.y))

    def click(self, pos):
        global currently_edited
        mx, my = pos
        if self.x < mx < self.x + self.width:
            if self.y < my < self.y + self.width:
                if currently_edited:
                    currently_edited.editing = False
                currently_edited = self
                self.editing = True

    def set_text(self):
        self.text = self.temp_text
        self.temp_text = ""
        board[self.row][self.col] = int(self.text)
        if valid_board(board):
            light = Thread(target=light_up)
            light.start()


def light_up():
    for i in range(255, -1, -1):
        for blck in blocks:
            blck.color = (i, 255, 0)
        sleep(0.015)
    for i in range(0, 256):
        for blck in blocks:
            blck.color = (i, 255, i)
        sleep(0.015)


blocks = [block() for _ in range(81)]


def solve(bo):
    find = find_empty(bo)
    if not find:
        light = Thread(target=light_up)
        light.start()
        for blck in blocks:
            blck.tracking = False
            blck.backtracking = False
        return True
    else:
        row, col = find
    for i in range(1, 10):
        if valid(bo, i, (row, col)):
            current_block = blocks[get_row_col(row, col)]
            bo[row][col] = i
            current_block.text = str(i)
            current_block.tracking = True
            current_block.backtracking = False
            RedrawGameWindow(blocks)
            clock.tick(backtracking_speed)
            # 2-if we return False this statement won't trigger
            if solve(bo):
                return True
            # 3-and this statement will, which will backtrack
            clock.tick(backtracking_speed * difficulty)
            blocks[get_row_col(row, col)].text = ""
            current_block.tracking = False
            current_block.backtracking = True
            RedrawGameWindow(blocks)
            bo[row][col] = 0
    # 1-if there are no possible solutions after trying 1-9 then return False
    return False


def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)  # row, column
    return None


def valid(bo, num, pos):
    # check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and i != pos[1]:
            return False
    # check column
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and i != pos[0]:
            return False
    # check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if bo[i][j] == num and (i, j) != pos:
                return False
    return True


def valid_board(bo):
    isValid = True
    if not find_empty(bo):
        for row in range(len(bo)):
            for col in range(len(bo[row])):
                if not valid(bo, bo[row][col], (row, col)):
                    return False
    else:
        isValid = False
    return isValid


def draw_blocks(win, blocks):
    x = 0;
    y = 0;
    row = 0;
    col = 0
    for i, blck in enumerate(blocks):
        blck.draw(win, x, y, row, col)
        if (i + 1) % 9 == 0:
            y += blck.width
            x = 0
            col = 0
            row += 1
        else:
            col += 1
            x += blck.width


def draw_bars():
    line_width = 5
    # vertical lines
    pygame.draw.line(win, (0, 0, 0), (screen_width // 3, 0), (screen_width // 3, screen_height), line_width)
    pygame.draw.line(win, (0, 0, 0), (screen_width // 1.5, 0), (screen_width // 1.5, screen_height), line_width)
    # horizontal lines
    pygame.draw.line(win, (0, 0, 0), (0, screen_height // 3), (screen_width, screen_height // 3), line_width)
    pygame.draw.line(win, (0, 0, 0), (0, screen_height // 1.5), (screen_width, screen_height // 1.5), line_width)


def RedrawGameWindow(blocks):
    win.fill(0)
    draw_blocks(win, blocks)
    draw_bars()
    pygame.display.update()


def get_row_col(row, col):
    return (row * 9) + col


def main():
    global currently_edited
    running = True
    while running:
        RedrawGameWindow(blocks)
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                for blck in blocks:
                    blck.click(pos)
            key = pygame.key.get_pressed()
            if event.type == pygame.KEYDOWN:
                # move with arrows
                if currently_edited:
                    try:
                        if key[pygame.K_RIGHT]:
                            currently_edited.editing = False
                            currently_edited = blocks[get_row_col(currently_edited.row, currently_edited.col + 1)]
                            currently_edited.editing = True
                        elif key[pygame.K_LEFT]:
                            currently_edited.editing = False
                            currently_edited = blocks[get_row_col(currently_edited.row, currently_edited.col - 1)]
                            currently_edited.editing = True
                        elif key[pygame.K_UP]:
                            currently_edited.editing = False
                            currently_edited = blocks[get_row_col(currently_edited.row - 1, currently_edited.col)]
                            currently_edited.editing = True
                        elif key[pygame.K_DOWN]:
                            currently_edited.editing = False
                            currently_edited = blocks[get_row_col(currently_edited.row + 1, currently_edited.col)]
                            currently_edited.editing = True
                    except:
                        pass
                else:
                    currently_edited = blocks[0]

                if key[pygame.K_RETURN]:
                    if currently_edited:
                        currently_edited.set_text()
                elif key[pygame.K_SPACE]:
                    thread = Thread(target=solve, args=[board])
                    thread.start()
                    # solve(board)
                elif key[pygame.K_BACKSPACE]:
                    if currently_edited:
                        currently_edited.text = ""
                        board[currently_edited.row][currently_edited.col] = 0
                try:
                    num = int(event.unicode)
                    if currently_edited:
                        currently_edited.temp_text = str(num)
                except Exception as e:
                    pass


main()
