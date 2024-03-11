import queue
from Servercomm import Server_comm
from PIL import Image
import pygame
import zlib


# current PIL image
currScreen = None


def build_Screen(top: int, left: int, right: int, bottom: int, img_bytes: bytes):
    """
    Function gets the location and bytes of the image to paste and pastes it on current screen
    :param top: top value of Image
    :param left: left value of Image
    :param right: right value of Image
    :param bottom: bottom value of Image
    :param img_bytes: bytes of Image
    """
    # location to paste Image
    paste_loc = (top, left)

    # Create a PIL Image object from the bytes of the image bytes
    diff_img = Image.frombytes('RGB', (bottom - top, right - left), img_bytes)

    # Paste the diff image on the current screen
    currScreen.paste(diff_img, paste_loc)


def main_Helper_screen(otherIP):
    recv_q = queue.Queue()
    port = 2003
    global currScreen
    # create new server that only gets messages from otherIP with port and recv_q gotten
    server = Server_comm(recv_q, port, otherIP)

    # create pygame screen and save width and height of screen
    pygame.init()
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

    while True:
        # get data from client
        data, ip = recv_q.get()
        if data == "disconnect":
            pygame.quit()
            break

        # if amount of params in data is 5, we got a part image, take out params decompress and
        # build_screen based on imageData gotten
        if len(data) == 5 and currScreen:
            top = data[0]
            left = data[1]
            bottom = data[2]
            right = data[3]
            diff_bytes = data[4]
            diff_bytes = zlib.decompress(diff_bytes)

            top, left, right, bottom = int(top), int(left), int(right), int(bottom)

            # call _build_screen with all params of image to paste this image on the current screen
            build_Screen(top, left, right, bottom, bytes(diff_bytes))
        # if only one param we got a full Image, decompress and build it as current screen
        elif len(data) == 1:
            newScreen_bytes = data[0]
            newScreen_bytes = zlib.decompress(newScreen_bytes)
            # Create a PIL Image object from the bytes of the image bytes
            currScreen = Image.frombytes('RGB', (screen_width, screen_height),
                                         bytes(newScreen_bytes))

        # if there is currently a valid PIL image object as current screen show it to user using pygame
        if currScreen:
            # transform PIL image object to pygame image
            currScreen_bytes = currScreen.tobytes()
            pygame_currScreen = pygame.image.frombuffer(currScreen_bytes,
                                                        (screen_width, screen_height), "RGB")

            # show image
            screen.blit(pygame_currScreen, (0, 0))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
