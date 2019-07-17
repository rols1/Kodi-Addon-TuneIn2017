# -*- coding: utf-8 -*-
# util_tunein2017.py
#	

import os, sys, glob, shutil, time
import urllib, urllib2, ssl
from StringIO import StringIO
import gzip, zipfile
from urlparse import parse_qsl
import random			# Zufallswerte für rating_key
import base64 			# url-Kodierung für Kontextmenüs
import json				# json -> Textstrings
import pickle			# persistente Variablen/Objekte
import re				# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
	
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

# Globals
NAME		= 'TuneIn2017'
KODI_VERSION = xbmc.getInfoLabel('System.BuildVersion')

ADDON_ID      	= 'plugin.audio.tunein2017'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path').decode('utf-8')	# Basis-Pfad Addon
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]				# plugin://plugin.video.ardundzdf/
HANDLE			= int(sys.argv[1])

DEBUG			= SETTINGS.getSetting('pref_info_debug')

FANART = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/fanart.jpg')
ICON = xbmc.translatePath('special://home/addons/' + ADDON_ID + '/icon.png')

TEMP_ADDON		= xbmc.translatePath("special://temp")
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)

M3U8STORE 		= os.path.join("%s/m3u8") % ADDON_DATA
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA


###################################################################################################
#									Hilfsfunktionen Kodiversion
#	Modulnutzung: 
#					import resources.lib.util as util
#					PLog=util.PLog;  home=util.home; ...  (manuell od.. script-generiert)
#
#	convert_util_imports.py generiert aus util.py die Zuordnungen PLog=util.PLog; ...
####################################################################################################
#----------------------------------------------------------------  
def PLog(msg, loglevel=xbmc.LOGDEBUG):
	if DEBUG == 'false':
		return
	if isinstance(msg, unicode):
		msg = msg.encode('utf-8')
	loglevel = xbmc.LOGNOTICE
	# PLog('loglevel: ' + str(loglevel))
	if loglevel >= 2:
		xbmc.log("%s --> %s" % (NAME, msg), level=loglevel)
	 
#---------------------------------------------------------------- 
#	03.04.2019 data-Verzeichnis des Addons:
#  		Check /Initialisierung / Migration
# 	27.05.2019 nur noch Check (s. Forum:
#		www.kodinerds.net/index.php/Thread/64244-RELEASE-Kodi-Addon-ARDundZDF/?pageNo=23#post528768
#	Die Funktion checkt bei jedem Aufruf des Addons data-Verzeichnis einschl. Unterverzeichnisse 
#		auf Existenz und bei Bedarf neu an. User-Info nur noch bei Fehlern (Anzeige beschnittener 
#		Verzeichnispfade im Kodi-Dialog nur verwirend).
#	 
def check_DataStores():
	PLog('check_DataStores:')
	store_Dirs = ["Dict", "m3u8"]
				
	# Check 
	#	falls ein Unterverz. fehlt, erzeugt make_newDataDir alle
	#	Datenverz. oder einzelne fehlende Verz. neu.
	ok=True	
	for Dir in store_Dirs:						# Check Unterverzeichnisse
		Dir_path = os.path.join("%s/%s") % (ADDON_DATA, Dir)
		if os.path.isdir(Dir_path) == False:	
			PLog('Datenverzeichnis fehlt: %s' % Dir_path)
			ok = False
			break
	
	if ok:
		return 'OK %s '	% ADDON_DATA			# Verz. existiert - OK
	else:
		# neues leeres Verz. mit Unterverz. anlegen / einzelnes fehlendes 
		#	Unterverz. anlegen 
		ret = make_newDataDir(store_Dirs)	
		if ret == True:						# ohne Dialog
			msg1 = 'Datenverzeichnis angelegt - Details siehe Log'
			msg2=''; msg3=''
			PLog(msg1)
			# xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)  # OK ohne User-Info
			return 	'OK - %s' % msg1
		else:
			msg1 = "Fehler beim Anlegen des Datenverzeichnisses:" 
			msg2 = ret
			msg3 = 'Bitte Kontakt zum Entwickler aufnehmen'
			PLog("%s\n%s" % (msg2, msg3))	# Ausgabe msg1 als exception in make_newDataDir
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
			return 	'Fehler: Datenverzeichnis konnte nicht angelegt werden'
				
#---------------------------
# ab Version 1.5.6
# 	erzeugt neues leeres Datenverzeichnis oder fehlende Unterverzeichnisse
def  make_newDataDir(store_Dirs):
	PLog('make_newDataDir:')
				
	if os.path.isdir(ADDON_DATA) == False:		# erzeugen, falls noch nicht vorh.
		try:  
			PLog('erzeuge %s' % ADDON_DATA)
			os.mkdir(ADDON_DATA)
		except Exception as exception:
			ok=False
			PLog(str(exception))
			return str(exception)		
				
	ok=True
	for Dir in store_Dirs:						# Unterverz. erzeugen
		Dir_path = os.path.join("%s/%s") % (ADDON_DATA, Dir)	
		if os.path.isdir(Dir_path) == False:	
			try:  
				PLog('erzeuge %s' % Dir_path)
				os.mkdir(Dir_path)
			except Exception as exception:
				ok=False
				PLog(str(exception))
				break
	if ok:
		return True
	else:
		return str(exception)
		
#---------------------------
# sichert Verz. für check_DataStores
def getDirZipped(path, zipf):
	PLog('getDirZipped:')	
	for root, dirs, files in os.walk(path):
		for file in files:
			zipf.write(os.path.join(root, file)) 
#----------------------------------------------------------------  
# Die Funktion Dict speichert + lädt Python-Objekte mittels Pickle.
#	Um uns das Handling mit keys zu ersparen, erzeugt die Funktion
#	trotz des Namens keine dicts. Aufgabe ist ein einfacher
#	persistenter Speicher. Der Name Dict lehnt sich an die
#	allerdings wesentlich komfortablere Dict-Funktion in Plex an.
#
#	Den Dict-Vorteil, dass beliebige Strings als Kennzeichnung ver-
#	wendet werden können, können wir bei Bedarf außerhalb von Dict
#	mit der vars()-Funktion ausgleichen (siehe Zuweisungen). 
#
#	Falls (außerhalb von Dict) nötig, kann mit der Zusatzfunktion 
#	name() ein Variablenname als String zurück gegeben werden.
#	
#	Um die Persistenz-Variablen von den übrigen zu unterscheiden,
#	kennzeichnen wir diese mit vorangestelltem Dict_ (ist aber
#	keine Bedingung).
#
# Zuweisungen: 
#	Dictname=value 			- z.B. Dict_sender = 'ARD-Alpha'
#	vars('Dictname')=value 	- 'Dict_name': _name ist beliebig (prg-generiert)
#	Bsp. für Speichern:
#		 Dict('store', "Dict_name", Dict_name)
#			Dateiname: 		"Dict_name"
#			Wert in:		Dict_name
#	Bsp. für Laden:
#		CurSender = Dict("load", "CurSender")
#   Bsp. für CacheTime: 5*60 (5min) - Verwendung bei "load", Prüfung mtime 
#	ev. ergänzen: OS-Verträglichkeit des Dateinamens

def Dict(mode, Dict_name='', value='', CacheTime=None):
	PLog('Dict: ' + mode)
	# PLog('Dict: ' + str(Dict_name))
	# PLog('Dict: ' + str(type(value)))
	dictfile = "%s/%s" % (DICTSTORE, Dict_name)
	# PLog("dictfile: " + dictfile)
	
	if mode == 'store':	
		with open(dictfile, 'wb') as f: pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
		f.close
		return True
	if mode == 'remove':		# einzelne Datei löschen
		try:
			 os.remove(dictfile)
			 return True
		except:	
			return False
			
	if mode == 'ClearUp':			# Files im Dictstore älter als maxdays löschen
		maxdays = int(Dict_name)
		return ClearUp(DICTSTORE, maxdays*86400) # 1 Tag=86400 sec
			
	if mode == 'load':	
		if os.path.exists(dictfile) == False:
			PLog('Dict: %s nicht gefunden' % dictfile)
			return False
		if CacheTime:
			mtime = os.path.getmtime(dictfile)	# modified-time
			now	= time.time()
			CacheLimit = now - CacheTime		# 
			# PLog("now %d, mtime %d, CacheLimit: %d" % (now, mtime, CacheLimit))
			if CacheLimit > mtime:
				PLog('Cache miss: CacheLimit > mtime')
				return False
			else:
				PLog('Cache hit: load')	
		try:			
			with open(dictfile, 'rb')  as f: data = pickle.load(f)
			f.close
			PLog('load from Cache')
			return data
		# Exception  ausführlicher: s.o.
		except Exception as e:	
			PLog('UnpicklingError' + str(e))
			return False

#-------------------------
# Zusatzfunktion für Dict - gibt Variablennamen als String zurück
# Aufruf: name(var=var) - z.Z. nicht genutzt
def name(**variables):				
	s = [x for x in variables]
	return s[0]
#----------------------------------------------------------------
# Dateien löschen älter als seconds
#		directory 	= os.path.join(path)
#		seconds		= int (1 Tag=86400, 1 Std.=3600)
# leere Ordner werden entfernt
def ClearUp(directory, seconds):	
	PLog('ClearUp: %s, sec: %s' % (directory, seconds))	
	PLog('älter als: ' + seconds_translate(seconds))
	now = time.time()
	cnt_files=0; cnt_dirs=0
	try:
		globFiles = '%s/*' % directory
		files = glob.glob(globFiles) 
		PLog("ClearUp: globFiles " + str(len(files)))
		# PLog(" globFiles: " + str(files))
		for f in files:
			# PLog(os.stat(f).st_mtime)
			if os.stat(f).st_mtime < (now - seconds):
				os.remove(f)
				cnt_files = cnt_files + 1
			if os.path.isdir(f):		# Leerverz. entfernen
				if not os.listdir(f):
					os.rmdir(f)
					cnt_dirs = cnt_dirs + 1
		PLog("ClearUp: entfernte Dateien %s, entfernte Ordner %s" % (str(cnt_files), str(cnt_dirs)))	
		return True
	except Exception as exception:	
		PLog(str(exception))
		return False

#----------------------------------------------------------------  
# Listitems verlangen encodierte Strings auch bei Umlauten. Einige Quellen liegen in unicode 
#	vor (s. json-Auswertung in get_page) und müssen rückkonvertiert  werden.
# Hinw.: Teilstrings in unicode machen str-Strings zu unicode-Strings.
def UtfToStr(line):
	if type(line) == unicode:
		line =  line.encode('utf-8')
		return line
	else:
		return line	
#----------------------------------------------------------------  
# In Kodi fehlen die summary- und tagline-Zeilen der Plexversion. Diese ersetzen wir
#	hier einfach durch infoLabels['Plot'], wobei summary und tagline durch 
#	2 Leerzeilen getrennt werden (Anzeige links unter icon).
#
#	Sofortstart + Resumefunktion, einschl. Anzeige der Medieninfo:
#		nur problemlos, wenn das gewählte Listitem als Video (Playable) gekennzeichnet ist.
# 		mediatype steuert die Videokennz. im Listing - abhängig von Settings (Sofortstart /
#		Einzelauflösungen).
#		Mehr s. PlayVideo
#
#	Kontextmenüs (Par. cmenu): base64-Kodierung benötigt für url-Parameter (nötig für router)
#		und als Prophylaxe gegen durch doppelte utf-8-Kodierung erzeugte Sonderzeichen.
#		Dekodierung erfolgt in ShowFavs.

def addDir(li, label, action, dirID, fanart, thumb, fparams, summary='', tagline='', mediatype='', cmenu=True):
	PLog('addDir:')
	PLog('addDir - label: %s, action: %s, dirID: %s' % (label, action, dirID))
	PLog('addDir - summary: %s, tagline: %s, mediatype: %s, cmenu: %s' % (summary, tagline, mediatype, cmenu))
	
	label=UtfToStr(label); thumb=UtfToStr(thumb); fanart=UtfToStr(fanart); 
	summary=UtfToStr(summary); tagline=UtfToStr(tagline); 
	fparams=UtfToStr(fparams);
	
	li.setLabel(label)			# Kodi Benutzeroberfläche: Arial-basiert für arabic-Font erf.
	# PLog('summary, tagline: %s, %s' % (summary, tagline))
	Plot = ''
	if tagline:								
		Plot = tagline
	if summary:									
		Plot = "%s\n\n%s" % (Plot, summary)
		
	if mediatype == 'video': 	# "video", "music" setzen: List- statt Dir-Symbol
		li.setInfo(type="video", infoLabels={"Title": label, "Plot": Plot, "mediatype": "video"})	
		isFolder = False		# nicht bei direktem Player-Aufruf - OK mit setResolvedUrl
		li.setProperty('IsPlayable', 'true')					
	else:
		li.setInfo(type="video", infoLabels={"Title": label, "Plot": Plot})	
		li.setProperty('IsPlayable', 'false')
		isFolder = True	
	
	li.setArt({'thumb':thumb, 'icon':thumb, 'fanart':fanart})
	xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
	PLog('PLUGIN_URL: ' + PLUGIN_URL)	# plugin://plugin.video.ardundzdf/
	PLog('HANDLE: ' + str(HANDLE))
	url = PLUGIN_URL+"?action="+action+"&dirID="+dirID+"&fanart="+fanart+"&thumb="+thumb+urllib.quote_plus(fparams)
	PLog("addDir_url: " + urllib.unquote_plus(url))
		
	
	if SETTINGS.getSetting('pref_watchlist') ==  'true':	# Merkliste verwenden 
		if cmenu:											# Kontextmenüs Merkliste hinzufügen	
			Plot = Plot.replace('\n', '||')		# || Code für LF (\n scheitert in router)
			# PLog('Plot: ' + Plot)
			fparams_add = "&fparams={'action': 'add', 'name': '%s', 'thumb': '%s', 'Plot': '%s', 'url': '%s'}" \
				%   (label, thumb,  urllib.quote_plus(Plot), base64.b64encode(urllib.quote_plus(url)))
				#%   (label, thumb,  urllib.quote_plus(Plot), urllib.quote_plus(url))
				# %   (label, thumb,  base64.b64encode(url))#möglich: 'Incorrect padding' error 
			fparams_add = urllib.quote_plus(fparams_add)

			fparams_del = "&fparams={'action': 'del', 'name': '%s'}" \
				%   (label)									# name reicht für del
				# %   (label, thumb,  base64.b64encode(url))
			fparams_del = urllib.quote_plus(fparams_del)	

			li.addContextMenuItems([('Zur Merkliste hinzufügen', 'RunAddon(%s, ?action=dirList&dirID=Watch%s)' \
				% (ADDON_ID, fparams_add)), ('Aus Merkliste entfernen', 'RunAddon(%s, ?action=dirList&dirID=Watch%s)' \
				% (ADDON_ID, fparams_del))])
		else:
			pass											# Kontextmenü entfernen klappt so nicht
			#li.addContextMenuItems([('Zur Merkliste hinzufügen', 'RunAddon(%s, ?action=dirList&dirID=dummy)' \
			#	% (ADDON_ID))], replaceItems=True)

		
	xbmcplugin.addDirectoryItem(handle=HANDLE,url=url,listitem=li,isFolder=isFolder)
	
	PLog('addDir_End')		
	return	


#---------------------------------------------------------------- 
# in tunein2017 RequestTunein statt get_page (Haupt-Prg)
# def get_page(path, header='', cTimeout=None, JsonPage=False, GetOnlyRedirect=None):
#---------------------------------------------------------------- 


#---------------------------------------------------------------- 

# Ersetzt R-Funktion von Plex (Pfad zum Verz. Resources, hier zusätzl. Unterordner möglich) 
# Falls abs_path nicht gesetzt, wird der Pluginpfad zurückgegeben, sonst der absolute Pfad
# für lokale Icons üblicherweise PluginAbsPath.
def R(fname, abs_path=False):	
	PLog('R(fname): %s' % fname); # PLog(abs_path)
	# PLog("ADDON_PATH: " + ADDON_PATH)
	if abs_path:
		try:
			# fname = '%s/resources/%s' % (PluginAbsPath, fname)
			path = os.path.join(ADDON_PATH,fname)
			return path
		except Exception as exception:
			PLog(str(exception))
	else:
		if fname.endswith('png'):	# Icons im Unterordner images
			fname = '%s/resources/images/%s' % (ADDON_PATH, fname)
			fname = os.path.abspath(fname)
			# PLog("fname: " + fname)
			return os.path.join(fname)
		else:
			fname = "%s/resources/%s" % (ADDON_NAME, fname)
			fname = os.path.abspath(fname)
			return fname 
#----------------------------------------------------------------  
# ersetzt Resource.Load von Plex 
# abs_path s.o.	R()	
def RLoad(fname, abs_path=False): # ersetzt Resource.Load von Plex 
	if abs_path == False:
		fname = '%s/resources/%s' % (ADDON_PATH, fname)
	path = os.path.join(fname) # abs. Pfad
	PLog('RLoad: %s' % str(fname))
	try:
		with open(path,'r') as f:
			page = f.read()		
	except Exception as exception:
		PLog(str(exception))
		page = ''
	return page
#----------------------------------------------------------------
# Gegenstück zu RLoad - speichert Inhalt page in Datei fname im  
#	Dateisystem. PluginAbsPath muss in fname enthalten sein,
#	falls im Pluginverz. gespeichert werden soll   
def RSave(fname, page): 
	PLog('RSave: %s' % str(fname))
	path = os.path.join(fname) # abs. Pfad
	msg = ''					# Rückgabe leer falls OK
	try:
		with open(path,'w') as f:
			f.write(page)		
	except Exception as exception:
		msg = str(exception)
		PLog(msg)
	return msg
#----------------------------------------------------------------  
# Bsp.: #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=61000,CODECS="mp4a.40.2"
def GetAttribute(text, attribute, delimiter1 = '=', delimiter2 = ','):
	PLog('GetAttribute:')
	if attribute == 'CODECS':	# Trenner = Komma, nur bei CODEC ist Inhalt 'umrahmt' 
		delimiter1 = '="'
		delimiter2 = '"'
	x = text.find(attribute)
	if x > -1:
		y = text.find(delimiter1, x + len(attribute)) + len(delimiter1)
		z = text.find(delimiter2, y)
		if z == -1:
			z = len(text)
		return text[y:z].strip()
	else:
		return ''
#----------------------------------------------------------------  
def repl_dop(liste):	# Doppler entfernen, im Python-Script OK, Problem in Plex - s. PageControl
	mylist=liste
	myset=set(mylist)
	mylist=list(myset)
	mylist.sort()
	return mylist
#----------------------------------------------------------------  
def repl_char(cut_char, line):	# problematische Zeichen in Text entfernen, wenn replace nicht funktioniert
	line_ret = line				# return line bei Fehlschlag
	pos = line_ret.find(cut_char)
	while pos >= 0:
		line_l = line_ret[0:pos]
		line_r = line_ret[pos+len(cut_char):]
		line_ret = line_l + line_r
		pos = line_ret.find(cut_char)
		#PLog(cut_char); PLog(pos); PLog(line_l); PLog(line_r); PLog(line_ret)	# bei Bedarf	
	return line_ret
#----------------------------------------------------------------
#	doppelte utf-8-Enkodierung führt an manchen Stellen zu Sonderzeichen
#  	14.04.2019 entfernt: (':', ' ')
def repl_json_chars(line):	# für json.loads (z.B.. in router) json-Zeichen in line entfernen
	line_ret = line
	for r in	(('"', ''), ('\\', ''), ('\'', '')
		, ('&', 'und'), ('(', '<'), (')', '>'),  ('∙', '|')):			
		line_ret = line_ret.replace(*r)
	
	return line_ret
#---------------------------------------------------------------- 
# strip-Funktion, die auch Zeilenumbrüche innerhalb des Strings entfernt
#	\s [ \t\n\r\f\v - s. https://docs.python.org/3/library/re.html
def mystrip(line):	
	line_ret = line	
	line_ret = re.sub(r"\s+", " ", line)	# Alternative für strip + replace
	# PLog(line_ret)		# bei Bedarf
	return line_ret
#----------------------------------------------------------------  	
# DirectoryNavigator - Nutzung des Kodi-builtin, der Code der PMS-Version kann entfallen
# S. http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/xbmcgui.html
# mytype: 	0 : ShowAndGetDirectory, 1 : ShowAndGetFile, 2
# mask: 	nicht brauchbar bei endungslosen Dateien, Bsp. curl
def DirectoryNavigator(settingKey, mytype, heading, shares='files', useThumbs=False, \
	treatAsFolder=False, path=''):
	PLog('DirectoryNavigator:')
	PLog(settingKey); PLog(mytype); PLog(heading); PLog(path);
	
	dialog = xbmcgui.Dialog()
	d_ret = dialog.browseSingle(int(mytype), heading, 'files', '', False, False, path)	
	PLog('d_ret: ' + d_ret)
	
	SETTINGS.setSetting(settingKey, d_ret)	
	return 
#----------------------------------------------------------------  
def stringextract(mFirstChar, mSecondChar, mString):  	# extrahiert Zeichenkette zwischen 1. + 2. Zeichenkette
	pos1 = mString.find(mFirstChar)						# return '' bei Fehlschlag
	ind = len(mFirstChar)
	#pos2 = mString.find(mSecondChar, pos1 + ind+1)		
	pos2 = mString.find(mSecondChar, pos1 + ind)		# ind+1 beginnt bei Leerstring um 1 Pos. zu weit
	rString = ''

	if pos1 >= 0 and pos2 >= 0:
		rString = mString[pos1+ind:pos2]	# extrahieren 
		
	#PLog(mString); PLog(mFirstChar); PLog(mSecondChar); 	# bei Bedarf
	#PLog(pos1); PLog(ind); PLog(pos2);  PLog(rString); 
	return rString
#---------------------------------------------------------------- 
def blockextract(blockmark, mString):  	# extrahiert Blöcke begrenzt durch blockmark aus mString
	#	blockmark bleibt Bestandteil der Rückgabe - im Unterschied zu split()
	#	Rückgabe in Liste. Letzter Block reicht bis Ende mString (undefinierte Länge),
	#		Variante mit definierter Länge siehe Plex-Plugin-TagesschauXL (extra Parameter blockendmark)
	#	Verwendung, wenn xpath nicht funktioniert (Bsp. Tabelle EPG-Daten www.dw.com/de/media-center/live-tv/s-100817)
	rlist = []				
	if 	blockmark == '' or 	mString == '':
		PLog('blockextract: blockmark or mString leer')
		return rlist
	
	pos = mString.find(blockmark)
	if 	mString.find(blockmark) == -1:
		PLog('blockextract: blockmark <%s> nicht in mString enthalten' % blockmark)
		# PLog(pos); PLog(blockmark);PLog(len(mString));PLog(len(blockmark));
		return rlist
	pos2 = 1
	while pos2 > 0:
		pos1 = mString.find(blockmark)						
		ind = len(blockmark)
		pos2 = mString.find(blockmark, pos1 + ind)		
	
		block = mString[pos1:pos2]	# extrahieren einschl.  1. blockmark
		rlist.append(block)
		# reststring bilden:
		mString = mString[pos2:]	# Rest von mString, Block entfernt	
	return rlist  
#----------------------------------------------------------------  
def my_rfind(left_pattern, start_pattern, line):  # sucht ab start_pattern rückwärts + erweitert 
#	start_pattern nach links bis left_pattern.
#	Rückgabe: Position von left_pattern und String ab left_pattern bis einschl. start_pattern	
#	Mit Python's rfind-Funktion nicht möglich

	# PLog(left_pattern); PLog(start_pattern); 
	if left_pattern == '' or start_pattern == '' or line.find(start_pattern) == -1:
		return -1, ''
	startpos = line.find(start_pattern)
	# PLog(startpos); PLog(line[startpos-10:startpos+len(start_pattern)]); 
	i = 1; pos = startpos
	while pos >= 0:
		newline = line[pos-i:startpos+len(start_pattern)]	# newline um 1 Zeichen nach links erweitern
		# PLog(newline)
		if newline.find(left_pattern) >= 0:
			leftpos = pos						# Position left_pattern in line
			leftstring = newline
			# PLog(leftpos);Log(newline)
			return leftpos, leftstring
		i = i+1				
	return -1, ''								# Fehler, wenn Anfang line erreicht
#----------------------------------------------------------------  	
def cleanhtml(line): # ersetzt alle HTML-Tags zwischen < und >  mit 1 Leerzeichen
	cleantext = line
	cleanre = re.compile('<.*?>')
	cleantext = re.sub(cleanre, ' ', line)
	return cleantext
#----------------------------------------------------------------  	
def decode_url(line):	# in URL kodierte Umlaute und & wandeln, Bsp. f%C3%BCr -> für, 	&amp; -> &
	urllib.unquote(line)
	line = line.replace('&amp;', '&')
	return line
#----------------------------------------------------------------  	
def unescape(line):
# HTML-Escapezeichen in Text entfernen, bei Bedarf erweitern. ARD auch &#039; statt richtig &#39;	
#					# s.a.  ../Framework/api/utilkit.py
#					# Ev. erforderliches Encoding vorher durchführen 
#	
	if line == None or line == '':
		return ''	
	for r in	(("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">")
		, ("&#39;", "'"), ("&#039;", "'"), ("&quot;", '"'), ("&#x27;", "'")
		, ("&ouml;", "ö"), ("&auml;", "ä"), ("&uuml;", "ü"), ("&szlig;", "ß")
		, ("&Ouml;", "Ö"), ("&Auml;", "Ä"), ("&Uuml;", "Ü"), ("&apos;", "'")
		, ("&nbsp;|&nbsp;", ""), ("&nbsp;", ""), 
		# Spezialfälle:
		#	https://stackoverflow.com/questions/20329896/python-2-7-character-u2013
		#	"sächsischer Genetiv", Bsp. Scott's
		#	Carriage Return (Cr)
		("–", "-"), ("&#x27;", "'"), ("&#xD;", ""), ("\xc2\xb7", "-"),
		('undoacute;', 'o'), ('&eacute;', 'e'), ('&egrave;', 'e')):
			
		line = line.replace(*r)
	return line
#----------------------------------------------------------------  
def serial_random(): # serial-ID's für tunein erzeugen (keine Formatvorgabe bekannt)
	basis = ['b8cfa75d', '4589', '4fc19', '3a64', '2c2d24dfa1c2'] # 5 Würfelblöcke
	serial = []
	for block in basis:
		new_block = ''.join(random.choice(block) for i in range(len(block)))
		serial.append(new_block)
	serial = '-'.join(serial)
	return serial
#----------------------------------------------------------------  
def transl_json(line):	# json-Umlaute übersetzen
	# Vorkommen: Loader-Beiträge ZDF/3Sat (ausgewertet als Strings)
	# Recherche Bsp.: https://www.compart.com/de/unicode/U+00BA
	# 
#	line = UtfToStr(line)
	for r in (('\\u00E4', "ä"), ('\\u00C4', "Ä"), ('\u00F6', "ö")		
		, ('\\u00C6', "Ö"), ('\\u00D6', "Ö"),('\\u00FC', "ü"), ('\\u00DC', 'Ü')
		, ('\\u00DF', 'ß'), ('\\u0026', '&'), ('\\u00AB', '"')
		, ('\\u00BB', '"')
		, ('\xc3\xa2', '*')):	# a mit Circumflex:  â<U+0088><U+0099> bzw. \xc3\xa2

		line = line.replace(*r)
	return line	
#---------------------------------------------------------------- 
# aus Kodi-Addon-ARDundZDF, Modul util
def repl_json_chars(line):	# für json.loads (z.B.. in router) json-Zeichen in line entfernen
	line_ret = line
	for r in	(('"', ''), ('\\', ''), ('\'', '')
		, ('&', 'und'), ('(', '<'), (')', '>'),  ('∙', '|')):			
		line_ret = line_ret.replace(*r)
	
	return line_ret
#---------------------------------------------------------------- 
# Format seconds	86400	(String, Int, Float)
# Rückgabe:  		1d, 0h, 0m, 0s	
def seconds_translate(seconds):
	if seconds == '' or seconds == 0  or seconds == 'null':
		return ''
	if int(seconds) < 60:
		return "%s sec" % seconds
	seconds = float(seconds)
	day = seconds / (24 * 3600)
	time = seconds % (24 * 3600)
	hour = time / 3600
	time %= 3600
	minutes = time / 60
	time %= 60
	seconds = time
	# return "%dd, %dh, %dm, %ds" % (day,hour,minutes,seconds)
	return  "%d:%02d" % (hour, minutes)		
#---------------------------------------------------------------- 	
# Holt User-Eingabe für Suche ab
#	s.a. get_query (für Search , ZDF_Search)
def get_keyboard_input():
	kb = xbmc.Keyboard('', 'Bitte Suchwort(e) eingeben')
	kb.doModal() # Onscreen keyboard
	if kb.isConfirmed() == False:
		return ""
	inp = kb.getText() # User Eingabe
	return inp		
#----------------------------------------------------------------
# Locale.LocalString( steht in Kodi nicht zur Verfügung. Um
#	die vorh. Sprachdateien (json-Format) unverändert nutzen zu
#	können, suchen wir hier den zum Addon-internen String 
#	passenden locale-String durch einfachen Textvergleich im 
#	passenden locale-Verzeichnis ( Dict('load', 'loc_file')).
# Die Plex-Lösung von czukowski entfällt damit.

def L(string):	
	PLog('L: ' + string)
	loc_file = Dict('load', 'loc_file')
	if os.path.exists(loc_file) == False:	
		return 	string
	
	lines = RLoad(loc_file, abs_path=True)
	lines = lines.splitlines()
	lstring = ''	
	for line in lines:
		term1 = line.split(':')[0].strip()
		term1 = term1.strip()
		term1 = term1.replace('"', '')			# Hochkommata entfernen
		# PLog(term1)
		if term1 == string:						# string stimmt mit Basis-String überein?
			lstring = line.split(':')[1]		# 	dann Ziel-String zurückgeben
			lstring = lstring.strip()
			lstring = lstring.replace('"', '') 	# Hochkommata + Komma entfernen
			lstring = lstring.replace(',', '')
			break
			
	PLog(string); PLog(lstring)		
	if lstring:
		return lstring
	else:
		return string						# Rückgabe Basis-String, falls kein Paar gefunden
#----------------------------------------------------------------

#################################################################
# SSL-Probleme in Kodi mit https-Code 302 (Adresse verlagert) - Lösung:
#	 Redirect-Abfrage vor Abgabe an Kodi-Player
# Kommt vor: Kodi kann lokale Audiodatei nicht laden - Kodi-Neustart ausreichend.
# 30.12.2018  Radio-Live-Sender: bei den SSL-Links kommt der Kodi-Audio-Player auch bei der 
#	weiter geleiteten Url lediglich mit  BR, Bremen, SR, Deutschlandfunk klar. Abhilfe:
#	Wir ersetzen den https-Anteil im Link durch den http-Anteil, der auch bei tunein 
#	verwendet wird. Der Link wird bei addradio.de getrennt und mit dem http-template
#	verbunden. Der Sendername wird aus dem abgetrennten Teil ermittelt und im template
#	eingefügt.
# 	Bsp. (Sender=ndr):
#		template: 		dg-%s-http-fra-dtag-cdn.cast.addradio.de'	# %s -> sender	
#		redirect-Url: 	dg-ndr-https-dus-dtag-cdn.sslcast.addradio.de/ndr/ndr1niedersachsen/..
#		replaced-Url: 	dg-ndr-http-dus-dtag-cdn.cast.addradio.de/ndr/ndr1niedersachsen/..
# url_template gesetzt von RadioAnstalten (Radio-Live-Sender)
# 18.06.2019 Kodi 17.6:  die template-Lösung funktioniert nicht mehr - dto. Redirect - 
#				Code für beides entfernt. Hilft ab er nur bei wenigen Sendern.
#				Neue Kodivers. ansch. nicht betroffen, Kodi 18.2. OK
# Param FavCall	entf. in Tunein2017
# CB enthält die Funktionsbez. für den Callback
#	
def PlayAudio(url, title, thumb, Plot, header=None, url_template=None, FavCall='', CB=''):
	PLog('PlayAudio:'); PLog(title); PLog(FavCall); 
				
	if url.startswith('http') == False:		# lokale Datei
		url = os.path.abspath(url)
				
	#if header:							
	#	Kodi Header: als Referer url injiziert - z.Z nicht benötigt	
	# 	header='Accept-Encoding=identity;q=1, *;q=0&User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36&Accept=*/*&Referer=%s&Connection=keep-alive&Range=bytes=0-' % slink	
	#	# PLog(header)
	#	url = '%s|%s' % (url, header) 
	
	PLog('PlayAudio Player_Url: ' + url)

	li = xbmcgui.ListItem(path=url)				# ListItem für Player
	li.setArt({'thumb': thumb, 'icon': thumb})
	ilabels = ({'Title': title})
	ilabels.update({'Comment': '%s' % Plot})	# Plot im MusicPlayer nicht verfügbar
	li.setInfo(type="music", infoLabels=ilabels)							
	li.setContentLookup(False)
	 	
	xbmc.Player().play(url, li, False)			# Player nicht mehr spezifizieren (0,1,2 - deprecated)

	if '.asf' not in url and '.aac' not in url:	# Rekursion möglich, s. myradiostations-Debug.txt
		if CB:									# Bsp. StationList
			Callback(CB)						# 
			
#----------------------------------------------------------------
# Callback - Rücksprung zum Aufrufer
#	Grund: CGUIMediaWindow::GetDirectory bei direkt-Calls aus Funktionen ohne Listitem.
#	Dict(CB) enthält die Parameter für die Funktion CB
#	Die Ermittlung der Funktionsadressen erfolgt im Haupt-PRG, (unterhalb router). 
#	Die dazugehörigen Parameter werden in der Funktion CB unmittelbar nach dem Aufruf
#		in Dict('ARGS_Funktionsname') gespeichert.
#	 
#	Hier werden die Parameter wieder geladen + wie in router in ein json-dict
#		konvertiert.
#	Schließlich folgt der Aufruf der Funktion mit Übergabe des Parameter-dicts.
# 
def Callback(CB):  						
	PLog('Callback:')
	
	func = Dict('load', CB)						# Funktionsadresse (Fuß Haupt-PRG)
	PLog(func)
	func_pars = Dict('load', "Args_%s" % CB)	# Funktionsparameter
	func_pars = urllib.unquote_plus(func_pars)
	PLog("func_pars: " + func_pars)		
												# unc_pars -> dict wie in router
	func_pars = func_pars.replace("'", "\"")	# json.loads-kompatible string-Rahmen
	func_pars = func_pars.replace('\\', '\\\\')	# json.loads-kompatible Windows-Pfade
	mydict = json.loads(func_pars)
	PLog("mydict: " + str(mydict)); 
	PLog('jump to: ' + CB)
	func(**mydict)								# Sprung zur Funktion
	return 
	

####################################################################################################


