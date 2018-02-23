# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 13:43:06 2018

@author: Sajjad Fouladvad
"""

import tkinter as tk
import tkinter.messagebox
top = tk.Tk()
top.title("Log in window")
top.geometry('300x150')
def printsomething(event):
    print("Helllo world..")

def showwarning(event):
    if txt_bx_name.get() == "VijaD" and txt_bx_pass.get() == "123":
        tk.messagebox.showinfo("SO Warning","Welcome!")
    else:
        tk.messagebox.showinfo("SO Warning","Access denied!")
    
btn_prt=tk.Button(top, text="click me to print")
btn_prt.bind("<Button-1>",printsomething)

btn_showinf=tk.Button(top, text="Log In")
btn_showinf.bind("<Button-1>",showwarning)


txt_bx_name=tk.Entry(top)
txt_bx_pass=tk.Entry(top)

txt_bx_name.pack()
txt_bx_pass.pack()
btn_showinf.pack()
btn_prt.pack()

top.mainloop()
