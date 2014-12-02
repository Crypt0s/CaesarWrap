import time,threading,ConfigParser

config = ConfigParser.ConfigParser()
config.read('settings.ini')
x = config.getint('creativetp','x')
y = config.getint('creativetp','y')
z = config.getint('creativetp','z')
r = config.getint('creativetp','r')
def creativezone(pipe):
    def tt():
        pipe.stdin.write("gamemode creative @a[x=%i,y=%i,z=%i,r=%i]\n" % (x,y,z,r))
    while pipe is not None:
        t = threading.Timer(30.0,tt)#pipe.stdin.write,["gamemode creative @a[x=%i,y=%i,z=%i,r=%i]\n" % (x,y,z,r)])
        t.start()
        time.sleep(30)
    print "Creativezone thread died"
