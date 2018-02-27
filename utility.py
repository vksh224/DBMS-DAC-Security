import mysql.connector
from Log import *

def CREATE_NEW_USER(cursor, host, newUser, newPasswd, grantOption):

    try:
        # CREATE USER
        creation = "CREATE USER '%s'@'%s'" % (newUser, host)
        cursor.execute(creation)

        setpass = "SET PASSWORD FOR '%s'@'%s' = PASSWORD('%s')" % (newUser, host, newPasswd)
        cursor.execute(setpass)

        # GIVE GRANT ACCESS TO CURRENTLY ADDED USER EXCEPT FORBIDDEN TABLE
        try:
            granting = "GRANT ALL ON dbmsProject.* TO '%s'@'%s' WITH GRANT OPTION" % (newUser, host)
            cursor.execute(granting)

        except mysql.connector.Error as e:
            print( e.msg)

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


def CREATE_TABLE(mydb, cursor, currUser, tableName):
    try:
        createTableQ = "CREATE TABLE IF NOT EXISTS %s(uID INT AUTO_INCREMENT PRIMARY KEY, clientName TEXT NOT NULL)" % (tableName)
        cursor.execute(createTableQ)
        # GIVE GRANT ACCESS TO CURRENTLY ADDED USER EXCEPT FORBIDDEN TABLE
        try:
            #granting = "GRANT ALL PRIVILEGES ON dbmsProject.%s TO '%s'@'localhost'" % (tableName, currUser)
            insertAssignedQ = "INSERT INTO ASSIGNED(uID, userName, tableName, grantBit) VALUES(NULL, '%s', '%s', 1) "%(currUser, tableName)
            print("GRANTING: " + insertAssignedQ)
            cursor.execute(insertAssignedQ)
            mydb.commit()
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

def SHOW_TABLE(cursor, tableName, userName):
    try:
        query = "SELECT * FROM %s" %(tableName)
        cursor.execute(query)
        # print("ENTRIES \n" )

        i = 1
        for row in cursor:
            #row = cursor.fetchone()
            print ("Entry: " + str(i) + " ", row)
            i = i + 1

    except mysql.connector.Error as e:
        print(e.msg)
        Log(userName, e.msg)

def CHECK_IF_USER_EXISTS(cursor, extantTable, tableName, userName):
    try:
        query = "SELECT count(*) FROM %s where userName = '%s' and tableName = '%s'" %(extantTable, userName, tableName)
        cursor.execute(query)
        results = cursor.fetchone()
        # print (query)
        # print("Results: "  + str(results[0]))
    except mysql.connector.Error as e:
        print (e.msg)

    return results[0]


def GRANT_ALL(mydb, cursor, currUser, tableName, userName, host, grantOption):
    # Check if user is in the FORBIDDEN
    rowCount = CHECK_IF_USER_EXISTS(cursor, "FORBIDDEN", tableName, userName)

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
            queryAssigned = "SELECT * FROM ASSIGNED where userName = '%s' and tablename = '%s'" % (currUser, tableName)
            # print ("QUERY: " + str(queryAssigned))
            result = cursor.execute(queryAssigned)
            grantBit = cursor.fetchone()
            # print("Grant bit is: " + str(grantBit))

            if '0' in str(grantBit):
                msg = " does not have GRANT OPTION"
                print (currUser + msg)
                Log(currUser, msg)

            else:
                try:
                    checkQuery = "SELECT grantBit FROM ASSIGNED where userName = '%s' and tableName ='%s'" % (userName, tableName)
                    cursor.execute(checkQuery)
                    result = cursor.fetchone()
                    print ("Result here is: " + str(result))
                    # Handle changes to ASSIGNED table
                    if result != None :
                        #print(str(str(result).find('0')) +" " + str(grantOption))
                        if str(result).find('0') > -1 and grantOption == 1:
                            #print("UPDATE TABLE")
                            UPDATE_TABLE(mydb, cursor, currUser, userName, tableName)
                        else:
                            print("Something is wrong")
                    else:
                        print("INSERT ASSIGNED")
                        INSERT_INTO_ASSIGNED(mydb, cursor, currUser, userName, tableName, grantOption)

                except mysql.connector.Error as e:
                    print(e.msg)
                    Log("root", e.msg)

                # Make an entry in ACCESS table
                INSERT_INTO_ACCESS(mydb, cursor, currUser, userName, tableName, grantOption)

                msgToCurrUser = "SUCCESS!! GRANTED ACCESS TO TABLE " + str(tableName) + " by USER: " + str(userName)
                print(str(currUser) + ": " + msgToCurrUser)
                Log(currUser, msgToCurrUser)

        except mysql.connector.Error as e:
            print (str(currUser) + " : " + e.msg)
            Log(currUser, e.msg)

def REVOKE_ALL(cursor, tableName, newUser, host):
    try:
        granting = "REVOKE ALL PRIVILEGES ON *.'%s' FROM '%s'@'%s'" % (tableName, newUser, host)
        results = cursor.execute(granting)
        print ("Revoking of privileges returned", results)

    except mysql.connector.Error as e:
        print(e.msg)

def INSERT_INTO_FORBIDDEN(mydb, cursor, userName, tableName, firstAttempt):
    rowCount = CHECK_IF_USER_EXISTS(cursor, "ASSIGNED", tableName, userName)

    if rowCount > 1:  # Multiple entries
        msgToCurrUser = "Something is wrong. Contact Security Officer to resolve the issue."
        print(msgToCurrUser)
        Log("root ", msgToCurrUser)

    elif rowCount == 0:
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
    else:
        if firstAttempt == 1:
            msg = "Inserting (" + str(userName) + " , " +  " Forbidden) may result in disruption of operations"
            print("root: "  + msg)
            Log("root", msg)
        else:
            print ("Revoke subsequent grants")

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


def INSERT_INTO_ASSIGNED(mydb, cursor, currUser, userName, tableName, grantOption):
    try:
        query ="INSERT INTO ASSIGNED VALUES(NULL, '%s', '%s', %s)" %(userName, tableName, grantOption)
        cursor.execute(query)
        msg = " SUCCESS!! Entry for " + str(userName) + " for " + str(tableName) + " is successfully added to ASSIGNED"
        print(currUser + msg)
        Log(currUser, msg)
        mydb.commit()

    except mysql.connector.Error as e:
        print("root " + " Error - INSERT ASSIGNED "  + e.msg)
        Log("root", " Error - INSERT ASSIGNED "  + e.msg)

def DELETE_USER_FROM_ASSIGNED(mydb, cursor, currUser, userName, tableName):
    try:
        query = "DELETE FROM ASSIGNED where userName ='%s' and tableName = '%s'" % (userName, tableName)
        cursor.execute(query)
        msg = " SUCCESS!! Entry for " + str(userName) + " for " + str(tableName) + " is successfully deleted from ASSIGNED"
        print(currUser + msg)
        Log(currUser, msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(currUser, " Error -  DELETE ASSIGNED " + e.msg)
        Log(currUser, " Error - DELETE ASSIGNED " + e.msg)

def INSERT_INTO_ACCESS(mydb, cursor, grantor, grantee, tableName, grantOption):
    try:
        query ="INSERT INTO ACCESS VALUES(NULL, '%s', '%s', '%s', %s)" %(grantor, grantee, tableName, grantOption)
        print("QUERY " + query)
        cursor.execute(query)
        msg = "SUCCESS!! " + str(grantor) + " gave access to " + str(tableName) + " " + str(grantee) +" with GRANT OPTION " + str(grantOption)
        print(msg)
        Log(grantor, msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(grantor + " : Error - INSERT ACCESS "  + e.msg)
        Log("root",  " : Error - INSERT ACCESS "  + e.msg)

def DELETE_USER_FROM_ACCESS(mydb, cursor, currUser, userName, tableName):
    try:
        query = "DELETE FROM ASSIGNED where userName ='%s' and tableName = '%s'" % (userName, tableName)
        cursor.execute(query)
        msg = " SUCCESS!! Entry for " + str(userName) + " for " + str(tableName) + " is successfully deleted from ASSIGNED"
        print(currUser + msg)
        Log(currUser, msg)
        mydb.commit()

    except mysql.connector.Error as e:
        print(currUser + " : Error - DELETE ACCESS " + e.msg)
        Log(currUser, " : Error - DELETE ACCESS " + e.msg)

def UPDATE_TABLE(mydb, cursor, currUser, userName, tableName):
    try:
        query = "UPDATE ASSIGNED SET grantBit = '1' where userName = '%s' and tableName = '%s'" % (
            userName, tableName)
        cursor.execute(query)
        msg = " SUCCESS!! User: " + currUser + " updated table "  + tableName + " for user " + userName
        print(currUser + msg)
        Log(currUser, msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(currUser +" : Error - UPDATE " + e.msg)
        Log(currUser, " : Error - UPDATE " + e.msg)
