import wx
import wx.adv
import Client_protocol
from pubsub import pub
import re
import pyperclip

class MyFrame(wx.Frame):
    def __init__(self, comm, parent=None):
        super(MyFrame, self).__init__(parent, title="UELP")
        self.Maximize()
        self.client = comm
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
        wx.Panel.__init__(self, parent)
        self.frame = parent
        self.SetBackgroundColour("#fcf6f5")
        v_box = wx.BoxSizer(wx.VERTICAL)
        # create object for each panel
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
        self.login.Show()
        self.SetSizer(v_box)
        self.Layout()

    def change_screen(self, cur_screen, screen):
        cur_screen.Hide()
        screen.Show()
        self.Layout()


class LoginPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")
        sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        self.about = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("info.png"), pos=(1850, 5))
        self.about.Bind(wx.EVT_LEFT_DOWN, self.show_info_dialog)

        signin = wx.StaticText(self, -1, label="Sign In", pos=(720, 100))
        signinFont = wx.Font(125, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Garamond")
        signin.SetFont(signinFont)
        signin.SetForegroundColour("#3f4043")

        self.nameField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER, size=(600, 100))
        self.nameField.SetFont(wx.Font(65, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        self.set_placeholder_text(self.nameField, "Username")
        # Adding the image to the left of the nameField
        wx.StaticBitmap(self, -1, wx.Bitmap("user.png"), pos=(550, 365))

        self.nameField.Bind(wx.EVT_TEXT, self.on_text_change)  # Bind text change event

        self.passField = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD, size=(600, 100))
        self.passField.SetFont(wx.Font(50, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        self.set_placeholder_text(self.passField, "a12fgtegp")
        wx.StaticBitmap(self, -1, wx.Bitmap("pass.png"), pos=(550, 502))
        self.passField.Bind(wx.EVT_TEXT, self.on_text_change)  # Bind text change event

        # next acting as a button
        self.login_bitmap = wx.Bitmap("login.png")
        self.login_off_bitmap = wx.Bitmap("login_off.png")
        self.next = wx.StaticBitmap(self, wx.ID_ANY, self.login_off_bitmap)
        self.next.Bind(wx.EVT_LEFT_DOWN, self.on_next_click)
        self.can_press = False

        self.signup_sizer = wx.BoxSizer(wx.HORIZONTAL)
        no_account = wx.StaticText(self, -1, label="Dont have an account?")
        no_account_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT")
        no_account.SetFont(no_account_font)
        self.signup = wx.StaticText(self, -1, label="Sign Up")
        signup_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, True, "Calisto MT")
        self.signup.Bind(wx.EVT_LEFT_DOWN, self.handle_signup_screen)
        self.signup.SetFont(signup_font)
        self.signup.SetForegroundColour("#0000FF")
        self.signup_sizer.Add(no_account, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.signup_sizer.AddSpacer(8)
        self.signup_sizer.Add(self.signup, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.interactive_elements = [self.nameField, self.passField, self.next]

        # Add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(260)
        sizer.Add(self.nameField, 0, wx.CENTER, 5)
        sizer.AddSpacer(35)
        sizer.Add(self.passField, 0, wx.CENTER, 5)
        sizer.AddSpacer(110)
        sizer.Add(self.next, 0, wx.CENTER, 5)
        sizer.Add(self.signup_sizer, 0, wx.CENTER, 5)

        # Add logo at the bottom right
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        # Arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()
        self.invalidText = None
        pub.subscribe(self.handle_login_ans, "login_ans")

    def handle_login_ans(self, ans):
        if ans == "1":
            self.show_invalid_message("Username or password incorrect", 2000)
        elif ans == "2":
            self.show_invalid_message("User is logged in", 2000)
        elif ans == "0":
            self.parent.change_screen(self, self.parent.select)

    def show_invalid_message(self, msg, time):

        # Show red text message for 5 seconds
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        self.invalidText.SetForegroundColour(wx.RED)
        self.invalidText.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        sizer = self.GetSizer()
        sizer.Insert(sizer.GetItemCount(), self.invalidText, 0, wx.ALIGN_TOP | wx.CENTER, 10)

        self.disable_interactive_elements()
        self.Layout()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(time, oneShot=True)

    def on_timer(self, event):
        # Remove the invalid message after certain time
        if self.invalidText is not None:
            self.invalidText.Destroy()
            self.Layout()
            self.enable_interactive_elements()

    def set_placeholder_text(self, text_ctrl, placeholder):
        text_ctrl.SetValue(placeholder)
        text_ctrl.SetForegroundColour('#808080')  # Set text color to grey
        text_ctrl.SetDefaultStyle(wx.TextAttr(wx.NullColour, wx.NullColour))  # Reset text style
        text_ctrl.Bind(wx.EVT_SET_FOCUS, self.on_set_focus)
        text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

    def on_set_focus(self, event):
        ctrl = event.GetEventObject()
        if ctrl.GetValue() == "Username" or ctrl.GetValue() == "a12fgtegp":
            ctrl.SetValue("")
            ctrl.SetForegroundColour(wx.BLACK)
            self.Layout()
        event.Skip()

    def on_kill_focus(self, event):
        ctrl = event.GetEventObject()
        if ctrl.IsEmpty():
            if ctrl == self.nameField:
                ctrl.SetValue("Username")
            elif ctrl == self.passField:
                ctrl.SetValue("a12fgtegp")
            ctrl.SetForegroundColour('#808080')  # Set text color to grey
        event.Skip()

    def on_text_change(self, event):
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if not username or not password or username == "Username" or password == "a12fgtegp":
            self.next.SetBitmap(self.login_off_bitmap)
            self.can_press = False
        elif not self.can_press:
            self.next.SetBitmap(self.login_bitmap)
            self.can_press = True

    def on_next_click(self, event):
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if self.can_press:
            msg2send = Client_protocol.pack_login_info(username, password)
            self.frame.client.send(msg2send)

    def show_info_dialog(self, event):
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
        self.parent.change_screen(self, self.parent.signup)

    def _check_password(self, password):
        pattern = r'[^a-zA-Z0-9\s]'
        is_ok = True
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
        for element in self.interactive_elements:
            element.Disable()

    def enable_interactive_elements(self):
        for element in self.interactive_elements:
            element.Enable()


class SignUpPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")
        sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        signup = wx.StaticText(self, -1, label="Sign Up", pos=(705, 100))
        signupFont = wx.Font(125, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Garamond")
        signup.SetFont(signupFont)
        signup.SetForegroundColour("#3f4043")

        self.nameField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER, size=(600, 100))
        self.nameField.SetFont(wx.Font(65, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        self.set_placeholder_text(self.nameField, "Username")
        # Adding the image to the left of the nameField
        wx.StaticBitmap(self, -1, wx.Bitmap("user.png"), pos=(550, 365))

        self.nameField.Bind(wx.EVT_TEXT, self.on_text_change)  # Bind text change event

        self.passField = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD, size=(600, 100))
        self.passField.SetFont(wx.Font(50, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        self.set_placeholder_text(self.passField, "a12fgtegp")
        wx.StaticBitmap(self, -1, wx.Bitmap("pass.png"), pos=(550, 502))
        self.passField.Bind(wx.EVT_TEXT, self.on_text_change)  # Bind text change event

        # next acting as a button
        self.signup_bitmap = wx.Bitmap("signup.png")
        self.signup_off_bitmap = wx.Bitmap("signup_off.png")
        self.next = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("signup_off.png"))
        self.next.Bind(wx.EVT_LEFT_DOWN, self.on_next_click)
        self.can_press = False

        self.signup_sizer = wx.BoxSizer(wx.HORIZONTAL)
        have_account = wx.StaticText(self, -1, label="Already have an account?")
        have_account_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT")
        have_account.SetFont(have_account_font)
        self.login = wx.StaticText(self, -1, label="Login")
        signup_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, True, "Calisto MT")
        self.login.Bind(wx.EVT_LEFT_DOWN, self.handle_signin_screen)
        self.login.SetFont(signup_font)
        self.login.SetForegroundColour("#0000FF")
        self.signup_sizer.Add(have_account, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.signup_sizer.AddSpacer(8)
        self.signup_sizer.Add(self.login, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.interactive_elements = [self.nameField, self.passField, self.next]

        # Add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(260)
        sizer.Add(self.nameField, 0, wx.CENTER, 5)
        sizer.AddSpacer(35)
        sizer.Add(self.passField, 0, wx.CENTER, 5)
        sizer.AddSpacer(110)
        sizer.Add(self.next, 0, wx.CENTER, 5)
        sizer.Add(self.signup_sizer, 0, wx.CENTER, 5)

        # Add logo at the bottom right
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        # Arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()
        self.invalidText = None
        pub.subscribe(self.handle_signup_ans, "signup_ans")

    def handle_signup_ans(self, ans):
        if not ans:
            self.show_invalid_message("Username already taken", 2000)
        else:
            self.parent.change_screen(self, self.parent.select)

    def show_invalid_message(self, msg, time):

        # Show red text message for 5 seconds
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        self.invalidText.SetForegroundColour(wx.RED)
        self.invalidText.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))

        sizer = self.GetSizer()
        sizer.Insert(sizer.GetItemCount(), self.invalidText, 0, wx.ALIGN_TOP | wx.CENTER, 10)

        self.disable_interactive_elements()
        self.Layout()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(time, oneShot=True)

    def on_timer(self, event):
        # Remove the invalid message after certain time
        if self.invalidText is not None:
            self.invalidText.Destroy()
            self.Layout()
            self.enable_interactive_elements()

    def set_placeholder_text(self, text_ctrl, placeholder):
        text_ctrl.SetValue(placeholder)
        text_ctrl.SetForegroundColour('#808080')  # Set text color to grey
        text_ctrl.SetDefaultStyle(wx.TextAttr(wx.NullColour, wx.NullColour))  # Reset text style
        text_ctrl.Bind(wx.EVT_SET_FOCUS, self.on_set_focus)
        text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

    def on_set_focus(self, event):
        ctrl = event.GetEventObject()
        if ctrl.GetValue() == "Username" or ctrl.GetValue() == "a12fgtegp":
            ctrl.SetValue("")
            ctrl.SetForegroundColour(wx.BLACK)
            self.Layout()
        event.Skip()

    def on_kill_focus(self, event):
        ctrl = event.GetEventObject()
        if ctrl.IsEmpty():
            if ctrl == self.nameField:
                ctrl.SetValue("Username")
            elif ctrl == self.passField:
                ctrl.SetValue("a12fgtegp")
            ctrl.SetForegroundColour('#808080')  # Set text color to grey
        event.Skip()

    def on_text_change(self, event):
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if not username or not password or username == "Username" or password == "a12fgtegp":
            self.next.SetBitmap(self.signup_off_bitmap)
            self.can_press = False
        elif not self.can_press:
            self.next.SetBitmap(self.signup_bitmap)
            self.can_press = True

    def on_next_click(self, event):
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if self.can_press and self._check_password(password):
            msg2send = Client_protocol.pack_signup_info(username, password)
            self.frame.client.send(msg2send)

    def handle_signin_screen(self, event):
        self.parent.change_screen(self, self.parent.login)

    def _check_password(self, password):
        pattern = r'[^a-zA-Z0-9\s]'
        is_ok = True
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
        for element in self.interactive_elements:
            element.Disable()

    def enable_interactive_elements(self):
        for element in self.interactive_elements:
            element.Enable()


class SelectUserPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")

        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        select = wx.StaticText(self, -1, label="Select User Type")
        selectfont = wx.Font(55, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Garamond")
        select.SetFont(selectfont)
        select.SetForegroundColour("#3f4043")

        # Helper & Assistance Seeker buttons
        btnBox = wx.BoxSizer(wx.HORIZONTAL)

        self.helper = wx.StaticBitmap(self, -1, wx.Bitmap("Helper_choose.png"))
        self.helper.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.helper.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.helper.Bind(wx.EVT_LEFT_DOWN, self.handle_helper)  # Bind left click event
        self.helper.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)  # Mark this bitmap as helper

        self.As = wx.StaticBitmap(self, -1, wx.Bitmap("assistance_seeker.png"))
        self.As.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.As.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.As.Bind(wx.EVT_LEFT_DOWN, self.handle_AS)  # Bind left click event
        self.As.SetWindowVariant(wx.WINDOW_VARIANT_NORMAL)  # Mark this bitmap as assistance seeker

        btnBox.Add(self.helper, 0, wx.Center, 5)
        btnBox.AddSpacer(150)
        btnBox.Add(self.As, 0, wx.Center)

        # Add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.Add(select, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(20)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        # Add logo at the bottom right
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        # Arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()
        self.invalidText = None
        self.userType = None
        self.interactive_elements = [self.As, self.helper]
        pub.subscribe(self.handle_typeUser_ans, "typeUser_ans")

    def on_hover(self, event):
        bitmap = event.GetEventObject()
        if bitmap.GetWindowVariant() == wx.WINDOW_VARIANT_SMALL:
            bitmap.SetBitmap(wx.Bitmap("Helper_choose_hover.png"))
        else:
            bitmap.SetBitmap(wx.Bitmap("assistance_seeker_hover.png"))
        event.Skip()

    def on_leave(self, event):
        bitmap = event.GetEventObject()
        if bitmap.GetWindowVariant() == wx.WINDOW_VARIANT_SMALL:
            bitmap.SetBitmap(wx.Bitmap("Helper_choose.png"))
        else:
            bitmap.SetBitmap(wx.Bitmap("assistance_seeker.png"))
        event.Skip()

    def handle_typeUser_ans(self, ans):
        if self.userType == "H":
            if not ans:
                self.show_invalid_message("You do not have Helper permissions", 2000)
            else:
                self.parent.change_screen(self, self.parent.helper)
                self.frame.client.send("03")

        elif self.userType == "A":
            if not ans:
                self.show_invalid_message("User type choice is not valid", 2000)
            else:
                self.parent.change_screen(self, self.parent.Assistance_seeker)

    def handle_helper(self, event):
        self.userType = "H"
        msg2send = Client_protocol.pack_type_user(self.userType)
        self.frame.client.send(msg2send)

    def handle_AS(self, event):
        self.userType = "A"
        msg2send = Client_protocol.pack_type_user(self.userType)
        self.frame.client.send(msg2send)

    def show_invalid_message(self, msg, time):
        # Show red text message for certain time
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        invalidTextfont = wx.Font(48, wx.DECORATIVE, wx.NORMAL, wx.NORMAL, False, "Calisto MT")
        self.invalidText.SetFont(invalidTextfont)
        self.invalidText.SetForegroundColour(wx.RED)

        self.invalidText.SetPosition((480, 540))
        self.As.Hide()
        self.helper.Hide()
        self.disable_interactive_elements()

        self.Layout()

        self.userType = None
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(time, oneShot=True)

    def on_timer(self, event):
        # Remove the invalid message after certain time
        if self.invalidText is not None:
            self.invalidText.Destroy()
            self.enable_interactive_elements()
            self.As.Show()
            self.helper.Show()
            self.Layout()

    def disable_interactive_elements(self):
        for element in self.interactive_elements:
            element.Disable()

    def enable_interactive_elements(self):
        for element in self.interactive_elements:
            element.Enable()


class HelperPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")

        sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        yourcode = wx.StaticText(self, -1, label="Your Code")
        yourcodefont = wx.Font(120, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Garamond")
        yourcode.SetFont(yourcodefont)
        yourcode.SetForegroundColour("#3f4043")

        self.code = wx.StaticText(self, -1, label="None")
        codefont = wx.Font(150, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT")
        self.code.SetForegroundColour("#000000")
        self.code.SetFont(codefont)
        self.code.Hide()

        self.copy_code_bitmap = wx.Bitmap("copy_code.png")
        self.copy_code_hover_bitmap = wx.Bitmap("copy_code_hover.png")
        self.copy_code = wx.StaticBitmap(self, -1, self.copy_code_bitmap)
        self.copy_code.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.copy_code.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.copy_code.Bind(wx.EVT_LEFT_DOWN, self.handle_copied)  # Bind left click event
        # Add to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(50)
        sizer.Add(yourcode, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(100)
        sizer.Add(self.code, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(100)
        sizer.Add(self.copy_code, 0, wx.CENTER, 5)

        # Add logo at the bottom right
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        # Arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

        pub.subscribe(self.handle_code_gotten, "gotten_code")
        pub.subscribe(self.handle_connecting_session, "connecting_session")

    def handle_code_gotten(self, ans):
        if ans == "2":
            result = wx.MessageDialog(None, "Your code expired!\nWould you like a new code?", "Code Expiration",
                                      wx.YES_NO | wx.ICON_QUESTION | wx.CENTRE)
            # Check the user's response
            if result == wx.YES:
                self.frame.client.send("03")
            else:
                self.parent.change_screen(self, self.parent.select)
        else:
            self.session_code = ans
            self.code.SetLabel(self.session_code)
            self.code.Show()
            self.Layout()

    def on_hover(self, event):
        self.copy_code.SetBitmap(wx.Bitmap("copy_code_hover.png"))

    def on_leave(self, event):
        self.copy_code.SetBitmap(wx.Bitmap("copy_code.png"))

    def handle_copied(self, event):
        self.copy_code.SetBitmap(wx.Bitmap("copied.png"))
        # copy Code to clipboard
        pyperclip.copy(self.code.GetLabel())

        # unbind all copy code events
        self.copy_code.Unbind(wx.EVT_ENTER_WINDOW)
        self.copy_code.Unbind(wx.EVT_LEAVE_WINDOW)
        self.copy_code.Unbind(wx.EVT_LEFT_DOWN)

    def handle_connecting_session(self):
        self.parent.change_screen(self, self.parent.connecting)
        self.parent.connecting.start_dots_animation()


class ASPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)
        enter = wx.StaticText(self, -1, label="Enter Session Code")
        enterfont = wx.Font(75, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Garamond")
        enter.SetForegroundColour("#3f4043")
        enter.SetFont(enterfont)

        # textctrl to enter code
        self.codeField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER, size=(800, -1))
        codefont = wx.Font(90, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT")
        self.codeField.SetFont(codefont)
        self.codeField.Bind(wx.EVT_TEXT, self.on_text_change)

        # connect acting as a button
        self.connect = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("connect_off.png"))
        self.connect.Bind(wx.EVT_LEFT_DOWN, self.on_connect)
        self.can_press = False

        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(75)
        sizer.Add(enter, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(100)
        sizer.Add(self.codeField, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(180)
        sizer.Add(self.connect, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Add logo at the bottom right
        wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"), pos=(1680, 920))

        self.invalidText = None
        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

        pub.subscribe(self.handle_code_ans, "code_ans")

    def handle_code_ans(self, ans):
        if ans:
            self.parent.change_screen(self, self.parent.connecting)
            self.parent.connecting.start_dots_animation()
        else:
            self.show_invalid_message("Session code incorrect", 2000)

    def on_text_change(self, event):
        text = self.codeField.GetValue()
        if text != "":
            if not self.can_press:
                self.connect.SetBitmap(wx.Bitmap("connect.png"))
                self.can_press = True
        else:
            self.connect.SetBitmap(wx.Bitmap("connect_off.png"))
            self.can_press = False

    def on_connect(self, event):
        code_in_text = self.codeField.GetValue()
        if self.can_press:
            msg2send = Client_protocol.pack_code(code_in_text)
            self.frame.client.send(msg2send)

    def show_invalid_message(self, msg, time):

        # Show red text message for 5 seconds
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        self.invalidText.SetFont(wx.Font(35, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Calisto MT"))
        self.invalidText.SetForegroundColour(wx.RED)

        sizer = self.GetSizer()
        sizer.Insert(sizer.GetItemCount(), self.invalidText, 0, wx.ALIGN_TOP | wx.CENTER, 10)

        self.codeField.Disable()
        self.can_press = False
        self.connect.SetBitmap(wx.Bitmap("connect_off.png"))
        self.Layout()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(time, oneShot=True)

    def on_timer(self, event):
        # Remove the invalid message after certain time
        if self.invalidText is not None:
            self.invalidText.Destroy()
            self.Layout()
            self.codeField.Enable()
            self.can_press = True
            self.connect.SetBitmap(wx.Bitmap("connect.png"))


class ConnectingPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour("#fdf0d0")
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(68, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Algerian")
        title.SetForegroundColour("#aa7c57")
        title.SetFont(titlefont)

        self.connecting_text = wx.StaticText(self, -1, label="Connecting to session")
        connecting_font = wx.Font(90, wx.DECORATIVE, wx.NORMAL, wx.NORMAL, False, "Garamond")
        self.connecting_text.SetForegroundColour("#3f4043")
        self.connecting_text.SetFont(connecting_font)

        self.disconnect_instruction = wx.StaticText(self, -1,
                                                    label="To disconnect from session press: Ctrl + Shift + D")
        disconnect_font = wx.Font(25, wx.DECORATIVE, wx.NORMAL, wx.NORMAL, False, "Garamond")
        self.disconnect_instruction.SetForegroundColour("#880808")
        self.disconnect_instruction.SetFont(disconnect_font)

        # Add connecting text to center vertically
        self.sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 5)
        self.sizer.AddStretchSpacer()
        self.sizer.Add(self.connecting_text, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 5)

        # Add a spacer to push disconnect instruction closer to the bottom
        self.sizer.AddStretchSpacer()

        # Add disconnect instruction just above the logo and in the middle
        self.sizer.Add(self.disconnect_instruction, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 20)

        # Add logo at the bottom right
        self.logo = wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"))
        # Add a flexible space to push the logo to the bottom-right
        self.sizer.Add(self.logo, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALL, 5)

        # arrange the screen
        self.SetSizer(self.sizer)
        self.Layout()
        self.Hide()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.dots_counter = 0

    def on_timer(self, event):
        text = self.connecting_text.GetLabel()
        if text.endswith("..."):
            self.connecting_text.SetLabel("Connecting to session")
            self.dots_counter += 1
        else:
            self.connecting_text.SetLabel(text + ".")

        if self.dots_counter >= 3:  # Stop after reaching 3 sets of 3 dots
            self.timer.Stop()
            self.parent.frame.Close()

    def start_dots_animation(self):
        self.timer.Start(500)


if __name__ == '__main__':
    app = wx.App()
    test = MyFrame("A")
    app.MainLoop()
