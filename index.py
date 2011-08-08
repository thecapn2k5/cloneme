#!/usr/bin/python2.7

# imports
import sys, re, cgi, traceback, datetime

# capture all of stdout
CURROUTSTR = ''
class OutStream:
   def write(self, text):
      """ capture stdout """
      # Let's store what is printed in a global
      global CURROUTSTR
      CURROUTSTR += text


def Main():
   """ this will run everything """
   # Get the mode they want
   form = cgi.FieldStorage()
   Mode = form.getvalue("mode")

   # use Home if they haven't specified
   if not Mode:
      Mode = 'Home'

   # complete setup is a different beast
   if Mode == 'CompleteSetup':
      CompleteSetup()

   # Dynamically import the mode they want or pull the default mode
   else:
      # Let's dynmically give them a mode by importing a class they ask for
      try:
         module = __import__(Mode)
      # if the mode doesn't exist, import Home
      except ImportError:
         error = " ".join(traceback.format_exc().splitlines()[-1].split()[:-1])
         if error == "ImportError: No module named":
            module = __import__('Home')
         else:
            RaiseException()
            return
      except:
         RaiseException()
         return

      # get the webapp and instantiate it
      myclass = getattr(module, 'Webapp')
      app = myclass(form=form)

      # Now let's run it but capture the stdout
      sys.stdout = OutStream()
      try:
         app.run()
      except:
         RaiseException()

      # let it print
      sys.stdout = sys.__stdout__

      # print this stuff before content type
      if form.getvalue('cm') == 'logmein' or re.match("Location", CURROUTSTR):
         print CURROUTSTR

      # get cookies
      username =  str(app.cookie('username'))
      session =  str(app.cookie('session'))
      demomode =  str(app.cookie('demomode'))

      # Set a cookie expire time
      expire = datetime.datetime.now() + datetime.timedelta(hours=+1)
      expire = expire.strftime("%a, %d-%b-%Y %H:%M:%S CST")

      # possibly put in demomode
      if app.config.get('general', 'demomode') == 'on':
         id = DemoMode(app)
         print "Set-Cookie: demomode=" + id + ";expires=" + expire + ";"

      # Print the cookies and page
      print "Set-Cookie: username=" + username + ";expires=" + expire + ";"
      print "Set-Cookie: session=" + session + ";expires=" + expire + ";"
      print "content-type: text/html\n"
      print CURROUTSTR


def CompleteSetup():
   """ make the setup files unusable/unfindable via browser """
   # take off the first line of the .py file
   f = open('setup.py', 'r')
   lines = f.readlines()
   lines.pop(0)
   f.close()
   f = open('setup.py', 'w')
   f.writelines(lines)
   f.close()

   # rename the html
   import uuid, os
   os.rename('templates/setup.html', 'templates/' + str(uuid.uuid4()))

   # go to the landing page
   print "Location: ?"
   print "content-type: text/html\n"


def DemoMode(app):
   """ let the demo mode run """
   import uuid, os
   if app.cookie('demomode'):
      id = app.cookie('demomode')
   else:
      id = re.sub('-', '', str(uuid.uuid4()))
      os.system('cp demo/demo_config.ini demo/%s_config.ini' % id)
   return id


def RaiseException():
   """ raise the exception from a hosing """
   firstItr = True
   for line in traceback.format_tb(sys.exc_traceback):
      if firstItr:
         print 'content-type: text/html \n'
         print "Traceback: " + line + '<br/>'
         firstItr = False
      else:
         print "           " + line + '<br/>'
   print traceback.format_exc().splitlines()[-1]
   return

try:
   Main()
except:
   RaiseException()
