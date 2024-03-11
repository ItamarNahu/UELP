import queue
from clientComm import Client_comm
from PIL import ImageChops, ImageGrab
import AssistanceSeeker_protocol
import zlib
import pygame
import sys


def getChanged(newScreen: ImageGrab, currScreen: ImageGrab):
    """
    Function checks if there is a difference between two images, if there is it returns the difference Image
     (Image that represents the differnce between the two Images) and the bounding box of the difference Image
    :param newScreen: the ImageGrab image of the new screen that might differ from the currScreen
    :param currScreen: the ImageGrab image of the current screen
    :return: if the Images don't differ return None otherwise return the diff Image and the bounding box of this Image
    """
    # Check if the images are equal
    diff = ImageChops.difference(currScreen, newScreen)
    bbox = diff.getbbox()

    # Images are identical
    if bbox is None:
        return None, None

    # Get the region of the difference
    diff_region = newScreen.crop(bbox)

    return diff_region, bbox


def getChangedPrecentage(bbox, total_pixels: int) -> float:
    """
    Function checks how much percentage Image changed since the last Image based on bounding box of diffImage
    :param bbox: The bounding box of the difference Image on the screen
    :param total_pixels: the total amount of pixels on screen
    :return: percentage representing how much the Image has changed based on the difference Image
    """
    # get loc of diff Image
    top, left, bottom, right = bbox

    # calculate the percentage of difference based on the pixel amount of the difference in total pixels of screen
    diff_pixels = (bottom - top) * (right - left)
    percentage_difference = (diff_pixels / total_pixels) * 100

    return percentage_difference


def main_AS_screen(otherIP):
    pygame.init()
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    recv_q = queue.Queue()
    port = 2003

    client = Client_comm(otherIP, port, recv_q)

    # get first screenshot
    currScreen = ImageGrab.grab()
    currScreen_bytes = currScreen.tobytes()

    currScreen_bytes = zlib.compress(currScreen_bytes)

    # send first screenshot to Helper based on protocol
    client.sendImage(AssistanceSeeker_protocol.pack_full_image(str(len(currScreen_bytes))), currScreen_bytes)
    while True:
        # get new screenshot
        newScreen = ImageGrab.grab()
        diffImage, diff_bbox = getChanged(newScreen, currScreen)
        if diffImage is not None:
            changed_precentage = getChangedPrecentage(diff_bbox, screen_height * screen_width)
            # if Image is more then 75 percent different, send the entire Image and not the difference
            if changed_precentage >= 75:
                newScreen_bytes = newScreen.tobytes()
                newScreen_bytes = zlib.compress(newScreen_bytes)
                # send full screenshot to Helper based on protocol
                client.sendImage(AssistanceSeeker_protocol.pack_full_image(str(len(newScreen_bytes))),
                                 newScreen_bytes)
            else:
                # get the bounding box values of the difference Image
                top, left, bottom, right = diff_bbox

                diffBytes = diffImage.tobytes()
                diffBytes = zlib.compress(diffBytes)
                # build difference Image header based on protocol
                msg = AssistanceSeeker_protocol.pack_part_image(str(top), str(left), str(bottom), str(right),
                                                                str(len(diffBytes)))

                # send difference Image and Image header to Helper
                client.sendImage(msg, diffBytes)

            # update currScreen as newScreen
            currScreen = newScreen
