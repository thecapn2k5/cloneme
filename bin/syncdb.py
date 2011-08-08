#!/usr/bin/python2.7

import ConfigParser, MySQLdb, os, shutil

# Get the config vars
config = ConfigParser.ConfigParser()
if 'config.ini' in os.listdir('.'):
   config.read('config.ini')
elif 'devconfig.ini' in os.listdir('.'):
   config.read('devconfig.ini')
else:
   print 'No Config File'

# Create a Database connection
conn = MySQLdb.connect(
   host = config.get('database', 'host'),
   db = str(config.get('database','database')),
   user = config.get('database','username'),
   passwd = config.get('database','password'))
cursor = conn.cursor(MySQLdb.cursors.DictCursor)

# Creating sessions table
cursor.execute('DROP TABLE IF EXISTS sessions')
cursor.execute('''
CREATE TABLE sessions (
   username varchar(255) DEFAULT NULL,
   id varchar(255) DEFAULT NULL,
   created datetime DEFAULT NULL,
   ip varchar(255) DEFAULT NULL)
''')
 
# Creating users table
cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('''
   CREATE TABLE users (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      username VARCHAR(255) DEFAULT '',
      password VARCHAR(255) DEFAULT '',
      active TINYINT(1) DEFAULT 1
)
''')

# Creating topnav table
cursor.execute('DROP TABLE IF EXISTS topnav')
cursor.execute('''
   CREATE TABLE topnav (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      name VARCHAR(255) DEFAULT ''
)
''')

# Creating pages table
cursor.execute('DROP TABLE IF EXISTS pages')
cursor.execute('''
   CREATE TABLE pages (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      name VARCHAR(255) DEFAULT '',
      parent VARCHAR(255) DEFAULT '',
      content TEXT NOT NULL
)
''')

# Creating families table
cursor.execute('DROP TABLE IF EXISTS families')
cursor.execute('''
   CREATE TABLE families (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      familyname VARCHAR(255) NOT NULL DEFAULT '',
      address VARCHAR(255) NOT NULL DEFAULT '',
      anniversary DATE,
      deleted TINYINT DEFAULT 0)
''')

# Creating members table
cursor.execute('DROP TABLE IF EXISTS members')
cursor.execute('''
   CREATE TABLE members (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      familyid INT NOT NULL DEFAULT 0,
      firstname VARCHAR(255) NOT NULL DEFAULT '',
      secondname VARCHAR(255) NOT NULL DEFAULT '',
      lastname VARCHAR(255) NOT NULL DEFAULT '',
      relationship VARCHAR(255) NOT NULL DEFAULT '',
      birthday DATE,
      deleted TINYINT DEFAULT 0)
''')

# Creating phones table
cursor.execute('DROP TABLE IF EXISTS phones')
cursor.execute('''
   CREATE TABLE phones (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      memberid INT DEFAULT 0,
      phone VARCHAR(255) NOT NULL DEFAULT '',
      description VARCHAR(255) NOT NULL DEFAULT '',
      deleted TINYINT DEFAULT 0)
''')

# Creating emails table
cursor.execute('DROP TABLE IF EXISTS emails')
cursor.execute('''
   CREATE TABLE emails (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      memberid INT DEFAULT 0,
      email VARCHAR(255) NOT NULL DEFAULT '',
      description VARCHAR(255) NOT NULL DEFAULT '',
      deleted TINYINT DEFAULT 0)
''')

# Creating services table
cursor.execute('DROP TABLE IF EXISTS services')
cursor.execute('''
   CREATE TABLE services (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      name VARCHAR(255) NOT NULL DEFAULT '',
      timestamp DATETIME,
      deleted TINYINT(1) DEFAULT 0)
''')

# Creating attendance table
cursor.execute('DROP TABLE IF EXISTS attendance')
cursor.execute('''
   CREATE TABLE attendance (
      serviceid INT,
      memberid INT)
''')

# Creating accounts table
cursor.execute('DROP TABLE IF EXISTS accounts')
cursor.execute('''
   CREATE TABLE accounts (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      name VARCHAR(255) NOT NULL DEFAULT '')
''')

# Creating transactions table
cursor.execute('DROP TABLE IF EXISTS transactions')
cursor.execute('''
   CREATE TABLE transactions (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      description TEXT NOT NULL,
      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
''')

# Creating allocations table
cursor.execute('DROP TABLE IF EXISTS allocations')
cursor.execute('''
   CREATE TABLE allocations (
      id INT NOT NULL AUTO_INCREMENT,
      PRIMARY KEY(id),
      transactionid INT,
      memberid INT,
      accountid INT,
      amount FLOAT(9,2) NOT NULL,
      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
''')


# Loading users table
cursor.execute('INSERT INTO users (username, password) VALUES ("chris", SHA1("password"))')

# Loading topnav table
cursor.execute('INSERT INTO topnav (name) VALUES ("Home")')

# Loading pages table
cursor.execute('INSERT INTO pages (parent, name, content) VALUES (1, "Home", "")')

# Loading accounts table
cursor.execute('INSERT INTO accounts (name) VALUES ("General")')

if os.path.exists('uploads'):
   shutil.rmtree('uploads')
os.mkdir('uploads')
os.chmod('uploads', 0777)
os.chown('uploads', -1, os.getegid())
os.system('touch uploads/.keepme')

