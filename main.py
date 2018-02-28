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

    #Root creates Forbidden table for one time
    if userV == 'root':
        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS FORBIDDEN(
            uID INT AUTO_INCREMENT PRIMARY KEY,
            userName TEXT NOT NULL,
            tableName TEXT NOT NULL)""")
        except mysql.connector.Error as e:
            print( "root : FORBIDDEN TABLE - " + e.msg)
            Log("root : FORBIDDEN TABLE - ", e.msg)

        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS ASSIGNED(
            uID INT AUTO_INCREMENT PRIMARY KEY,
            userName TEXT NOT NULL,
            tableName TEXT NOT NULL,
            grantBit INT NOT NULL)""")
        except mysql.connector.Error as e:
            print("root : ASSIGNED TABLE - " + e.msg)
            Log("root: ASSIGNED TABLE - ", e.msg)

        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS ACCESS(
            uID INT AUTO_INCREMENT PRIMARY KEY,
            grantorName TEXT NOT NULL,
            granteeName TEXT NOT NULL,
            tableName TEXT NOT NULL,
            grantBit INT NOT NULL)""")
        except mysql.connector.Error as e:
            print("root: ACCESS TABLE - " + e.msg)
            Log("root: ACCESS TABLE - ", e.msg)


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

        firstAttempt = 0
        while (1):
            inputV = input("Command: ")

            if inputV == 'GRANT' or inputV == 'grant':
                print(" \n ===  GRANT ALL PRIVILEGES ==== \n")
                userName = input("User name: ")
                tableName = input("Table name: ")
                grantOption = input("grant option? (1/0) ")
                GRANT_ALL(mydb, cursor, userV, tableName, userName, hostV, grantOption)
                print("======== END =========== \n")

            elif inputV == 'REVOKE' or inputV == 'revoke':
                print(" \n ===  REVOKE ALL PRIVILEGES ==== \n")
                userName = input("User name: ")
                tableName = input("Table name: ")
                REVOKE_ALL(mydb, cursor, userV, userName, tableName)
                print("======== END =========== \n")

            elif inputV == 'ADD' or inputV == 'add':
                userName = input("User name: ")
                tableName = input("Table name: ")
                firstAttempt = firstAttempt + 1
                INSERT_INTO_FORBIDDEN(mydb, cursor, userName, tableName, firstAttempt)

            elif inputV == 'DELETE' or inputV == 'delete':
                print(" \n ===  DELETE USER FROM FORBIDDEN ==== \n")
                userName = input("User name: ")
                tableName = input("Table name: ")
                DELETE_USER_FROM_FORBIDDEN(mydb, cursor, userName, tableName)
                print("======== END =========== \n")

            elif inputV == 'SHOW USERS' or inputV == 'show users' or inputV == 'show U':
                print(" \n ===  LIST OF ALL USERS ==== \n")
                SHOW_ALL_USERS(cursor)
                print("======== END =========== \n")

            elif inputV == 'CREATE' or inputV == 'create':
                print(" \n ===  ADD A NEW USER TO THE DATABASE ==== \n")
                newUser = input("Username: ")
                newPasswd = input("Password: ")
                # grantOption = input("grant option? (Y/N) ")
                CREATE_NEW_USER(cursor, hostV, newUser, newPasswd, grantOption)
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
        print("4. SHOW  A CERTAIN TABLE ")
        print("5. Exit")

        while (1):
            inputV = input("Command: ")

            if inputV == 'GRANT' or inputV == 'grant':
                print(" \n ===  GRANT ALL PRIVILEGES ==== \n")
                userName = input("User name: ")
                tableName = input("Table name: ")
                grantOption = int(input("grant option? (1/0) "))
                GRANT_ALL(mydb, cursor, userV, tableName, userName, hostV, grantOption)
                print("======== END =========== \n")

            elif inputV == 'REVOKE' or inputV == 'revoke':
                print(" \n ===  REVOKE ALL PRIVILEGES ==== \n")
                userName = input("User name: ")
                tableName = input("Table name: ")
                REVOKE_ALL(mydb, cursor, userV, userName, tableName)
                print("======== END =========== \n")

            elif inputV == 'CREATE' or inputV == 'create':
                print(" \n === CREATE A NEW TABLE ==== \n")
                tableName = input("Table name: ")
                CREATE_TABLE(mydb, cursor, userV, tableName)
                print("======== END =========== \n")

            elif (inputV == 'SHOW TABLE' or inputV == 'show table' or inputV== 'show T'):
                print(" \n === SHOW TABLE ==== \n")
                tableName = input("Table name: ")
                SHOW_TABLE(cursor, tableName, userV)
                print("======== END =========== \n")


            elif inputV == 'EXIT' or inputV == 'exit':
                break

            else:
                print("Wrong input, please try again: \n")

except mysql.connector.Error as e:
    print(e.msg)