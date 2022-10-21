import socket, errno, threading, ctypes, sys, re, os, configparser
from datetime import datetime
from tkinter import *
from tkinter import scrolledtext

global HEADER_LENGTH, IP, PORT, username, my_username, client_socket


# parse existing file
config = configparser.ConfigParser()
config.read('setting.ini')
IP = config.get('settings', 'IP')
PORT = config.get('settings', 'PORT')
my_username = config.get('settings', 'username')


window=Tk()
name    = "PCR_Chat"
version = "Version. "
ver     = "1.0.0"
info    = "By Boolty"
HEADER_LENGTH = 10
#IP = "84.190.240.212"
#PORT = 1234
#my_username = 'ALFONSO'


window.title(name + " | " + version + ver + " | " + info)
window.resizable(width=False, height=False)
window.geometry("500x300+10+10")


# Create a socket
# socket.AF_INET - address family, IPv4, some other possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to a given ip and port
client_socket.connect((str(IP), int(PORT)))
# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)


#Send Button
def send():
    now = datetime.now()
    dt_string = now.strftime("%H:%M:%S")
    # Wait for user to input a message
    txt.config(state="normal")
    txt.insert(INSERT, dt_string + ' ' + my_username + ' > ' + txtfld.get() + '\n')
    txt.see('insert')
    txt.config(state="disabled")
    message = dt_string + ' > ' + txtfld.get() + '\n'
    txtfld.delete(0, "end")

    # If message is not empty - send it
    if message:
        # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)


def chat():

    # Prepare username and header and send them
    # We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + username)

    while True:
        now = datetime.now()
        dt_string = now.strftime("%H:%M:%S")
        try:
            # Now we want to loop over received messages (there might be more than one) and print them
            while True:

                # Receive our "header" containing username length, it's size is defined and constant
                username_header = client_socket.recv(HEADER_LENGTH)

                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()

                # Convert header to int value
                username_length = int(username_header.decode('utf-8').strip())

                # Receive and decode username
                username = client_socket.recv(username_length).decode('utf-8')

                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                # Print message
                #print(f'{username} > {message}')
                txt.config(state="normal")
                txt.insert(INSERT,dt_string + ' ' + username + ' > ' + message + '\n')
                txt.config(state="disabled")
                txt.see('insert')
        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            # We just did not receive anything
            continue

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error: '.format(str(e)))
            sys.exit()


# Output-Chat
txt = scrolledtext.ScrolledText(window, width=62, height=10)
txt.config(state="disabled")
txt.grid(column=0, row=0)
txt.place(x=0, y=40)


# Input Chat
txtfld = Entry(window, width=62, bd=10)
txtfld.place(x=0, y=260)


#Send Button
btn = Button(window, text="Send", fg='blue', font=("Helvetica", 15),height = 3, width = 7, command=send)
btn.place(x=400, y=210)


#Username DISPLAY
lbl = Label(window, text="Username: " + my_username, fg='black', font=("Helvetica", 16))
lbl.place(x=5, y=210)


#HOST DISPLAY
lbl = Label(window, text="Server: " + str(IP) +':'+ str(PORT), fg='black', font=("Helvetica", 16))
lbl.place(x=5, y=0)

threading.Thread(target=chat, args=()).start()
window.mainloop()
