import re

import pyperclip
import wx
import wx.adv
from pubsub import pub

import Client_protocol


class MyFrame(wx.Frame):
    def __init__(self, comm, parent=None):
        """
        Initialize frame
        :param comm: client object to comm with server
        :param parent: parent panel
        """
        super(MyFrame, self).__init__(parent, title="UELP")
        self.Maximize()
        self.client = comm

        # set icon
        self.SetIcon(wx.Icon("logo.png", wx.BITMAP_TYPE_PNG))

        # create main panel - to put on the others panels
        self.main_panel = MainPanel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.main_panel, 1, wx.EXPAND)
        # arrange the frame
        self.SetSizer(box)
        self.Layout()
        self.Show()


class MainPanel(wx.Panel):
    def __init__(self, parent):
        """
        Initialize Main  panel all other panels are put on
        :param parent: Parent panel
        """
        wx.Panel.__init__(self, parent)
        self.frame = parent
        self.SetBackgroundColour("#fcf6f5")
        v_box = wx.BoxSizer(wx.VERTICAL)
        # create object for each panel to switch between
        self.login = LoginPanel(self, self.frame)
        v_box.Add(self.login)
        self.signup = SignUpPanel(self, self.frame)
        v_box.Add(self.signup)
        self.select = SelectUserPanel(self, self.frame)
        v_box.Add(self.select)
        self.helper = HelperPanel(self, self.frame)
        v_box.Add(self.helper)
        self.Assistance_seeker = ASPanel(self, self.frame)
        v_box.Add(self.Assistance_seeker)
        self.connecting = ConnectingPanel(self, self.frame)
        v_box.Add(self.connecting)

        # show first panel - login
        self.login.Show()

        self.SetSizer(v_box)
        self.Layout()

    def change_screen(self, cur_screen, screen):
        """
        Function changes panel currently viewed
        :param cur_screen: current panel viewed
        :param screen: new Panel to view
        """
        cur_screen.Hide()
        screen.Show()
        self.Layout()


class LoginPanel(wx.Panel):
    def __init__(self, parent, frame):
        """
        Login screen panel
        :param parent: Parent panel
        :param frame: Frame parent
        """
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")

        sizer = wx.BoxSizer(wx.VERTICAL)

        # initialize title on panel
        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        # initialize about button on panel
        self.about = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("info.png"), pos=(1850, 5))
        self.about.Bind(wx.EVT_LEFT_DOWN, self.show_info_dialog)

        # initialize signin title on panel
        signin = wx.StaticText(self, -1, label="Sign In", pos=(720, 100))
        signinFont = wx.Font(125, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Garamond")
        signin.SetFont(signinFont)
        signin.SetForegroundColour("#3f4043")

        # initialize username textctrl on panel
        self.nameField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER, size=(600, 100))
        self.nameField.SetFont(wx.Font(65, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        self.set_placeholder_text(self.nameField, "Username")

        # Add username image to the left of the nameField
        wx.StaticBitmap(self, -1, wx.Bitmap("user.png"), pos=(550, 365))

        # bind text change event to function for username textctrl
        self.nameField.Bind(wx.EVT_TEXT, self.on_text_change)

        # initialize password textctrl on panel
        self.passField = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD, size=(600, 100))
        self.passField.SetFont(wx.Font(50, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        self.set_placeholder_text(self.passField, "a12fgtegp")

        # Add password image to the left of the nameField
        wx.StaticBitmap(self, -1, wx.Bitmap("pass.png"), pos=(550, 502))

        # bind text change event to function for password textctrl
        self.passField.Bind(wx.EVT_TEXT, self.on_text_change)

        # initialize login button bitmaps and the static bitmap acting as the button
        self.login_bitmap = wx.Bitmap("login.png")
        self.login_off_bitmap = wx.Bitmap("login_off.png")
        self.next = wx.StaticBitmap(self, wx.ID_ANY, self.login_off_bitmap)
        self.next.Bind(wx.EVT_LEFT_DOWN, self.on_next_click)
        self.can_press = False

        # set sizer for switching to signup panel elements
        signup_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # initialize no account text to panel
        no_account = wx.StaticText(self, -1, label="Dont have an account?")
        no_account_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT")
        no_account.SetFont(no_account_font)

        # initialize signup text so can be pressed to switch to signup panel
        self.signup = wx.StaticText(self, -1, label="Sign Up")
        signup_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, True, "Calisto MT")
        self.signup.Bind(wx.EVT_LEFT_DOWN, self.handle_signup_screen)
        self.signup.SetFont(signup_font)
        self.signup.SetForegroundColour("#0000FF")

        # add all text to signup sizer
        signup_sizer.Add(no_account, 0, wx.ALL, 5)
        signup_sizer.AddSpacer(8)
        signup_sizer.Add(self.signup, 0, wx.ALL, 5)

        # create list of all interactive elemnts to disable/enable when needed
        self.interactive_elements = [self.nameField, self.passField, self.next]

        # Add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(260)
        sizer.Add(self.nameField, 0, wx.CENTER, 5)
        sizer.AddSpacer(35)
        sizer.Add(self.passField, 0, wx.CENTER, 5)
        sizer.AddSpacer(110)
        sizer.Add(self.next, 0, wx.CENTER, 5)
        sizer.Add(signup_sizer, 0, wx.CENTER, 5)

        # Add logo at the bottom right of screen
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        # Arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

        # invalidText shown when gotten negetive answer and need to show on screen
        self.invalidText = None

        pub.subscribe(self.handle_login_ans, "login_ans")

    def handle_login_ans(self, ans):
        """
        Function called when gotten login request ans from server, act accordingly
         (change screen or let user know login incorrect)
        :param ans: answer to login request user sent
        """

        if ans == "1":
            self.show_invalid_message("Username or password incorrect", 2000)
        elif ans == "2":
            print(333)
            self.show_invalid_message("User is logged in", 2000)
        elif ans == "0":
            self.parent.change_screen(self, self.parent.select)

    def show_invalid_message(self, msg, time):
        """
        Function shows invalid message on screen for certain time
        :param msg: msg to show on screen
        :param time: amount of time to show message on screen
        """
        # Set invalid text as msg gotten
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        self.invalidText.SetForegroundColour(wx.RED)
        self.invalidText.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))

        # place invalid text in right position in sizer
        sizer = self.GetSizer()
        sizer.Insert(sizer.GetItemCount(), self.invalidText, 0, wx.ALIGN_TOP | wx.CENTER, 10)

        # disable interactive elements so user has to view invalid text for certain time
        self.disable_interactive_elements()
        self.Layout()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        # start timer for certain time gotten
        self.timer.Start(time, oneShot=True)

    def on_timer(self, event):
        """
        Function called when timer ends and erases invalid text currently seen
        :param event: event for time
        """
        # Remove the invalid message if still exists
        if self.invalidText is not None:
            self.invalidText.Destroy()
            self.Layout()
            self.enable_interactive_elements()

    def set_placeholder_text(self, text_ctrl, placeholder):
        """
        Function called to set certain placeholder text in textctrl and bind focus and unfocus events for textctrl
        :param text_ctrl: text_ctrl to place text in
        :param placeholder: text to place in text ctrl
        """
        text_ctrl.SetValue(placeholder)
        # Set text color to grey
        text_ctrl.SetForegroundColour('#808080')
        # Reset text style
        text_ctrl.SetDefaultStyle(wx.TextAttr(wx.NullColour, wx.NullColour))

        # bind focus events to textctrl
        text_ctrl.Bind(wx.EVT_SET_FOCUS, self.on_set_focus)
        text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

    def on_set_focus(self, event):
        """
        Function called when text ctrl is focused on, if placeholder texts for textctrls are there then
        empty text ctrl and change text color
        :param event: event of focus
        """
        ctrl = event.GetEventObject()

        if ctrl.GetValue() == "Username" or ctrl.GetValue() == "a12fgtegp":
            ctrl.SetValue("")
            ctrl.SetForegroundColour(wx.BLACK)
            self.Layout()
        event.Skip()

    def on_kill_focus(self, event):
        """
        Function called when text ctrl is not focused on, if text ctrl is empty set text in textctrl to placeholder
        text and change text color
        :param event: event of kill focus
        """
        ctrl = event.GetEventObject()

        if ctrl.IsEmpty():
            if ctrl == self.nameField:
                ctrl.SetValue("Username")
            elif ctrl == self.passField:
                ctrl.SetValue("a12fgtegp")
            ctrl.SetForegroundColour('#808080')  # Set text color to grey
        event.Skip()

    def on_text_change(self, event):
        """
        Function called when text in text ctrl is changed and checks if text fit criteria for pressing/not pressing
        login button and changes boolean value accordingly
        :param event: event of text change
        """
        username = self.nameField.GetValue()
        password = self.passField.GetValue()

        # if text in username and password textctrl isn't placeholder text and both are not empty can press button
        if not username or not password or username == "Username" or password == "a12fgtegp":
            # change bitmap of button and boolean value if can press button
            self.next.SetBitmap(self.login_off_bitmap)
            self.can_press = False
        elif not self.can_press:
            self.next.SetBitmap(self.login_bitmap)
            self.can_press = True

    def on_next_click(self, event):
        """
        Function called when login button pressed, function checks if user can press button
        and packs username and password gotten from user by protocol and sends to server
        :param event: event of button click
        """
        username = self.nameField.GetValue()
        password = self.passField.GetValue()

        if self.can_press:
            msg2send = Client_protocol.pack_login_info(username, password)
            self.frame.client.send(msg2send)

    def show_info_dialog(self, event):
        """
        Function called when info button pressed, show info on system
        :param event: event of info click
        """
        info = wx.adv.AboutDialogInfo()
        info.SetName("Itamar system")
        info.SetDescription("This system allow you to Control and help friends computer from your own")
        info.SetCopyright("(C) 2024-2030")
        info.AddDeveloper("Itamar Nahum")
        info.AddArtist("Itamar Nahum")
        info.AddDocWriter("Itamar Nahum")
        info.SetVersion("1.0")
        info.SetName("UELP")
        info.SetLicence("Atid \n Cramim \n Israel")
        wx.adv.AboutBox(info)

    def handle_signup_screen(self, event):
        """
        Function called when signup text pressed, change screen to signup panel
        :param event: event of signup screen click
        """
        self.parent.change_screen(self, self.parent.signup)

    def _check_password(self, password):
        """
        Function checks password user entered
        :param password: password gotten from user
        """
        pattern = r'[^a-zA-Z0-9\s]'
        is_ok = True
        # password must have at least 8 characters one uppercase letter and one special character,
        # show invalid message accordingly
        if len(password) < 8:
            self.show_invalid_message("Password should be 8 characters and up", 2000)
            is_ok = False
        elif not re.search(pattern, password):
            self.show_invalid_message("Password must include one special character", 2000)
            is_ok = False
        elif password == password.lower():
            self.show_invalid_message("Password must include one uppercase letter", 2000)
            is_ok = False

        return is_ok

    def disable_interactive_elements(self):
        """
        Function disables all interactive elements in interactive elements list
        """
        for element in self.interactive_elements:
            element.Disable()

    def enable_interactive_elements(self):
        """
        Function enables all interactive elements in interactive elements list
        """
        for element in self.interactive_elements:
            element.Enable()


class SignUpPanel(wx.Panel):
    def __init__(self, parent, frame):
        """
        Signup screen panel
        :param parent: parent panel
        :param frame: frame parent
        """
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")
        sizer = wx.BoxSizer(wx.VERTICAL)

        # initialize title on panel
        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        # initialize signup title on panel
        signup = wx.StaticText(self, -1, label="Sign Up", pos=(705, 100))
        signupFont = wx.Font(125, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Garamond")
        signup.SetFont(signupFont)
        signup.SetForegroundColour("#3f4043")

        # initialize username textctrl on panel
        self.nameField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER, size=(600, 100))
        self.nameField.SetFont(wx.Font(65, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        self.set_placeholder_text(self.nameField, "Username")

        # Add username image to the left of the nameField
        wx.StaticBitmap(self, -1, wx.Bitmap("user.png"), pos=(550, 365))

        # bind text change event to function for username textctrl
        self.nameField.Bind(wx.EVT_TEXT, self.on_text_change)

        # initialize password textctrl on panel
        self.passField = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD, size=(600, 100))
        self.passField.SetFont(wx.Font(50, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        self.set_placeholder_text(self.passField, "a12fgtegp")

        # Add password image to the left of the nameField
        wx.StaticBitmap(self, -1, wx.Bitmap("pass.png"), pos=(550, 502))

        # bind text change event to function for password textctrl
        self.passField.Bind(wx.EVT_TEXT, self.on_text_change)  # Bind text change event

        # initialize signup button bitmaps and the static bitmap acting as the button
        self.signup_bitmap = wx.Bitmap("signup.png")
        self.signup_off_bitmap = wx.Bitmap("signup_off.png")
        self.next = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("signup_off.png"))
        self.next.Bind(wx.EVT_LEFT_DOWN, self.on_next_click)
        self.can_press = False

        # set sizer for switching to signin panel elements
        signin_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # initialize have account text to panel
        have_account = wx.StaticText(self, -1, label="Already have an account?")
        have_account_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT")
        have_account.SetFont(have_account_font)

        # initialize text acting as button to switch to login panel
        self.login = wx.StaticText(self, -1, label="Login")
        signin_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, True, "Calisto MT")
        self.login.Bind(wx.EVT_LEFT_DOWN, self.handle_signin_screen)
        self.login.SetFont(signin_font)
        self.login.SetForegroundColour("#0000FF")

        # add elements to sizer
        signin_sizer.Add(have_account, 0, wx.ALL, 5)
        signin_sizer.AddSpacer(8)
        signin_sizer.Add(self.login, 0, wx.ALL, 5)

        # create list of all interactive elemnts to disable/enable when needed
        self.interactive_elements = [self.nameField, self.passField, self.next]

        # Add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(260)
        sizer.Add(self.nameField, 0, wx.CENTER, 5)
        sizer.AddSpacer(35)
        sizer.Add(self.passField, 0, wx.CENTER, 5)
        sizer.AddSpacer(110)
        sizer.Add(self.next, 0, wx.CENTER, 5)
        sizer.Add(signin_sizer, 0, wx.CENTER, 5)

        # Add logo at the bottom right of panel
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        # Arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

        # invalidText shown when gotten negetive answer and need to show on screen
        self.invalidText = None

        pub.subscribe(self.handle_signup_ans, "signup_ans")

    def handle_signup_ans(self, ans):
        """
        Function called when gotten signup request ans from server, act accordingly
        (change screen or let user know signup incorrect)
        :param ans: answer to signup request user sent
        """
        if not ans:
            self.show_invalid_message("Username already taken", 2000)
        else:
            self.parent.change_screen(self, self.parent.select)

    def show_invalid_message(self, msg, time):
        """
        Function shows invalid message on screen for certain time
        :param msg: msg to show on screen
        :param time: amount of time to show message on screen
        """
        # Set invalid text as msg gotten
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        self.invalidText.SetForegroundColour(wx.RED)
        self.invalidText.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))

        # place invalid text in right position in sizer
        sizer = self.GetSizer()
        sizer.Insert(sizer.GetItemCount(), self.invalidText, 0, wx.ALIGN_TOP | wx.CENTER, 10)

        # disable interactive elements so user has to view invalid text for certain time
        self.disable_interactive_elements()
        self.Layout()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        # start timer for certain time gotten
        self.timer.Start(time, oneShot=True)

    def on_timer(self, event):
        """
        Function called when timer ends and erases invalid text currently seen
        :param event: event for time
        """
        # Remove the invalid message if still exists
        if self.invalidText is not None:
            self.invalidText.Destroy()
            self.Layout()
            self.enable_interactive_elements()

    def set_placeholder_text(self, text_ctrl, placeholder):
        """
        Function called to set certain placeholder text in textctrl and bind focus and unfocus events for textctrl
        :param text_ctrl: text_ctrl to place text in
        :param placeholder: text to place in text ctrl
        """
        text_ctrl.SetValue(placeholder)

        # Set text color to grey
        text_ctrl.SetForegroundColour('#808080')

        # Reset text style
        text_ctrl.SetDefaultStyle(wx.TextAttr(wx.NullColour, wx.NullColour))

        # bind focus events to textctrl
        text_ctrl.Bind(wx.EVT_SET_FOCUS, self.on_set_focus)
        text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

    def on_set_focus(self, event):
        """
        Function called when text ctrl is focused on, if placeholder texts for textctrls are there then
        empty text ctrl and change text color
        :param event: event of focus
        """
        ctrl = event.GetEventObject()

        if ctrl.GetValue() == "Username" or ctrl.GetValue() == "a12fgtegp":
            ctrl.SetValue("")
            ctrl.SetForegroundColour(wx.BLACK)
            self.Layout()
        event.Skip()

    def on_kill_focus(self, event):
        """
        Function called when text ctrl is not focused on, if text ctrl is empty set text in textctrl to placeholder
        text and change text color
        :param event: event of kill focus
        """
        ctrl = event.GetEventObject()

        if ctrl.IsEmpty():
            if ctrl == self.nameField:
                ctrl.SetValue("Username")
            elif ctrl == self.passField:
                ctrl.SetValue("a12fgtegp")
            # Set text color to grey
            ctrl.SetForegroundColour('#808080')
        event.Skip()

    def on_text_change(self, event):
        """
        Function called when text in text ctrl is changed and checks if text fit criteria for pressing/not pressing
        signup button and changes boolean value accordingly
        :param event: event of text change
        """
        username = self.nameField.GetValue()
        password = self.passField.GetValue()

        # if text in username and password textctrl isn't placeholder text and both are not empty can press button
        if not username or not password or username == "Username" or password == "a12fgtegp":
            # change bitmap of button and boolean value if can press button
            self.next.SetBitmap(self.signup_off_bitmap)
            self.can_press = False
        elif not self.can_press:
            self.next.SetBitmap(self.signup_bitmap)
            self.can_press = True

    def on_next_click(self, event):
        """
        Function called when signup button pressed, function checks if user can press button
        and packs username and password gotten from user by protocol and sends to server
        :param event: event of button click
        """
        username = self.nameField.GetValue()
        password = self.passField.GetValue()

        if self.can_press and self._check_password(password):
            msg2send = Client_protocol.pack_signup_info(username, password)
            self.frame.client.send(msg2send)

    def handle_signin_screen(self, event):
        """
        Function called when signin text pressed, change screen to signup panel
        :param event: event of signup screen click
        """
        self.parent.change_screen(self, self.parent.login)

    def _check_password(self, password):
        """
        Function checks password user entered
        :param password: password gotten from user
        """
        pattern = r'[^a-zA-Z0-9\s]'
        is_ok = True

        # password must have at least 8 characters one uppercase letter and one special character,
        # show invalid message accordingly
        if len(password) < 8:
            self.show_invalid_message("Password should be 8 characters and up", 2000)
            is_ok = False
        elif not re.search(pattern, password):
            self.show_invalid_message("Password must include one special character", 2000)
            is_ok = False
        elif password == password.lower():
            self.show_invalid_message("Password must include one uppercase letter", 2000)
            is_ok = False

        return is_ok

    def disable_interactive_elements(self):
        """
        Function disables all interactive elements in interactive elements list
        """
        for element in self.interactive_elements:
            element.Disable()

    def enable_interactive_elements(self):
        """
        Function enables all interactive elements in interactive elements list
        """
        for element in self.interactive_elements:
            element.Enable()


class SelectUserPanel(wx.Panel):
    def __init__(self, parent, frame):
        """
        Select user panel
        :param parent: Parent panel
        :param frame: frame parent
        """
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")

        sizer = wx.BoxSizer(wx.VERTICAL)

        # initialize title on panel
        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        # Initialize select user text on panel
        select = wx.StaticText(self, -1, label="Select User Type")
        selectfont = wx.Font(55, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Garamond")
        select.SetFont(selectfont)
        select.SetForegroundColour("#3f4043")

        # Initialize sizer for Helper & Assistance Seeker buttons
        btnBox = wx.BoxSizer(wx.HORIZONTAL)

        # Initialize helper static bitmap button on panel, bind to hover and pressing events
        self.helper = wx.StaticBitmap(self, -1, wx.Bitmap("Helper_choose.png"))
        self.helper.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.helper.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.helper.Bind(wx.EVT_LEFT_DOWN, self.handle_helper)

        # Mark this bitmap as window variant to differ helper from Assistance Seeker button
        self.helper.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        # Initialize Assistance Seeker static bitmap button on panel, bind to hover and pressing events
        self.As = wx.StaticBitmap(self, -1, wx.Bitmap("assistance_seeker.png"))
        self.As.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.As.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.As.Bind(wx.EVT_LEFT_DOWN, self.handle_AS)  # Bind left click event
        # Mark this bitmap as window variant to differ Assistance seeker from Helper button
        self.As.SetWindowVariant(wx.WINDOW_VARIANT_NORMAL)

        # Add elements to sizer
        btnBox.Add(self.helper, 0, wx.Center, 5)
        btnBox.AddSpacer(150)
        btnBox.Add(self.As, 0, wx.Center)

        # Add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.Add(select, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(20)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        # Add logo at the bottom right of panel
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        # Arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()
        self.invalidText = None
        self.userType = None

        pub.subscribe(self.handle_typeUser_ans, "typeUser_ans")

    def on_hover(self, event):
        """
        Function called when button hovered on, change bitmap of button accordingly to hover bitmap
        :param event: event of button of hover
        """
        bitmap = event.GetEventObject()
        # check which button gotten, AS or Helper
        if bitmap.GetWindowVariant() == wx.WINDOW_VARIANT_SMALL:
            bitmap.SetBitmap(wx.Bitmap("Helper_choose_hover.png"))
        else:
            bitmap.SetBitmap(wx.Bitmap("assistance_seeker_hover.png"))
        event.Skip()

    def on_leave(self, event):
        """
        Function called when button stops hovered on, change bitmap of button accordingly to normal bitmap
        :param event: event of button of hover
        """
        bitmap = event.GetEventObject()
        # check which button gotten, AS or Helper
        if bitmap.GetWindowVariant() == wx.WINDOW_VARIANT_SMALL:
            bitmap.SetBitmap(wx.Bitmap("Helper_choose.png"))
        else:
            bitmap.SetBitmap(wx.Bitmap("assistance_seeker.png"))
        event.Skip()

    def handle_typeUser_ans(self, ans):
        """
        Function called when gotten type user request ans from server, act accordingly
        (change screen or let user know user type pressed invalid based on user type pressed)
        :param ans: answer to type user request user sent
        """
        if self.userType == "H":
            if not ans:
                self.show_invalid_message("You do not have Helper permissions", 2000)
            else:
                # when changing to helper screen send opcode for getting new code request to server
                self.parent.change_screen(self, self.parent.helper)
                self.frame.client.send("03")

        elif self.userType == "A":
            if not ans:
                self.show_invalid_message("User type choice is not valid", 2000)
            else:
                self.parent.change_screen(self, self.parent.Assistance_seeker)

    def handle_helper(self, event):
        """
        Function called when helper button pressed, send user type request based on protocol and set user Type asked for
        :param event: event of button pressed
        """
        self.userType = "H"
        msg2send = Client_protocol.pack_type_user(self.userType)
        self.frame.client.send(msg2send)

    def handle_AS(self, event):
        """
        Function called when AS button pressed, send user type request based on protocol and set user Type asked for
        :param event: event of button pressed
        """
        self.userType = "A"
        msg2send = Client_protocol.pack_type_user(self.userType)
        self.frame.client.send(msg2send)

    def show_invalid_message(self, msg, time):
        """
        Function shows invalid message on screen for certain time
        :param msg: msg to show on screen
        :param time: amount of time to show message on screen
        """
        # Set invalid text as msg gotten
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        invalidTextfont = wx.Font(48, wx.DECORATIVE, wx.NORMAL, wx.NORMAL, False, "Calisto MT")
        self.invalidText.SetFont(invalidTextfont)
        self.invalidText.SetForegroundColour(wx.RED)

        # set invalid text position and hide buttons to press
        self.invalidText.SetPosition((480, 540))

        # hide both buttons to show invalid message
        self.As.Hide()
        self.helper.Hide()
        self.Layout()

        # set user type to be None as user type asked for was not gotten
        self.userType = None

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        # start timer for certain time gotten
        self.timer.Start(time, oneShot=True)

    def on_timer(self, event):
        """
        Function called when timer ends and erases invalid text currently seen
        :param event: event for time
        """
        # Remove the invalid message if still exists and show buttons again
        if self.invalidText is not None:
            self.invalidText.Destroy()
            self.As.Show()
            self.helper.Show()
            self.Layout()


class HelperPanel(wx.Panel):
    def __init__(self, parent, frame):
        """
        Helper user panel
        :param parent: Parent panel
        :param frame: frame parent
        """
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Initialize title on panel
        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        # Initialize your code text on panel
        yourcode = wx.StaticText(self, -1, label="Your Code")
        yourcodefont = wx.Font(120, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Garamond")
        yourcode.SetFont(yourcodefont)
        yourcode.SetForegroundColour("#3f4043")

        # Initialize Code static text on panel (Set as hidden until gotten code from server)
        self.code = wx.StaticText(self, -1, label="None")
        codefont = wx.Font(150, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT")
        self.code.SetForegroundColour("#000000")
        self.code.SetFont(codefont)
        self.code.Hide()

        # Initialize static Bitmap button of copying code to clipboard, bind to hover and clicking events
        self.copy_code_bitmap = wx.Bitmap("copy_code.png")
        self.copy_code_hover_bitmap = wx.Bitmap("copy_code_hover.png")
        self.copy_code = wx.StaticBitmap(self, -1, self.copy_code_bitmap)
        self.copy_code.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.copy_code.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.copy_code.Bind(wx.EVT_LEFT_DOWN, self.handle_copied)

        # Add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(50)
        sizer.Add(yourcode, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(100)
        sizer.Add(self.code, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(100)
        sizer.Add(self.copy_code, 0, wx.CENTER, 5)

        # Add logo at the bottom right of panel
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        # Arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

        pub.subscribe(self.handle_code_gotten, "gotten_code")
        pub.subscribe(self.handle_connecting_session, "connecting_session")

    def handle_code_gotten(self, ans):
        """
        Function called when gotten code request answer from server, act accordingly
        (ask user if wants new code or show code)
        :param ans: answer to code request (code or expired code opcode)
        """

        # answer gotten is either expired code opcode ot just the code gotten
        if ans == "2":
            result = wx.MessageDialog(None, "Your code expired!\nWould you like a new code?", "Code Expiration",
                                      wx.YES_NO | wx.ICON_QUESTION | wx.CENTRE)
            # Check the user's response to expired code message, if wants new code send a new request
            # if not take user back to select screen
            if result == wx.YES:
                self.frame.client.send("03")
            else:
                self.parent.change_screen(self, self.parent.select)
        else:
            # set session code element as code gotten and show code
            self.code.SetLabel(ans)
            self.code.Show()
            self.Layout()

    def on_hover(self, event):
        """
        Function called when button hovered on, change bitmap of button accordingly to hover bitmap
        :param event: event of button of hover
        """
        self.copy_code.SetBitmap(self.copy_code_hover_bitmap)

    def on_leave(self, event):
        """
        Function called when button not hovered on, change bitmap of button accordingly to regular bitmap
        :param event: event of button of hover
        """
        self.copy_code.SetBitmap(self.copy_code_bitmap)

    def handle_copied(self, event):
        """
        Function called when copy button is pressed, change bitmap of button,
         disable button and copy code of session to clipboard
        :param event: event of button press
        """
        self.copy_code.SetBitmap(wx.Bitmap("copied.png"))
        # copy Code to clipboard
        pyperclip.copy(self.code.GetLabel())

        # unbind all copy code events
        self.copy_code.Unbind(wx.EVT_ENTER_WINDOW)
        self.copy_code.Unbind(wx.EVT_LEAVE_WINDOW)
        self.copy_code.Unbind(wx.EVT_LEFT_DOWN)

    def handle_connecting_session(self):
        """
        Function is called from client logic when other user connected to session, switch to connecting screen panel
        and start the animation of dots
        """
        self.parent.change_screen(self, self.parent.connecting)
        self.parent.connecting.start_dots_animation()


class ASPanel(wx.Panel):
    def __init__(self, parent, frame):
        """
        Helper user panel
        :param parent: Parent panel
        :param frame: frame parent
        """
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Initialize title on panel
        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        # Initialize enter code text on panel
        enter = wx.StaticText(self, -1, label="Enter Session Code")
        enterfont = wx.Font(75, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Garamond")
        enter.SetForegroundColour("#3f4043")
        enter.SetFont(enterfont)

        # Initialize textctrl to enter code on panel, bind to text changing event
        self.codeField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER, size=(800, -1))
        codefont = wx.Font(90, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT")
        self.codeField.SetFont(codefont)
        self.codeField.Bind(wx.EVT_TEXT, self.on_text_change)

        # Initialize static bitmap button to connect to session, bind to click event
        self.connect = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("connect_off.png"))
        self.connect.Bind(wx.EVT_LEFT_DOWN, self.on_connect)
        self.can_press = False

        # Add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(75)
        sizer.Add(enter, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(100)
        sizer.Add(self.codeField, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(180)
        sizer.Add(self.connect, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Add logo at the bottom right of panel
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        # arrange the screen
        self.SetSizer(sizer)
        self.invalidText = None
        self.Layout()
        self.Hide()

        pub.subscribe(self.handle_code_ans, "code_ans")

    def handle_code_ans(self, ans):
        """
        Function called when gotten code entered answer from server, act accordingly
        (switch to connecting session panel or show invalid message)
        :param ans: answer to code entered (code valid or invalid)
        """
        if ans:
            self.parent.change_screen(self, self.parent.connecting)
            self.parent.connecting.start_dots_animation()
        else:
            self.show_invalid_message("Session code incorrect", 2000)

    def on_text_change(self, event):
        """
        Function called when text in textctrl changes, checks if text is empty or isn't and changes bitmap of button and
         can_press boolean value accordingly
        :param event: event of textctrl value change
        """
        text = self.codeField.GetValue()

        if text != "":
            if not self.can_press:
                self.connect.SetBitmap(wx.Bitmap("connect.png"))
                self.can_press = True
        else:
            self.connect.SetBitmap(wx.Bitmap("connect_off.png"))
            self.can_press = False

    def on_connect(self, event):
        """
        Function called when connect button is pressed, check if boolean value of can_press is True
         and send code in textctrl field by protocol to server
        :param event: event of connect button pressed
        """
        code_in_text = self.codeField.GetValue()

        if self.can_press:
            msg2send = Client_protocol.pack_code(code_in_text)
            self.frame.client.send(msg2send)

    def show_invalid_message(self, msg, time):
        """
        Function shows invalid message on screen for certain time
        :param msg: msg to show on screen
        :param time: amount of time to show message on screen
        """
        # Set invalid text as msg gotten
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        self.invalidText.SetFont(wx.Font(35, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        self.invalidText.SetForegroundColour(wx.RED)

        # place invalid text in right position in sizer
        sizer = self.GetSizer()
        sizer.Insert(sizer.GetItemCount(), self.invalidText, 0, wx.ALIGN_TOP | wx.CENTER, 10)

        # Disable interactive elements
        self.codeField.Disable()
        self.can_press = False
        self.connect.SetBitmap(wx.Bitmap("connect_off.png"))
        self.Layout()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        # start timer for certain time gotten
        self.timer.Start(time, oneShot=True)

    def on_timer(self, event):
        """
        Function called when timer ends and erases invalid text currently seen
        :param event: event for time
        """
        # Remove the invalid message if still exists and enable button and textctrl back
        if self.invalidText is not None:
            self.invalidText.Destroy()
            self.Layout()
            self.codeField.Enable()
            self.can_press = True
            self.connect.SetBitmap(wx.Bitmap("connect.png"))


class ConnectingPanel(wx.Panel):
    def __init__(self, parent, frame):
        """
        Connecting to session panel
        :param parent: Parent panel
        :param frame: frame parent
        """
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # Initialize title on panel
        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        # Initialize connecting to session text on panel
        self.connecting_text = wx.StaticText(self, -1, label="Connecting to session")
        connecting_font = wx.Font(90, wx.DECORATIVE, wx.NORMAL, wx.NORMAL, False, "Garamond")
        self.connecting_text.SetForegroundColour("#3f4043")
        self.connecting_text.SetFont(connecting_font)

        # Initialize disconnect from session instructions on panel
        disconnect_instruction = wx.StaticText(self, -1,
                                               label="To disconnect from session press: Ctrl + Shift + D")
        disconnect_font = wx.Font(25, wx.DECORATIVE, wx.NORMAL, wx.NORMAL, False, "Garamond")
        disconnect_instruction.SetForegroundColour("#880808")
        disconnect_instruction.SetFont(disconnect_font)

        # Add elements to sizer
        self.sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 5)
        self.sizer.AddStretchSpacer()
        self.sizer.Add(self.connecting_text, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 5)
        self.sizer.AddStretchSpacer()
        self.sizer.Add(disconnect_instruction, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 20)

        # Add logo at the bottom right of panel
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        # arrange the screen
        self.SetSizer(self.sizer)
        self.Layout()
        self.Hide()

        # Initialize timer for dot animation
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.dots_counter = 0

    def on_timer(self, event):
        """
        Function called when timer ends, add dot to end of connecting text dynamically
        :param event: event of timer ending
        """
        text = self.connecting_text.GetLabel()

        # if text already has three dots start new set of dots and update the dot set counter otherwise add dot to text
        if text.endswith("..."):
            self.connecting_text.SetLabel("Connecting to session")
            self.dots_counter += 1
        else:
            self.connecting_text.SetLabel(text + ".")

        # Stop after reaching 3 sets of 3 dots and close connecting frame as user is connecting to session
        if self.dots_counter == 3:
            self.timer.Stop()
            self.parent.frame.Close()

    def start_dots_animation(self):
        """
        Function called to start dot animation (new dot every half second)
        :return:
        """
        self.timer.Start(500)


if __name__ == '__main__':
    app = wx.App()
    test = MyFrame("A")
    app.MainLoop()
