import wx
import Client_protocol
from pubsub import pub
import re


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
        self.select = SelectUserPanel(self, self.frame)
        v_box.Add(self.select)
        self.helper = HelperPanel(self, self.frame)
        v_box.Add(self.helper)
        self.Assistance_seeker = ASPanel(self, self.frame)
        v_box.Add(self.Assistance_seeker)
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
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour("#c4dfe6")
        title.SetFont(titlefont)
        # username
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        self.nameField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER, size=(150, -1))
        self.set_placeholder_text(self.nameField, "Username")
        nameBox.Add(wx.StaticBitmap(self, -1, wx.Bitmap("user.png")), 0, wx.ALL, 5)  # Add username image
        nameBox.Add(self.nameField, 0, wx.ALL, 5)
        self.nameField.Bind(wx.EVT_TEXT, self.on_text_change)  # Bind text change event
        # password
        passBox = wx.BoxSizer(wx.HORIZONTAL)
        self.passField = wx.TextCtrl(self, -1, style=wx.TE_PASSWORD, size=(150, -1))
        self.set_placeholder_text(self.passField, "a12fgtegp")
        passBox.Add(wx.StaticBitmap(self, -1, wx.Bitmap("pass.png")), 0, wx.ALL, 5)  # Add password image
        passBox.Add(self.passField, 0, wx.ALL, 5)
        self.passField.Bind(wx.EVT_TEXT, self.on_text_change)  # Bind text change event

        # login & registration buttons
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.loginBtn = wx.Button(self, wx.ID_ANY, label="login", size=(100, 40))
        self.loginBtn.Bind(wx.EVT_BUTTON, self.handle_login)
        self.loginBtn.Disable()
        btnBox.Add(self.loginBtn, 0, wx.ALL, 5)

        self.regBtn = wx.Button(self, wx.ID_ANY, label="Registration", size=(100, 40))
        self.regBtn.Bind(wx.EVT_BUTTON, self.handle_reg)
        self.regBtn.Disable()
        btnBox.Add(self.regBtn, 1, wx.ALL, 5)

        self.interactive_elements = [self.nameField, self.passField, self.loginBtn,
                                     self.regBtn]

        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(10)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(passBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(10)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        # Add logo at the bottom right
        logo = wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"))
        sizer.Add(logo, 0, wx.ALIGN_RIGHT | wx.BOTTOM, 5)

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()
        self.invalidText = None
        pub.subscribe(self.handle_login_ans, "login_ans")
        pub.subscribe(self.handle_signup_ans, "signup_ans")

    def handle_login_ans(self, ans):
        if ans == "1":
            self.show_invalid_message("Username or password incorrect", 2000)
        elif ans == "2":
            self.show_invalid_message("User is logged in", 2000)
        elif ans == "0":
            self.parent.change_screen(self, self.parent.select)

    def handle_signup_ans(self, ans):
        if not ans:
            self.show_invalid_message("Username already taken", 2000)
        else:
            self.parent.change_screen(self, self.parent.select)

    def show_invalid_message(self, msg, time):

        # Show red text message for 5 seconds
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        self.invalidText.SetForegroundColour(wx.RED)

        sizer = self.GetSizer()
        sizer.Insert(sizer.GetItemCount() - 2, self.invalidText, 0, wx.ALIGN_TOP | wx.CENTER, 10)

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
            self.loginBtn.Disable()
            self.regBtn.Disable()
        else:
            self.loginBtn.Enable()
            self.regBtn.Enable()

    def handle_login(self, event):
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        msg2send = Client_protocol.pack_login_info(username, password)
        self.frame.client.send(msg2send)

    def handle_reg(self, event):
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if self._check_password(password):
            msg2send = Client_protocol.pack_signup_info(username, password)
            self.frame.client.send(msg2send)

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
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.title.SetForegroundColour("#c4dfe6")
        self.title.SetFont(titlefont)
        select = wx.StaticText(self, -1, label="Select User Type")
        selectfont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        select.SetForegroundColour("#c4dfe6")
        select.SetFont(selectfont)

        # Helper & Assistance Seeker buttons
        btnBox = wx.BoxSizer(wx.HORIZONTAL)

        # Helper button with image
        self.HelperBtn = wx.Button(self, wx.ID_ANY, label="Helper", size=(650, 425))
        self.HelperBtn.SetFont(wx.Font(40, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.HelperBtn.Bind(wx.EVT_BUTTON, self.handle_helper)
        helper_image = wx.StaticBitmap(self, -1, wx.Bitmap("Helper.png"))
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer.Add(helper_image, 0, wx.CENTER)
        btn_sizer.Add(self.HelperBtn, 0, wx.CENTER)
        btnBox.Add(btn_sizer, 0, wx.ALL, 5)

        btnBox.AddSpacer(100)
        # Assistance Seeker button with image
        self.ASBtn = wx.Button(self, wx.ID_ANY, label="Assistance Seeker", size=(650, 425))
        self.ASBtn.SetFont(wx.Font(40, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.ASBtn.Bind(wx.EVT_BUTTON, self.handle_AS)
        as_image = wx.StaticBitmap(self, -1, wx.Bitmap("assistance_seeker.png"))
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer.Add(as_image, 0, wx.CENTER)
        btn_sizer.AddSpacer(12)
        btn_sizer.Add(self.ASBtn, 0, wx.CENTER)
        btnBox.Add(btn_sizer, 0, wx.ALL, 5)

        # Add all elements to sizer
        sizer.Add(self.title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(50)
        sizer.Add(select, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(50)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Arrow acting as a button
        arrow_bitmap = wx.Bitmap("arrow_off.png")
        self.arrow = wx.StaticBitmap(self, wx.ID_ANY, arrow_bitmap)
        self.arrow.Bind(wx.EVT_LEFT_DOWN, self.on_arrow_click)
        bottomsizer.Add(self.arrow, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        bottomsizer.AddStretchSpacer()  # Add spacer to push logo to the right

        # Add logo at the bottom right
        logo = wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"))
        bottomsizer.Add(logo, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, 5)

        sizer.Add(bottomsizer, 0, wx.EXPAND | wx.ALL, 5)

        # Arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()
        self.invalidText = None
        self.userType = None
        self.interactive_elements = [self.HelperBtn, self.ASBtn, self.arrow]
        pub.subscribe(self.handle_typeUser_ans, "typeUser_ans")

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
        if self.userType is None:
            self.arrow.SetBitmap(wx.Bitmap("arrow_on.png"))
        self.userType = "H"
        self.userType = "H"
        self.HelperBtn.Disable()
        self.ASBtn.Enable()

    def handle_AS(self, event):
        if self.userType is None:
            self.arrow.SetBitmap(wx.Bitmap("arrow_on.png"))
        self.userType = "A"
        self.ASBtn.Disable()
        self.HelperBtn.Enable()

    def on_arrow_click(self, event):
        if self.userType is not None:
            msg2send = Client_protocol.pack_type_user(self.userType)
            self.frame.client.send(msg2send)

    def show_invalid_message(self, msg, time):
        # Show red text message for certain time
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        invalidTextfont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.invalidText.SetFont(invalidTextfont)
        self.invalidText.SetForegroundColour(wx.RED)

        sizer = self.GetSizer()
        sizer.Insert(sizer.GetItemCount() - 2, self.invalidText, 0, wx.ALIGN_TOP | wx.CENTER, 10)

        self.disable_interactive_elements()
        self.Layout()

        self.arrow.SetBitmap(wx.Bitmap("arrow_off.png"))
        self.userType = None
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(time, oneShot=True)

    def on_timer(self, event):
        # Remove the invalid message after certain time
        if self.invalidText is not None:
            self.invalidText.Destroy()
            self.Layout()
            self.enable_interactive_elements()

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
        self.SetBackgroundColour(wx.LIGHT_GREY)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a sizer for the title and code label
        title_code_sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.title.SetForegroundColour("#c4dfe6")
        self.title.SetFont(titlefont)
        title_code_sizer.Add(self.title, 0, wx.CENTER | wx.TOP, 5)
        title_code_sizer.AddSpacer(50)

        self.yourcode = wx.StaticText(self, -1, label="Your Code")
        yourcodefont = wx.Font(120, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.yourcode.SetForegroundColour("#c4dfe6")
        self.yourcode.SetFont(yourcodefont)
        title_code_sizer.Add(self.yourcode, 0, wx.CENTER | wx.TOP, 5)
        title_code_sizer.AddSpacer(100)

        self.code = wx.StaticText(self, -1, label="None")
        codefont = wx.Font(150, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.code.SetForegroundColour("#000000")
        self.code.SetFont(codefont)
        title_code_sizer.Add(self.code, 0, wx.CENTER | wx.TOP, 5)
        self.code.Hide()
        # Add the title and code label sizer to the main sizer
        sizer.Add(title_code_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # Create a sizer for the logo
        logo_sizer = wx.BoxSizer(wx.HORIZONTAL)
        logo = wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"))
        logo_sizer.AddStretchSpacer()
        logo_sizer.Add(logo, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALL, 5)

        # Add the logo sizer to the main sizer
        sizer.Add(logo_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

        pub.subscribe(self.handle_code_gotten, "gotten_code")

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


class ASPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, style=wx.SIMPLE_BORDER, size=(1920, 1080))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, -1, label="UELP")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour("#c4dfe6")
        title.SetFont(titlefont)
        enter = wx.StaticText(self, -1, label="Enter Session Code:")
        enterfont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        enter.SetForegroundColour("#c4dfe6")
        enter.SetFont(enterfont)

        # textctrl to enter code
        self.codeField = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER, size=(550, -1))
        codefont = wx.Font(90, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        self.codeField.SetFont(codefont)

        # Button to connect
        self.connect_btn = wx.Button(self, wx.ID_ANY, label="Connect")
        self.connect_btn.Bind(wx.EVT_BUTTON, self.on_connect)

        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(200)
        sizer.Add(enter, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(50)
        sizer.Add(self.codeField, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(50)
        sizer.Add(self.connect_btn, 0, wx.CENTER | wx.ALL, 5)

        # Add logo at the bottom right
        logo = wx.StaticBitmap(self, -1, wx.Bitmap("logo.png"))
        # Add a flexible space to push the logo to the bottom-right
        sizer.AddStretchSpacer()
        sizer.Add(logo, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALL, 5)

        self.interactive_elements = [self.codeField, self.connect_btn]
        self.invalidText = None
        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

        pub.subscribe(self.handle_code_ans, "code_ans")

    def handle_code_ans(self, ans):
        if ans:
            pass
            # connect screen
        else:
            self.show_invalid_message("Session code incorrect", 2000)

    def on_connect(self, event):
        code_in_text = self.codeField.GetValue()
        if code_in_text != "":
            msg2send = Client_protocol.pack_code(code_in_text)
            self.frame.client.send(msg2send)

    def show_invalid_message(self, msg, time):

        # Show red text message for 5 seconds
        self.invalidText = wx.StaticText(self, label=msg, style=wx.ALIGN_CENTER)
        self.invalidText.SetForegroundColour(wx.RED)

        sizer = self.GetSizer()
        sizer.Insert(sizer.GetItemCount() - 1, self.invalidText, 0, wx.ALIGN_TOP | wx.CENTER, 10)

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

    def disable_interactive_elements(self):
        for element in self.interactive_elements:
            element.Disable()

    def enable_interactive_elements(self):
        for element in self.interactive_elements:
            element.Enable()


if __name__ == '__main__':
    app = wx.App()
    test = MyFrame()
    app.MainLoop()
