from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
import json
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
import requests


#from Web3Client import *
w3_client = None
help_str = ''' 

ScreenManager:
    WelcomeScreen:
    LoginScreen:
    SignupScreen:
    MainScreen:
    AddNewItemScreen:

<WelcomeScreen>:
    name:"splitceiptWelcome"
    MDLabel:
        text: 'Welcome to SplitCeipt'
        font_style: 'H4'
        halign: 'center'
        pos_hint: { 'center_y':0.65}
    MDRaisedButton:
        text: 'LOGIN'
        pos_hint: {'center_x':0.4,'center_y':0.3}
        size_hint: (0.12, 0.1)
        on_press:
            root.manager.current = 'loginscreen'
            root.manager.transition.direction = 'left'
    MDRaisedButton:
        text: 'SIGNUP'
        pos_hint: {'center_x':0.6,'center_y':0.3}
        size_hint: (0.13, 0.1)
        on_press:
            root.manager.current = 'signupscreen'
            root.manager.transition.direction = 'left'

<LoginScreen>:
    name: 'loginscreen'
    MDLabel:
        id:login_message
        text: 'Login Here'
        font_style: 'H2'
        halign: 'center'
        pos_hint: {'center_y':0.8, 'center_x':0.25}
    MDTextField:
        id:login_username
        pos_hint: {'center_y':0.6,'center_x':0.5}
        size_hint : (0.5,0.1)
        hint_text: 'Username'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
    MDTextField:
        id:login_password
        pos_hint: {'center_y':0.4,'center_x':0.5}
        size_hint : (0.5,0.1)
        hint_text: 'Password'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'eye-off'
        icon_right_color: app.theme_cls.primary_color
        required: True
        password: 'true'
    MDRaisedButton:
        text:'Login'
        size_hint: (0.13,0.07)
        pos_hint: {'center_x':0.5,'center_y':0.2}
        on_press:
            login_message.text = root.do_login(login_username.text,login_password.text)
            root.manager.current = 'addnewitemscreen' if login_message.text=="Login Success" else 'loginscreen'
            
    MDTextButton:
        text: 'New Here? Create an Account'
        pos_hint: {'center_x':0.5,'center_y':0.1}
        on_press:
            root.manager.current = 'signupscreen'
            root.manager.transition.direction = 'up'

<SignupScreen>:
    name:'signupscreen'
    MDLabel:
        text:'SIGNUP'
        font_style: 'H2'
        halign: 'left'
        pos_hint: {'center_y':0.9}
    MDTextField:
        id:email_address
        pos_hint: {'center_y':0.6,'center_x':0.5}
        size_hint : (0.7,0.1)
        hint_text: 'Email'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
        
    MDTextField:
        id:username
        pos_hint: {'center_y':0.75,'center_x':0.5}
        size_hint : (0.7,0.1)
        hint_text: 'username'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'account'
        icon_right_color: app.theme_cls.primary_color
        required: True
        
    MDTextField:
        id:password
        pos_hint: {'center_y':0.4,'center_x':0.5}
        size_hint : (0.7,0.1)
        hint_text: 'Password'
        helper_text:'Required'
        helper_text_mode:  'on_error'
        icon_right: 'eye-off'
        icon_right_color: app.theme_cls.primary_color
        required: True
        
        password: 'true'
    MDRaisedButton:
        text:'SIGNUP'
        size_hint: (0.13,0.07)
        pos_hint: {'center_x':0.5,'center_y':0.2}
        on_press:
            root.do_signup(username.text,password.text)
            root.manager.current = 'addnewitemscreen'
    MDFloatingActionButton:
        icon: 'arrow-left'
        pos_hint:{'center_y':0.1, 'center_x':0.5}
        md_bg_color: app.theme_cls.primary_color
        on_press:
            root.manager.current = 'loginscreen'
            root.manager.transition.direction = 'up'
<MainScreen>:
    MDLabel:
        text: 'Your bills:'
        font_style: 'H2'
        pos_hint: {"center_y": 0.8, "center_x":0.25}
        halign: 'center'
    MDFloatingActionButton:
        icon: 'plus'
        pos_hint: {"center_x":0.5, "center_y":0.1}
        md_bg_color: app.theme_cls.primary_color
        on_press:
            root.manager.current = 'addnewitemscreen'
            root.manager.transition = 'pop-out'

<AddNewItemScreen>:
    name: 'addnewitemscreen'
    MDLabel:
        text:'Manage Receipts'
        halign: 'center'
        pos_hint: {'center_y':0.95}
    BoxLayout:
        orientation: 'horizontal'
        pos_hint: {'center_y':0.5,'center_x':0.5}
        TextInput:
            pos_hint: {'center_y':0.8,'center_x':0.5}
            size_hint: .5, .15
            text: 'Buyers'
            halign: 'left'
            id: buyers
            multiline:False


        TextInput:
            pos_hint: {'center_y':0.8,'center_x':0.5}
            size_hint: .5, .15
            text:'Payers'
            halign: 'left'
            id: payers
            multiline:False


        TextInput:
            pos_hint: {'center_y':0.8,'center_x':0.5}
            size_hint: .5, .15
            text:'Arbitrator'
            halign: 'left'
            id: arb
            multiline:False



        TextInput:
            pos_hint: {'center_y':0.8,'center_x':0.5}
            size_hint: .5, .15
            text:'Prices'
            halign: 'left'
            id: prices
            multiline:False


        Button:
            pos_hint: {'center_y':0.8,'center_x':0.5}
            size_hint: .15, .15
            text:'+'
            halign: 'left'
            font_size: 28
            on_press: root.add_receipt(buyers.text,payers.text,arb.text,prices.text)

    MDFlatButton:
        pos_hint: {'center_y':0.4,'center_x':0.5}
        text:'Your Receipts'
        font_style: 'H2'
        halign: 'center'
        md_bg_color: app.theme_cls.primary_color
        on_release: root.show_items(box)

    BoxLayout:
        pos_hint: {'center_y':0.25,'center_x':0.5}
        text:''
        id:box
        halign: 'center'
        orientation: 'vertical'

'''

class WelcomeScreen(Screen):
    pass

class LoginScreen(Screen):
  def do_login(self, usernameText, passwordText):
    result = w3_client.login(usernameText,passwordText)
    print(result)
    if result: w3_client.groups.append(w3_client.createGroup()) # Default group
    return "Login Success" if result else "Try Again"
 

class MainScreen(Screen):
    pass

class SignupScreen(Screen):
  def do_signup(self, usernameText, passwordText):
    result = w3_client.signup(usernameText,passwordText)
    print(result)

class AddNewItemScreen(Screen):
    def __init__(self, **kwargs):
      super(AddNewItemScreen, self).__init__(**kwargs)
      self.btns=[]
      self.d = 1

    def print_receipt(self,parent,idx):
      receipt = list(w3_client.receipts.items())[idx][1]
      parent.text = '\n'.join(list(map(str,receipt)))

    def confirm_receipt(self,button,idx):
      receipt = list(w3_client.receipts.items())[idx]
      w3_client.confirm(receipt[0])

    def dispute_receipt(self,button,idx):
      receipt = list(w3_client.receipts.items())[idx]
      w3_client.confirm(receipt[0],self.d)
      self.d = 0 if self.d==1 else 1

    def show_items(self,parent, *args):
        self.btns = [Button(text="Receipt %d"%i, color=(1, 1, 1, 1), size_hint=(None, None),padding=(50,0),halign='center')
                     for i in range(len(list(w3_client.receipts.items())))]
        for btn in self.btns:
            btn.bind(on_release=self.show_dropdown(button=btn,parent=parent))
            self.add_widget(btn)

    def show_dropdown(self,button, parent):
        dp = DropDown()
        dp.bind(on_select=lambda instance, x: setattr(button, 'text', x))
        row  = ["View","Confirm","Dispute","Edit"]
        funs = []
        for i in range(len(row)):
            item = Button(text=str(row[i]), size_hint_y=None, height=24, color=(1, 1, 1, 1),padding=(50,0),halign='center')

            if i==0: item.bind(on_press=(lambda btn: dp.select(btn.text)))
            elif i==1: item.bind(on_press=self.confirm_receipt(button,self.btns.index(button)))
            elif i==2: item.bind(on_press=self.dispute_receipt(button,self.btns.index(button)))
            elif i==3: item.bind(on_press=self.print_receipt(parent,self.btns.index(button)))
            else: item.bind(on_release=(lambda btn: dp.select(item.text)))
            dp.add_widget(item)
        dp.open(parent)

    def add_receipt(self,buyers,payers,arb,prices):
      """
      Create receipt
      """
      buyers = buyers.replace('[','').replace(']','').split(',')
      payers = payers.replace('[','').replace(']','').split(',')
      prices = prices.replace('[','').replace(']','').split(',')
      prices = [int(p)%256 for p in prices]
      w3_client.initReceipt(w3_client.groups[0],[buyers,payers,arb,prices])
      print("[*] Receipt:",buyers,payers,arb,prices,"@",list(w3_client.receipts.items())[-1][0])

sm = ScreenManager()
sm.add_widget(WelcomeScreen(name = 'loginscreen'))
sm.add_widget(MainScreen(name = 'mainscreen'))
sm.add_widget(LoginScreen(name = 'loginscreen'))
sm.add_widget(SignupScreen(name = 'signupscreen'))
sm.add_widget(AddNewItemScreen(name = 'addnewitemscreen'))

class SplitCeiptApp(MDApp):
    def build(self):
        self.strng = Builder.load_string(help_str)
        return self.strng


if __name__ == '__main__':
  w3_client = Web3Client()
  if w3_client.connect('http://127.0.0.1:8545'):
    SplitCeiptApp().run()
  else:
    print("[!] Failed to connect to http RPC server")
