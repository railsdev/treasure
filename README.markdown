# Treasure - A Terminal-based Game

Find the treasure...if you can stay alive long enough.

# OS X and Linux Instructions

1. Clone the git repository.  (See github for help with that.)
1. Install pygame 1.9.1 or newer from http://pygame.org/download.shtml
1. Install pyzmq -- for OS X and most Linux distros, the following command will do:

    sudo easy_install pyzmq


Then start a server (binds and listens on all interfaces):

    ./treasure_server

Then start any number of clients, where a.b.c.d is the IP address of the server:

    ./treasure PlayerName --server a.b.c.d   # You can omit the server argument if the server is on localhost

Catch the pigs....hey, it's just a prototype.

Suggestions?
