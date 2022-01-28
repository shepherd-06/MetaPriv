import os
import tkinter as tk
from base64 import b64encode
# imports from created files 
from crypto import Hash, aes_encrypt
from password_class import Create_Password_UI


INFO_TEXT = """Welcome to MetaPriv!
This is your first run, so please input your
facebook credentials, a seed keyword and the 
browser you mostly use (Firefox or Chrome). 
This is a one time input, as new keywords 
will be generated automatically and the 
login will happen from a browser profile 
folder after the first run.\n"""

class First_launch_UI:
	def __init__(self):
		self.choose_password()
		self.mainwindow = tk.Tk()
		self.mainwindow.title("Choose options")
		self.mainwindow.resizable(False, False)
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)

		#Labels
		tk.Label(self.mainwindow, text=INFO_TEXT).grid(row=0, column=0,columnspan=2)
		tk.Label(self.mainwindow, text="Facebook Credentials:").grid(row=1, column=0,columnspan=2)

		#Entry boxes
		tk.Label(self.mainwindow, text="Email: ").grid(row=2, column=0)
		self.Email = tk.Entry(self.mainwindow)
		self.Email.grid(row=2, column=1)

		tk.Label(self.mainwindow, text="Password: ").grid(row=3, column=0)
		self.Password = tk.Entry(self.mainwindow,show='*')
		self.Password.grid(row=3, column=1)

		self.hidden = True
		self.check_box = tk.Checkbutton(self.mainwindow, text='Show password', command=self.showpass).grid(row=4, columnspan=2)

		tk.Label(self.mainwindow, text="keyword: ").grid(row=5, column=0)
		self.Keyword = tk.Entry(self.mainwindow)
		self.Keyword.grid(row=5, column=1)

		self.browser = tk.StringVar()
		R1 = tk.Radiobutton(self.mainwindow, text="Chrome", variable=self.browser, value='Chrome').grid(row=6, column=0)
		R2 = tk.Radiobutton(self.mainwindow, text="Firefox", variable=self.browser, value='Firefox').grid(row=6, column=1)

		self.comment = tk.Label(self.mainwindow, text="")
		self.comment.grid(row=7, column=0)

		#Buttons
		self.continue_button = tk.Button(self.mainwindow, text="Continue", 
			command=self.continue_to_next_window).grid(row=7, column=1)

	def showpass(self):
		if self.hidden:
			self.Password.configure(show='')
			self.hidden = False
		else:
			self.Password.configure(show='*')
			self.hidden = True

	def continue_to_next_window(self):
		if self.Email.get() == '':
			self.comment.configure(text="Input Email.")
			return
		if self.Password.get() == '':
			self.comment.configure(text="Input Password.")
			return
		if self.Keyword.get() == '':
			self.comment.configure(text="Input Keyword.")
			return
		if self.browser.get() == '':
			self.comment.configure(text="Choose Browser.")
			return
		with open('.saved_data','w') as f:
			f.write(self.Email.get()+'\n')
			f.write(aes_encrypt(self.Password.get(),self.h_password)+'\n')
			f.write(self.Keyword.get()+'\n')
			f.write(self.browser.get()+'\n')
			f.write(self.salt+'\n')
			f.write(b64encode(self.h_salted_password).decode('utf-8'))
		self.mainwindow.destroy()

	def start(self):
		self.mainwindow.mainloop()

	def close(self):
		exit()

	def choose_password(self):
		passwrd_class = Create_Password_UI(None)
		passwrd_class.title("Choose password")
		passwrd_class.resizable(False, False)
		passwrd_class.mainloop()
		self.salt = b64encode(os.urandom(32)).decode('utf-8')
		#print(self.salt)
		self.h_password = Hash(passwrd_class.password)
		self.h_salted_password = Hash(self.salt + passwrd_class.password)
		#print(self.h_password)
		passwrd_class.stop()
		del passwrd_class
