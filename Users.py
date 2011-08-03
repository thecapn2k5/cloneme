import os, sys, re
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
      varHash = {}
      varHash['Users'] = self.UsersModel.Browse({'active':1})
      varHash['Deleted'] = self.UsersModel.Browse({'active':0})

      # the template
      return self.template('users/browse.html', varHash)

   def Edit(self):
      """ show details for one user """
      # vars
      varHash = self.UsersModel.Read(self.form.getvalue('id'))

      # the template
      return self.template('users/edit.html', varHash)


   def Update(self):
      """ save an updated user's data from the form """
      varHash = {}
      id = self.form.getvalue('id')

      if self.form.getvalue('username'):
         varHash['username'] = self.form.getvalue('username')

      if self.form.getvalue('password'):
         varHash['password'] = self.form.getvalue('password')

      if varHash:
         self.UsersModel.Edit({'id':id}, varHash)

      return self.redirect('?mode=Users&cm=Browse')


   def JSONValidateUsername(self):
      """ make sure it's a unique username """
      # get either the duplicate or an empty string
      user = self.UsersModel.Browse({'username':self.form.getvalue('username')})
      if not user:
         user = ''

      # show the results
      print 'content-type: application/json \n'
      print json.dumps(user)


   def ProcessRegistration(self):
      """ add a new user """
      # catch the pertinent vars
      varHash = {}
      for key in ['password', 'username']:
         varHash[key] = self.form.getvalue(key)

      # add the user and send them to the login page
      self.UsersModel.Add(varHash)
      return self.redirect('?mode=Users')


   def JSONToggleActive(self):
      """ toggle whether a user is active or not """
      # only admins can do this
      if self.CurrentUser:
         self.UsersModel.Edit({'id':self.form.getvalue('id')}, {'active':self.form.getvalue('active')})

         print 'content-type: application/json \n'
         print json.dumps(self.form.getvalue('id'))


if __name__ == '__main__':
   # run the app
   x = Webapp()
   x.run()
