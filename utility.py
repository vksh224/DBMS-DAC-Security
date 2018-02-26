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
            granting = "GRANT ALL ON dbmsProject.* TO '%s'@'%s'" % (newUser, host)
            print("GRANTING: " + granting)
            cursor.execute(granting)
            granting = "GRANT SELECT ON dbmsProject.FORBIDDEN TO '%s'@'%s'" % (newUser, host)
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
        # GIVE GRANT ACCESS TO CURRENTLY ADDED USER EXCEPT FORBIDDEN TABLE
        try:
            # print(" I am here: ")
            granting = "GRANT ALL PRIVILEGES ON dbmsProject.%s TO '%s'@'localhost'" % (tableName, currUser)
            print("GRANTING: " + granting)
            cursor.execute(granting)
        except mysql.connector.Error as e:
            print(e.msg)

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


def GRANT_ALL(cursor, currUser, tableName, userName, host, grantOption):
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
            print ("RESULTS: " + results[0])

        except mysql.connector.Error as e:
            print (str(currUser) + " : " + e.msg)
            Log(currUser, e.msg)

        if "ALL" in results[0]:
            try:
                if grantOption == 'Y' or grantOption == 'y':
                    granting = "GRANT ALL PRIVILEGES ON dbmsProject.%s TO '%s'@'%s' WITH GRANT OPTION" % (tableName, userName, host)
                else:
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

def INSERT_INTO_FORBIDDEN(mydb, cursor, userName, tableName):
    try:
        query ="INSERT INTO FORBIDDEN VALUES(NULL, '%s', '%s')" %(userName, tableName)
        cursor.execute(query)
        msg = "SUCCESS!! Entry for " + str(userName) + " for " + str(tableName) + " is successfully added to FORBIDDEN"
        print("root : " + msg)
        Log("root", msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(e.msg)
        Log("root", e.msg)

def DELETE_USER_FROM_FORBIDDEN(mydb, cursor, userName, tableName):
    try:
        query = "DELETE FROM FORBIDDEN where userName ='%s' and tableName = '%s'" % (userName, tableName)
        cursor.execute(query)
        msg = "SUCCESS!! Entry for " + str(userName) + " for " + str(tableName) + " is successfully deleted from FORBIDDEN"
        print("root : " + msg)
        Log("root", msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(e.msg)
        Log("root", e.msg)

