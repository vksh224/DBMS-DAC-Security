import mysql.connector
from Log import *
from utility import *

#https://www.packtpub.com/books/content/granting-access-mysql-python

# =========== ASSUMPTIONS ==============
# 1. Every user has access to the database
# 2. We have 5 users: Marek, Dexter, Baxter, Vijay, Sajjad
# 3. Marek creates Table "CLIENT"
# 4. Marek -> Dexter (with GRANT option)
# 5. Marek -> Baxter (with NO GRANT option)
# 6. Dexter -> Vijay (with GRANT option)

# 7. Command 1: Vijay wants to give GRANT to Sajjad (for CLIENT) - GRANT
# 8. Command 2: Dexter wants to revoke for Vijay (for CLIENT)    - REVOKE
# 9. Command 3: SO adds Dexter to Forbidden
# 10. Run commands GRANT and REVOKE, again


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
    # Check if user is in the FORBIDDEN
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
        # print ("Check access table now")
        try:
            query = "SHOW GRANTS FOR '%s'@'%s'" % (currUser, host)
            print ("QUERY: " + str(query))
            cursor.execute(query)
            results = cursor.fetchone()
            print ("RESULTS " + results[0])

        except mysql.connector.Error as e:
            print (str(currUser) + " : " + e.msg)
            Log(currUser, e.msg)

        if "ALL" in results[0]:
            try:
                print(" I am here: ")
                granting = "GRANT ALL PRIVILEGES ON dbmsProject.%s TO '%s'@'%s'" % (tableName, userName, host)
                print(granting)
                cursor.execute(granting)
                msgToCurrUser = "SUCCESS!! GRANTED ACCESS TO TABLE" + str(tableName) + " by USER: " + str(userName)
                print(str(currUser) + ": " + msgToCurrUser)
                Log(currUser, msgToCurrUser)

            except mysql.connector.Error as e:
                print(str(currUser) + " : " + e.msg)
                Log(currUser, e.msg)

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



# ================ PROGRAM STARTS HERE ==================

hostV = 'localhost'
userV = 'root'
passwdV = 'vijay'
databaseV = "dbmsProject"

userV = input("Username: ")
passwdV = input("Password: ")

print("=========== Welcome " + str(userV) + "==============")

try:
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
        print("2. REVOKE PERMISSION")
        print("3. ADD USER FORBIDDEN")
        print("4. DELETE USER FROM FORBIDDEN")
        print("5. SHOW USERS")
        print("6. CREATE NEW USER")
        print("7. DROP AN EXISTING USER")
        print("8. SHOW FORBIDDEN")
        print("9. Exit \n")

        while (1):
            inputV = input("Command: ")

            if inputV == 'GRANT' or inputV == 'grant':
                print(" \n ===  GRANT ALL PRIVILEGES ==== \n")
                userName = input("User name: ")
                tableName = input("Table name: ")
                GRANT_ALL(cursor, userV, tableName, userName, hostV)
                print("======== END =========== \n")

            elif inputV == 'REVOKE' or inputV == 'revoke':
                print(" \n ===  REVOKE ALL PRIVILEGES ==== \n")
                userName = input("User name: ")
                tableName = input("Table name: ")
                REVOKE_ALL(cursor, userName, tableName)
                print("======== END =========== \n")

            elif inputV == 'ADD':
                userName = input("User name: ")
                tableName = input("Table name: ")
                INSERT_INTO_FORBIDDEN(cursor, userName, tableName)

            elif inputV == 'DELETE' or inputV == 'delete':
                print(" \n ===  DELETE USER FROM FORBIDDEN ==== \n")
                userName = input("User name: ")
                tableName = input("Table name: ")
                DELETE_USER_FROM_FORBIDDEN(cursor, userName, tableName)
                print("======== END =========== \n")

            elif inputV == 'SHOW USERS' or inputV == 'show users' or inputV == 'show U':
                print(" \n ===  LIST OF ALL USERS ==== \n")
                SHOW_ALL_USERS(cursor)
                print("======== END =========== \n")

            elif inputV == 'CREATE' or inputV == 'create':
                print(" \n ===  ADD A NEW USER TO THE DATABASE ==== \n")
                newUser = input("Username: ")
                newPasswd = input("Password: ")
                CREATE_NEW_USER(cursor, hostV, newUser, newPasswd)
                print ("======== END =========== \n")

            elif inputV == 'DROP' or inputV == 'drop':
                print(" \n === REMOVE EXISTING USER FROM THE DATABASE ==== \n")
                existingUser = input("Username: ")
                DROP_EXISTING_USER(cursor, hostV, existingUser)
                print("======== END =========== \n")

            elif (inputV == 'SHOW FORBIDDEN' or inputV == 'show forbidden' or inputV== 'show F'):
                print(" \n === SHOW FORBIDDEN TABLE ==== \n")
                SHOW_FORBIDDEN(cursor)
                print("======== END =========== \n")

            elif inputV == 'EXIT' or inputV == 'exit':
                break

            else:
                print("Wrong input, please try again: \n")


    # IF OTHER USER
    else:
        print("============ MENU ================ ")
        print("1. GRANT PERMISSION")
        print("2. REVOKE PERMISSION")
        print("3. CREATE TABLE")
        print("4. Exit")


        while (1):
            inputV = input("Command: ")

            if inputV == 'GRANT' or inputV == 'grant':
                print(" \n ===  GRANT ALL PRIVILEGES ==== \n")
                userName = input("User name: ")
                tableName = input("Table name: ")
                GRANT_ALL(cursor, userV, tableName, userName, hostV)
                print("======== END =========== \n")

            elif inputV == 'REVOKE' or inputV == 'revoke':
                print("REVOKE ALL ACCESS: ")
                userName = 'sajjad1'
                tableName = 'CLIENT'
                REVOKE_ALL(cursor, userName, tableName)

            elif inputV == 'CREATE' or inputV == 'create':
                print(" \n === CREATE A NEW TABLE ==== \n")
                tableName = input("Table name: ")
                CREATE_TABLE(cursor, userV, tableName)
                print("======== END =========== \n")

            elif inputV == 'EXIT' or inputV == 'exit':
                break

            else:
                print("Wrong input, please try again: \n")


    #CREATE_NEW_USER(cursor, hostV, user2, passwd2)
    #REVOKE_ALL(cursor, hostV, user1)

except mysql.connector.Error as e:
    print(e.msg)