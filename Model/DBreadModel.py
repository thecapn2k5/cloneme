"""
   Author: Chris Morgan <chris@chrism.biz>

   USAGE INSTRUCTIONS

   The purpose of this class is to dynamically handle the database layer for a single bread.  It provides all of the basic database functionality for a BREAD style web app.
"""

class DBreadModel:
   " Dynamic Bread Model "

   def __init__(self, table, cursor, CurrentUser=False):
      """ this must be passed the name of the table that you're working on and a MySQLdb cursor """
      # local vars
      columns = [] 		# get the list of columns
      self.cursor = cursor      # allow access to the cursor
      self.table = str(table)   # set the var for the table

      try:
         # describe the table being asked for
         describe = "DESCRIBE " + self.table
         self.cursor.execute(describe)
         columninfo = self.cursor.fetchall()

         # build the list of columns from the hash
         if columninfo:
            for column in columninfo:
               columns.append(str(column['Field']))

      # this will catch it if they request a table that doesn't exist
      except:
         raise Exception, 'You have requested an unrecognized table.  Try again.'

      # set the class variable for columns as columns
      self.columns = columns

      # from Kengine, an object containing stuff needed for current user
      self.CurrentUser = CurrentUser

      # call a local init function to be overwritten by a child class
      self.local_init()


   def local_init(self):
      """ overwrite this sub to have a local function that is run on init """
      pass


   def Browse(self, queryDict={}, columns=[]):
      """ this is the Browse function.  Pass it a list of columns or you will get the all the columns.  If you pass it a queryDict, the keys must be the column names and the values must be the values you want in the column. """
      # local vars
      results = ''
      args = []

      # make sure they want something
      if not columns:
         columns = self.columns

      # the base query
      myQuery = "SELECT DISTINCT %s FROM %s" % (','.join(columns), self.table)

      # if they specified parameters, factor them in
      if queryDict:
         myQuery += " WHERE "

         # go through the dict and factor in all the key/value pairs
         for key in queryDict.keys():
            myQuery += str(key) + "=%s AND "
            args.append(str(queryDict[key]))

         # delete the last ' AND '
         myQuery = myQuery[:-5]

      # make the query sort
      myQuery += " ORDER BY "

      # sort in order of the columns in the list
      for column in columns:
         myQuery += column + " ASC, "

      # take off the last ", "
      myQuery = myQuery[:-2]

      # execute the query and give back results
      self.cursor.execute(myQuery, args)
      return list(self.cursor.fetchall())


   def Read(self, id, columns=[]):
      """ pass an id and an optional list of columns to get all the info for a given id.  the list of columns will limit which columns are returned """
      # local vars
      args = [str(id)]

      # if they specify a list of columns, give it to them.  otherwise, give them everything
      if not columns:
         columns = self.columns

      # the base query
      myQuery = 'SELECT DISTINCT %s FROM %s ' % (','.join(columns), str(self.table))

      # add the WHERE clause
      myQuery += 'WHERE id=%s'

      # execute the query and return the result
      self.cursor.execute(myQuery, args)
      return self.cursor.fetchone()


   def Edit(self, currDict, newDict):
      """ this will update the database on the row(s) where the keys=values in currDict to reflect the key/value pairs in newDict.  the dictionaries are to exist where the keys are the titles of the columns and the values are to be the new values for those columns. """
      # local vars
      args = []
      newQuery = ''   # build the SET part of the query

      if not newDict:
         return

      for (k, v) in newDict.items():
         # if there is no value, insert MySQL Null value
         if not v:
            v = ''
         # if it's a password, use SHA1
         if str(k) == 'password':
            newQuery += str(k) + "=SHA1(%s), "
         # if it's not a password, handle it
         else:
            newQuery += str(k) + "=%s, "
         # add the value to the list of arguments to allow MySQLdb to sanitize it
         args.append(str(v))

      # shave off the last ", "
      newQuery = newQuery[:-2]

      # build the WHERE part of the query
      oldQuery = ''
      for (k, v) in currDict.items():
         # if there is no value, insert MySQL Null value
         if not v:
            v = ''
         # if it's a password, use SHA1
         if str(k) == 'password':
            oldQuery += str(k) + "=SHA1(%s) AND "
         # if it's not a password, handle it
         else:
            oldQuery += str(k) + "=%s AND "
         # add the value to the list of arguments to allow MySQLdb to sanitize it
         args.append(str(v))

      # shave off the last " AND "
      oldQuery = oldQuery[:-5]

      # prep the query
      myQuery = "UPDATE " + str(self.table) + " SET " + str(newQuery) + " WHERE " + str(oldQuery)

      # execute the query
      self.cursor.execute(myQuery, args)


   def Add(self, addHash):
      """ pass this function a hash of all the columns/values you want to put in """
      # local vars
      args = []
      myColumns = ''
      myValues = ''

      # build the args and the columns
      for (k, v) in addHash.items():
         myColumns += str(k) + ", "
         if k == 'password':
            myValues += "SHA1(%s), "
         else:
            myValues += "%s, "
         args.append(str(v))

      # take off the last ", " from myColumns and myValues
      myColumns = myColumns[:-2]
      myValues = myValues[:-2]

      # build the add query and execute
      myQuery = "INSERT INTO %s (%s) VALUES (%s)" % (str(self.table), myColumns, myValues)
      self.cursor.execute(myQuery, args)

      return self.GetLastInsertId()


   def Delete(self, delHash):
      """ pass a hash of what must be true to this function to delete from the table """
      # local vars
      args = []
      myQuery = 'DELETE FROM %s WHERE ' % str(self.table)

      # build the args list and the WHERE part of the query
      for (k, v) in delHash.items():
         if not v:
            v = ''
         if str(k) == 'password':
            myQuery += str(k) + "=SHA1(%s) AND "
         else:
            myQuery += str(k) + "=%s AND "
         args.append(str(v))

      # shave off the last " AND "
      myQuery = myQuery[:-5]

      # do the delete from the questions table
      self.cursor.execute(myQuery, args)


   def GetLastInsertId(self):
      """ returns the last id inserted as a string """
      self.cursor.execute('SELECT LAST_INSERT_ID() AS id')
      return self.cursor.fetchone()['id']

