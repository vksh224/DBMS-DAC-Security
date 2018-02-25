def Log(userName, logStr):
    with open("Log.txt" ,"a") as fp:
        fp.write(str(userName) +": " + str(logStr) + "\n")
    fp.close()