"""
Please ensure that "manual.txt" is in the same directory as this shell, thank you.

"""

from cmd import Cmd
import os
import sys
import subprocess
from multiprocessing import Process, Lock

class MyShell(Cmd):

	def overwrite(self, args, output):

		"""The idea behind this function was to use it for all internal commands that allowed i/o redirection
			However as you will soon find out I didn't make this happen, but at least is easily improveable!
		"""

		if ">>" in args:
			args = args.split()
			with open(args[-1], "a+") as f: # a+ for appending
				f.write(output)
				f.close()

		elif ">" in args:
			args = args.split()
			with open(args[-1], "w+") as f: # w+ for overwriting
				f.write(output)
				f.close()

		else:
			print(output) # if there's not overwriting / appending necessary, just print

	def do_cd(self, args):
		"""cd <directory> allows you to move directory, cd.. moves you back one directory, cd on it's own tells you what directory you're in"""
		try:
			os.chdir(args)
			self.prompt = "Turtle:~" + os.getcwd() + ">" # change the prompt as we move directories
			os.environ["PWD"] = os.getcwd() # change the PWD environment string too
		except:
			if args:
				print ("Cannot find directory {}".format(args)) # if there's an argument that isn't a directory in the CWD
			else:
				print (os.getcwd()) # if no arguments are giving, return the CWD

	def do_clr(self, args):
		"""clr removes all previous commands from the terminal"""
		print("\033c",end="") # \033c is ASCII code for "esc" and "c" which most linux ternimals interpret as a call to clear the screen. DOES NOT WORK ON WINDOWS
		return

	def do_dir(self, args):
		"""dir <directory> tells you what's in a certain directory, dir on it's own tells you what's in your cwd"""

		if ">>" in args: # if we're appending to a file
			args = args.split()
			with open(args[-1], "a+") as f:
				for files in os.listdir("."):
					f.write(files + "\n")
				f.close()

		elif ">" in args: # if we're overwriting a file
			args = args.split()
			with open(args[-1], "w+") as f:
				for files in os.listdir("."):
					f.write(files + "\n")
				f.close()

		else: # if we're just printing
			try:
				if args:
					files = os.listdir(args)
				else:
					files = os.listdir(".")
				for f in files:
					print(f)
			except: # if the directory doesn't exist
				print ("Cannot find directory {}".format(args))
			

	def do_environ(self, args):
		"""environ shows the environment strings."""

		def sorter(t): # This is to sort the environment string by alphabetical order
			return t[0]

		output = ""
		for k,v in sorted(os.environ.items(), key=sorter):
			output += k + v + "\n"
		self.overwrite(args, output) # the one time I got the overwrite function to work

	def do_echo(self, args):
		"""echo <message? repeats the message"""

		if ">>" in args: # if we're appending to a file
			args = args.split()
			arg = "".join(args[0:-2])
			with open(args[-1], "a+") as f:
				f.write(arg)
				f.close()

		elif ">" in args: # if we're overwriting a file
			args = args.split()
			arg = "".join(args[0:-2])
			with open(args[-1], "w+") as f:
				f.write(arg)
				f.close()

		else: # otherwise just print
			print(" ".join(args.split()))

	def do_pause(self, args):
		"""Pauses the shell, it ignores all inputs untill enter is entered."""

		try: # try brought in here so that the pause can only be unpaused by ENTER and not broken with a "ctrl + c"  or "ctrl + d"
			input("press 'Enter' to unpause..")
		except (KeyboardInterrupt, EOFError):
			print()

	def do_quit(self, args):
		"""Quits the program."""
		print ("Quitting.")
		raise SystemExit

	def do_help(self, args):
		"""The manual for this shell, it's not perfect you need to input a space character, rather than just being able to hit the spacebar to continue"""

		if ">>" in args: # for appending to a file
			args = args.split()
			with open(args[-1], "a+") as f: # file we're appending to
				with open("manual.txt", "r") as h: # help file
					h = h.readlines()
					h = "".join(h)
					f.write(h)
				f.close()

		elif ">" in args: # for overwriting a file
			args = args.split()
			with open(args[-1], "w+") as f: # file we're overwriting
				with open("manual.txt", "r") as h: # help file
					h = h.readlines()
					h = "".join(h)
					f.write(h)
				f.close()

		else: # for printing the file
			start = 0 # the start of the 20 line block of text
			finish = 20 # then end of the 20 line block of text

			with open("manual.txt", "r") as man: # open the help file
				man = man.readlines()

			print("".join(man[start:finish]), end="") # print the first 20 lines
			while True: # while we've still got more of the help file to read
				if input() == " ": # if space bar is entered (rather than if spacebar is pressed)
					start += 20 # move 20 lines up the help file
					finish += 20 
					if finish > len(man): # if finish is bigger than the length of the help file, change it so that it doesn't go off then end
						finish = len(man)
						print("".join(man[start:finish]), end="\n")
						return # exit the while loop
					else:
						print("".join(man[start:finish]), end="\n")


	def emptyline(self, args=None):
		"""Found an unusual bug where if I entered a command (say dir) if I then entereed an empty string afterwards, it would do dir again instead of giving me a new line.
		 	This is my was of dealing with it"""

		print("",end="")

	def fork(self, args, lock):
		"""Function to allow to me to fork things (goes hand in hand with default)"""

		try:
			lock.acquire() # get the lock for the process
			os.system(args) # do the process
			lock.release() # release the lock
		except:
			print("Command not found") # if the command doesn't exist

	def default(self, args):
		try:
			lock = Lock() # introduce the lock
			p = Process(target=self.fork, args=(args, lock)) # create a new process for the forking to take place
			p.start() # start the process
			p.join() # make sure that the process is done before the shell can interrupt it
		except:
			print(args + " is not a valid command") # if it's not a valid command


if __name__ == "__main__":

	prompt = MyShell()
	prompt.prompt = "Turtle:~" + os.getcwd() + ">" # making the terminal promt the CWD, with a nice little nickname
	os.environ["SHELL"] = os.getcwd() # changing the SHELL environment string
	if len(sys.argv) > 1: # if there's a batchfile being entered on startup
		try:
			with open(sys.argv[1], "r") as f: # read the batchfile
				lines = f.readlines()
				for line in lines:
					prompt.onecmd(line) # excecute the batchfile using the shell's toold
		except FileNotFoundError as fe: # if the batchfiles not found
			if fe:
				print("Could not read from batchfile\n")

	prompt.cmdloop("Starting shell...") # Start the shell properly
