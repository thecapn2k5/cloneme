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

   def Browse(self):
      ''' the browse page of the families '''
      varHash = {'Services':self.ServicesModel.Browse({'deleted':0})}
      return self.template('attendance/browse.html', varHash)


   def AddService(self):
      ''' save the new service '''
      # save the basic stuff
      varHash = {}
      varHash['name'] = self.form.getvalue('name')

      # get the date properly
      date = '%s %s:%s%s' % (self.form.getvalue('date'), self.form.getvalue('hour'), self.form.getvalue('minute'), self.form.getvalue('ampm'))
      varHash['timestamp'] = datetime.datetime.strptime(date, '%Y-%m-%d %I:%M%p')

      # add and return
      self.ServicesModel.Add(varHash)
      return self.redirect('?mode=Attendance')


   def Edit(self):
      ''' show the attendance tracker '''
      # the base
      varHash = self.ServicesModel.Read(self.form.getvalue('id'))
      varHash['timestamp'] = str(varHash['timestamp'])

      # get lists
      members = self.MembersModel.Browse({'deleted':0})
      attendees = self.AttendanceModel.Browse({'serviceid':varHash['id']})

      # i only want the ids
      for attendee in attendees:
         attendees[attendees.index(attendee)] = attendee['memberid']

      # check present members
      for member in members:
         if member['id'] in attendees:
            member['checked'] = 'checked'
            attendees.pop(attendees.index(member['id']))

      # attendees who have been deleted
      for attendee in attendees:
         members.append(self.MembersModel.Read(attendee))
         members[-1]['checked'] = 'checked'

      # save the members
      varHash['Members'] = members

      # give the template
      return self.template('attendance/edit.html', varHash)


   def AjaxTogglePresent(self):
      ''' toggle whether they were there or not '''
      line = {'serviceid':self.form.getvalue('serviceid'), 'memberid':self.form.getvalue('memberid')}

      if int(self.form.getvalue('present')):
         self.AttendanceModel.Add(line)
      else:
         self.AttendanceModel.Delete(line)
      print 'content-type: application/json \n'
      print json.dumps(line)


   def AjaxDeleteService(self):
      ''' delete the service '''
      # catch and toggle deleted
      service = {'id':self.form.getvalue('id')}
      self.ServicesModel.Edit(service, {'deleted':1})

      # debug info
      print 'content-type: application/json \n'
      print json.dumps(service)


if __name__ == '__main__':
   # run the app
   x = Webapp()
   x.run()

