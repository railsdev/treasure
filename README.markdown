# Treasure - A Terminal-based Game

Find the treasure...if you can stay alive long enough.

# Install on OS X

First, clone the github repository.  (See github for help with that.)

Next, install the dependencies:

    sudo easy_install pyzmq
    sudo easy_install urwid

Then start a server on your local machine:

    ./treasure_server

Then start any number of clients, also on your local machine (for now):

    ./treasure

(For the moment, treasure acts like a brain-dead IRC server/client)
