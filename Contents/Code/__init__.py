
# Superchillin.com Plugin for Plex Media Center

import hashlib

TITLE = "Superchillin"
PREFIX = "/video/superchillin"

ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_NEXT = "icon-next.png"
ICON_PREV = "icon-prev.png"

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

PAGESIZE = 200
CACHETIME = 300

SERVERS = {
	"Frankfurt (Free)":             '24',
	"Global CDN (Premium)":         '8',
	"London (Premium)":             '10',
	"Amsterdam (Premium)":          '18',
	"Frankfurt (Premium)":          '30',
	"Washington D.C. (Premium)":    '42',
	"Dallas (Premium)":             '52',
	"San Jose (Premium)":           '65',
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
	if Prefs['usecookie'] and checksum == hashlib.md5(Prefs["auth"]+Prefs["noob"]).hexdigest():
		Log.Debug('Manual cookie has not changed not changed.')
		COOKIE = Dict['cookie']
		Log.Debug('Cookie loaded from last session.')
	if not Prefs['usecookie'] and checksum == hashlib.md5(Prefs["email"]+Prefs["password"]).hexdigest() and 'cookie' in Dict:
		Log.Debug('Login info has not changed.')
		COOKIE = Dict['cookie']
		Log.Debug('Cookie loaded from last session.')
	
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = TITLE
	DirectoryObject.thumb = R(ICON)

# ####################################################################################################
@handler(PREFIX, TITLE)
def MainMenu():
	global PAGESIZE

	PAGESIZE = int(Prefs['pages'])

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
def Movies(url=None, title='Movies', showSearch=True, letter=None, page=1):
	oc = ObjectContainer(title1=title)
	
	if showSearch:
		oc.add(InputDirectoryObject(key=Callback(SearchMovies), title="Search", prompt="Search Movies", summary="Search Movies"))

	if not url:
		oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESLATEST), title="Order by Latest"))
		oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESAZ), title="Order by A-Z"))
		oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESYEAR), title="Order by Release Date"))
		oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESRATING), title="Order by IMDb Rating"))
		oc.add(DirectoryObject(key=Callback(Movies, url=QUERY % 'High+Bitrate'), title="High Bitrate"))
		return oc

	if url == MOVIESAZ and not letter:
		oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESAZ, letter='#'), title="#"))
		for i in map(chr, range(65, 91)):
			oc.add(DirectoryObject(key=Callback(Movies, url=MOVIESAZ, letter=i), title=i))
		return oc

	req = HTML.ElementFromString(HTTP.Request(url,cacheTime = CACHETIME,headers = Header(referer=MAIN)).content)

	if not letter:
		title = req.xpath("//a[@class='tippable']/text()|//a[@style='color:#fff']/text()")
		fileId = req.xpath("//a[@class='tippable']/@id|//a[@style='color:#fff']/@id")
	elif letter != '#':
		title = req.xpath("//a[@class='tippable' and starts-with(text(),'"+letter+"')]/text()")
		fileId = req.xpath("//a[@class='tippable' and starts-with(text(),'"+letter+"')]/@id")
	elif letter == '#':
		title = req.xpath("//a[@class='tippable' and starts-with(text(),'0') or starts-with(text(),'1') or starts-with(text(),'2') or starts-with(text(),'3') or starts-with(text(),'4') or starts-with(text(),'5') or starts-with(text(),'6') or starts-with(text(),'7') or starts-with(text(),'8') or starts-with(text(),'9')]/text()")
		fileId = req.xpath("//a[@class='tippable' and starts-with(text(),'0') or starts-with(text(),'1') or starts-with(text(),'2') or starts-with(text(),'3') or starts-with(text(),'4') or starts-with(text(),'5') or starts-with(text(),'6') or starts-with(text(),'7') or starts-with(text(),'8') or starts-with(text(),'9')]/@id")

	page=int(page)
	filesForPage = range(len(fileId))[ (page-1)*PAGESIZE : page*PAGESIZE ]

	for i in filesForPage:
		thisTitle = title[i].decode('utf-8','ignore')
		thisFileId = fileId[i]
		oc.add(DirectoryObject(
			key=Callback(VideoDetail, title=thisTitle, fileId=thisFileId, tv=0),
			thumb = THUMB % thisFileId,
			title = thisTitle
		))
	if page > 1:
		oc.add(DirectoryObject(key=Callback(Movies, url=url, letter=letter, page=page-1), title="Previous Page", thumb=R(ICON_PREV)))
	if page*PAGESIZE < len(fileId):
		oc.add(DirectoryObject(key=Callback(Movies, url=url, letter=letter, page=page+1), title="Next Page", thumb=R(ICON_NEXT)))
	return oc

# ####################################################################################################
def SearchMovies(query):
	return Movies(url=(QUERY % query.replace(" ", "+")), title='Search: '+query, showSearch=False)

# ####################################################################################################
@route(PREFIX + '/tv')
def TV(url=None, title='Series', showSearch=True, letter=None, page=1):
	oc = ObjectContainer(title1=title)
	
	if showSearch:
		oc.add(InputDirectoryObject(key=Callback(SearchTV), title="Search", prompt="Search TV", summary="Search TV"))

	if not url:
		oc.add(DirectoryObject(key=Callback(TV, url=TVSHOWSLATEST), title="Order by Latest"))
		oc.add(DirectoryObject(key=Callback(TV, url=TVSHOWSALPHA), title="Order by A-Z"))
		oc.add(DirectoryObject(key=Callback(TV, url=TVSHOWS), title="Regular Listing"))
		return oc

	if url == TVSHOWSALPHA and not letter:
		oc.add(DirectoryObject(key=Callback(TV, url=TVSHOWSALPHA, letter='#'), title="#"))
		for i in map(chr, range(65, 91)):
			oc.add(DirectoryObject(key=Callback(TV, url=TVSHOWSALPHA, letter=i), title=i))
		return oc

	req = HTML.ElementFromString(HTTP.Request(url,cacheTime = CACHETIME,headers = Header(referer=MAIN)).content)

	if not showSearch:
		title = req.xpath("//a[@style='text-decoration:underline;color:#ffff00;font-family: verdana,geneva,sans-serif;']/text()")
		fileId = req.xpath("//a[@style='text-decoration:underline;color:#ffff00;font-family: verdana,geneva,sans-serif;']/@href")
	elif not letter:
		title = req.xpath("//a[@style='color:#fff']/text()")
		fileId = req.xpath("//a[@style='color:#fff']/@href")
	elif letter != '#':
		title = req.xpath("//a[@style='color:#fff' and starts-with(text(),'"+letter+"')]/text()")
		fileId = req.xpath("//a[@style='color:#fff' and starts-with(text(),'"+letter+"')]/@href")
	elif letter == '#':
		title = req.xpath("//a[@style='color:#fff' and starts-with(text(),'0') or starts-with(text(),'1') or starts-with(text(),'2') or starts-with(text(),'3') or starts-with(text(),'4') or starts-with(text(),'5') or starts-with(text(),'6') or starts-with(text(),'7') or starts-with(text(),'8') or starts-with(text(),'9')]/text()")
		fileId = req.xpath("//a[@style='color:#fff' and starts-with(text(),'0') or starts-with(text(),'1') or starts-with(text(),'2') or starts-with(text(),'3') or starts-with(text(),'4') or starts-with(text(),'5') or starts-with(text(),'6') or starts-with(text(),'7') or starts-with(text(),'8') or starts-with(text(),'9')]/@href")

	page=int(page)
	filesForPage = range(len(fileId))[ (page-1)*PAGESIZE : page*PAGESIZE ]

	for i in filesForPage:
		thisTitle = title[i].decode('utf-8','ignore')
		thisFileId = fileId[i].split('?')[1]
		oc.add(DirectoryObject(
			key=Callback(TVSeries, title=thisTitle, showId=thisFileId),
			thumb = THUMB % ('sh'+thisFileId),
			title = thisTitle
		))
	if page > 1:
		oc.add(DirectoryObject(key=Callback(TV, url=url, letter=letter, page=page-1), title="Previous Page", thumb=R(ICON_PREV)))
	if page*PAGESIZE < len(fileId):
		oc.add(DirectoryObject(key=Callback(TV, url=url, letter=letter, page=page+1), title="Next Page", thumb=R(ICON_NEXT)))
	return oc

# ####################################################################################################
def SearchTV(query):
	return TV(url=(QUERY % query.replace(" ", "+")), title='Search: '+query, showSearch=False)

# ####################################################################################################
@route(PREFIX + '/kids')
def KidsZone():
	oc = ObjectContainer(title1='Kids Zone')
	oc.add(DirectoryObject(key=Callback(KidsZoneMovies), title="Movies"))
	oc.add(DirectoryObject(key=Callback(KidsZoneTV), title="TV"))
	return oc

# ####################################################################################################
@route(PREFIX + '/kidsmovies')
def KidsZoneMovies(page=1):
	oc = ObjectContainer(title1='Movies')

	req = HTML.ElementFromString(HTTP.Request(MOVIESKIDS,cacheTime = CACHETIME,headers = Header(referer=MAIN)).content)
	title =  req.xpath('//a[@style=\'color:#fff\' and contains(@href,\'/?\')]/text()')
	fileId = req.xpath('//a[@style=\'color:#fff\' and contains(@href,\'/?\')]/@href')

	page=int(page)
	filesForPage = range(len(fileId))[ (page-1)*PAGESIZE : page*PAGESIZE ]

	for i in filesForPage:
		thisTitle = title[i].decode('utf-8','ignore')
		thisFileId = fileId[i].split('?')[1]
		oc.add(DirectoryObject(
			key=Callback(VideoDetail, title=thisTitle, fileId=thisFileId, tv=0),
			thumb = THUMB % thisFileId,
			title = thisTitle
		))
	if page > 1:
		oc.add(DirectoryObject(key=Callback(KidsZoneMovies, page=page-1), title="Previous Page", thumb=R(ICON_PREV)))
	if page*PAGESIZE < len(fileId):
		oc.add(DirectoryObject(key=Callback(KidsZoneMovies, page=page+1), title="Next Page", thumb=R(ICON_NEXT)))
	return oc

# ####################################################################################################
@route(PREFIX + '/kidstv')
def KidsZoneTV(page=1):
	oc = ObjectContainer(title1='TV')
	
	req = HTML.ElementFromString(HTTP.Request(MOVIESKIDS,cacheTime = CACHETIME,headers = Header(referer=MAIN)).content)
	title =  req.xpath('//a[@style=\'color:#fff\' and contains(@href,\'episodes\')]/text()')
	fileId = req.xpath('//a[@style=\'color:#fff\' and contains(@href,\'episodes\')]/@href')

	page=int(page)
	filesForPage = range(len(fileId))[ (page-1)*PAGESIZE : page*PAGESIZE ]

	for i in filesForPage:
		thisTitle = title[i].decode('utf-8','ignore')
		thisFileId = fileId[i].split('?')[1]
		oc.add(DirectoryObject(
			key=Callback(TVSeries, title=thisTitle, showId=thisFileId),
			thumb = THUMB % ('sh'+thisFileId),
			title = thisTitle
		))
	if page > 1:
		oc.add(DirectoryObject(key=Callback(KidsZoneTV, page=page-1), title="Previous Page", thumb=R(ICON_PREV)))
	if page*PAGESIZE < len(fileId):
		oc.add(DirectoryObject(key=Callback(KidsZoneTV, page=page+1), title="Next Page", thumb=R(ICON_NEXT)))
	return oc
	
# ####################################################################################################
@route(PREFIX + '/tv/show')
def TVSeries(title, showId, page=1):
	oc = ObjectContainer(title1=title)
	
	req = HTML.ElementFromString(HTTP.Request(TVSERIES % showId, cacheTime = CACHETIME, headers = Header(referer=MAIN)).content)
	
	fileList = req.xpath('//b[position() > 1]')

	page=int(page)
	filesForPage = range(len(fileList))[ (page-1)*PAGESIZE : page*PAGESIZE ]

	for i in filesForPage:
		thisNum = fileList[i].xpath('./text()')[0]
		thisTitle = fileList[i].xpath('./a/text()')[0].decode('utf-8','ignore')
		thisFileId = fileList[i].xpath('./a/@href')[0].split('?')[1].split('&')[0]
		oc.add(DirectoryObject(
			key=Callback(VideoDetail, title=thisTitle, fileId=thisFileId, tv=1),
			thumb = THUMB % ('ep'+thisFileId),
			title = (thisNum + thisTitle)
		))
	if page > 1:
		oc.add(DirectoryObject(key=Callback(TVSeries, title=title, showId=showId, page=page-1), title="Previous Page", thumb=R(ICON_PREV)))
	if page*PAGESIZE < len(fileList):
		oc.add(DirectoryObject(key=Callback(TVSeries, title=title, showId=showId, page=page+1), title="Next Page", thumb=R(ICON_NEXT)))
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
	
	if Prefs['usecookie']:
		COOKIE = "auth="+Prefs['auth']+"; noob="+Prefs['noob']
	else:
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
		if not Prefs['usecookie']:
			COOKIE = HTTP.CookiesForURL(MAIN)
		Dict['cookie'] = COOKIE
		if Prefs['usecookie']:
			Dict['checksum'] = hashlib.md5(Prefs["auth"]+Prefs["noob"]).hexdigest()
		else:
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
