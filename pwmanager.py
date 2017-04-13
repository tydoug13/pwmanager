#!/usr/bin/python

import pwmd, util
import sys, json, subprocess, xml.etree.ElementTree as ET
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

HOST = '127.0.0.1'
GET_PORT = 80
POST_PORT = 1234

class Handler(BaseHTTPRequestHandler):
	def serve_image(self, path):
		with open(path, 'rb+') as iconfile:
			buf = iconfile.read(1024)

			while buf != '':
				self.wfile.write(buf)
				buf = iconfile.read(1024)

			self.wfile.flush()
			self.wfile.close()

	def serve_login(self):
		with open('pwmlogin.html', 'r+') as htmlfile:
			html_string = (htmlfile.read()
						  		   .replace('$INSERT-HOST-NAME$', HOST)
						  		   .replace('$INSERT-HOST-PORT$', str(POST_PORT)))
			
			self.wfile.write(html_string)
			self.wfile.flush()
			self.wfile.close()

	def serve_redirect(self):
		util.redirect_login(self, HOST, GET_PORT)

	def serve_table_loader(self):
		with open('pwmloader.html', 'r+') as htmlfile:
			html_string = (htmlfile.read()
						  		   .replace('$INSERT-HOST-NAME$', HOST)
						  		   .replace('$INSERT-HOST-PORT$', str(POST_PORT)))
			
			self.wfile.write(html_string)
			self.wfile.flush()
			self.wfile.close()

	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()

		if self.path == '/favicon.ico':
			self.serve_image('cipher_icon.gif')
			print('Serving icon...')
		elif '.gif' in self.path:
			self.serve_image(self.path.split('/')[1])
			print('Serving fti...')
		elif self.path == '/':
			print('Serving login page...')
			self.serve_login()
		elif self.path == '/pwmcreate.html':
			with open('pwmcreate.html', 'r+') as create_html:
				html_string = (create_html.read()
										  .replace('$INSERT-HOST-NAME$', HOST)
										  .replace('$INSERT-GET-PORT$',  str(GET_PORT))
										  .replace('$INSERT-POST-PORT$', str(POST_PORT)))
				
				self.wfile.write(html_string)
				self.wfile.flush()
				self.wfile.close()
		else:
			user = self.path.split('/')[1]
			user_exists = False

			with open('login.json', 'r+') as loginfile:
				user_exists = user in json.load(loginfile)

			if not user_exists:
				print('Serving redirect page...')
				self.serve_redirect()
			else:
				print('Serving table loader...')
				self.serve_table_loader()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def main():
	subprocess.Popen([
		'./pwmd.py',
		'-h', ('%s' % HOST),
		'-g', ('%d' % GET_PORT),
		'-p', ('%d' % POST_PORT)
	])

	httpd = ThreadedHTTPServer(('', GET_PORT), Handler)
	print('Serving on ports %d (GET) and %d (POST)...\n' % (GET_PORT, POST_PORT))
	httpd.serve_forever()

if __name__ == "__main__":
	if '-g' in sys.argv:
		GET_PORT = sys.argv[sys.argv.index('-g')+1]

	if '-p' in sys.argv:
		POST_PORT = sys.argv[sys.argv.index('-p')+1]

	main()
