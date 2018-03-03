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
            granting = "GRANT ALL ON dbmsProject.* TO '%s'@'%s' WITH GRANT OPTION" % (newUser, host)
            cursor.execute(granting)

        except mysql.connector.Error as e:
            print( e.msg)

        msg = "SUCCESS!! User " + str(newUser) + " added to the database"
        # print("root: " + msg)
        Log("root" , msg)

    except mysql.connector.Error as e:
        print (e.msg)
        Log("root", e.msg)

def DROP_EXISTING_USER(cursor, host, existingUser):
    try:
        query = "DROP USER '%s'@'%s'" % (existingUser, host)
        cursor.execute(query)

        msg = "SUCCESS!! User " + str(existingUser) + " removed from the database"
        # print("root: " + msg)
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
            # print("GRANTING: " + insertAssignedQ)
            cursor.execute(insertAssignedQ)
            mydb.commit()
        except mysql.connector.Error as e:
            print(e.msg)

        msg ="SUCCESS!! New table " + str(tableName) + " created"
        print(str(currUser) + " : " + msg)
        Log(str(currUser), msg)
        INSERT_INTO_ACCESS(mydb, cursor, "root", currUser, tableName, 1);

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
            # Check whether the current user "currUser" can give privilege (has the GRANT OPTION) to new user "userName"
            queryAssigned = "SELECT * FROM ASSIGNED where userName = '%s' and tablename = '%s'" % (currUser, tableName)
            # print ("QUERY: " + str(queryAssigned))
            result = cursor.execute(queryAssigned)
            grantBit = cursor.fetchone()

            # Current User does not GRANT OPTION
            if '0' in str(grantBit):
                msg = " does not have GRANT OPTION"
                print (currUser + msg)
                Log(currUser, msg)

            else:
                # Give privilege to the new user "userName". For that, make entry to the assigned table. Also, keep track in the graph
                # table i.e., "ACCESS TABLE"
                # Handle Assigned Table
                try:
                    checkQuery = "SELECT grantBit FROM ASSIGNED where userName = '%s' and tableName ='%s'" % (userName, tableName)
                    cursor.execute(checkQuery)
                    result = cursor.fetchone()
                    # print ("1: Result here is: " + str(result))

                    if result is not None: #Entry already exists, update it to most recent value
                        UPDATE_ASSIGNED_TABLE(mydb, cursor, currUser, userName, tableName, grantOption)

                    else: # No entry exists in the ASSIGNED table
                        INSERT_INTO_ASSIGNED(mydb, cursor, currUser, userName, tableName, grantOption)

                except mysql.connector.Error as e:
                    print("ASSIGNED " + e.msg)
                    Log("root", e.msg)

                # Handle ACCESS Table
                try:
                    checkQuery2 = "SELECT grantBit FROM ACCESS where grantorName = '%s' and granteeName = '%s' and tableName ='%s'" % (currUser, userName, tableName)
                    # print("Query: " + checkQuery2)
                    cursor.execute(checkQuery2)
                    result2 = cursor.fetchone()
                    # print("2: Result here is: ", result2)

                    # Handle changes to ASSIGNED table
                    if result2 is not None:
                        UPDATE_ACCESS_TABLE(mydb, cursor, currUser, userName, tableName, grantOption)
                    else:
                        INSERT_INTO_ACCESS(mydb, cursor, currUser, userName, tableName, grantOption)

                except mysql.connector.Error as e:
                    print("ACCESS  here: " + e.msg)
                    Log("root", e.msg)

        except mysql.connector.Error as e:
            print (str(currUser) + " : " + e.msg)
            Log(currUser, e.msg)

def REVOKE_ALL(mydb, cursor, currUser, userName, tableName):
        rowCount, grantBit = CHECK_IF_GRANTED_ACCESS(cursor, "ACCESS", currUser, userName, tableName)

        if (rowCount == '0'):
            msg = "\nCASE 1: Warning!! User " + str(currUser) + " has NOT granted access to user " + str(userName) +" for table " + str(tableName) + " in the first place. "
            print(str(currUser) + " " + msg)
            Log(currUser, msg )
            return
        else:
            if grantBit == '0':
                msg = "User " + str(currUser) + " has not given GRANT OPTION to " + str(userName) + ". Safe to delete the link."
                print(msg)
                Log(currUser, msg)
                msg = "\nCASE 2: Delete <" + str(currUser) + " , "  + str(userName) + " , " + str(tableName) + " , 0> from ACCESS TABLE"
                print(msg)
                Log(currUser, msg )
                DELETE_USER_FROM_ACCESS(mydb, cursor, currUser, userName, tableName)
                HANDLE_ASSIGNED(mydb, cursor, currUser, userName, tableName, '0')
                return
            else:

                REVOKE_ALL_ITER(mydb, cursor, currUser, userName, tableName)
                msg = "\nCASE 4. Delete <" + str(currUser) + " , " + str(userName) + " , " + str(tableName) + " , 1> from ACCESS TABLE "
                print(str(currUser) + " " + msg)
                Log(currUser, msg)
                DELETE_USER_FROM_ACCESS(mydb, cursor, currUser, userName, tableName)
                HANDLE_ASSIGNED(mydb, cursor, currUser, userName, tableName, '1')

def REVOKE_ALL_ITER(mydb, cursor, currUser, userName, tableName):
    # Check if any other grantor with grantBit = 1
    rowCount = CHECK_IF_OTHER_GRANTOR_EXISTS(cursor, "ACCESS", currUser, userName, tableName, '1')

    # If another grant provided GRANT OPTION TO userName
    if rowCount > '0':
        msg = "\nThere exists another grantor WITH GRANT OPTION. No need to make any additional changes."
        print(str(userName) + " " + msg)
        Log(userName, msg)
        return

    granteeList, grantBitList = GET_ALL_GRANTEES(cursor, "ACCESS", userName, tableName)

    # If userName has no other neighbors, simply delete the link <currUser, userName>
    if (len(granteeList) == 0):
        return

    else:

        for index in range(len(granteeList)):
            print("\nNeighbors for " + str(userName) + " are: " + str(granteeList[index]))

            if (grantBitList[index] == '0'):
                msg = "\nUser " + str(userName) + " did not gave GRANT OPTION to " + str(
                    granteeList[index]) + ". Safe to delete the link."
                print(str(userName) + " " + msg)
                Log(userName, msg)
                msg = "\nCASE 3: Delete entry <" + str(userName) + " , " + str(granteeList[index]) + " , " + str(tableName) +  " , 0 > from ACCESS TABLE"
                print(str(userName) + " " + msg)
                Log(userName, msg)
                DELETE_USER_FROM_ACCESS(mydb, cursor, currUser, userName, tableName)
                HANDLE_ASSIGNED(mydb, cursor, userName, str(granteeList[index]), tableName, '0')
                return

            else:
                REVOKE_ALL_ITER(mydb, cursor,  userName, granteeList[index], tableName)
                msg = "\nCASE 4. Delete <" + str(userName) + " , " + str(granteeList[index]) + " , " + str(tableName) +  ", 1> from ACCESS TABLE"
                print (str(userName) + " " + msg)
                Log(userName, msg)
                DELETE_USER_FROM_ACCESS(mydb, cursor, currUser, userName, tableName)
                HANDLE_ASSIGNED(mydb, cursor, userName, str(granteeList[index]), tableName, '1')

def HANDLE_FORBIDDEN(mydb, cursor, userName, tableName, firstAttempt):
    rowCount = CHECK_IF_USER_EXISTS(cursor, "ASSIGNED", tableName, userName)

    if rowCount > 1:  # Multiple entries
        msgToCurrUser = "Something is wrong. Contact Security Officer to resolve the issue."
        print(msgToCurrUser)
        Log("root ", msgToCurrUser)

    elif rowCount == 0:
        INSERT_INTO_FORBIDDEN(mydb, cursor, userName, tableName)
    else:
        if firstAttempt == 1:
            msg = "Inserting (" + str(userName) + " , " +  " Forbidden) may result in disruption of operations"
            print("root: "  + msg)
            Log("root", msg)
        elif firstAttempt > 1:
            INSERT_INTO_FORBIDDEN(mydb, cursor, userName, tableName)
            print("\nRevoke subsequent grants")
            print("Remove entry <" + str(userName) + " , " + str(tableName) + " >  from ASSIGNED TABLE")
            DELETE_USER_FROM_ASSIGNED(mydb, cursor, "root", userName, tableName)

            #remove all grantor, username entries
            grantorList, grantBitList = GET_ALL_GRANTORS(cursor, "ACCESS", userName, tableName)
            if (len(grantorList) > 0):
                for index in range(len(grantorList)):
                    print("Remove entry < " + str(grantorList[index]) + " , " +  str(userName) + " , " + str(tableName) +  " , " + str(grantBitList[index]) + " > from ACCESS TABLE")
                    DELETE_USER_FROM_ASSIGNED(mydb, cursor, grantorList[index], userName, tableName)

            # remove all username, grantee entries
            granteeList, grantBitList = GET_ALL_GRANTEES(cursor, "ACCESS", userName, tableName)

            if(len(granteeList) > 0):
                for index in range(len(granteeList)):
                    REVOKE_ALL(mydb, cursor, userName, granteeList[index], tableName)


def INSERT_INTO_FORBIDDEN(mydb, cursor, userName, tableName):
    try:
        query = "INSERT INTO FORBIDDEN VALUES(NULL, '%s', '%s')" % (userName, tableName)
        cursor.execute(query)
        msg = "SUCCESS!! Entry for " + str(userName) + " for table " + str(tableName) + " is successfully added to FORBIDDEN"
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
        msg = "SUCCESS!! Entry for " + str(userName) + " for table " + str(tableName) + " is successfully deleted from FORBIDDEN"
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
        msg = " SUCCESS!! Entry < " + str(userName) + " , " + str(tableName) + " , "  + str(grantOption) +  " > is successfully added to ASSIGNED"
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
        msg = " SUCCESS!! Entry < " + str(userName) + " , " + str(tableName) + " > is successfully deleted from ASSIGNED"
        print(currUser + msg)
        Log(currUser, msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(currUser, " Error -  DELETE ASSIGNED " + e.msg)
        Log(currUser, " Error - DELETE ASSIGNED " + e.msg)

def INSERT_INTO_ACCESS(mydb, cursor, grantor, grantee, tableName, grantOption):
    try:
        query ="INSERT INTO ACCESS VALUES(NULL, '%s', '%s', '%s', %s)" %(grantor, grantee, tableName, grantOption)
        # print("QUERY " + query)
        cursor.execute(query)
        msg = "SUCCESS!! Entry <" + str(grantor) + " , " + str(tableName) + " , " + str(grantee) + " " + str(grantOption) +" > in ACCESS table"
        # print(msg)
        Log(grantor, msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(grantor + " : Error - INSERT ACCESS "  + e.msg)
        Log("root",  " : Error - INSERT ACCESS "  + e.msg)

def DELETE_USER_FROM_ACCESS(mydb, cursor, currUser, userName, tableName):
    try:
        query = "DELETE FROM ACCESS where grantorName ='%s' and granteeName = '%s' and tableName = '%s'" % (currUser, userName, tableName)
        cursor.execute(query)
        msg = " SUCCESS!! Entry < " + str(userName) + " , " + str(tableName) + " > is successfully deleted from ASSIGNED"
        # print(currUser + msg)
        Log(currUser, msg)
        mydb.commit()

    except mysql.connector.Error as e:
        print(currUser + " : Error - DELETE ACCESS " + e.msg)
        Log(currUser, " : Error - DELETE ACCESS " + e.msg)

def UPDATE_ASSIGNED_TABLE(mydb, cursor, currUser, userName, tableName, grantOption):
    try:
        query = "UPDATE ASSIGNED SET grantBit = %s where userName = '%s' and tableName = '%s' " % ( grantOption,
            userName, tableName)
        cursor.execute(query)
        msg = " SUCCESS!! User: " + currUser + " updated ASSIGNED table "  + tableName + " for user " + userName
        # print(currUser + msg)
        Log(currUser, msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(currUser +" : Error - UPDATE ASSIGN " + e.msg)
        Log(currUser, " : Error - UPDATE ASSIGN " + e.msg)

def  UPDATE_ACCESS_TABLE(mydb, cursor, currUser, userName, tableName, grantOption):
    try:
        query = "UPDATE ACCESS SET grantBit =  %s where grantorName = '%s' and granteeName = '%s' and tableName = '%s'" % (
            grantOption, currUser, userName, tableName)
        cursor.execute(query)
        msg = " SUCCESS!! User: " + currUser + " updated ACCESS table "  + tableName + " for user " + userName
        # print(currUser + msg)
        Log(currUser, msg)
        mydb.commit()
    except mysql.connector.Error as e:
        print(currUser +" : Error - UPDATE ACCESS " + e.msg)
        Log(currUser, " : Error - UPDATE ACCESS " + e.msg)


def CHECK_IF_OTHER_GRANTOR_EXISTS(cursor, extantTable, currUser, userName, tableName, grantOption):
    try:
        query = "SELECT count(*) FROM %s where grantorName != '%s' and granteeName = '%s' and tableName = '%s' and grantBit = %s" %(extantTable, currUser, userName, tableName, grantOption)
        #print("Query " + query)
        cursor.execute(query)

        row = cursor.fetchone()
        #print("CHECK_IF_OTHER_GRANTOR_EXISTS "  + str(row[0]))
    except mysql.connector.Error as e:
        print("root: " + e.msg)
        Log("root: ", e.msg)
    return str(row[0])

def CHECK_IF_GRANTED_ACCESS(cursor, extantTable, currUser, userName, tableName):

    try:
        query = "SELECT count(*), grantBit FROM %s where grantorName = '%s' and granteeName = '%s' and tableName = '%s'" %(extantTable, currUser, userName, tableName)
        #print("Query: "  + query)
        cursor.execute(query)
        row = cursor.fetchone()

    except mysql.connector.Error as e:
        print("root " + e.msg)
        Log("root: ", e.msg)
    return str(row[0]), str(row[1])

def GET_ALL_GRANTEES(cursor, extantTable, userName, tableName):
    try:
        granteeList = []
        grantBitList = []
        query = "SELECT granteeName, grantBit FROM %s where grantorName = '%s' and tableName = '%s'" %(extantTable, userName, tableName)
        cursor.execute(query)

        rows = cursor.fetchall()
        for row in rows:
            granteeList.append(str(row[0]))
            grantBitList.append(str(row[1]))

    except mysql.connector.Error as e:
        print(e.msg)
        Log("root: ", e.msg)
    return granteeList, grantBitList

def GET_ALL_GRANTORS(cursor, extantTable, userName, tableName):
    try:
        grantorList = []
        grantBitList = []
        query = "SELECT grantorName, grantBit FROM %s where granteeName = '%s' and tableName = '%s'" %(extantTable, userName, tableName)
        cursor.execute(query)

        rows = cursor.fetchall()
        for row in rows:
            grantorList.append(str(row[0]))
            grantBitList.append(str(row[1]))

    except mysql.connector.Error as e:
        print(e.msg)
        Log("root: ", e.msg)
    return grantorList, grantBitList

def HANDLE_ASSIGNED(mydb, cursor, currUser, userName, tableName, grantOption):
    rowWithGrantOptionCount = CHECK_IF_OTHER_GRANTOR_EXISTS(cursor, "ACCESS", currUser, userName, tableName, '1')
    if rowWithGrantOptionCount > '0':
        UPDATE_ASSIGNED_TABLE(mydb, cursor, currUser, userName, tableName, '1')
        print("Update entry <" + str(userName) + " , " + str(tableName) + " , 1> in ASSIGNED Table" )
    else:
        rowWithNoGrantOptionCount = CHECK_IF_OTHER_GRANTOR_EXISTS(cursor, "ACCESS", currUser, userName, tableName, '0')

        if rowWithNoGrantOptionCount > '0':
            UPDATE_ASSIGNED_TABLE(mydb, cursor, currUser, userName, tableName, '0')
            print("Update entry <" + str(userName) + " , " + str(tableName) + " , 0> in ASSIGNED Table")
        else:
            DELETE_USER_FROM_ASSIGNED(mydb, cursor, currUser, userName, tableName)
            print("Delete entry <" + str(userName) + " , " + str(tableName) + " " + grantOption +  " > from ASSIGNED Table")


