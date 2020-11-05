# !/usr/bin/python
# A looping python script that takes user input to automate the
# process of adding games to the games.txt file. Up to 10 games
# can be added at once.

loopNUMraw = input("How many games are you planning on adding? (max:10) ")
loopNUM = int(loopNUMraw)
a = 10
b = 0
while a >= loopNUM > b:
	gameID = input("Type the game identifier here: ")
	gameNAME = input("Type the game's full name here: ")

	print("")
	print(gameID + "_00 " + "#" + " " + gameNAME)
	loopNUM = loopNUM - 1
	print("")
	file1 = open("games.txt","a")
	file1.write(gameID + "_00 " + "#" + " " + gameNAME)
	file1.write("\n")
input("Here's what I just added to your game.txt file. Press any key to exit.")
