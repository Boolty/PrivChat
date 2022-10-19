import socket

ipadress = 'localhost'
port = 9999

server = socket-socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ipadress, port))

server.listen()
client, addr = server.accept()

done = False

while not done:
  print(client.recv(1024).decode('utf-8'))
  if msg == 'quit':
    done = True
  else:
    print(msg)
  client.send(input('Message: ').encode('utf-8'))
