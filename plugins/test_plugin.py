#!/usr/bin/python
##########################################################################
#                                                                        #
#   How to write Plugins:                                                #
#                                                                        #
# 1. Plugins must have a function with the same name as the file         #
# 2. Plugins must return a string without a newline                      #
# 3. Plugins must accept a list as an argument to their function.        #
#        The list contains the arguments the user called your cmd with   #
# 4. Call your plugin with !name_of_plugin arg1 arg2...arg#              #
# 5. Give users permission to use your plugin in permissions.txt         #
#                                                                        #
##########################################################################


# Sample
def test_plugin(user,list):
    return "/say" + ''.join(list)
