import mysql.connector
from Log import *

def CREATE_NEW_USER(cursor, host, newUser, newPasswd):

    try:
        # CREATE USER
        creation = "CREATE USER '%s'@'%s'" % (newUser, host)
        cursor.execute(creation)

        setpass = "SET PASSWORD FOR '%s'@'%s' = PASSWORD('%s')" % (newUser, host, newPasswd)
        cursor.execute(setpass)

        # GIVE GRANT ACCESS TO CURRENTLY ADDED USER EXCEPT FORBIDDEN TABLE
        try:
            # print(" I am here: ")
            granting = "GRANT ALL PRIVILEGES ON dbmsProject.* TO '%s'@'%s'" % (newUser, host)
            print("GRANTING: " + granting)
            cursor.execute(granting)
        except mysql.connector.Error as e:
            print( e.msg)

        # # REVOKE ACCESS TO FORBIDDEN
        # try:
        #     granting = "REVOKE ALL PRIVILEGES ON dbmsProject.FORBIDDEN FROM '%s'@'%s' " % (newUser, host)
        #     print("REVOKE: " + granting)
        #     cursor.execute(granting)
        # except mysql.connector.Error as e:
        #     print(e.msg)

        msg = "SUCCESS!! User " + str(newUser) + " added to the database"
        print("root: " + msg)
        Log("root" , msg)

    except mysql.connector.Error as e:
        print (e.msg)
        Log("root", e.msg)

def DROP_EXISTING_USER(cursor, host, existingUser):
    try:
        query = "DROP USER '%s'@'%s'" % (existingUser, host)
        cursor.execute(query)

        msg = "SUCCESS!! User " + str(existingUser) + " removed from the database"
        print("root: " + msg)
        Log("root", msg)

    except mysql.connector.Error as e:
        print(e.msg)
        Log("root", e.msg)

def SHOW_ALL_USERS(cursor):
    try:
        query = "SELECT user FROM mysql.user GROUP BY user"
        cursor.execute(query)

        i = 1
        for row in cursor:
            #row = cursor.fetchone()
            print (str(i) + " USER: ", row)
            # Log("root: " + str(row))
            i = i + 1

    except mysql.connector.Error as e:
        print(e.msg)
        Log("root: ", e.msg)


def CREATE_TABLE(cursor, currUser, tableName):
    try:
        query = "CREATE TABLE IF NOT EXISTS %s(uID INT AUTO_INCREMENT PRIMARY KEY, clientName TEXT NOT NULL)" % (tableName)
        cursor.execute(query)
        msg ="SUCCESS!! New table " + str(tableName) + " created"
        print(str(currUser) + " : " + msg)
        Log(str(currUser), msg)

    except mysql.connector.Error as e:
        print(e.msg)
        Log(str(currUser), e.msg)


def SHOW_FORBIDDEN(cursor):
    try:
        query = "SELECT * FROM FORBIDDEN"
        cursor.execute(query)
        # print("ENTRIES \n" )

        i = 1
        for row in cursor:
            #row = cursor.fetchone()
            print ("Entry: " + str(i) + " ", row)
            i = i + 1

    except mysql.connector.Error as e:
        print(e.msg)
        Log("root ", e.msg)