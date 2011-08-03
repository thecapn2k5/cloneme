import os, sys, re
sys.path.append("./lib")
from Kengine import Webapp
try:
   import json
except:
   import simplejson as json

class Webapp(Webapp):
   """ this is a webapp """

   def Browse(self):
      ''' the home page '''
      # local vars
      varHash = {'Files':[]}

      # get the files
      for file in os.listdir('uploads'):
         varHash['Files'].append({'filename':file, 'extension':file.split('.')[-1].lower()})

      # template
      return self.template('files.html', varHash)

if __name__ == '__main__':
   # run the app
   x = Webapp()
   x.run()
