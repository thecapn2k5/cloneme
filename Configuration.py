import os, sys, re, ConfigParser
sys.path.append("./lib")
from Kengine import Webapp
try:
   import json
except:
   import simplejson as json

class Webapp(Webapp):
   """ This is a webapp """


   def Browse(self):
      """ show a list of all users """
      # vars
      layouts = []
      colors = []
      varHash = {'Options':[]}
      varHash['Options'].append({'name':'Layouts', 'List':[]})
      varHash['Options'].append({'name':'Colors', 'List':[]})
      varHash['Options'].append({'name':'Secondary Navigation', 'List':[]})
      varHash['Options'].append({'name':'Custom Templates', 'List':[], 'customtemplates':1})

      varHash['Options'][-1]['List'].append({'original':' ', 'name':'None', 'category':'customtemplates', 'selected':'checked'})

      # get the toggles
      layoutbool = self.config.getboolean('toggles', 'layout')
      colorbool = self.config.getboolean('toggles', 'color')
      secondarybool = self.config.getboolean('toggles', 'secondarynav')
      customcssbool = self.config.getboolean('toggles', 'customcss')
      headerbool = self.config.getboolean('toggles', 'header')
      customtemplatesbool = self.config.getboolean('toggles', 'customtemplates')

      # get your configs
      layoutconfig = self.config.get('options', 'layout')
      colorconfig = self.config.get('options', 'color')
      secondaryconfig = self.config.get('options', 'secondarynav')
      customtemplatesconfig = self.config.get('options', 'customtemplates')
      varHash['configtitle'] = self.config.get('options', 'title')

      # get the customcss
      if customcssbool:
         # saved a custom css
         if 'customcss' in self.config.options('options'):

            css = self.config.get('options', 'customcss')
            if len(css) == 0:
               css = ' '
            else:
               css = re.sub('<br>', '\r\n', css)
         # no custom css
         else:
            css = ' '
         varHash['customcss'] = css

      # get the custom header
      if headerbool:
         # saved a custom header
         if 'header' in self.config.options('options'):

            header = self.config.get('options', 'header')
            if len(header) == 0:
               header = ' '
            else:
               header = re.sub('<br>', '\r\n', header)
         # no custom header
         else:
            header = ' '
         varHash['header'] = header

      # get all your sheets
      sheets = os.listdir('css')
      sheets.sort()

      # compile your regex
      layoutregex = re.compile('^layout\..+\.css$')
      colorregex = re.compile('^color\..+\.css$')
      secondaryregex = re.compile('^secondary\..+\.css$')
      customtemplatesregex = re.compile('^custom\..+\.css$')
      nameregex = re.compile('\.(?P<name>.+)\.')

      # go through each sheet
      for sheet in sheets:
         # don't bother.  it's not one you want
         if not nameregex.search(sheet):
            continue

         # in-loop vars
         i = 0
         original = nameregex.search(sheet).group('name')
         name = self.CapWords(original)
         hash = {'original':original, 'name':name}

         # it's a layout template
         if layoutbool and layoutregex.match(sheet):
            i = 1
            hash['category'] = 'layout'

            # select the radio if you've already chosen it
            if hash['original'] == layoutconfig:
               hash['selected'] = 'checked'

         # if it's a color template
         elif colorbool and colorregex.match(sheet):
            i = 2
            hash['category'] = 'color'

            # select the radio if you've already chosen it
            if hash['original'] == colorconfig:
               hash['selected'] = 'checked'

         # if it's a secondary nav template
         elif secondarybool and secondaryregex.match(sheet):
            i = 3
            hash['category'] = 'secondarynav'

            # select the radio if you've already chosen it
            if hash['original'] == secondaryconfig:
               hash['selected'] = 'checked'

         elif customtemplatesbool and customtemplatesregex.match(sheet):
            i = 4
            hash['category'] = 'customtemplates'

            # select the radio if you've already chosen it
            if hash['original'] == customtemplatesconfig:
               hash['selected'] = 'checked'

         # add the hash
         if i:
            varHash['Options'][i-1]['List'].append(hash)

      # the template
      return self.template('configuration.html', varHash)


   def Save(self):
      """ save the edited configuration stuff """
      # vars
      exceptions = ['mode', 'cm']

      # config
      newconfig = ConfigParser.RawConfigParser()

      for section in self.config.sections():
         if section != 'options':
            newconfig.add_section(section)
            for option in self.config.options(section):
               newconfig.set(section, option, self.config.get(section, option))

      # catch keys
      newconfig.add_section('options')

      for key in ['customcss', 'header']:
         if not key in self.form.keys():
            newconfig.set('options', key, '')

      for key in self.form.keys():
         if not key in exceptions:
            value = self.form.getvalue(key)
            if key == 'customcss' or key == 'header':
               value = re.sub('\r\n', '<br>', value)
            newconfig.set('options', key, value)

      # write the file
      if 'config.ini' in os.listdir('.'):
         with open('config.ini', 'wb') as configfile:
            newconfig.write(configfile)
      elif 'devconfig.ini' in os.listdir('.'):
         with open('devconfig.ini', 'wb') as configfile:
            newconfig.write(configfile)

      # send to config page
      return self.redirect('?mode=Configuration')

   def CapWords(self, name):
      """ split the name up and capitalize every word """
      # split the filename on underscore
      name = name.split('_')

      # capitalize every word
      for i in xrange(len(name)):
         name[i-1] = name[i-1][0].upper() + name[i-1][1:]

      # return the space-delineated name
      return ' '.join(name)

if __name__ == '__main__':
   # run the app
   x = Webapp()
   x.run()
