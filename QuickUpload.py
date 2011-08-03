#!/usr/bin/python2.7

import os, sys, re
sys.path.append("./lib")
from Kengine import Webapp
try:
   import json
except:
   import simplejson as json
import uuid

class Webapp(Webapp):
   """ this is a webapp """

   def CGIAppInit(self):
      " Hook mechanism to allow sub classes to change CGIAPP "
      self.start_mode = 'QuickUpload'
      self.mode_param('cm')


   def QuickUpload(self):
      """ upload an image via jquery.  return the new url """
      field = 'image'

      # Let's save a file if they gave us one :-)
      if not self.form.has_key(field):
         print 'content-type: text/html \n'
         print "HTTP/1.x 400 Bad Request\n\n No file object name found."
         return

      # Get the file item (with all it's goodies)
      fileitem = self.form[field]

      # Did not get a file object so quit
      if not fileitem.file:
         print 'content-type: text/html \n'
         print "HTTP/1.x 400 Bad Request\n\n No file object sent."
         return

      # get your new filename
      newfilename = str(uuid.uuid4()) + '.' + self.form[field].filename.split('.')[-1]

      # open the tempfile for the upload
      fout = open('uploads/' + newfilename, 'wb')

      # Download the filestream from the browser and save it to the temp file
      while 1:
         chunk = fileitem.file.read(100000)
         if not chunk: break
         try:
            fout.write(chunk)
         except:
            print "HTTP/1.x 400 Bad Request\n"
      fout.close()

      # chmod file to ensure permissions are how we want them
      os.chmod('uploads/' + newfilename, 0666)
      os.chown('uploads/' + newfilename, -1, os.getegid())

      # give back the new filename
      print 'content-type: text/html \n'
      print 'uploads/' + newfilename
      return


if __name__ == '__main__':
   # run the app
   x = Webapp()
   x.run()
