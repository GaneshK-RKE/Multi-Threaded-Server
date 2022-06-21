# Multi-Threaded-Server
A simple Multi Threaded Chat room using Python

To run the chat system,
open up the server code first and then open up as many as client models you want.

we have used a static IP in this project but the IPV4 can be fetched using the command
ip_socket = socket.gethostbyname(socket.gethostname())


The project consists of 2 files namely clientstar.py and serverstar.py

Client file , when initiated , connects to the server using a separate thread. This holds true for multiple clients.

We have used the inbuilt libraries such as socket and threading to vreate the sockets and threads respectively

we haave also used the datetime module to print the system time in our chat server

We have several features in this chatroom such as members and admins where the admins have several functions such as to Ban, Kick , Unban members.

The admin functions are protected by a password .


Learnings :

I learnt about the basic socket programming and multi threading in python.

I also learnt about the basics of networking system and came across terms like Port, Socket , IP address ,Host etc.

Resources used:

https://realpython.com/python-sockets/
https://www.tutorialspoint.com/python/python_multithreading.htm
https://commotionwireless.net/docs/cck/networking/learn-networking-basics/





