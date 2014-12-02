import ConfigParser

config = ConfigParser.ConfigParser()
config.read('settings.ini')
x = config.getint('creativetp','x')
y = config.getint('creativetp','y')
z = config.getint('creativetp','z')
def creativetp(user,usrArgs):
    # I want to get away from doing this -- i wonder if the namespace is preserved on import and if I can grab from the space around the def...
    # don't do it
    if user != usrArgs[0]:
        return "/say denied -- you can't teleport other users."
    else:    
        return "/tp %s %i %i %i" % (user,x,y,z)
