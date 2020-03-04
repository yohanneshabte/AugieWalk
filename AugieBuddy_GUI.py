import tkinter
import AugieBuddy_V3 as AB

# constants to keep track of users input
COUNT = 0
startLoc = ""
endLoc = ""

#function to quit the program
def quit():
    global top
    top.destroy()
    
#function that connects AugieBuddy_V3.py and AugieBuddy_GUI.py
def callBack(num,button,x,y):
     global COUNT, startLoc, endLoc
     button.destroy()
     b = tkinter.Button(top, image=cross,anchor="nw",width=25,height=25)
     canvas.create_window(x, y, anchor='nw', window=b)
     if COUNT == 0:
         startLoc = str(num)
         COUNT += 1
     elif COUNT == 1:
         endLoc = str(num)
         AB.main(startLoc,endLoc)
         COUNT = 0
         quit()
    
# create the GUI interface
top = tkinter.Tk()
top.title("Augie Buddy: Optimal route solution for getting around campus!")
top.geometry("700x760")

# setup background image: augie map
canvas = tkinter.Canvas(top, width=800, height=880)
canvas.grid(row=0, column=0)
image2=tkinter.PhotoImage(file='campus_map.gif')
photo = canvas.create_image(20,50,image=image2,anchor="nw")

#numbered icon import and setup to overlay over the background
img1 = tkinter.PhotoImage(file="1.gif")
img1 = img1.subsample(10)
img2 = tkinter.PhotoImage(file="2.gif")
img2 = img2.subsample(10)
img3 = tkinter.PhotoImage(file="3.gif")
img3 = img3.subsample(10)
img4 = tkinter.PhotoImage(file="4.gif")
img4 = img4.subsample(10)
img5 = tkinter.PhotoImage(file="5.gif")
img5 = img5.subsample(10)
img6 = tkinter.PhotoImage(file="6.gif")
img6 = img6.subsample(10)
img7 = tkinter.PhotoImage(file="7.gif")
img7 = img7.subsample(10)
img8 = tkinter.PhotoImage(file="8.gif")
img8 = img8.subsample(10)
img9 = tkinter.PhotoImage(file="9.gif")
img9 = img9.subsample(10)
img10 = tkinter.PhotoImage(file="10.gif")
img10 = img10.subsample(10)
cross = tkinter.PhotoImage(file="cross.gif")
cross = cross.subsample(2)

#create the buttons using the icon and 
b1 = tkinter.Button(top, image=img1,anchor="nw",width=25,height=25,command=lambda: callBack(1,b1,180,570))
b1_image = canvas.create_window(180, 570, anchor='nw', window=b1) #solberg
b2 = tkinter.Button(top, image=img2,anchor="nw",width=25,height=25,command=lambda: callBack(2,b2,230, 600))
b2_image = canvas.create_window(230, 600, anchor='nw', window=b2) #bergsaker
b3 = tkinter.Button(top, image=img3,anchor="nw",width=25,height=25,command=lambda: callBack(3,b3,340, 600))
b3_image = canvas.create_window(340, 600, anchor='nw', window=b3) #froiland
b4 = tkinter.Button(top, image=img4,anchor="nw",width=25,height=25,command=lambda: callBack(4,b4,245, 550))
b4_image = canvas.create_window(245, 550, anchor='nw', window=b4) #Intersection 1
b5 = tkinter.Button(top, image=img5,anchor="nw",width=25,height=25,command=lambda: callBack(5,b5,345, 530))
b5_image = canvas.create_window(345, 530, anchor='nw', window=b5) #madsen center
b6 = tkinter.Button(top, image=img6,anchor="nw",width=25,height=25,command=lambda: callBack(6,b6,245, 460))
b6_image = canvas.create_window(245, 460, anchor='nw', window=b6) #humanites
b7 = tkinter.Button(top, image=img7,anchor="nw",width=25,height=25,command=lambda: callBack(7,b7,330, 470))
b7_image = canvas.create_window(330, 470, anchor='nw', window=b7) #intersection with chapel
b8 = tkinter.Button(top, image=img8,anchor="nw",width=25,height=25,command=lambda: callBack(8,b8,400, 455))
b8_image = canvas.create_window(400, 455, anchor='nw', window=b8) #western studies 
b9 = tkinter.Button(top, image=img9,anchor="nw",width=25,height=25,command=lambda: callBack(9,b9,410, 415))
b9_image = canvas.create_window(410, 415, anchor='nw', window=b9) #library
b10 = tkinter.Button(top, image=img10,anchor="nw",width=25,height=25,command=lambda: callBack(10,b10,325, 380))
b10_image = canvas.create_window(325, 380, anchor='nw', window=b10) #the commons

# create the legend on the top left corner 
labelframe = tkinter.LabelFrame(top,text="Legend",padx=0,pady=0,width=140,height=100)
labelframe.grid(row=0,column=0)
test = canvas.create_window(10,0, anchor='nw', window=labelframe)
tkinter.Label(labelframe, text="1 - Solberg").grid(row=0,column=0,sticky="nw")
tkinter.Label(labelframe, text="2 - Bergsaker").grid(row=1,column=0,sticky="nw")
tkinter.Label(labelframe, text="3 - Froiland").grid(row=2,column=0,sticky="nw")
tkinter.Label(labelframe, text="4 - Intersection 1").grid(row=3,column=0,sticky="nw")
tkinter.Label(labelframe, text="5 - Madsen Center").grid(row=4,column=0,sticky="nw")
tkinter.Label(labelframe, text="6 - Humanities").grid(row=5,column=0,sticky="nw")
tkinter.Label(labelframe, text="7 - Intersection with Chapel").grid(row=6,column=0,sticky="nw")
tkinter.Label(labelframe, text="8 - Western Studies").grid(row=7,column=0,sticky="nw")
tkinter.Label(labelframe, text="9 - Library").grid(row=8,column=0,sticky="nw")
tkinter.Label(labelframe, text="10 - The Commons").grid(row=9,column=0,sticky="nw")

top.mainloop()
