import os, sys, re
sys.path.append("./lib")
from Kengine import Webapp
try:
   import json
except:
   import simplejson as json

class Webapp(Webapp):
   """ this is a webapp """

   def CGIAppInit(self):
      " Hook mechanism to allow sub classes to change CGIAPP "
      self.start_mode = 'Static'
      self.mode_param('cm')


   def Top(self):
      """ get the first page associated with a link from the top nav """
      id = self.PagesModel.Browse({'parent':self.form.getvalue('id')})[0]['id']
      return self.Static(id)


   def Static(self, id=0):
      """ get dynamic tinymce content without copying this code all over """
      # local vars
      if not id:
         id = self.form.getvalue('id')

      # do the redirect if they clicked a redirect link
      redirect = self.RedirectsModel.Browse({'pageid':id})
      if redirect:
         return self.redirect('?mode=%s&cm=%s' % (redirect[0]['mode'], redirect[0]['cm']))

      varHash = self.PagesModel.Read(id)

      # you just deleted the page you're on
      # you're looking for the home page and you don't have an id
      if not varHash:
         parent = self.TopnavModel.Browse()
         if parent:
            parent = parent[0]['id']
            id = self.PagesModel.Browse({'parent':parent})[0]['id']
            varHash = self.PagesModel.Read(id)
         else:
            # you have deleted everything off the top nav and have nothing
            id = 0
            varHash = {'content':"<p>You have deleted everything off the top navigation bar.  The site cannot function without one page there.  Please add a page.</p>"}

      varHash['staticid'] = id

      # pull out the actual content
      if not varHash['content']:
         varHash['content'] = "<p>This is content that needs to be filled in later by the admin</p>"

      # return useful content
      return self.template('static.html', varHash)


   def SaveStatic(self):
      """ save a static page """
      # local vars
      varHash = {'id':self.form.getvalue('id'), 'content':self.form.getvalue('content')}

      self.PagesModel.Edit({'id':varHash['id']}, varHash)

      return self.redirect('?id=%s' % (varHash['id']))


   def AddTopNav(self):
      """ add a new top nav page """
      # catch the vars and add to db
      varHash = {'name':self.form.getvalue('name')}
      varHash['id'] = self.TopnavModel.Add(varHash)

      self.PagesModel.Add({"name":varHash['name'], "parent":varHash['id']})

      # show that you've gotten it
      print 'content-type: application/json \n'
      print json.dumps(varHash)


   def AddSideNav(self):
      """ add a new side nav page """
      # catch the vars and add to db
      varHash = {'parent':self.form.getvalue('parent'), 'name':self.form.getvalue('name')}
      varHash['id'] = self.PagesModel.Add(varHash)

      # show that you've gotten it
      print 'content-type: application/json \n'
      print json.dumps(varHash)


   def EditTopNav(self):
      """ update a topnav name """
      # catch the vars and update the database
      varHash = {'name':self.form.getvalue('name')}
      self.TopnavModel.Edit({'id':self.form.getvalue('id')}, varHash)
      varHash = self.TopnavModel.Read(self.form.getvalue('id'))

      # give valid response
      print 'content-type: appliation/json \n'
      print json.dumps(varHash)


   def EditSideNav(self):
      """ update a sidenav name """
      # catch the vars and update the database
      varHash = {'name':self.form.getvalue('name')}
      self.PagesModel.Edit({'id':self.form.getvalue('id')}, varHash)
      varHash = self.PagesModel.Read(self.form.getvalue('id'))

      # give valid response
      print 'content-type: appliation/json \n'
      print json.dumps(varHash)


   def DeleteTopNav(self):
      """ delete a page from the top nav """
      # get the vars and delete the page
      varHash = {'id':self.form.getvalue('id')}
      self.TopnavModel.Delete(varHash)

      # give back the response
      print 'content-type: application/json \n'
      print json.dumps(varHash)


   def DeleteSideNav(self):
      """ delete a page from the side nav """
      # get the vars and delete the page
      varHash = {'id':self.form.getvalue('id')}
      self.PagesModel.Delete(varHash)

      # give back the response
      print 'content-type: application/json \n'
      print json.dumps(varHash)


if __name__ == '__main__':
   # run the app
   x = Webapp()
   x.run()
