import os, sys, re
sys.path.append("./lib")
from Kengine import Webapp
try:
   import json
except:
   import simplejson as json

import datetime
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

class Webapp(Webapp):
   """ this is a webapp """

   def Browse(self):
      ''' the browse page of the families '''
      # local vars
      varHash = {'Transactions':self.TransactionsModel.Browse()}
      varHash['Accounts'] = self.AccountsModel.Browse()

      # get stuff for member filter
      varHash['Members'] = self.MembersModel.Browse({'deleted':0})
      varHash['Allocations'] = self.AllocationsModel.BrowseForFinance()
      if not self.config.getboolean('toggles', 'families'):

         # you need the ids and names
         accountids = {}
         accountnames = {}
         for allocation in varHash['Allocations']:
            accountids[allocation['transactionid']] = allocation['accountid']
            accountnames[allocation['transactionid']] = allocation['accountname']

         # put them in the hash
         for transaction in varHash['Transactions']:
            transaction['accountid'] = accountids[transaction['id']]
            transaction['accountname'] = accountnames[transaction['id']]

         # free the ram
         varHash['Allocations'] = []

      # loop through the transactions
      for transaction in varHash['Transactions'] + varHash['Allocations']:
         # you need a description
         if 'description' in transaction and not transaction['description']:
            transaction['description'] = 'No Description'

         # you need the amount
         if 'id' in transaction:
            transaction['amount'] = 0
            allocations = self.AllocationsModel.Browse({'transactionid':transaction['id']})
            for allocation in allocations:
               transaction['amount'] += allocation['amount']

         # positive or negative?
         if transaction['amount'] > 0:
            transaction['income'] = 1
            transaction['type'] = 'income'
         else:
            transaction['expense'] = 1
            transaction['type'] = 'expense'

         # add commas
         transaction['amount'] = locale.currency(transaction['amount'], grouping=True, symbol='')

      return self.template('finance/browse.html', varHash)


   def Add(self):
      ''' show template for adding a transaction '''
      # get vars
      varHash = {'Accounts':self.AccountsModel.Browse()}
      varHash['Members'] = self.MembersModel.Browse({'deleted':0})

      # get template
      return self.template('finance/addedit.html', varHash)


   def AddTransaction(self):
      ''' add a new transaction '''

      # local vars
      varHash = {}

      # not needed
      if self.form.getvalue('description'):
         varHash['description'] = self.form.getvalue('description')

      # catch your transactionid
      transactionid = self.TransactionsModel.Add(varHash)

      # you're allocating to the members
      if self.config.getboolean('toggles', 'families'):
         # build your allocations hash
         allocations = {}
         for key in self.form.keys():
            if key in self.AllocationsModel.columns:
               allocations[key] = self.form.getlist(key)[1:]

         # make sure you're adding something
         if 'amount' in allocations:
            # each allocation
            for i in xrange(len(allocations['amount'])):
               # take out garbage
               amount = re.sub('[^0-9\.-]', '', allocations['amount'][i])
               try:
                  amount = float(amount)
               except:
                  amount = 0

               # build the allocation
               allocation = {'transactionid':transactionid, 'amount':amount}
               allocation['memberid'] = allocations['memberid'][i]
               allocation['accountid'] = allocations['accountid'][i]

               # add it to the database
               self.AllocationsModel.Add(allocation)

      else:
         # base allocation
         allocation = {'transactionid':transactionid, 'accountid':self.form.getvalue('accountid'), 'memberid':0}

         # get the amount as a guaranteed float
         amount = self.form.getvalue('amount')
         if amount:
            amount = re.sub('[^0-9\.-]', '', amount)
            try:
               amount = float(amount)
            except:
               amount = 0
         else:
            amount = 0
         allocation['amount'] = amount

         # add allocation
         self.AllocationsModel.Add(allocation)

      # return to browse
      return self.redirect('?mode=Finance')


   def Read(self):
      """ read mode for a transaction """
      # local vars
      varHash = self.TransactionsModel.Read(self.form.getvalue('id'))
      varHash['amount'] = 0
      varHash['timestamp'] = str(varHash['timestamp'])

      # get the allocations
      varHash['Allocations'] = self.AllocationsModel.ReadForFinance(varHash['id'])

      # get sum and monitize
      for allocation in varHash['Allocations']:
         varHash['amount'] += allocation['amount']
         allocation['amount'] = locale.currency(allocation['amount'], grouping=True, symbol='')

      # monitize the total
      varHash['amount'] = locale.currency(varHash['amount'], grouping=True, symbol='')

      # template
      return self.template('finance/read.html', varHash)


   def JsonAddAccount(self):
      ''' add a new account and return all the accounts '''
      # add the account
      id = self.AccountsModel.Add({'name':self.form.getvalue('name')})

      # give a list of all the accounts
      print 'content-type: application/json \n'
      print json.dumps(self.AccountsModel.Read(id))


if __name__ == '__main__':
   # run the app
   x = Webapp()
   x.run()

