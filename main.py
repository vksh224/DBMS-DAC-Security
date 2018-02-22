import mysql.connector

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


def GRANT_ALL(cursor, host, newUser):
    try:
        granting = "GRANT ALL ON *.CLIENT TO '%s'@'%s'" % (newUser, host)
        results = cursor.execute(granting)
        print ("Granting of privileges returned" + str(results))

    except mysql.connector.Error as e:
        print (e.msg)


def REVOKE_ALL(cursor, host, newUser):
    try:
        granting = "REVOKE ALL PRIVILEGES ON *.* FROM '%s'@'%s'" % (newUser, host)
        results = cursor.execute(granting)
        print ("Revoking of privileges returned", results)

    except mysql.connector.Error as e:
        print(e.msg)


hostV = 'localhost'
userV = 'root'
passwdV = 'vijay'
databaseV = "dbmsProject"

mydb = mysql.connector.connect(host=hostV, user=userV, passwd=passwdV, database=databaseV)
cursor = mydb.cursor()

user1 = "sajjad1"
passwd1 = "sajjad1"

user2 = "vijay1"
passwd2 = "vijay1"

CREATE_NEW_USER(cursor, hostV, user2, passwd2)
REVOKE_ALL(cursor, hostV, user1)