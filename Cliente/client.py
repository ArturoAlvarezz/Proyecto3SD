import threading
import socket
import os
import argparse
import sys
import tkinter as tk

class Send(threading.Thread):
  def __init__(self, sock, name):
    super().__init__()
    self.sock = sock
    self.name = name

  def run(self):
    while True:

      # Send message to server
      print('{}: '.format(self.name), end='')
      sys.stdout.flush()
      message = sys.stdin.readline()[:-1]

      # Type 'QUIT' on the console to quit the chatroom
      if message == 'QUIT':
        self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('utf-8'))
        break
      else:
        self.sock.sendall('{}: {}'.format(self.name, message).encode('utf-8'))
    
    print('\nQuitting...')
    self.sock.close()
    os._exit(0)

class Receive(threading.Thread):

  # Listens for messages from the server
  def __init__(self, sock, name):
    super().__init__()
    self.sock = sock
    self.name = name
    self.messages = None
  
  def run(self):
    while True:
      message = self.sock.recv(1024).decode('utf-8')
      if message:
        if self.messages:
          self.messages.insert(tk.END, message)
          print('\r{}\n{}: '.format(message, self.name), end = '')
        else:
          print('\r{}\n{}: '.format(message, self.name), end = '')
      else:
        print('\nOh no, we have lost connection to the server!')
        print('\nQuitting...')
        self.sock.close()
        os._exit(0)

class Client:
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.name = None
    self.messages = None

  def start(self):
    print('Trying to connect to {}:{}...'.format(self.host, self.port))
    self.sock.connect((self.host, self.port))
    print('Successfully connected to {}:{}'.format(self.host, self.port))

    print()
    self.name = input('Your name: ')

    # Send name to server
    self.sock.sendall('Server: {} has joined the chat.'.format(self.name).encode('utf-8'))

    # Create send and receive threads
    send = Send(self.sock, self.name)
    send.daemon = True
    send.start()

    receive = Receive(self.sock, self.name)
    receive.daemon = True
    receive.start()

    print('\rConnected to {}:{}'.format(self.host, self.port))
    print('{}: '.format(self.name), end = '')

    return receive
  
  def exit(self, textInput):
    textInput.insert(tk.END, 'QUIT')
    textInput.config(state = tk.DISABLED)
    textInput.quit()
    