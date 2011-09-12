# Treasure - A Terminal-based Game

Find the treasure...if you can stay alive long enough.

# Install on OS X

First, clone the github repository.  (See github for help with that.)

Next, install the dependencies:

    sudo easy_install pyzmq
    sudo easy_install urwid

Then start a server (binds and listens on all interfaces):

    ./treasure_server

Then start any number of clients, where a.b.c.d is the IP address of the server:

    ./treasure a.b.c.d                 # You can omit the IP address if the server is on localhost

(For the moment, treasure acts like a brain-dead IRC server/client)
