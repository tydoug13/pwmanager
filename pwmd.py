#!/usr/bin/python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
from datetime import datetime
import util, hashlib, urllib, os 
import json, uuid, time, pytz, sys

HOST = ''
GET_PORT = -1
POST_PORT = -1

class Handler(BaseHTTPRequestHandler):
	def _set_headers(self):
		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin','*')
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		
	def do_POST(self):
		self._set_headers()

		field_list = self.rfile.read(int(self.headers['Content-Length'])).split('&')
		field_dict = dict([f.split('=') for f in field_list])

		if 'create' in field_dict:
			create_user = json.loads(urllib.unquote(field_dict['create']).replace('+', ' '))
			create_user = dict([(str(k),str(create_user[k])) for k in create_user])

			print(create_user)
			self.wfile.write(do_create(self, create_user))
		elif 'login' in field_dict:
			login_user = json.loads(urllib.unquote(field_dict['login']).replace('+', ' '))
			login_user = dict([(str(k),str(login_user[k])) for k in login_user])

			print(login_user)
			self.wfile.write(do_login(self, login_user))
		elif 'start' in field_dict:
			session = field_dict['start']
			if session == '-1':
				util.redirect_login(self, HOST, POST_PORT);
			else:
				start_user = json.loads(urllib.unquote(field_dict['start']).replace('+', ' '))
				start_user = dict([(str(k),str(start_user[k])) for k in start_user])

				print(start_user)
				do_start(self, start_user)
		elif 'logout' in field_dict:
			do_logout(field_dict['logout'])
		else:
			do_command(self, field_dict)

		print('\n' + '-'*80 + '\n')

def do_create(socket, create_user):
	user = create_user['user']
	token = create_user['token']
	hashed_pass_check = str(hashlib.sha256(create_user['token']).hexdigest())

	login_dict = {}
	with open('login.json', 'r+') as loginfile:
		login_dict = json.load(loginfile)

	if user in login_dict:
		return -1
	else:
		cred_dict = {}
		with open('cred.json', 'r+') as credfile:
			cred_dict = json.load(credfile)
			cred_dict[user] = {}
			
		with open('cred.json', 'w+') as credfile:
			json.dump(cred_dict, credfile, sort_keys=True, indent=4, separators=(',', ': '))

	login_dict[user] = {}
	login_dict[user]['hashed_pass'] = str(hashlib.sha256(create_user['token']).hexdigest())
	login_dict[user]['session'] = str(uuid.uuid4())
	login_dict[user]['last_addr'] = socket.client_address[0]
	login_dict[user]['last_time'] = pytz.utc.localize(datetime.utcfromtimestamp(time.time())) \
											.strftime('%Y-%m-%d %H:%M:%S %Z')

	print(dict([(str(k),str(login_dict[user][k])) for k in login_dict[user]]))
	with open('login.json', 'w+') as loginfile:
		json.dump(login_dict, loginfile, sort_keys=True, indent=4, separators=(',', ': '))

	return login_dict[user]['session']

def do_login(socket, login_user):
	user = login_user['user']
	token = login_user['token']
	hashed_pass_check = str(hashlib.sha256(login_user['token']).hexdigest())

	login_dict = {}
	with open('login.json', 'r+') as loginfile:
		login_dict = json.load(loginfile)

	if not user in login_dict:
		print('User %s not found!' % user)
		return '-1'

	hashed_pass = login_dict[user]['hashed_pass']
	if hashed_pass_check != hashed_pass:
		print('Invalid credentials!')
		print(hashed_pass_check + '!=' + hashed_pass)
		return '-1'
	else:
		login_dict[user]['session'] = str(uuid.uuid4())
		login_dict[user]['last_addr'] = socket.client_address[0]
		login_dict[user]['last_time'] = pytz.utc.localize(datetime.utcfromtimestamp(time.time())) \
												.strftime('%Y-%m-%d %H:%M:%S %Z')

		print(dict([(str(k),str(login_dict[user][k])) for k in login_dict[user]]))
		with open('login.json', 'w+') as loginfile:
			json.dump(login_dict, loginfile, sort_keys=True, indent=4, separators=(',', ': '))

		return login_dict[user]['session']

def do_start(socket, start_user):
	user = start_user['user']
	sess = start_user['session']

	login_dict = {}
	with open('login.json', 'r+') as loginfile:
		login_dict = json.load(loginfile)

	if not user in login_dict:
		util.redirect_login(socket, HOST, GET_PORT)

	session = login_dict[user]['session']
	if sess == '-1' or session == '-1' or sess != session:
		print('Invalid session!')
		util.redirect_login(socket, HOST, GET_PORT)
	else:
		util.serve_table(socket, HOST, GET_PORT, POST_PORT, user)

def do_command(socket, field_dict):
	user = urllib.unquote(field_dict['user'])
	target = urllib.unquote(field_dict['site'])
	command = urllib.unquote(field_dict['command'])

	with open('login.json', 'r+') as loginfile:
		login_dict = json.load(loginfile)
		if login_dict[user]['session'] == '-1':
			return

	cred_dict = {}
	if os.path.exists('cred.json'):
		with open('cred.json', 'r+') as credfile:
			cred_dict = json.load(credfile)

	if command == 'del':
		cred_dict[user] = dict([(site, cred_dict[user][site]) for site in cred_dict[user] if site != target])
	elif command == 'add':
		site = target
		passwd = urllib.unquote(field_dict['passwd'])
		cred_dict[user][site] = passwd

	with open('cred.json', 'w+') as credfile:
		json.dump(cred_dict, credfile, sort_keys=True, indent=4, separators=(',', ': '))

	util.serve_table(socket, HOST, GET_PORT, POST_PORT, user)

def do_logout(user):
	login_dict = {}
	with open('login.json', 'r+') as loginfile:
		login_dict = json.load(loginfile)

	if not user in login_dict:
		util.redirect_login(socket, HOST, GET_PORT)
	else:
		login_dict[user]['session'] = '-1'
		print(login_dict)

		with open('login.json', 'w+') as loginfile:
			json.dump(login_dict, loginfile, sort_keys=True, indent=4, separators=(',', ': '))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def run():
	httpd = ThreadedHTTPServer(('', POST_PORT), Handler)
	print('Serving on port %d...\n' % POST_PORT)
	httpd.serve_forever()

if __name__ == "__main__":
	if '-h' in sys.argv:
		HOST = sys.argv[sys.argv.index('-h')+1]

	if '-g' in sys.argv:
		GET_PORT = int(sys.argv[sys.argv.index('-g')+1])

	if '-p' in sys.argv:
		POST_PORT = int(sys.argv[sys.argv.index('-p')+1])

	run()