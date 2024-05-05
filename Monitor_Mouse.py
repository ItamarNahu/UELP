import pynput
from Servercomm import Server_comm
import queue


# class to monitor mouse
class Mouse_monitor:
    def __init__(self, server, clientIP: str):
        """
        Builder function creates new Mouse_monitor object to monitor mouse functions
        :param server: server to send through data about mouse
        :param clientIP: ip of client to send mouse data too
        """
        self.server = server
        self.clientIP = clientIP
        self.listener = None  # Initialize listener attribute

        self._monitor_mouse()

    def _monitor_mouse(self):
        """
        Function creates a new listener for the mouse to listen for scroll clicks and movement
        """
        self.listener = pynput.mouse.Listener(on_move=self._on_move, on_click=self._on_click,
                                              on_scroll=self._on_scroll)
        self.listener.start()

    def stop_listening(self):
        """
        Stops the mouse listener.
        """
        if self.listener:
            self.listener.stop()

    def _on_move(self, x: int, y: int):
        """
        Function called when listener detects new pos of mouse and sends the pos to client by protocol
        :param x: x loc of mouse
        :param y: y loc of mouse
        """
        self.server.send(self.clientIP, str(x).zfill(4) + str(y).zfill(4) + "4")

    def _on_click(self, x: int, y: int, button, pressed):
        """
        Function checks if mouse clicked and sends gotten data to client by protocol
        :param x: x pos of mouse click
        :param y: y pos of mouse click
        :param button: button to check mouse type click
        :param pressed: check pressed or released
        """
        msg = str(x).zfill(4) + str(y).zfill(4)
        if button == pynput.mouse.Button.left:
            # check if button was pressed or released and add to protocol accordingly
            if pressed:
                msg += "0"
            else:
                msg += "5"
        elif button == pynput.mouse.Button.right:
            # check if button was pressed or released and add to protocol accordingly
            if pressed:
                msg += "1"
            else:
                msg += "6"

        # send data to client by protocol
        self.server.send(self.clientIP, msg)

    def _on_scroll(self, x: int, y: int, dx: int, dy: int):
        """
        Function checks and listens to mouse scroll wheel and sends to client data if mouse scrolled by protocol
        :param x: x pos of mouse scroll
        :param y: y pos of mouse scroll
        :param dx: added x for mouse scroll
        :param dy: added y for mouse scroll
        """
        msg = str(x).zfill(4) + str(y).zfill(4)
        if dy > 0:
            msg += "2"
        else:
            msg += "3"

        # send data to client by protocol
        self.server.send(self.clientIP, msg)


if __name__ == '__main__':
    m = Mouse_monitor(Server_comm(queue.Queue(), 2000, "0.0.0.0"), "127.0.0.1")
