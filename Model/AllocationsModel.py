from DBreadModel import DBreadModel

class AllocationsModel(DBreadModel):

   def BrowseForFinance(self):
      """ this will get all the info for the allocations """
      self.cursor.execute("""
         SELECT
            allocations.transactionid,
            allocations.accountid,
            allocations.amount,
            allocations.timestamp,
            allocations.memberid,
            accounts.name AS accountname,
            IF(allocations.memberid,
               members.firstname,
               "Nobody") AS firstname,
            IF(allocations.memberid,
               members.secondname,
               "") AS secondname,
            IF(allocations.memberid,
               members.lastname,
               "") AS lastname
       FROM accounts, allocations
      LEFT JOIN members on allocations.memberid=members.id
      WHERE accounts.id=allocations.accountid
      """)
      return list(self.cursor.fetchall())


   def ReadForFinance(self, transactionid):
      """ this will get all the info for one transaction """
      self.cursor.execute("""
         SELECT
            allocations.transactionid,
            allocations.accountid,
            allocations.amount,
            allocations.timestamp,
            allocations.memberid,
            accounts.name AS accountname,
            IF(allocations.memberid,
               members.firstname,
               "Nobody") AS firstname,
            IF(allocations.memberid,
               members.secondname,
               "") AS secondname,
            IF(allocations.memberid,
               members.lastname,
               "") AS lastname
       FROM accounts, allocations
      LEFT JOIN members on allocations.memberid=members.id
      WHERE accounts.id=allocations.accountid
        AND allocations.transactionid=%s
      """, (transactionid))
      return list(self.cursor.fetchall())

