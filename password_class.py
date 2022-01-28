import tkinter as tk


class Create_Password_UI(tk.Tk):
	def __init__(self, parent):
		tk.Tk.__init__(self,parent)
		self.parent = parent
		self.protocol('WM_DELETE_WINDOW', self.close)
		tk.Label(self, text="Choose a strong password\n with minimum 8 characters").grid(row=0, columnspan=3)
		self.grid()

		tk.Label(self, text="Choose a password: ").grid(row=1, column=0)
		self.Password = tk.Entry(self,show='*')
		self.Password.grid(row=1, column=1, columnspan=2)

		tk.Label(self, text="Repeat password: ").grid(row=2, column=0)
		self.r_Password = tk.Entry(self,show='*')
		self.r_Password.grid(row=2, column=1, columnspan=2)
		self.hidden = True

		self.comment = tk.Label(self, text="")
		self.comment.grid(row=3, column=0)

		self.check_box = tk.Checkbutton(self, text='Show password', command=self.showpass).grid(row=3, column=1)
		self.OK_button = tk.Button(self, text="continue", command=self.check_pass).grid(row=3, column=2)

	def showpass(self):
		if self.hidden:
			self.Password.configure(show='')
			self.r_Password.configure(show='')
			self.hidden = False
		else:
			self.Password.configure(show='*')
			self.r_Password.configure(show='*')
			self.hidden = True

	def check_pass(self):
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
		exit()