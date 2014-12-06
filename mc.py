#!/usr/bin/python
#########################################################
#            CaesarWrap Minecraft Wrapper               #
#                                                       #
# Wraps the minecraft server so that users can do stuff #
# Also allows for commands to be executed from OUTSIDE  #
# via a "RPC" server.                                   #
#########################################################
import subprocess, string, time, sys, socket, select, threading, glob, os, os.path, signal, sys, threads, ConfigParser, json
import pdb
# Todo: now that i wrote in error handling, display the errors
# Where the commands are processed and turned into strings for the main loop to put back in over the popen pipe
class executor:
    # TODO: Need destruction class that cleans up threads spawned here
    def __init__(self,permissions,pipe):
        self.pipe = pipe
        self.permissions = permissions
        self.commands = {
            'help':self.help
        }
        print "Parsing the plugins folder..."
        plugins = self.__loadplugins__('plugins/')
        # Plugins override any builtins, but the only builtin is kill for now
        self.commands = dict(self.commands.items() + plugins.items())
        print "Finished parsing plugins."

        print "Parsing Threaded plugins"
        self.threads = self.__loadplugins__('threads/')
        print "Starting threaded plugins"
        for thread in self.threads.values():
            print "."
            thisthread = threading.Thread(target=thread,args=(self.pipe,))
            thisthread.start()
            #print "!! Error starting thread %s, skipping..." % thread

        print "Finished starting threads"

    def __loadplugins__(self,folder):
        function_dict = {}
        pyfiles = glob.glob(folder+'*.py')
        folder = folder.replace(os.sep,'.')
        for pyfile in pyfiles:
            if '__' in pyfile:
                continue
            pyfile = pyfile.split('/')[1].split('.')[0]
            # import file
            try:
                mod = getattr(__import__(folder+pyfile),pyfile)
                # we expect there to be a function name that matches the filename in that file we imported
                func = getattr(mod,pyfile)
                print "loaded plugin " + pyfile
                function_dict[pyfile] = func
            except:
                print "Failed to load plugin %s" % pyfile
        print "Loaded " + str(len(function_dict.values())) + " Plugins"
        return function_dict 

    def __handle__(self,user,usrCommand,usrArgs):
        # Does user have an entry in permissions.txt?
        if usrCommand not in self.permissions['all'] and user not in self.permissions.keys():
            return self.__respond__("Denied - User not in permissions.txt file.",user)

        # Does the user have the ability to run that command?
        if usrCommand in self.permissions['all'] or 'all' in self.permissions[user] or usrCommand in self.permissions[user]:
            # Does the command exist?
            if usrCommand in self.commands.keys():
                # Run the command!
                try:
                    return self.commands[usrCommand](user,usrArgs)
                except:
                    e = sys.exc_info()[0]
                    print e
                    return "An error occured with command %s" % usrCommand
            elif 'all' in self.permissions:
                # assume that the command is some minecraft server command we didn't choose to handle in executor
                return "/" + usrCommand + " " + usrArgs#/cmd args is echo'd directly to server, so only ppl with "all" permission get it. all == admin
            else:
                return self.__respond__("Denied - Command not found or Permission denied to a raw server command. Do you have the all permission?",user)
        else:
            return self.__respond__("Denied - User not in permissions.txt file.",user)

    # creates response text in the event we need to send text out
    def __respond__(self,message,user=None):
        if user == None:
            # Broadcast message with /say
            return "/say %s" % message
        else:
            return "/tell %s %s" % (user, message)
   
    def help(self,user,usrArgs):
        aggregate = ''
        for key in self.commands.keys():
            aggregate += key + ","
        aggregate = "commands: " + aggregate
        return self.__respond__(aggregate)


# RPC server allows you to not have to worry about doing RCON
# Obviously it's not encrypted and allows only password-based auth, but it can be useful in situations where
# maybe you want to connect an IRC bot to your minecraft server
class RPCserver(threading.Thread):

    def __init__(self,pipe,execObj,config):
        self.config = config
        threading.Thread.__init__(self)
        self.pipe = pipe
        self.execObj = execObj
        try:
            self.host = self.config.get('rpcserver','ip')
            self.port = self.config.getint('rpcserver','port')
            self.password = self.config.get('rpcserver','password')
        except:
            print "Bad settings on RPC server, could not start"
            exit(1)

    # This is where we accept input from ethernet  .
    def run(self):
        # socket junk
        print "Starting RPC server..."
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((self.host,self.port))
        except socket.error as msg:
            print 'Bind failed: ' + str(msg[0])
        s.listen(10)
        #s.setblocking(0)
        #s.timeout(1)
        print "RPC Server started"
        # connection-handler loop
        while 1:
            conn,addr = s.accept()
            print "Recv'd RPC connection from" + addr[0]
            # Actual event loop
            s_input = [s]
            while 1:
                input,output,rdyexcept = select.select(s_input,[],[])
                for i in input:
                    data = i.recv(1024)
                    if data:
                        #json is so much easier to parse
                        #keys: password,usr,cmd,args
                        try:
                            j_data = json.loads(data)
                        except:
                            print "Recv'd non-parsable JSON message - skipping"
                            pass
                        if self.password != j_data['password']:
                            print "Invalid password"
                            continue
                        # pass to execObj and then write out to pipe
                        self.pipe.write(self.execObj.__handle__(j_data['user'],j_data['cmd'],j_data['args']))
                    else:
                        input.remove(i)
        # We probably wont ever reach here.
        s.close()
        print "RPC Server shut down."

if __name__ == "__main__":

    execObj = None

    # Not sure if I want to have this here or what but w/e
    if not os.path.exists('settings.ini'):
        print "No settings.ini file detected!"

    # Handle signals
    def sighandle(signal, frame):
        # clean up stuff
        print "Detected Control-Break!"
        for thread in execObj.threads.values():
            print "."
            # todo: kill threads here regardless of their state
            # Todo: kill the rpc server thread
        print "Cleaning up server, please wait..."
        # threads in threads/ are designed to die if the pipe should go Null, so null it here to let them know to clean up.
        p = None
        sys.exit(0)
    signal.signal(signal.SIGINT, sighandle)

    # Read the config file here.  Plugins/Threads may read from it at some other point in time, but we need it now.
    config = ConfigParser.ConfigParser()
    if len(sys.argv) > 1:
        settings = sys.argv[1]
    else:
        settings = 'settings.ini'
    config.read(settings)
    mc_location = config.get('caesarwrap','minecraft_server_location')
    permissions_loc = config.get('caesarwrap','permissions_file_location')

    # load permissions file
    permissions = {}
    try:
        with open(permissions_loc,'r') as permFile:
            perms = permFile.readlines()
        # parse the perms
        for perm in perms:
            # user:perm,perm,perm,perm
            perm = perm.strip()
            perm = perm.split(':')
            permlist = perm[1].split(',')
            permissions[perm[0]] = permlist
    except:
        print "Couldn't open permissions.txt -- exiting."
        exit(1)

    print "Parsed permissions file..."

    # got this from James Tidman's wrapper.py script and adapted
    restartstatus = 1
    while (restartstatus == 1):
        print "Starting the minecraft server..."
        onlinenumber=0
        p = subprocess.Popen('java -Xmx1024M -Xms1024M -jar '+mc_location,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        longp = p
        # had to move this down here.
        print "Starting command handler..."
        execObj = executor(permissions, p)

        print "Starting RPC listener thread..."
        #def __init__(self,pipe,execObj):
        RPCObj = RPCserver(p.stdin,execObj,config)
        RPCObj.start()
        print "RPC Listener thread should be listening."
    
        # Main loop here
        while(p.poll() == None):
            log = p.stdout.readline()
            words = log.split()
            words = words[3:] # strip the first two non-important columns
            # now we make sure we are listening to a chat by testing to see if <> is present where we expect the username

            print words
            if len(words) <= 0:
                continue

            user = words[0] # user is pretty much always here.
            if '<' != user[0] or '>' != user[-1] or '!' != words[1][0]:
                #immediately bail out if we don't have a chat or we have a chat without the first letter being a '!'.
                continue

            user = user[1:][:-1] #strip "<>"
            user = user.lower()
            # handle a valid chat here and execute that command
            usrCommand = words[1][1:] #strip !
            usrArgs = words[2:] # Everything else after the command

            print "recv'd " + usrCommand + " from " + user

            # We use execObj to wrap everything and perform command permission checking.  Handle returns a string from the command defined in executor
            try:
                result = execObj.__handle__(user,usrCommand,usrArgs)
                print result
                p.stdin.write(result+"\n")
            except:
                e = sys.exc_info()[0]
                print user + " did something weird"
                print e

# now we need to handle input from IRC
