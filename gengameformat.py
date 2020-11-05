# !/usr/bin/python
# A looping python script that takes user input to automate the
# process of adding games to the games.txt file. Up to 10 games
# can be added at once.

import os
import shutil
print("Welcome to the PlayStationDiscord game automator.")
print("")
loopNUMraw = input("How many games are you planning on adding? (max:100) ")
loopNUM = int(loopNUMraw)
a = 100
b = 0
while a >= loopNUM > b:
#	Let's gather the gameID and gameNAME and set our variables for later.
	gameID = input("Type the game identifier here: ")
	gameNAME = input("Type the game's full name here: ")
	print("")
#	Showing you how it's supposed to look.
	print(gameID + "_00 " + "#" + " " + gameNAME)
	input("This is what you typed. Press any key to confirm.")
	loopNUM = loopNUM - 1
	print("")
#	Begin appending the game.txt file.
	file1 = open("games.txt","a")
	file1.write(gameID + "_00 " + "#" + " " + gameNAME)
	file1.write("\n")
#	Asks for the games.png file to copy into the /ps4 folder.
	print("Drag you game's icon into this folder and rename it to game.png.")
	input("Press any key to continue.")
	old_file_name = "game.png"
	new_file_name = ("ps4/" + gameID + "_00.png")
	os.rename(old_file_name, new_file_name)
	print("")
#	Showing you that it's done copying.
	print("I just moved the icon into the right spot with the right name.")
#	Final notes
input("This automator finished the copy process sucessfully. Press any key to exit.")
