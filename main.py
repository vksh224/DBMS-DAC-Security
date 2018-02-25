import mysql.connector
from Log import *

#https://www.packtpub.com/books/content/granting-access-mysql-python

def SHOW_ALL_USERS(cursor):
    try:
        query = "SELECT user FROM mysql.user GROUP BY user"
        cursor.execute(query)
        print("ALL USERS \n" )

        i = 1
        for row in cursor:
            #row = cursor.fetchone()
            print (str(i) + ". USER: ", row)
            i = i + 1

    except mysql.connector.Error as e:
        print(e.msg)

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
        msgToCurrUser = "Something is wrong. Contact Security Officer to resolve the issue."
        print (msgToCurrUser)
        Log(currUser, msgToCurrUser)

    elif rowCount == 1: #Exists in table - single entry
        msgToCurrUser = "Grant of access to " + str(tableName) + " by " + str(userName) +" is unacceptable"
        msgToRoot = "Attempted to provide an access to " + str(userName) + " to a restricted table " + str(tableName)
        print(str(currUser) + " : " + msgToCurrUser)
        Log(str(currUser), msgToCurrUser)
        Log("Root ", msgToRoot)

    else:
        print ("Check access table now")
        try:
            query = "SHOW GRANTS FOR '%s'@'%s'" % (currUser, host)
            print ("SHOW GRANT QUERY: " + str(query))
            cursor.execute(query)
            results = cursor.fetchone()
            print ("RESULTS " + str(results))

            try:
                granting = "GRANT ALL ON *.'%s' TO '%s'@'%s'" % (tableName, userName, host)
                cursor.execute(granting)
                msgToCurrUser = "SUCCESS!! GRANTED ACCESS TO TABLE" + str(tableName) + " by USER: " + str(userName)
                print(str(currUser) + ": " + msgToCurrUser)
                Log(currUser, msgToCurrUser)

            except mysql.connector.Error as e:
                print(e.msg)

        except mysql.connector.Error as e:
            print (e.msg)
            Log(currUser, e.msg)


def REVOKE_ALL(cursor, tableName, newUser, host):
    try:
        granting = "REVOKE ALL PRIVILEGES ON *.'%s' FROM '%s'@'%s'" % (tableName, newUser, host)
        results = cursor.execute(granting)
        print ("Revoking of privileges returned", results)

    except mysql.connector.Error as e:
        print(e.msg)


def SHOW_FORBIDDEN(cursor):
    try:
        query = "SELECT * FROM FORBIDDEN"
        cursor.execute(query)
        print("ENTRIES \n" )

        i = 1
        for row in cursor:
            #row = cursor.fetchone()
            print ("Entry: " + str(i) + " ", row)
            i = i + 1

    except mysql.connector.Error as e:
        print(e.msg)

def INSERT_INTO_FORBIDDEN(cursor, newUser, tableName):
    try:
        query ="INSERT INTO FORBIDDEN VALUES(NULL, '%s', '%s')" %(newUser, tableName)
        cursor.execute(query)
        msg = "SUCCESS!! Entry for " + str(userName) + " for " + str(tableName) + " is successfully deleted from FORBIDDEN"
        print("root : " + msg)
        Log("root", msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(e.msg)
        Log("root", e.msg)

def DELETE_USER_FROM_FORBIDDEN(cursor, newUser, tableName):
    try:
        query = "DELETE FROM FORBIDDEN where userName ='%s' and tableName = '%s'" % (newUser, tableName)
        cursor.execute(query)
        msg = "SUCCESS!! Entry for " + str(userName) + " for " + str(tableName) + " is successfully deleted from FORBIDDEN"
        print("root : " + msg)
        Log("root", msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(e.msg)
        Log("root", e.msg)

hostV = 'localhost'
userV = 'root'
passwdV = 'vijay'
databaseV = "dbmsProject"

# userV = input("Username: ")
# passwdV = input("Password: ")

print("=========== Welcome " + str(userV) + "==============")

try:
    mydb = mysql.connector.connect(host=hostV, user=userV, passwd=passwdV, database=databaseV)
    cursor = mydb.cursor()

    user1 = "sajjad1"
    passwd1 = "sajjad1"

    user2 = "vijay1"
    passwd2 = "vijay1"

    SHOW_FORBIDDEN(cursor)

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
        print ("2. REVOKE PERMISSION")
        print("3. ADD USER FORBIDDEN")
        print("4. DELETE USER FROM FORBIDDEN")
        print("5. SHOW ALL USERS")
        print("6. Exit \n")

        while (1):
            inputV = int(input("Choose an option: "))

            if inputV == 1:
                print("\n GRANT ALL ACCESS: \n")
                # userName = input("User name: ")
                # tableName = input("Table name: ")
                userName = 'vijay2'
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
                userName = input("User name: ")
                tableName = input("Table name: ")
                DELETE_USER_FROM_FORBIDDEN(cursor, userName, tableName)

            elif inputV == 5:
                SHOW_ALL_USERS(cursor)

            elif inputV == 6:
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
                GRANT_ALL(cursor, userV, tableName, userName, hostV)

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

except mysql.connector.Error as e:
    print(e.msg)