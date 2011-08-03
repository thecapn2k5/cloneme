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
      ''' the browse page of the families '''
      varHash = {'Families':self.FamiliesModel.Browse({'deleted':0})}
      return self.template('families/browse.html', varHash)


   def Add(self):
      ''' show the template to add a family '''
      return self.template('families/addedit.html')


   def Read(self):
      ''' show the read template for a family '''
      # family base
      varHash = self.FamiliesModel.Read(self.form.getvalue('id'))

      # htmltmpl is dumb
      varHash['anniversary'] = str(varHash['anniversary'])

      # process every member
      varHash['Members'] = self.MembersModel.Browse({'familyid':varHash['id'], 'deleted':0})
      for member in varHash['Members']:
         member['Phones'] = self.PhonesModel.Browse({'memberid':member['id'], 'deleted':0})
         member['Emails'] = self.EmailsModel.Browse({'memberid':member['id'], 'deleted':0})

      # template
      return self.template('families/read.html', varHash)


   def Edit(self):
      ''' show the read template for a family '''
      # family base
      varHash = self.FamiliesModel.Read(self.form.getvalue('id'))
      varHash['familyid'] = varHash['id']

      # htmltmpl is dumb
      varHash['anniversary'] = str(varHash['anniversary'])

      # process every member
      varHash['Members'] = self.MembersModel.Browse({'familyid':varHash['id'], 'deleted':0})
      for member in varHash['Members']:
         member['Phones'] = self.PhonesModel.Browse({'memberid':member['id'], 'deleted':0})
         member['Emails'] = self.EmailsModel.Browse({'memberid':member['id'], 'deleted':0})

      varHash['iterator'] = len(varHash['Members'])

      # template
      return self.template('families/addedit.html', varHash)


   def Create(self):
      ''' save the new family '''
      #local vars
      varHash = {}

      # catch stuff just for one family
      for key in self.form.keys():
         if key in self.FamiliesModel.columns:
            varHash[key] = self.form.getvalue(key)

      # get the familyid because you saved it
      familyid = self.FamiliesModel.Add(varHash)

      # save member, phones, and emails
      members = self.SaveMembers(familyid)
      self.SavePhones(members)
      self.SaveEmails(members)

      # return to read
      return self.redirect('?mode=Families&cm=Read&id=' + str(familyid))


   def Update(self):
      ''' save the edited family '''
      #local vars
      varHash = {}
      familyid = self.form.getvalue('familyid')

      # catch stuff just for one family
      for key in self.form.keys():
         if key in self.FamiliesModel.columns:
            varHash[key] = self.form.getvalue(key)

      # update the family
      self.FamiliesModel.Edit({'id':familyid}, varHash)

      # save member, phones, and emails
      members = self.SaveMembers(familyid)
      self.SavePhones(members)
      self.SaveEmails(members)

      # return to read
      return self.redirect('?mode=Families&cm=Read&id=' + str(familyid))


   def SaveMembers(self, familyid):
      ''' save family members '''
      # local vars
      varHash = {}
      members = []
      newmembers = self.form.getlist('memberid')[:-1]

      # collect the data for each of the members
      for key in self.form.keys():
         if key in self.MembersModel.columns and key != 'familyid':
            varHash[key] = self.form.getlist(key)

      # you're editing
      if self.form.getvalue('familyid'):
         # compare the lists
         oldmembers = self.MembersModel.Browse({'familyid':familyid, 'deleted':0}, ['id'])
         for oldmember in oldmembers:
            # found a deleted member.  delete the phones and emails as well
            if not str(oldmember['id']) in newmembers:
               id = oldmember['id']
               self.MembersModel.Edit({'id':id}, {'deleted':1})
               self.PhonesModel.Edit({'memberid':id}, {'deleted':1})
               self.EmailsModel.Edit({'memberid':id}, {'deleted':1})

      # make sure you save every member
      for i in xrange(len(varHash['lastname'])-1):
         member = {'familyid':familyid}

         # the rest of the keys
         for key in varHash:
            member[key] = varHash[key][i]

         # editing, update it
         if newmembers[i] != '0':
            self.MembersModel.Edit({'id':newmembers[i]}, member)
            members.append(int(newmembers[i]))
         # add the member
         else:
            members.append(self.MembersModel.Add(member))

      # give back a list of members
      return members


   def SavePhones(self, members):
      ''' save phone numbers '''
      # don't waste your time
      if not 'phonenumber' in self.form.keys():
         return

      # local vars
      i = 0
      counts = self.form.getvalue('phones').split(',')[:-1]
      numbers = self.form.getlist('phonenumber')[:-1]
      types = self.form.getlist('phonetype')[:-1]

      # you're editing, so get a list of expected phones
      if self.form.getvalue('familyid'):
         self.CheckPhoneDeletes(members)

      # every member gets his phone numbers
      for member in members:
         # loop vars
         index = members.index(member)
         numberschunk = numbers[:int(counts[index])]
         typeschunk = types[:int(counts[index])]

         # add each one
         while numberschunk:
            # save one phone
            if numberschunk[0] != ' ' or typeschunk[0] != ' ':
               phone = {'memberid':member, 'phone':numberschunk[0], 'description':typeschunk[0]}

               id = self.form.getlist('phoneid')[i]
               if id != '0':
                  self.PhonesModel.Edit({'id':id}, phone)
               else:
                  self.PhonesModel.Add(phone)

            # take that phone out of the queue
            del numberschunk[0]
            del typeschunk[0]
            del numbers[0]
            del types[0]
            i += 1


   def CheckPhoneDeletes(self, members):
      ''' look and see if any phones were deleted '''
      # check all the old phones for each member
      for member in members:
         oldphones = self.PhonesModel.Browse({'memberid':member, 'deleted':0}, ['id'])
         for phone in oldphones:
            # if that phone isn't in the new list, delete it
            if not str(phone['id']) in self.form.getlist('phoneid'):
               self.PhonesModel.Edit({'id':phone['id']}, {'deleted':1})


   def SaveEmails(self, members):
      ''' save emails '''
      # don't waste your time
      if not 'email' in self.form.keys():
         return

      # local vars
      i = 0
      counts = self.form.getvalue('emails').split(',')[:-1]
      emails = self.form.getlist('email')[:-1]
      types = self.form.getlist('emailtype')[:-1]

      # you're editing, so get a list of expected emails
      if self.form.getvalue('familyid'):
         self.CheckEmailDeletes(members)

      # every member gets their emails
      for member in members:
         # loop vars
         index = members.index(member)
         emailschunk = emails[:int(counts[index])]
         typeschunk = types[:int(counts[index])]

         # do every email
         while emailschunk:
            # insert the emails
            if emailschunk[0] != ' ' or typeschunk[0] != ' ':
               email = {'memberid':member, 'email':emailschunk[0], 'description':typeschunk[0]}

               id = self.form.getlist('emailid')[i]
               if id != '0':
                  self.EmailsModel.Edit({'id':id}, email)
               else:
                  self.EmailsModel.Add(email)

            # delete it out of the queue
            del emailschunk[0]
            del typeschunk[0]
            del emails[0]
            del types[0]
            i += 1


   def CheckEmailDeletes(self, members):
      ''' look and see if any emails were deleted '''
      # check all the old emails for each member
      for member in members:
         oldemails = self.EmailsModel.Browse({'memberid':member, 'deleted':0}, ['id'])
         for email in oldemails:
            # if that email isn't in the new list, delete it
            if not str(email['id']) in self.form.getlist('emailid'):
               self.EmailsModel.Edit({'id':email['id']}, {'deleted':1})


   def AjaxDeleteFamily(self):
      ''' delete the family '''
      # catch and toggle deleted
      family = {'id':self.form.getvalue('id')}
      self.FamiliesModel.Edit(family, {'deleted':1})

      # debug info
      print 'content-type: application/json \n'
      print json.dumps(family)


if __name__ == '__main__':
   # run the app
   x = Webapp()
   x.run()

