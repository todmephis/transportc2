#!/usr/bin/env python3
# License: GPL-3.0

import ssl
from base64 import b64decode, b64encode

##################################################################
#
# If needed, edit variables below prior to: ./setup.sh
#
##################################################################
# External IP for Admin Server links and Client Server HTTP Headers
EXTERNALIP      = '127.0.0.1'

# Set DB File Location
DATABASE_FILE   = 'server/transportdb.sqlite'

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
SSL_VERSION = ssl.PROTOCOL_TLSv1


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

def cmd_encode(send_data):
    # Encode data b64 encoded (really messy with byte/string formatting)
    return b64encode(send_data.encode('utf-8')).decode('utf-8')

def cmd_decode(send_data):
    # Decode data b64 encoded (really messy with byte/string formatting)
    if not send_data:
        return ""
    return b64decode(send_data.encode('utf-8')).decode('utf-8')
