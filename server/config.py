#!/usr/bin/env python3
# License: GPL-3.0

import ssl

##################################################################
#
# Edit Below Variables before ./setup.sh
#
##################################################################
# External IP for Admin Server links and Client Server HTTP Headers
EXTERNALIP      = '127.0.0.1'

# Set DB File Location
DATABASE_FILE   = 'server/transportdb.sqlite'

# Set TransportC2 log file location
LOG_FILE = 'logs/master.log'

# Page to signify Client connection to server - **Ensure Client version is the same
CLIENT_PAGE      = "/main.css"

# Secret Key for Client checkin - **Ensure Client version is the same
CLIENT_KEY       = '000000000000000116s92k48dss923j640s234v849c2001qi231d950g3s9df01esdr'


##################################################################
#
# SSL Configuration Settings
#
##################################################################
# Cert file for HTTPS servers - Dynamically Generated in ./setup
CERT_FILE       = 'server/AdminServer/certs/cert.crt'
# Key file for HTTPS servers - Dynamically Generated in ./setup
KEY_FILE        = 'server/AdminServer/certs/key.pem'
# TLS Protocol Version  - **Ensure Client version is the same
SSL_VERSION = ssl.PROTOCOL_TLSv1_1


##################################################################
#
# Shared Functions
#
##################################################################
def sock_close(sock):
    sock.close()
    del sock

def sock_send(sock, msg):
    sock.send(msg.encode('utf-8'))

def sock_recv(sock):
    # Receive all data
    buff_size = 1024
    data = b''
    try:
        while True:
            new =sock.recv(buff_size)
            data += new
            #print(new)
            if len(str(new)) < buff_size:
                return data.decode('utf-8').rstrip('\n')
    except:
        return data.decode('utf-8').rstrip('\n')