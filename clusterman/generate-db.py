import argparse, bcrypt, sqlite3

conn = sqlite3.connect('rbmc-master.db')
c = conn.cursor()

parser = argparse.ArgumentParser(description='Save username and hash password.')

parser.add_argument('-u', '--username')
parser.add_argument('-p', '--password')

args = vars(parser.parse_args())
print("Username:", args['username'])
print("Password:", '*'*len(args['password']))
pw = bcrypt.hashpw(args['password'].encode('utf8'), bcrypt.gensalt())

tests = \
    [
        '''SELECT * FROM users;''',
    ]

commands = \
    [
        '''CREATE TABLE devices (name text, address text, video_url text, video_format text, vnc_url text);''',
        '''CREATE TABLE users (username text, password_hash text);''',
        '''-''',
    ]

c1 = str(args['username'].encode('utf8'))
c2 = str(pw)

commands[2] = '''INSERT INTO users(username, password_hash) VALUES(''' + c1 + ', ' + c2 + ');'

print(commands[2])

print("Initializing table")

for command in tests:
    exists = True
    try:
        c.execute(command)
    except sqlite3.OperationalError:
        exists = False
        break

confirm = True

if exists == True:
    confirm = False
    user = input("A table currently exists! Do you want to create a new one anyway? [y/N] ")
    if user.lower() == 'y':
        user = input("Confirm complete wipe of saved data? [y/N] ")
        if user.lower() == 'y':
            confirm = True

if confirm == False:
    print("Abort.")
    exit()
else:
    print("Initializing new table...")
    for command in commands:
        c.execute(command)