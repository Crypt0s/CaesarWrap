import time,threading,ConfigParser
config = ConfigParser.ConfigParser()
config.read('settings.ini')
x = config.getint('creativetp','x')
y = config.getint('creativetp','y')
z = config.getint('creativetp','z')
r = config.getint('creativetp','r')
def survivalzone(pipe):
    while pipe is not None:
        t = threading.Timer(30.1,pipe.stdin.write,["gamemode survival @a[x=%i,y=%i,z=%i,rm=%i]\n" % (x,y,z,r)])
        t.start()
        time.sleep(30)
    print "Survivalzone thread died"
