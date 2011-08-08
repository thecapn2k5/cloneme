#!/usr/bin/python2.7

# imports
import sys, cgi, traceback, datetime

def Main():
   ''' call their requested mode and print the nocache stuff '''
   # no cache
   print "Expires: Sat, 1 Jan 2005 00:00:00 GMT"
   print "Last-Modified: " + datetime.datetime.today().strftime("%A, %d %B %Y %H:%I GMT")
   print "Cache-Control: no-cache, must-revalidate,no-store"
   print "Pragma: no-cache"

   # local vars
   form = cgi.FieldStorage()
   mode = form.getvalue("mode")

   if not mode:
      mode = "Home"

   # Let's dynmically give them a mode by importing a class they ask for
   try:
      module = __import__(mode)
   # the mode doesn't exist, using inherited cm and an implied mode.
   # use Home if you can.
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

   MyClass = getattr(module, 'Webapp')
   App = MyClass(form=form)
   App.run()


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
