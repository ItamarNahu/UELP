from pynput import keyboard
from pynput.keyboard import Key


# class to monitor keyboard
class Keyboard_monitor:
    def __init__(self, server, clientIP: str):
        """
        builder function creates new Keyboard_monitor object with the vars gotten and calls function _monitor_keyboard
        :param server: server to send keyboard data through
        :param clientIP: client ip to send keyboard data too
        """
        self.server = server
        self.clientIP = clientIP
        self.special_keys_mapping = {Key.ctrl_l: 1114112,
                                     Key.ctrl_r: 1114113,
                                     Key.shift_l: 1114114,
                                     Key.shift_r: 1114115,
                                     Key.alt_l: 1114116,
                                     Key.alt_r: 1114117,
                                     Key.cmd: 1114118,
                                     Key.cmd_l: 1114119,
                                     Key.cmd_r: 1114120,
                                     Key.enter: 1114121,
                                     Key.backspace: 1114122,
                                     Key.tab: 1114123,
                                     Key.space: 1114124,
                                     Key.delete: 1114125,
                                     Key.esc: 1114126,
                                     Key.f1: 1114127,
                                     Key.f2: 1114128,
                                     Key.f3: 1114129,
                                     Key.f4: 1114130,
                                     Key.f5: 1114131,
                                     Key.f6: 1114132,
                                     Key.f7: 1114133,
                                     Key.f8: 1114134,
                                     Key.f9: 1114135,
                                     Key.f10: 1114136,
                                     Key.f11: 1114137,
                                     Key.f12: 1114138,
                                     Key.home: 1114139,
                                     Key.end: 1114140,
                                     Key.page_up: 1114141,
                                     Key.page_down: 1114142,
                                     Key.insert: 1114143,
                                     Key.menu: 1114144,
                                     Key.caps_lock: 1114145,
                                     Key.num_lock: 1114146,
                                     Key.scroll_lock: 1114147,
                                     Key.pause: 1114148,
                                     Key.print_screen: 1114149,
                                     Key.shift: 1114150,
                                     Key.ctrl: 1114151,
                                     Key.alt: 1114152,
                                     Key.up: 1114153,
                                     Key.down: 1114154,
                                     Key.left: 1114155,
                                     Key.right: 1114156}
        self._monitor_keyboard()

    def _monitor_keyboard(self):
        """
        function monitors and listens to keyboard clicks and releases and calls functions accordingly
        :return: nothing
        """
        with keyboard.Listener(on_press=self._on_press, on_release=self._on_release) as listener:
            listener.join()

    def _on_press(self, key):
        """
        function is called when key is pressed, and checks if key is a special key or not and sneds value of key based on protocol and special keys mapping
        :param key:
        :return:
        """

        msg = "01"
        if key in self.special_keys_mapping.keys():
            msg += str(self.special_keys_mapping[key])
        else:
            msg += str(ord(key.char))

        self.server.send(self.clientIP, msg)

    def _on_release(self, key):
        """

        :param key:
        :return:
        """
        msg = "02"
        if key in self.special_keys_mapping.keys():
            msg += str(self.special_keys_mapping[key])
        else:
            msg += str(ord(key.char))
        self.server.send(self.clientIP, msg)
