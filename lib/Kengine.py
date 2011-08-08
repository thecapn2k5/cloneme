import ConfigParser, MySQLdb, re, os
from cgi_app import CGI_Application


class Webapp(CGI_Application):
   """ Basic Web application with db connection, config, templates, etc. """

   def CGIAppInit(self):
      """ Hook mechanism to allow sub classes to change CGIAPP """
      self.start_mode = 'Browse'
      self.mode_param('cm')


   def localSetup(self):
      """ This is a setup fuction for anything the mode """
      pass


   def template(self, template_file, data={}, nav=True):
      """ overwrite the template function in cgi_app """
      from htmltmpl import TemplateCompiler, TemplateProcessor, TemplateManager

      # get the configuration
      self.GetConfigs(data)

      # get the navigation
      self.GetNavs(data)

      # set compilers, processors, and managers
      temp = TemplateManager(precompile=0).prepare("%s/%s" % (self.template_dir, template_file))
      proc = TemplateProcessor()
      cmpl = TemplateCompiler()

      # set keys
      for key in self.__globals__.keys():
         proc.set(key,self.__globals__[key])

      # set vars
      for key in data.keys():
         proc.set(key,data[key])

      # make body to be put in to the string to be compiled
      try:
         body = proc.process(temp)
      except:
         body = ''

      # make string to compile
      tempStr = ''

      # add nav bars
      tempStr += open("%s/%s" % (self.template_dir, "inc/header.html")).read()
      tempStr += body
      tempStr += open("%s/%s" % (self.template_dir, "inc/footer.html")).read()

      # return a TemplateManager object
      return self.html_template(cmpl.compile_string(tempStr), data)


   def html_template(self,compiled_template,data={}):
      """ replaces a mode in htmltmpl """
      from htmltmpl import TemplateManager, TemplateProcessor

      mgr = TemplateManager()
      tproc = TemplateProcessor(html_escape=0)

      for key in self.__globals__.keys():
         tproc.set(key,self.__globals__[key])

      for key in data.keys():
         tproc.set(key,data[key])

      return tproc.process(compiled_template)


   def setup(self):
      """ Inititalization """

      # Get the config vars
      self.config = ConfigParser.ConfigParser()

      files = os.listdir('.')
      if 'config.ini' in files:
         self.config.read('config.ini')

      elif 'devconfig.ini' in files:
         self.config.read('devconfig.ini')

      else:
         print 'content-type: text/html \n'
         print 'You haven\'t set up the database yet.'
         return

      if self.cookie('demomode') and self.config.get('general', 'demomode') == 'on':
         self.config.read('demo/%s_config.ini' % self.cookie('demomode'))

      # If debugging is enabled, set up the cgitb eodule
      import cgitb; cgitb.enable()

      # Create a Database connection
      self.conn = MySQLdb.connect(
         host = self.config.get('database', 'host'),
         db = self.config.get('database','database'),
         user = self.config.get('database','username'),
         passwd = self.config.get('database','password'))
      self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

      # Set some defaults for CGIAPP
      self.CGIAppInit()

      # get the session
      from Model.SessionModel import SessionModel
      self.SessionModel = SessionModel(self.cursor)

      # make the current user
      from Model.DBreadModel import DBreadModel
      self.UsersModel = DBreadModel('users', self.cursor)

      # check a login
      user = self.UsersModel.Browse({'username':self.cookie('username'), 'active':1})
      if user:
         self.CurrentUser = self.UsersModel.Read(user[0]['id'])
      elif self.config.get('general', 'debug') == 'on':
         self.CurrentUser = self.UsersModel.Read(1)
      else:
         self.CurrentUser = False

      # the non-customized models
      self.AccountsModel = DBreadModel('accounts', self.cursor)
      self.AttendanceModel = DBreadModel('attendance', self.cursor)
      self.EmailsModel = DBreadModel('emails', self.cursor)
      self.FamiliesModel = DBreadModel('families', self.cursor)
      self.MembersModel = DBreadModel('members', self.cursor)
      self.PhonesModel = DBreadModel('phones', self.cursor)
      self.PagesModel = DBreadModel('pages', self.cursor)
      self.ServicesModel = DBreadModel('services', self.cursor)
      self.TopnavModel = DBreadModel('topnav', self.cursor)
      self.TransactionsModel = DBreadModel('transactions', self.cursor)

      from Model.AllocationsModel import AllocationsModel
      self.AllocationsModel = AllocationsModel('allocations', self.cursor)

      # Run the localSetup() to allow children to manipulate the Kengine
      self.localSetup()

      # We are done here
      return


   def prerun(self, runmode=''):
      """ Run me first """
      # local vars
      globals = {}
      validated = True

      # not debug check login
      if self.config.get('general', 'debug') != 'on':
         # Let's see if their session matches their database session
         if self.cookie('username'):
            if self.cookie('session') != self.SessionModel.Get(self.cookie('username')):
               return self.logout()

         else:
            validated = False

      # use the demomode
      if self.cookie('demomode') and self.config.get('general', 'demomode') == 'on':
         globals['demosite'] = 1
         validated = True

      # get permissions and extra vars
      if validated and self.CurrentUser:
         globals.update(self.GetPermissions())

      # save your globals and continue
      self.add_globals(globals)
      return 1


   def GetPermissions(self):
      """ get a hash of the things a user is able to do """
      # instantiate the hash
      phash = {'validated': 1, 'headerid':self.CurrentUser['id']}

      # debug uses user 1, which is an admin
      if self.config.get('general', 'debug') == 'on':
         phash['headerfirstname'] = 'DEBUG'
      elif self.config.get('general', 'demomode') == 'on':
         phash['headerfirstname'] = 'DEMO MODE'

      # get the header firstname for the user
      else:
         phash['headerfirstname'] = self.CurrentUser['username']

      # give the permissions back
      return phash


   def login(self, error=''):
      """ show the login screen """
      if error:
         varHash = {'error':error}
      elif self.form.getvalue('error'):
         varHash = {'error':self.form.getvalue('error')}
      else:
         varHash = {}

      # template
      return self.template("login.html", varHash)


   def logout(self):
      """ Log the user out and return to home """
      self.set_cookie("username", '')
      return self.redirect('?')


   def logmein(self):
      """ Perform a login if they have the right creds """
      # local vars
      username = self.form.getvalue('username')
      password = self.form.getvalue('password')

      # If they didn't send a username or password let's try again
      if not username or not password:
         print "Location: ?cm=login&error=Enter Username And Password"
         return

      # try to get a session
      session = self.SessionModel.Validate(username, password)

      # Check the login
      if not session:
         print "Location: ?cm=login&error=Incorrect Username Or Password"
         return

      # Print the cookies and return
      print "Set-Cookie: username=" + username + ";"
      print "Set-Cookie: session=" + session + ";"
      return self.redirect('?')


   def GetNavs(self, data):
      """ get the navigation bars """
      # all the topnav
      data['Topnav'] = self.TopnavModel.Browse()

      # show the currently-used parent
      if 'parent' in data and data['parent']:
         for parent in data['Topnav']:
            if str(parent['id']) == data['parent']:
               parent['currentparent'] = 'current'

      # get the right sidenav
      if 'staticid' in data and data['staticid']:
         data['parent'] = self.PagesModel.Read(data['staticid'])['parent']
         data['Sidenav'] = self.PagesModel.Browse({'parent':data['parent']}, ['id', 'name', 'parent'])

         # get the currently-used page
         for page in data['Sidenav']:
            if int(page['id']) == int(data['staticid']):
               page['currentpage'] = 'currentpage'

      # you're in a non-db mode/cm
      else:
         # select it properly
         currentpage = ''
         if self.form.getvalue('mode'):
            currentpage += self.form.getvalue('mode').lower()

            # set the proper vars
            data['parent'] = self.form.getvalue('mode')
            data['admincurrent'] = 'current'

            # get any extra side nav pages
            data['Sidenav'] = self.PagesModel.Browse({'parent':data['parent']}, ['id', 'name', 'parent'])

         if self.form.getvalue('cm'):
            currentpage += self.form.getvalue('cm').lower()

         if self.form.getvalue('mode'):
            data['currentpage' + self.form.getvalue('mode').lower()] = 'currentpage'

         data['currentpage' + currentpage] = 'currentpage'

      # check if they're hiding side nav
      side = 0
      if 'Sidenav' in data and data['Sidenav']:
         side = len(data['Sidenav'])
      if 'admincurrent' in data:
         side += 2

      if side < 2:
         data['hidesidenav'] = 1
      else:
         data['hidesidenav'] = 0


   def GetConfigs(self, data):
      """ get the stuff out of the config files """
      # Get the config vars
      customcssbool = self.config.getboolean('toggles', 'customcss')

      for option in self.config.options('toggles'):
         if self.config.getboolean('toggles', option):
            data['bool' + option] = 1

      for option in self.config.options('options'):
         data['config' + option] = self.config.get('options', option)
         data['config' + option + self.config.get('options', option).lower()] = 1

         if option == 'customtemplates' and self.config.get('options', option):
            data['chosencustom'] = data['config' + option]

      if 'configlayoutsquare' in data or 'configlayoutbubble' in data:
         data['configunified'] = 1
      else:
         data['configdivided'] = 1

      if 'configcustomcss' in data:
         if data['configcustomcss'] == 1:
            data['configcustomcss'] = ''
         else:
            data['configcustomcss'] = re.sub('<br>', '\r\n', data['configcustomcss'])
      if not customcssbool:
         data['configcustomcss'] = ''

