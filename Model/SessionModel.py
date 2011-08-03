import uuid, os

class SessionModel:
   """ Handles all session transactions """
   def __init__(self, cursor):
      self.cursor = cursor


   def Get(self, username):
      """ Get a session if one exists """
      self.cursor.execute("SELECT id from sessions where username=%s", username)
      session = self.cursor.fetchone()

      # Did we get one?
      if session:
         return session['id']
      else:
         return 0


   def Validate(self, username, password):
      """ test to see valid username/password """
      self.cursor.execute("SELECT username, password FROM users WHERE username=%s and password=SHA1(%s) AND active=1", (username, password))

      # if we got one, save a new session
      if self.cursor.fetchone():
         self.cursor.execute("DELETE FROM sessions WHERE username=%s", username)
         session = str(uuid.uuid4())

         # Record the session
         self.cursor.execute("INSERT INTO sessions(username, id, created, ip) VALUES (%s, %s, now(), %s)", (username, session, os.environ['REMOTE_ADDR']))
         return session

      else:
         return 0
