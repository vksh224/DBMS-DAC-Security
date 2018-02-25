import mysql.connector
from Log import *

#https://www.packtpub.com/books/content/granting-access-mysql-python

def CREATE_NEW_USER(cursor, host, newUser, newPasswd):

    try:
        creation = "CREATE USER '%s'@'%s'" % (newUser, host)
        results = cursor.execute(creation)
        print("User creation returned ", results)

        setpass = "SET PASSWORD FOR '%s'@'%s' = PASSWORD('%s')" % (newUser, host, newPasswd)
        results = cursor.execute(setpass)
        print("Setting of password returned ", results)

    except mysql.connector.Error as e:
        print (e.msg)

def CHECK_IF_USER_EXISTS(cursor, tableName, userName):
    try:
        query = "SELECT count(*) FROM FORBIDDEN where userName = '%s' and tableName = '%s'" %(userName, tableName)
        cursor.execute(query)
        results = cursor.fetchone()
        # print (query)
        # print("Results: "  + str(results[0]))
    except mysql.connector.Error as e:
        print (e.msg)

    return results[0]

def GRANT_ALL(cursor, currUser, tableName, userName, host):

    rowCount = CHECK_IF_USER_EXISTS(cursor, tableName, userName)

    if rowCount > 1: #Multiple entries
        msgToCurrUser = "Something is wrong. Contact Security Officer for resolving the issue."
        print (msgToCurrUser)
        Log(currUser, msgToCurrUser)

    elif rowCount == 1: #Exists in table - single entry
        msgToCurrUser = "Grant of access to " + str(tableName) + " by " + str(userName) +" is unacceptable "
        msgToRoot = str(currUser) + " attempted to provide an access to " + str(userName) + " to a restricted table " + str(tableName)
        print (msgToCurrUser)
        Log(str(currUser), msgToCurrUser)
        Log("Root ", msgToRoot)

    else:
        print ("Check access table now")
        try:
            granting = "GRANT ALL ON *.'%s' TO '%s'@'%s'" % (tableName, userName, host)
            results = cursor.execute(granting)
            print ("Granting of privileges returned" + str(results))

        except mysql.connector.Error as e:
            print (e.msg)


def REVOKE_ALL(cursor, tableName, newUser, host):
    try:
        granting = "REVOKE ALL PRIVILEGES ON *.'%s' FROM '%s'@'%s'" % (tableName, newUser, host)
        results = cursor.execute(granting)
        print ("Revoking of privileges returned", results)

    except mysql.connector.Error as e:
        print(e.msg)


def INSERT_INTO_FORBIDDEN(cursor, newUser, tableName):
    try:
        query ="INSERT INTO FORBIDDEN VALUES(NULL, '%s', '%s')" %(newUser, tableName)
        results = cursor.execute(query)
        print("Successfully inserted", results)
        mydb.commit()
    except mysql.connector.Error as e:
        print(e.msg)



hostV = 'localhost'
userV = 'root'
passwdV = 'vijay'
databaseV = "dbmsProject"

# userV = input("Username: ")
# passwdV = input("Password: ")

print("=========== Welcome " + str(userV) + "==============")

mydb = mysql.connector.connect(host=hostV, user=userV, passwd=passwdV, database=databaseV)
cursor = mydb.cursor()

user1 = "sajjad1"
passwd1 = "sajjad1"

user2 = "vijay1"
passwd2 = "vijay1"


#Root creates Forbidden table for one time
if userV == 'root':
    cursor.execute("""CREATE TABLE IF NOT EXISTS FORBIDDEN(
    uID INT AUTO_INCREMENT PRIMARY KEY,
    userName TEXT NOT NULL,
    tableName TEXT NOT NULL)""")
    mydb.commit()


if userV == 'root':
    print("============ MENU ================ \n ")
    print("1. GRANT PERMISSION")
    print("3. ADD A USER TO FORBIDDEN TABLE")
    print("4. Exit \n")

    while (1):
        inputV = int(input("Choose an option: "))

        if inputV == 1:
            print("\n GRANT ALL ACCESS: \n")
            # userName = input("User name: ")
            # tableName = input("Table name: ")
            userName = 'sajjad1'
            tableName = 'CLIENT'
            GRANT_ALL(cursor, userV, tableName, userName, hostV)

        elif inputV == 2:
            print("\n REVOKE ALL ACCESS: \n")
            # userName = input("User name: ")
            # tableName = input("Table name: ")
            userName = 'sajjad1'
            tableName = 'CLIENT'
            REVOKE_ALL(cursor, userName, tableName)

        elif inputV == 3:
            userName = input("User name: ")
            tableName = input("Table name: ")

            INSERT_INTO_FORBIDDEN(cursor, userName, tableName)

        elif inputV == 4:
            break

        else:
            print("Wrong input, please try again: \n")


else:
    print("============ MENU ================ ")
    print("1. GRANT PERMISSION")
    print("2. REVOKE PERMISSION")
    print("3. Exit")


    while (1):
        inputV = int(input("Choose an option"))

        if inputV == 1:
            print("GRANT ALL ACCESS: ")
            # userName = input("User name: ")
            # tableName = input("Table name: ")
            userName = 'sajjad1'
            tableName = 'CLIENT'
            GRANT_ALL(cursor, tableName, userName, hostV)

        elif inputV == 2:
            print("REVOKE ALL ACCESS: ")
            # userName = input("User name: ")
            # tableName = input("Table name: ")
            userName = 'sajjad1'
            tableName = 'CLIENT'
            REVOKE_ALL(cursor, userName, tableName)

        elif inputV == 3:
            break

        else:
            print("Wrong input, please try again: \n")

        inputV = input("Choose an option")
#CREATE_NEW_USER(cursor, hostV, user2, passwd2)
#REVOKE_ALL(cursor, hostV, user1)