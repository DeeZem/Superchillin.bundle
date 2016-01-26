
# Superchillin.com Plugin for Plex Media Center

import hashlib

TITLE = "Superchillin"
PREFIX = "/video/superchillin"

ART = "art-default.jpg"
ICON = "icon-default.png"

DOMAIN = 'superchillin.com'
MAIN = 'http://' + DOMAIN + '/'
LOGIN = MAIN + "login.php"
LOGIN2 = MAIN + "login2.php"
THUMB = "http://superchillin.com/2img/%s.jpg"
MOVIESLATEST = MAIN + "latest.php"
MOVIESAZ = MAIN + "azlist.php"
MOVIESYEAR = MAIN + "year.php"
MOVIESRATING = MAIN + "rating.php"
MOVIESKIDS = MAIN + "kids.php"
MOVIELINK = MAIN + "fork.php?file=%s&loc=%s&hd=%s&tv=%s&type=%s&auth=%s&noob=%s&authcook=%s&"
QUERY = MAIN + "search.php?q=%s"
TVSHOWS = MAIN + "series.php"
TVSHOWSALPHA = TVSHOWS + "?dl=1"
TVSHOWSLATEST = TVSHOWS + "?bl=1"
TVSERIES = MAIN + "episodes.php?%s"

SERVERS = {
	"Dallas (Free)":                '22',
	"Frankfurt (Free)":             '24',
	"Global CDN (Premium)":         '8',
	"London (Premium)":             '10',
	"Amsterdam (Premium)":          '18',
	"Copenhagen (Premium)":         '20',
	"Frankfurt (Premium)":          '30',
	"New York City (Premium)":      '38',
	"Washington D.C. (Premium)":    '42',
	"Chicago (Premium)":            '46',
	"Dallas (Premium)":             '52',
	"Los Angeles (Premium)":        '62',
	"San Jose (Premium)":           '65',
	"Miami (Premium)":              '72',
	"Toronto (Premium)":            '76',
	"Sydney (Premium)":             '80'
}

COOKIE = None
AUTHCODE = None
PREMIUM = False

# ####################################################################################################
def Start():
	global COOKIE
	
	checksum = None
	if 'checksum' in Dict:
		checksum = Dict['checksum']
		
	# if the login info has not been changed, load the previous cookie
	if checksum == hashlib.md5(Prefs["email"]+Prefs["password"]).hexdigest() and 'cookie' in Dict:
		Log.Debug('Login info has not changed.')
		COOKIE = Dict['cookie']
		Log.Debug('Cookie loaded from last session.')
	
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R(ICON)

# ####################################################################################################
@handler(PREFIX, TITLE)
def MainMenu():

	if not Login(): return MediaContainer(no_cache=True, message="Login Failed.")
	if not Login(): return MediaContainer(no_cache=True, message="Login Failed.")
	if not PREMIUM: return MediaContainer(no_cache=True, message="Premium account required.")

	oc = ObjectContainer()
	oc.add(DirectoryObject(key=Callback(Movies), title="Movies"))
	oc.add(DirectoryObject(key=Callback(TV), title="TV"))
	oc.add(DirectoryObject(key=Callback(KidsZone), title="Kids Zone"))
	return oc

# ####################################################################################################
@route(PREFIX + '/movies')
def Movies(url=None, title='Movies', showSearch=True, letter=None):
	oc = ObjectContainer(title1=title)
	
	if showSearch:
		oc.add(InputDirectoryObject(key=Callback(SearchMovies), title="Search", prompt="Search Movies", summary="Search Movies"))

	if not url:
		oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESLATEST), title="Order by Latest"))
		oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESAZ), title="Order by A-Z"))
		oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESYEAR), title="Order by Release Date"))
		oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESRATING), title="Order by IMDb Rating"))
		oc.add(DirectoryObject(key=Callback(Movies, url=QUERY % 'High+Bitrate+Test'), title="High Bitrate Test"))
		return oc

	if url == MOVIESAZ and not letter:
		oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESAZ, letter='#'), title="#"))
		for i in map(chr, range(65, 91)):
			oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESAZ, letter=i), title=i))
		return oc

	req = HTML.ElementFromString(HTTP.Request(url,cacheTime = 300,headers = Header(referer=MAIN)).content)

# HTML was changed. Had to modify xpath query to compensate
	#title = req.xpath('//a[@style=\'text-decoration:underline;color:#fff;font-family: verdana,geneva,sans-serif;\']/text()')
	#fileId = req.xpath('//a[@style=\'text-decoration:underline;color:#fff;font-family: verdana,geneva,sans-serif;\']/@id')
	title = req.xpath('//a[@class=\'tippable\']/text()')
	fileId = req.xpath('//a[@class=\'tippable\']/@id')
	if len(fileId) == 0:
		title = req.xpath('//a[@style=\'color:#fff\']/text()')
		fileId = req.xpath('//a[@style=\'color:#fff\']/@id')

	for i in range(len(fileId)):
		# .decode() removes any incompatible characters
		thisTitle = title[i].decode('utf-8','ignore')
		thisfileId = fileId[i]
		if thisTitle[:1].upper() == letter or (letter == '#' and thisTitle[:1].upper() not in map(chr, range(65, 91))):
			oc.add(DirectoryObject(
				key=Callback(VideoDetail, title=thisTitle, fileId=thisfileId, tv=0),
				thumb = THUMB % thisfileId,
				title = thisTitle
			))
	return oc

# ####################################################################################################
def SearchMovies(query):
	return Movies(url=(QUERY % query.replace(" ", "+")), title='Search: '+query, showSearch=False)

# ####################################################################################################
@route(PREFIX + '/tv')
def TV(url=None, title='Series', showSearch=True):
	oc = ObjectContainer(title1=title)
	
	if showSearch:
		oc.add(InputDirectoryObject(key=Callback(SearchTV), title="Search", prompt="Search TV", summary="Search TV"))

	if not url:
		oc.add(DirectoryObject(key=Callback(TV, url=TVSHOWSLATEST), title="Order by Latest"))
		oc.add(DirectoryObject(key=Callback(TV, url=TVSHOWSALPHA), title="Order by A-Z"))
		oc.add(DirectoryObject(key=Callback(TV, url=TVSHOWS), title="Regular Listing"))
		return oc

	req = HTML.ElementFromString(HTTP.Request(url,cacheTime = 300,headers = Header(referer=MAIN)).content)
	title = req.xpath('//a[@style=\'color:#fff\']/text()') if showSearch else req.xpath('//a[@style=\'text-decoration:underline;color:#ffff00;font-family: verdana,geneva,sans-serif;\']/text()')
	showId = req.xpath('//a[@style=\'color:#fff\']/@href') if showSearch else req.xpath('//a[@style=\'text-decoration:underline;color:#ffff00;font-family: verdana,geneva,sans-serif;\']/@href')

	for i in range(len(showId)):
		# .decode() removes any incompatible characters
		thisTitle = title[i].decode('utf-8','ignore')
		thisshowId = showId[i].split('?')[1]
		oc.add(DirectoryObject(
			key=Callback(TVSeries, title=thisTitle, showId=thisshowId),
			thumb = THUMB % ('sh'+thisshowId),
			title = thisTitle
		))
	return oc

# ####################################################################################################
def SearchTV(query):
	return TV(url=(QUERY % query.replace(" ", "+")), title='Search: '+query, showSearch=False)

# ####################################################################################################
@route(PREFIX + '/kids')
def KidsZone():
	oc = ObjectContainer(title1='Kids Zone')

	req = HTML.ElementFromString(HTTP.Request(MOVIESKIDS,cacheTime = 300,headers = Header(referer=MAIN)).content)
	title = req.xpath('//a[@style=\'color:#fff\']/text()')
	fileId = req.xpath('//a[@style=\'color:#fff\']/@href')

	for i in range(len(fileId)):
		# .decode() removes any incompatible characters
		thisTitle = title[i].decode('utf-8','ignore')
		thisfileId = fileId[i].split('?')[1]
		oc.add(DirectoryObject(
			key=Callback(VideoDetail, title=thisTitle, fileId=thisfileId, tv=0),
			thumb = THUMB % thisfileId,
			title = thisTitle
		))
	return oc
	
# ####################################################################################################
@route(PREFIX + '/tv/show')
def TVSeries(title, showId):
	oc = ObjectContainer(title1=title)
	
	req = HTML.ElementFromString(
		HTTP.Request(TVSERIES % showId, cacheTime = 300, headers = Header(referer=MAIN)).content
	)
	epTitle = req.xpath('//a[@style=\'color:#fff\']/text()')
	epId = req.xpath('//a[@style=\'color:#fff\']/@href')

	for episode in req.xpath('//b[position() > 1]'):
		# .decode() removes any incompatible characters
		epNum = episode.xpath('./text()')[0]
		epTitle = episode.xpath('./a/text()')[0].decode('utf-8','ignore')
		epFileId = episode.xpath('./a/@href')[0].split('?')[1].split('&')[0]
		oc.add(DirectoryObject(
			key=Callback(VideoDetail, title=epTitle, fileId=epFileId, tv=1),
			thumb = THUMB % ('ep'+epFileId),
			title = (epNum + epTitle)
		))
	return oc

# ######################################################################################
@route(PREFIX + "/detail")
def VideoDetail(title, fileId, tv):
	url = MAIN + '?' + fileId + '&tv=' + tv
	fullHD = 'Watch in 1080p' in HTTP.Request(url,headers = Header(referer=MAIN)).content

	oc = ObjectContainer(title1 = title)
	oc.add(VideoClipObject(title = "720p", url = CreateURL(fileId, hd=0, tv=tv)))
	if fullHD and PREMIUM:
		oc.add(VideoClipObject(title = "1080p", url = CreateURL(fileId, hd=1, tv=tv)))

	return oc

# ####################################################################################################
def Header(referer=None, host=DOMAIN):
	headers = {
			"Host":              host,
			"User-Agent":        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
			"Accept":            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
			"Accept-Language":   "en-US,en;q=0.5",
			"Accept-Encoding":   "gzip, deflate",
			"Connection":        "keep-alive",
			"Content-Type":      "application/x-www-form-urlencoded",
			"If-Modified-Since": "*"
		}
	if referer:
		headers['Referer'] = referer
	if COOKIE:
		headers['Cookie'] = COOKIE
	return headers

# ####################################################################################################
def GetCookie(name):
	if not COOKIE:
		return None
	cookies = COOKIE.split("; ")
	for cookie in cookies:
		key, val = cookie.split("=")
		if key == name:
			return val
	return None

# ####################################################################################################
def Login():
	global COOKIE
	global AUTHCODE
	global PREMIUM

	logged_in = False
	page = None
	
	if not Prefs['email'] or not Prefs['password']:
		return False # we can't login if we don't have credentials

	if COOKIE: # if we've already logged in
		try: # make sure we are still logged in
			req = HTTP.Request(LOGIN, follow_redirects=False, headers=Header())
			req.load()
		except Ex.RedirectError, e:
			logged_in = True # if login page redirected, we are already logged in
	
	# no need to continue if we already have the authcode
	if logged_in and AUTHCODE:
		return True
	
	# if we've gotten this far and aren't logged in
	if not logged_in:
		# let's send the login request
		Log.Debug('Logging into server.')
		COOKIE = None
		page = HTML.ElementFromURL(LOGIN2,
			headers=Header(referer=LOGIN),
			values={
				"email": Prefs["email"],
				"password": Prefs["password"],
				"remember": "on",
				"x": "0",
				"y": "0",
				"echo": "echo"
			},
			cacheTime=0)
		
		# if there is still a login button on the page then the login failed
		loginbutton = page.xpath("//form[@name='login']//@action")
		logged_in = True if not loginbutton else False
	else:
		page = HTML.ElementFromURL(MAIN, headers=Header(), cacheTime=0)

	# if we logged in successfully...
	if logged_in:
		# save cookie
		COOKIE = HTTP.CookiesForURL(MAIN)
		Dict['cookie'] = COOKIE
		Dict['checksum'] = hashlib.md5(Prefs["email"]+Prefs["password"]).hexdigest()
		# retrieve the auth code
		script = page.xpath("//div[@style='position:relative']//script[@type='text/javascript']//text()")[0]
		AUTHCODE = script.split('auth=')[1].split('&')[0]
		# check for premium
		PREMIUM = page.xpath("//a[@href='premium.php']/text()")[0] != 'Inactive'
	return logged_in

# ####################################################################################################
def CreateURL(file, hd=0, tv=0):
	return MOVIELINK % (
		file, # file
		SERVERS[Prefs['server']], # loc
		hd, # hd
		tv, # tv
		'mp4' if PREMIUM else 'flv', # type
		AUTHCODE, # auth
		GetCookie('noob'), # noob
		GetCookie('auth') # authcook
	)
