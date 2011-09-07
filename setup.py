#!/usr/bin/python2.7

# My imports
import sys, os, re, cgi, traceback, ConfigParser, time, datetime, MySQLdb
import subprocess
sys.path.append("./lib")
try:
   import json
except:
   import simplejson as json
import uuid
from htmltmpl import TemplateCompiler, TemplateProcessor, TemplateManager
from cgi_app import CGI_Application

class Webapp(CGI_Application):

   def setup(self):
      " Hook mechanism to allow sub classes to change CGIAPP "

      # no cache
      print "Expires: Sat, 1 Jan 2005 00:00:00 GMT"
      print "Last-Modified: " + datetime.datetime.today().strftime("%A, %d %B %Y %H:%I GMT")
      print "Cache-Control: no-cache, must-revalidate,no-store"
      print "Pragma: no-cache"

      if self.form.getvalue('cm'):
         cm = self.form.getvalue('cm').lower()
      else:
         cm = 'main'
      self.globals = {'cm'+cm: 1}
      self.start_mode = 'Main'
      self.mode_param('cm')

      for key in self.form.keys():
         self.globals[key] = self.form.getvalue(key)

      self.conn = MySQLdb.connect(
         host = 'localhost',
         db = 'information_schema',
         user = 'chris_master',
         passwd = '1337jew.')
      self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)



   def Main(self):
      """ render the page """
      print 'content-type: text/html \n'
      print self.template()


   def CheckDB(self):
      """ check to see if a database with the given name already exists """
      print 'content-type: application/json \n'

      db = self.form.getvalue('db')

      try:
         self.cursor.execute('SHOW TABLES IN %s' % db)
         tables = self.cursor.fetchall()
         if tables:
            print json.dumps({'pass':'in use'})
         else:
            print json.dumps({'pass':'available'})
      except:
         print json.dumps({'pass':0})


   def ChooseDB(self):
      """ create the database and the config file """
      # give results
      self.globals['db'] = self.form.getvalue('db')
      print 'content-type: application/json \n'
      print json.dumps({'html':self.template()})


   def ChooseToggles(self):
      ''' get the toggles to save nicely '''
      print 'content-type: application/json \n'
      print json.dumps({'html':self.template()})


   def ChooseOptions(self):
      ''' save all the chosen options in config.ini '''
      # split each toggle
      toggles = {}
      togglelist = self.form.getvalue('toggles').split('/')[:-1]
      for i in xrange(len(togglelist)):
         key = togglelist[i].split('=')[0]
         value = togglelist[i].split('=')[-1]
         toggles[key] = value

      # catch the options section
      options = {'customtemplates':' ', 'customcss':' ', 'header':' '}
      for key in ['layout', 'color', 'secondarynav', 'title']:
         options[key] = self.form.getvalue(key)

      # create config.ini and run syncdb
      self.CreateConfigIni(toggles, options)

      # setup complete return the good stuff
      print 'content-type: application/json \n'
      print json.dumps({'html':self.template()})



   def CreateConfigIni(self, toggles, options):
      ''' create the config.ini '''
      config = ConfigParser.RawConfigParser()

      # add the general section
      config.add_section('general')
      config.set('general', 'debug', 'off')
      config.set('general', 'demomode', 'off')

      # add the database section
      config.add_section('database')
      config.set('database', 'username', 'chris_master')
      config.set('database', 'password', '1337jew.')
      config.set('database', 'host', 'localhost')
      config.set('database', 'database', self.form.getvalue('db'))

      # add the toggles section
      config.add_section('toggles')
      for key in toggles.keys():
         config.set('toggles', key, toggles[key])

      # add the options section
      config.add_section('options')
      for key in options.keys():
         config.set('options', key, options[key])

      # write the file
      with open('config.ini', 'wb') as configfile:
         config.write(configfile)

      os.chmod('config.ini', 0775)
      os.chown('config.ini', -1, os.getegid())

      # run syncdb
      subprocess.Popen('./bin/syncdb.py')


   def template(self, file='setup.html'):
      """ overwrite the template function in cgi_app """
      proc = TemplateProcessor()
      temp = TemplateManager(precompile=0).prepare("templates/%s" % file)
      for key in self.globals.keys():
         proc.set(key,self.globals[key])
      body = proc.process(temp)
      return body


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


if __name__ == '__main__':
   # running in terminal, set permissions
   if os.isatty(sys.stdout.fileno()):
      if os.path.exists('config.ini'):
         os.remove('config.ini')
      site = os.getcwd().split('/')[-1]
      os.chdir('../')
      os.chmod(site, 0755)
   # running in browser, run the app
   else:
      try:
         x = Webapp()
         x.run()
      except:
         RaiseException()
