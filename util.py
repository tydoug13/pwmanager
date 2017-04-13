import sys, json, xml.etree.ElementTree as ET

def redirect_login(socket, hostname, get_port):
	socket.wfile.write(
		'<html>' +
		'<script type="text/javascript">' +
		'window.location = "http://%s:%d"' % (hostname, get_port) +
		'</script>' +
		'</html>'
	)

	socket.wfile.flush()
	socket.wfile.close()

def serve_table(socket, hostname, get_port, post_port, user):
	cred_dict = {}
	with open('cred.json', 'r+') as credfile:
		cred_dict = json.load(credfile)[user]

	jstring = ''
	with open('pwmanager.js', 'r+') as jfile:
		jstring = (jfile.read()
						.replace('$INSERT-HOST-NAME$', hostname)
						.replace('$INSERT-GET-PORT$',  str(get_port))
						.replace('$INSERT-POST-PORT$', str(post_port)))

	jstring_dict = {}
	for site in cred_dict:
		passwd = cred_dict[site]

		newjs = jstring.replace('$INSERT-SITE-ID$', site)
		newjs = newjs.replace('$INSERT-PASSWORD$', passwd)

		jstring_dict[site] = newjs

	outstr = ''
	with open('pwmanager.html', 'r+') as htmlfile:
		html = ET.fromstring(''.join([l for l in htmlfile]))
		table = html.findall('.//table')[0]
		script = html.findall('.//script')[1]

		for site in sorted(cred_dict):
			add_row(script, jstring_dict[site], table, site, cred_dict[site])

		outstr = ET.tostring(html, method='html') \
				   .replace('&lt;', '<') 		  \
				   .replace('&gt;', '>')          \
				   .replace('&amp;', '&')         \
				   .replace('$INSERT-USER$', user) \
				   .replace('$INSERT-HOST-NAME$', hostname) \
				   .replace('$INSERT-HOST-PORT$', str(post_port))

	socket.wfile.write(outstr)
	socket.wfile.flush()
	socket.wfile.close()

def add_col(trow, site, passwd, pos):
	col_weights = [6, 20, 20, 42, 6, 6]

	if pos == 0:
		remove_button = ET.Element('button', {
				'onclick':'%s_del()' % site,
				'class':'minus-button'
			}
		)
		remove_button.text = '&#8211;'

		tcol = ET.SubElement(trow, 'th', {
				'class':'first-col',
				'style':'font-weight:normal;'
						'width:%d%%;' % col_weights[pos]
			}
		)
		tcol.append(remove_button)
	
	elif pos == 1:
		tcol = ET.SubElement(trow, 'th', {
				'id':'%s_site' % site,
				'style':'font-weight:normal;'
						'width:%d%%;' % col_weights[pos]
			}
		)
		tcol.text = site.replace('_APOS_', '\'')
		tcol.text = tcol.text.replace('_QUOT_', '\"')
		tcol.text = tcol.text.replace('_SPACE_', ' ')

	elif pos == 2:
		tcol = ET.SubElement(trow, 'th', {
				'style':'font-weight:normal;'
						'width:%d%%;' % col_weights[pos]
			}
		)

		tcol.append(
			ET.Element('input', {
				'type':'password',
				'id':'%s_decrypt_key' % site,
				'oninput':'%s_decrypt()' % site,
				'style':'font-weight:bolder;'
						'font-size:100%;'
						'text-align:center;'
						'width:90%;'
			})
		)

	elif pos == 3:
		tcol = ET.SubElement(trow, 'th', {
				'id':'%s_passwd' % site,
				'style':'font-weight:normal;'
						'width:%d%%;' % col_weights[pos]
			}
		)
		tcol.text = passwd

	elif pos == 4:
		tcol = ET.SubElement(trow, 'th', {
				'style':'font-weight:normal;'
						'width:%d%%;' % col_weights[pos]
			}
		)

		tcol.append(
			ET.Element('input', {
				'type':'checkbox',
				'id':'%s_toggle_input' % site,
				'onclick':'%s_do_hide()' % site,
				'style':'border: 1px solid black;'
						'font-weight:normal;'
						'text-align: center;'
						'width:90%;'
			})
		)

	elif pos == 5:
		remove_button = ET.Element('img', {
				'onclick':'%s_do_copy()' % site,
				'class':'copy-img',
				'src': 'data:image/png;base64,'
						'iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAABtUlEQVRoQ+'
						'2Z4VHDMAyFXyeADWADugGwARtAN6ATACMwQbsJsAFswAhsAPdyNmdCmkiKnPqHdJcfvZNsffaT7KQr+'
						'NkrgEuH4TYA9tJxVlJHgZ8XAKcSQ9QAuAZAGK09AngogkQQLQJ8ALhIIJMQLQI8AfgEsJNAtApAOd1JIDwB1kn'
						'7NzNrgDtAANokBAE8Wh8newNACNq7toJT0iziEmASggDfhsmGQti7WXRWy12oDzAKUQIw0GLc5rMUOAdiDOAgRAlgrYf+'
						'AWaFmAIYhPAE2CYdn6SrgFZOGYALMnYQsknkWtt4AvAE/kqTWyD6J7FIzt4AXLncTrUQVwD4SK27dtQA4LhWCGny9Ou6Zy'
						'2AJSCqA9SGWASgJsRiALUg3AF4/2EbPWTnAPjQngHcayp2wNcdQJMPL36aljk0thuAJnEm/ZJurgHgdQ7EDmhWoPCNGrAsXBRx'
						'SMiimyImJBQSCgnFXehXA3ESW8oh2mhrbZSvmLeWrcz/IXh8F9LM35dQ/q0Z44/vsQFOiw+1JohjA5iSLoMCQLmEnm20mzp2oKUdUOYyy'
						'93jy9w/Cc3KSBnsBvADPNzWtVGfFQAAAAAASUVORK5CYII='
			}
		)
	
		tcol = ET.SubElement(trow, 'th', {
				'class':'last-col',
				'style':'font-weight:normal;'
						'border-right: none;'
						'width:%d%%;' % col_weights[pos]
			}
		)
		tcol.append(remove_button)

def add_row(script, jstring, table, site, passwd):
	script.text = script.text + '\n' + jstring + '\n'
	trow = ET.Element('tr', {'class':'data-row'})

	for pos in range(6):
		add_col(trow, site, passwd, pos)

	table.insert(-1, trow)