from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import socket
import threading
import json

#ADMIN_ADDR = "192.168.1.12"
ADMIN_ADDR = socket.gethostbyname(socket.gethostname())
ADMIN_PORT = 5505 

print(ADMIN_ADDR)

FORMAT = "utf8"
MAX_CILENT = 10

MODE_LOGIN = 1
MODE_SIGNIN = 2

MESS_SUCCESS = "SUCCESS"
MESS_FAILURE = "FAILED"

COLOR_1="#753422"
COLOR_2="#B05B3B"
COLOR_3="#D79771"
COLOR_4="#FFEBC9"

user_list = {}
class Admin:
    def __init__(self):
        #-----------------Back End
        self.host_server = socket.gethostbyname(ADMIN_ADDR)
        self.port_server = ADMIN_PORT
        self.curr_client = 0

        self.server_process = socket.socket()
        self.server_process.bind((self.host_server, self.port_server))
        self.server_process.listen(10)
        #----------------Front End
        self.gui = Tk()
        self.gui.title("Gui for Admin")
        self.gui.geometry("500x500")
        self.gui.protocol("WM_DELETE_WINDOW", self.onClosing)
        #ID Frame
        self.idFrame = Frame(self.gui)
        self.idIntro = Label(self.idFrame, text="CLONE META")
        self.idLabel = Label(self.idFrame, text="ID ROOM")
        self.idInput = Label(self.idFrame, text=self.host_server)
        #--------Component config
        self.idFrame.config(bg=COLOR_4)
        self.idIntro.config(bg=COLOR_1, fg=COLOR_4)
        self.idLabel.config(bg=COLOR_3, fg=COLOR_1)
        self.idInput.config(bg="#ffffff", fg=COLOR_1)
        #--------Component place
        self.idFrame.place(relheight=0.3, relwidth=1)
        self.idIntro.place(relheight=0.15, relwidth=0.7, relx=0.15, rely=0.32)
        self.idLabel.place(relheight=0.15, relwidth=0.15, relx=0.15, rely=0.52)
        self.idInput.place(relheight=0.15, relwidth=0.5, relx=0.35, rely=0.52)

        #Action Frame
        self.actFrame = Frame(self.gui)
        self.onlFrame = Frame(self.actFrame)
        self.offFrame = Frame(self.actFrame)
        self.actIntro = Label(self.actFrame, text="LIST OF REGISTED USER")
        
        self.onlIntro = Label(self.onlFrame, text="ONLINE")
        self.offIntro = Label(self.offFrame, text="OFFLINE")
        #-------Component config
        self.onlFrame.config(bg = COLOR_4)
        self.offFrame.config(bg = COLOR_4)
        self.actFrame.config(bg = COLOR_3)
        self.actIntro.config(bg = COLOR_1, fg = COLOR_4)
        self.onlIntro.config(bg = COLOR_4, fg = COLOR_1)
        self.offIntro.config(bg = COLOR_4, fg = COLOR_1)
        #-------Component place
        self.onlFrame.place(relheight=0.55, relwidth=0.35, relx=0.1, rely=0.3)
        self.offFrame.place(relheight=0.55, relwidth=0.35, relx=0.55, rely= 0.3)
        self.actFrame.place(relheight=0.7, relwidth=1, rely=0.3)
        self.actIntro.place(relheight=0.07, relwidth=0.7, relx= 0.15, rely=0.12)
        self.onlIntro.place(relheight=0.1, relwidth=0.6, relx=0.2)
        self.offIntro.place(relheight=0.1, relwidth=0.6, relx=0.2)
        self.onlUser = []
        self.offUser = []


#------------------------ BASIC FUNCTION ---------------------   
    #server-process listen to client
    def listen(self):                           
        while self.curr_client<MAX_CILENT:
            channel,client = self.server_process.accept()
            print(f"Client: {client}")
            try:
                self.curr_client += 1
                thr = threading.Thread(target=self.userHandle, args=(channel,client))
                thr.daemon = False
                thr.start()
            except:
                print("error")
    #server-process recieve message from other
    def recv(self, channel, client):            
        mess = channel.recv(1024).decode(FORMAT)
        return mess
    #server-process send message to other
    def send(self, channel, client, message):   
        channel.sendall(str(message).encode(FORMAT))
    #fucntion support for close the connection
    def onClosing(self):
        self.server_process.close()
        self.gui.destroy()
    #function support for update user list
    def updateUserList(self):
        with open("account.json", "rb") as f:
            jsonFile = json.load(f)
        self.onlUser = {}
        self.offUser = {}
        
        for account in jsonFile["account"]:
            self.onlUser[account["name"]] = Label(self.onlFrame, text=account['name'])
            self.onlUser[account["name"]].config(bg=COLOR_1, fg=COLOR_4)
            self.offUser[account["name"]] = Label(self.offFrame, text=account['name'])
            self.offUser[account["name"]].config(bg=COLOR_1, fg=COLOR_4)

        onlIndex = 0
        offIndex = 0
    
        for widget in self.onlFrame.winfo_children():
            widget.place(relheight=0, relwidth=0)
        for widget in self.offFrame.winfo_children():
            widget.place(relheight=0, relwidth=0)

        self.onlIntro.place(relheight=0.1, relwidth=0.6, relx=0.2)
        self.offIntro.place(relheight=0.1, relwidth=0.6, relx=0.2)
        for account in jsonFile["account"]:
            if account["isAct"] == 1:
                onlIndex+=1
                self.onlUser[account["name"]].place(relheight=0.1, relwidth = 0.8, relx=0.1, rely =  onlIndex*0.15)
            
            else:
                offIndex+=1
                self.offUser[account["name"]].place(relheight=0.1, relwidth = 0.8, relx=0.1, rely =  offIndex*0.15)
                

        with open('account.json','w') as f:
            json.dump(jsonFile,f) 
        pass
    #function support for Authentification    
    def processAccount(self, acc, adr):
        infor = {}
        accInfor=acc.replace("{","").replace("}","").replace("'","").replace(" ","").split(":")
        adrInfor=adr.replace("{","").replace("}","").replace("'","").replace(" ","").split(":")
        infor["name"] = accInfor[0]
        infor["password"] = accInfor[1]
        infor["address"] = adrInfor[0]
        infor["port"] = adrInfor[1]
        infor["isAct"] = 1
        return infor
    def checkAccount(self, jsonFile, jsonObject):
        for account in jsonFile["account"]:
            if account["name"] == jsonObject["name"] and account["password"]==jsonObject["password"]: 
                account["address"] = jsonObject["address"]
                account["port"] = jsonObject["port"]
                account["isAct"] = 1
                return jsonFile, MESS_SUCCESS
        return jsonFile, MESS_FAILURE
    def createAccount(self, jsonFile, jsonObject):
        jsonFile["account"].append(jsonObject)
        return jsonFile, MESS_SUCCESS
    def deactiveAccount(self, userName):
        with open("account.json", "rb") as f:
            jsonFile = json.load(f)
        
        for account in jsonFile["account"]:
            if account["name"] == userName:
                account["isAct"] = 0
        with open('account.json','w') as f:
            json.dump(jsonFile,f)   

        self.updateUserList()
#------------------------ SERVER PROCESS ---------------------
    #FOR ADMIN USER
    # Enforce normal user to  login before allow them to chat with other
    def userHandle(self,channel, client):
        self.userAuthen(channel, client)
        self.updateUserList()
        self.userChat(channel, client)
    # Authentification for normal user
    def userAuthen(self, channel, client):
        acc = None
        mess = None
        while mess!=MESS_SUCCESS:
            print("-------------------------------------------")
            mode = self.recv(channel,client)
            self.send(channel, client, "Received")      # ensure client receive inorder
            acc = self.recv(channel, client)
            self.send(channel, client, "Received")      # ensure client receive inorder
            adr = self.recv(channel , client)
            self.send(channel, client, "Received") 
            
            # Update 
            jsonObject = self.processAccount(acc, adr)
            print(jsonObject)
            with open("account.json", "rb") as f:
                jsonFile = json.load(f)

            print(self.recv(channel , client))
            if int(mode)==MODE_LOGIN: 
                jsonFile, mess = self.checkAccount(jsonFile, jsonObject)
                self.send(channel, client, mess)
            elif int(mode)==MODE_SIGNIN:
                jsonFile, mess = self.createAccount(jsonFile, jsonObject)
                self.send(channel, client, mess)
            print(self.recv(channel, client))

            with open('account.json','w') as f:
                json.dump(jsonFile,f)

            print("-------------------------------------------")
    # Communication with Normal User
    def userChat(self, channel, client):
        friendID = 0
        while friendID != -1:
            print("check")
            if friendID>=-1 or friendID==-2:
                with open("account.json", "rb") as f:
                    jsonFile = json.load(f)
                    self.send(channel, client, json.dumps(jsonFile))
                    self.recv(channel, client)
            
            friendID = int(self.recv(channel, client))
            self.send(channel, client, "Received")


        userName = self.recv(channel, client)
        self.send(channel, client, "Diconnected")
        self.deactiveAccount(userName)
        self.curr_client -= 1
    
    # Admin user just have server-process, which keeps track on database, normal user information

if __name__=="__main__":
    print("Messenger Clone: Admin")
    admin = Admin()
    
    
    threadAct = threading.Thread(target = admin.listen)
    threadAct.daemon= True
    threadAct.start()

    admin.gui.mainloop()
   