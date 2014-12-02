CaesarWrap.py
=============
A full-featured Minecraft wrapper written in Python 2.7 for *Nix distros


Features:
---------
 - RPC server
 - User Plugins and Threaded Plugins
 - Integration with Vanilla Minecraft through the Server stdin API
 - Permissions system: allow specific users and access to specific commands
 - Command Passthrough - if it's not a plugin it'll pass direct to the server


Existing Plugins:
-----------------
 - Creative mode in a specific area on a server
 - Teleport to that creative mode area


Usage:
------
 1. Place the minecraft server jar in the same folder.
 2. Run minecraft regularly the first time
 3. python mc.py

Python will start the server for you.
In the future this will change slightly to allow customization of the server start string


Permissions
-----------
The permissions file is found at permissions.txt
The format is thus:
```
lowercaseusername:permission,permission,permission
```
"all" will make you an administrator capable of running any command in the wrapper and on the server, so watch out.
other permissions should be the names of the functions defined in the executor class in mc.py


Writing Plugins
---------------
Plugins are run when called by users.
Plugins accept several arguments - username,args
Args are the words after the command that the user said in chat.

In order to write a valid plugin, there must be a method with the same name as the filename.
This method (and the file name) is the name by which your command will be called from the minecraft chat.


Writing Threads
---------------
Basically, I handle the threading on your behalf.
You put in a constant while loop (i recommend using the pipe as a while condition so that you exit cleanly when I shut the server down)

If you make the thread eat resources, expect stuff to get slow, and don't forget about the global interpreter lock.


Misc
----

I can be reached for bugs on twitter @Crypt0s or on gmail (bryanhalf) or here on Github, I usually get back to you in 48 hrs or less.

