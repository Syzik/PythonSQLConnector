import os
import psycopg2
import sys
import re
import chardet
import codecs
from typing import Any

################################ nobody should do that shit ###############################
directory = sys.argv[1]
global linecount
global error
error = 0
linecount = 0

def main():
    readDirectory(directory)

def readDirectory(directory):
    filecount = 0
    global  linecount
    print('directory = ' + directory)
    print('directory (absolute) = ' + os.path.abspath(directory))
    conn = connectdatabase()

    for root, subdirs, files in os.walk(directory):
        print('--\nroot = ' + root)
        list_file_path = os.path.join(root, 'my-directory-list.txt')
        print('list_file_path = ' + list_file_path)

        with open(list_file_path, 'wb') as list_file:
            for subdir in subdirs:
                print('\t- subdirectory ' + subdir)

            for filename in files:
                file_path = os.path.join(root, filename)
                print('\t- file %s (full path: %s)' % (filename, file_path))
                with open(file_path, 'rb') as f:
                    filecount = filecount + 1
                    print("filecount = %s\n" % (filecount))
                    readfile(file_path, conn)
                    print('line count : %s' % linecount)
                    f_content = f.read()
                    list_file.write(('The file %s contains:\n' % filename).encode('utf-8'))
                    list_file.write(f_content)
                    list_file.write(b'\n')

def readfile(filename, conn):
    global linecount
    global error
    with open(filename) as f:
        for line in f:
            charesult = chardet.detect(line)
            try :
                parse(line.decode(charesult['encoding']),conn)
            except :
                error += 1
                print("error : %s\n" % (error))
                continue
            linecount = linecount + 1

def checkmailorlogin(world):
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if not EMAIL_REGEX.match(world):
        return 0
    else:
        return 1

def whatToDo(conn, user, password):
    if ((checkuserexist(conn, user) == 1) and (checkpassexist(conn, password)) == 1):
        # get id pass/user
        userid = getuserid(conn,user)
        passid = getpassid(conn,password)
        # new entry t_dico -> id user id pass
        insertdico(conn, userid, passid)
    elif (checkuserexist(conn, user) == 0 and checkpassexist(conn, password) == 0):
        # new entry t_pass
        insertpass(conn,password)
        # get id pass/user
        insertuser(conn,user)
        userid = getuserid(conn,user)
        passid = getpassid(conn,password)
        # new entry t_dico ->. iduser idpa.ss
        insertdico(conn, userid, passid)
    elif (checkuserexist(conn, user) == 0 and checkpassexist(conn, password) == 1):
        # new entry user
        insertuser(conn,user)
        # get id pass / user
        userid = getuserid(conn,user)
        passid = getpassid(conn,password)
        # new entry t_dico ->. idpass idus.er
        insertdico(conn, userid, passid)
    elif (checkuserexist(conn, user) == 1 and checkpassexist(conn, password) == 0):
        # get id user
        userid = getuserid(conn,user)
        # new entry password / get password id
        insertpassword(conn,password)
        passid = getpassid(conn,password)
        # new entry t_dico ->. iduser idpassword
        insertdico(conn, userid, passid)
        
def parse(line, conn):
    world = line.split(':')
    print(world)
    conn = connectdatabase()
    whatTodo(conn, world[0], world[1])

def insertdico(conn, userid, passwordid):
    try :
        cur.execute("INSERT INTO t_dico (id_dico, idpassword, iduser) \
                  VALUES (, %s, %s)", (idpassword, iduser));
        conn.commit()
        print("Insert Success")
    except Exception :
        print("Insert t_dico didn't work")
        
def insertuser(conn, entry):
    if (checkmailorlogin(entry) == 0):
        #login
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO t_user (id_user, login, mail) \
                 VALUES (, %s, %s)", (entry, ""));
            conn.commit()
            print("Insert Success")
        except Exception:
            print("Insert t_user didn't work")
    else:
        #email
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO t_user (id_user, login, mail) \
                 VALUES (, %s, %s)", ("", entry));
            conn.commit()
            print("Insert Success")
        except Exception:
            print("Insert t_user didn't work") 
        
def insertpassword(conn, entrypass):
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO password (id_password, password) \
               VALUES (, %s)", (entrypass));
        conn.commit()
        print("Insert Success")
    except Exception :
        print("Insert t_password didn't work")

def checkentry(conn):
    outputpasswords(conn)
    outputusers(conn)

def connectdatabase():
    try :
        conn = psycopg2.connect("dbname='dbpass' user='postgres' host='localhost' password='postgres'")
        print("Database Connected....")
        return conn
    except Exception :
        print("Connection bdd didn't work")

def decodatabase(conn):
    conn.close()

def getuserid(conn, user):
    cur = conn.cursor()
    cur.execute("select id_user from t_user where t_user.login like %s OR t_user.email like %s", (user, user))
    rows = cur.fetchall()
    for row in rows:
        return row[0]

def getpassid(conn, password):
    cur = conn.cursor()
    cur.execute("select id_password from t_password where password like %s", (password))
    rows = cur.fetchall()
    for row in rows:
        return row[0]

def checkpassexist(conn, password):
    cur = conn.cursor()
    cur.execute("SELECT * from t_password")
    rows = cur.fetchall()
    for row in rows:
        if (password == row[1]):
            return 1
    return 0

def checkuserexist(conn, user):
    cur = conn.cursor()
    cur.execute("SELECT * from t_user")
    rows = cur.fetchall()
    for row in rows:
        if (user == row[1]):
            return 1
    return 0

if __name__== "__main__":
    main()
