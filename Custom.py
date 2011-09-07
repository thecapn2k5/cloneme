import os, sys, re
sys.path.append("./lib")
from Kengine import Webapp
try:
   import json
except:
   import simplejson as json

import datetime

class Webapp(Webapp):
   """ this is a webapp """

   def dummy(self):
      ''' this is a placeholder '''

if __name__ == '__main__':
   # run the app
   x = Webapp()
   x.run()

