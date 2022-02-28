import sys
import tkinter as tk
from crypto import Hash
from base64 import b64encode


class Create_Password_UI(tk.Tk):
	def __init__(self, parent):
		tk.Tk.__init__(self,parent)
		self.parent = parent
		# Window options
		self.protocol('WM_DELETE_WINDOW', self.close)

		# Info
		tk.Label(self, text="Choose a strong password\n with minimum 8 characters").grid(row=0, columnspan=3)
		self.grid()

		# Create password
		tk.Label(self, text="Choose a password: ").grid(row=1, column=0)
		self.Password = tk.Entry(self,show='*')
		self.Password.grid(row=1, column=1, columnspan=2)

		tk.Label(self, text="Repeat password: ").grid(row=2, column=0)
		self.r_Password = tk.Entry(self,show='*')
		self.r_Password.grid(row=2, column=1, columnspan=2)
		self.hidden = True

		# Invalid input comment
		self.comment = tk.Label(self, text="")
		self.comment.grid(row=3, column=0)

		# Show/hide password
		self.check_box = tk.Checkbutton(self, text='Show password', command=self.showpass).grid(row=3, column=1)
		# Continue button
		self.OK_button = tk.Button(self, text="Continue", command=self.check_pass).grid(row=3, column=2)

	def showpass(self):
		# Show/hide password
		if self.hidden:
			self.Password.configure(show='')
			self.r_Password.configure(show='')
			self.hidden = False
		else:
			self.Password.configure(show='*')
			self.r_Password.configure(show='*')
			self.hidden = True

	def check_pass(self):
		# Check if passwords match
		self.password = self.Password.get()
		self.r_password = self.r_Password.get()

		if self.password != self.r_password:
			self.comment.configure(text="No match, retry!")
		elif len(self.password) < 8:
			self.comment.configure(text="Min 8 characters!")
		else:
			self.quit()

	def stop(self):
		self.destroy()

	def close(self):
		sys.exit()

class Enter_Password_UI(tk.Tk):
	def __init__(self, parent):
		tk.Tk.__init__(self,parent)
		self.parent = parent
		# Window options
		self.protocol('WM_DELETE_WINDOW', self.close)
		self.grid()

		# Input password
		tk.Label(self, text="Enter password: ").grid(row=1, column=0)
		self.Password = tk.Entry(self,show='*')
		self.Password.grid(row=1, column=1, columnspan=2)
		self.hidden = True

		# Invalid input comment
		self.comment = tk.Label(self, text="")
		self.comment.grid(row=2, column=0)

		# Show/hide password
		self.check_box = tk.Checkbutton(self, text='Show password', command=self.showpass).grid(row=2, column=1)
		# Continue button
		self.OK_button = tk.Button(self, text="Continue", command=self.check_pass).grid(row=2, column=2)

	def showpass(self):
		# Show/hide password
		if self.hidden:
			self.Password.configure(show='')
			self.hidden = False
		else:
			self.Password.configure(show='*')
			self.hidden = True

	def check_pass(self):
		# Check password by encrypting the salt + input
		with open('.saved_data','r') as f:
			text = f.read()
			text = text.split('\n')
			salt = text[4]
			h_salted_password_compare = text[5]

		self.password = self.Password.get()
		h_salted_password = b64encode(Hash(salt + self.password)).decode('utf-8')

		if h_salted_password != h_salted_password_compare:
			self.comment.configure(text="Wrong password, retry!")
		else:
			self.h_password = Hash(self.password)
			self.quit()

	def stop(self):
		self.destroy()

	def close(self):
		exit()