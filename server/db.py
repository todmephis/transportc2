#!/usr/bin/env python3
# License: GPL-3.0

from hashlib import md5
from os import remove, path
from sqlite3 import connect
from server.logger import logger, log_time
from server.config import DATABASE_FILE, cmd_decode, cmd_encode

##################################################################
#
# General connection / query functions
#
##################################################################
def db_connect():
    try:
        return connect(DATABASE_FILE, timeout=3, check_same_thread=False)
    except:
        return False

def db_query(con, query):
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    con.commit()
    cur.close()
    return data

##################################################################
#
# Create Database/Tables - IF NOT EXISTS
#
##################################################################
def init_db():
    try:
        # check if db file exists:
        if not path.exists(DATABASE_FILE):
            logger("Database file created")

        con = db_connect()
        create_tables(con)
        default_admin(con)
        con.close()
        return True
    except Exception as e:
        logger("Error in init_db: {}".format(str(e)))
        return False

def clear_db():
    # Delete database
    try:
        remove(DATABASE_FILE)
        return True
    except Exception:
        return False

def create_tables(con):
    # CMDS table
    cmd = ('CREATE TABLE IF NOT EXISTS CMD (CMD_ID INTEGER PRIMARY KEY AUTOINCREMENT,'
          'CLIENT_ID INTEGER NOT NULL,'
          'ADMIN_ID INTEGER NOT NULL,'
          'TIME TEXT NOT NULL,'
          'COMMAND TEXT NOT NULL,'
          'RESULT TEXT);')
    db_query(con, cmd)
    # AGENTS Table - (Status: Active/Inactive)
    cmd = ('CREATE TABLE IF NOT EXISTS CLIENT (CLIENT_ID INTEGER PRIMARY KEY AUTOINCREMENT,'
          'IP TEXT NOT NULL,'
          'HOSTNAME TEXT NOT NULL,'
          'OS TEXT NOT NULL,'
          'PID INTEGER,'
          'TYPE TEXT,'
          'PROTOCOL TEXT,'
          'LAST_CHECKIN TEXT NOT NULL,'
          'STATUS TEXT NOT NULL);')
    db_query(con, cmd)
    # Admins table (perms: User/Admin, Status: Active/Inactive)
    cmd = ('CREATE TABLE IF NOT EXISTS ADMIN (ADMIN_ID INTEGER PRIMARY KEY AUTOINCREMENT,'
          'USERNAME TEXT NOT NULL,'
          'PASSWORD TEXT NOT NULL,'
          'LAST_LOGIN TEXT NOT NULL,'
          'STATUS TEXT NOT NULL);')
    db_query(con, cmd)

def default_admin(con):
    # Create default user if not exists
    if not get_adminid(con, 'admin'):
        # Default creds left in clear text, in the event ppl want to change default value
        update_admin(con, 'admin', 'admin', 'Inactive')

##################################################################
#
# ID Lookups - Support functions
#
##################################################################
def get_adminid(con, username):
    # Get USER_ID from USERS Table using USERNAME value
    try:
        return db_query(con, """SELECT ADMIN_ID FROM ADMIN WHERE USERNAME='{}' LIMIT 1;""".format(username))[0][0]
    except:
        return False

def get_clientid(con, hostname, pid):
    # Get AGENT_ID from AGENTS Table using HOSTNAME value
    try:
        return db_query(con, """SELECT CLIENT_ID FROM CLIENT WHERE (HOSTNAME='{}' AND PID={}) LIMIT 1;""".format(hostname, pid))[0][0]
    except Exception as e:
        #print(e)
        return False

def get_hostname(con, client_id):
    # Get client hostname from client_id
    try:
        return db_query(con, """SELECT HOSTNAME FROM CLIENT WHERE CLIENT_ID='{}' LIMIT 1;""".format(client_id))[0][0]
    except:
        return False

##################################################################
#
# Agent Table Functions
#
##################################################################
def update_client(con, ip, hostname, os, status, pid, client_type, protocol):
    id = get_clientid(con, hostname, pid)
    if id:
        db_query(con, """UPDATE CLIENT SET IP='{}', HOSTNAME='{}', OS='{}', PID='{}', TYPE='{}', PROTOCOL='{}', LAST_CHECKIN='{}', STATUS='{}' WHERE CLIENT_ID={};""".format(ip,hostname,os,pid,client_type,protocol,log_time(),status,id))
        if status == 'Inactive':
            logger("CLIENT: {} record updated ({}, {}, {})".format(hostname, ip, os, status))
    else:
        db_query(con, """INSERT INTO CLIENT (IP, HOSTNAME, OS, PID, TYPE, PROTOCOL, LAST_CHECKIN, STATUS) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}');""".format(ip,hostname,os,pid,client_type,protocol,log_time(),status))
        logger("CLIENT: New Connection from: {} ({}, {}, {})".format(hostname, ip, os, status))
        id = get_clientid(con, hostname, pid)
    return id

def cmd_check(con, id):
    # Check CMD table for active results for specified ID
    cmd = db_query(con, """SELECT COMMAND FROM CMD WHERE CLIENT_ID={} AND RESULT='' LIMIT 1;""".format(id))
    if not cmd:
        return False
    return cmd[0][0]

def update_results(con, client_id, data):
    # Add results to cmd table - used by agent server when receiving new result from client
    try:
        db_query(con, """UPDATE CMD SET RESULT='{}' WHERE CLIENT_ID={} and RESULT='' LIMIT 1;""".format(data, client_id))
        logger("CMD: {} returned {}".format(get_hostname(con,client_id), cmd_decode(data).strip()))
    except Exception as e:
        #print(e)
        pass

def active_clients(con):
    DATA = []
    # List all active agents + OS Version - used for admin https site
    try:
        cmd = db_query(con, """SELECT ClIENT_ID, HOSTNAME, OS, IP, PID, TYPE, PROTOCOL FROM CLIENT WHERE STATUS = 'Active';""")
        for x in cmd:
            tmp = {}
            tmp["ID"]       = x[0]
            tmp["HOSTNAME"] = x[1]
            tmp["OS"]       = x[2]
            tmp["IP"]       = x[3]
            tmp["PID"]      = x[4]
            tmp["TYPE"]     = x[5]
            tmp["PROTOCOL"] = x[6]
            DATA.append(tmp)
    except:
        DATA = []
    return DATA

def clear_pending(con):
    # clear are any commands that have no response
    try:
        for client_id in db_query(con, """SELECT CLIENT_ID FROM CMD WHERE RESULT='';""")[0]:
            update_results(con, client_id, cmd_encode("Manually Cleared"))
    except:
        # Catch when clicked with no clients
        pass

def post_command(con, client_id, username, command):
    # Post a command from the admin http server
    admin_id = get_adminid(con,username)
    hostname = get_hostname(con, client_id)
    db_query(con, """INSERT INTO CMD (CLIENT_ID, ADMIN_ID, TIME, COMMAND, RESULT) VALUES ({},{},'{}','{}','');""".format(client_id, admin_id, log_time(),command))
    logger("CMD: {} executed a command on {} ({})".format(username, hostname, cmd_decode(command).strip()))

##################################################################
#
# User Table Functions
#
##################################################################
def update_admin(con, username, password, status):
    # update user pwd or add new user
    id = get_adminid(con, username)
    password = md5(password.encode('utf-8')).hexdigest()
    if id:
        db_query(con, """UPDATE ADMIN SET USERNAME='{}', PASSWORD='{}', LAST_LOGIN='{}', STATUS='{}' WHERE ADMIN_ID={};""".format(username,password,log_time(),status,id))
        logger("Admin: {} record updated".format(username))
    else:
        db_query(con, """INSERT INTO ADMIN (USERNAME, PASSWORD, LAST_LOGIN, STATUS) VALUES ('{}','{}','{}','{}');""".format(username,password,log_time(),status))
        logger("Admin: {} user added to database".format(username))
    return

def active_admins(con):
    # List all active users - used for admin https site
    cmd = db_query(con, """SELECT USERNAME FROM ADMIN WHERE STATUS = 'Active';""")
    if not cmd:
        return []
    return cmd

def admin_login(con, username, password):
    # used for login page to authenticate users
    result = False
    password = md5(password.encode('utf-8')).hexdigest()
    try:
        id = get_adminid(con, username)
        passwd = db_query(con, """SELECT PASSWORD FROM ADMIN WHERE ADMIN_ID={};""".format(id))
        if str(password) == str(passwd[0][0]):
            valid_login(con, id) # Set user as active in DB
            result = True
    except Exception as e:
        pass
    logger("Admin: {} Login attempt: {}".format(username, str(result)))
    return result

def valid_login(con, id):
    # Set user status as "Active" on successful login
    db_query(con, """UPDATE ADMIN SET STATUS='Active' WHERE ADMIN_ID={}""".format(id))

def admin_logout(con, username):
    # Set user status as "Inactive" on logout
    admin_id = get_adminid(con, username)
    db_query(con, """UPDATE ADMIN SET STATUS='Inactive' WHERE ADMIN_ID={}""".format(admin_id))
    logger("Admin: {} Logged out".format(username))
    return

##################################################################
#
# CMDS Table (Logging) Functions
#
##################################################################
def cmd_log(con):
    # Used in admin html to display last 5 commands and responses
    results = db_query(con, """SELECT ADMIN.USERNAME, CLIENT.HOSTNAME, Time, COMMAND, RESULT from CMD JOIN ADMIN ON CMD.ADMIN_ID = ADMIN.ADMIN_ID JOIN CLIENT ON CLIENT.CLIENT_ID = CMD.CLIENT_ID ORDER BY CMD.Time desc LIMIT 5;""")
    if not results:
        results = [["-","-","-","LQo=","LQo="]]
    return results