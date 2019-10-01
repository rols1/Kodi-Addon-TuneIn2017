# -*- coding: utf-8 -*-
# XBM
import xbmc	
import xbmcaddon
import xbmcplugin		
import xbmcgui

# Python
import urllib			# urllib.quote()
from urlparse import parse_qsl
import urllib2			# urllib2.Request
import ssl				# HTTPS-Handshake
from StringIO import StringIO
import gzip, zipfile

import os, subprocess 	# u.a. Behandlung von Pfadnamen
import shlex			# Parameter-Expansion
import signal			# für os.kill
import time				# Verzögerung
import random			# Zufallswerte für rating_key
import sys				# Plattformerkennung
import re				# u.a. Reguläre Ausdrücke, z.B. in CalculateDuration
import json				# json -> Textstrings
from urlparse import urlparse # Check Portnummer in Url
import base64			# zusätzliche url-Kodierung für addDir/router

import resources.lib.updater 			as updater		

# Addonmodule + Funktionsziele (util_imports.py)
import resources.lib.util_tunein2017 as util
PLog=util.PLog; check_DataStores=util.check_DataStores;  make_newDataDir=util. make_newDataDir; 
getDirZipped=util.getDirZipped; Dict=util.Dict; name=util.name; ClearUp=util.ClearUp; 
UtfToStr=util.UtfToStr; addDir=util.addDir; R=util.R; RLoad=util.RLoad; seconds_translate=util.seconds_translate
RSave=util.RSave; GetAttribute=util.GetAttribute; repl_dop=util.repl_dop; repl_char=util.repl_char; 
repl_json_chars=util.repl_json_chars; mystrip=util.mystrip; DirectoryNavigator=util.DirectoryNavigator; 
stringextract=util.stringextract; blockextract=util.blockextract; my_rfind=util.my_rfind; 
cleanhtml=util.cleanhtml; decode_url=util.decode_url; unescape=util.unescape; serial_random=util.serial_random; 
transl_json=util.transl_json; repl_json_chars=util.repl_json_chars; get_keyboard_input=util.get_keyboard_input; 
L=util.L; PlayAudio=util.PlayAudio; Callback=util.Callback; 

# +++++ TuneIn2017  - Addon Kodi-Version, migriert von der Plexmediaserver-Version +++++

VERSION =  '1.4.4'	
VDATE = '01.10.2019'

# 
#	

# (c) 2019 by Roland Scholz, rols1@gmx.de
# 
# 	Licensed under MIT License (MIT)
# 	(previously licensed under GPL 3.0)
# 	A copy of the License you find here:
#		https://github.com/rols1/TuneIn2017/blob/master/LICENSE.md
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 08.08.2019	1.4.1	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

# Wikipedia:	https://de.wikipedia.org/wiki/TuneIn
#				https://de.wikipedia.org/wiki/Internetradio
#				https://de.wikipedia.org/wiki/Streaming-Format
#				https://de.wikipedia.org/wiki/Audioformat
#
# Wicki Ubuntu: https://wiki.ubuntuusers.de/Internetradio/Stationen/


ICON_OK 				= "icon-ok.png"
ICON_WARNING 			= "icon-warning.png"
ICON_NEXT 				= "icon-next.png"
ICON_CANCEL 			= "icon-error.png"
ICON_MEHR 				= "icon-mehr.png"
ICON_SEARCH 			= 'suche.png'

ICON_RECORD				= 'icon-record.png'						
ICON_STOP				= 'icon-stop.png'
MENU_RECORDS			= 'menu-records.png'
MENU_CUSTOM				= 'menu-custom.png'
MENU_CUSTOM_ADD			= 'menu-custom-add.png'
MENU_CUSTOM_REMOVE		= 'menu-custom-remove.png'
ICON_FAV_ADD			= 'fav_add.png'
ICON_MYRADIO			= 'myradio.png'
ICON_FAV_REMOVE			= 'fav_remove.png'
ICON_FAV_MOVE			= 'fav_move.png'
ICON_FOLDER_ADD			= 'folder_add.png'
ICON_FOLDER_REMOVE		= 'folder_remove.png'
ICON_MYLOCATION			= 'mylocation.png'
ICON_MYLOCATION_REMOVE	= 'mylocation-remove.png'
						

ICON_MAIN_UPDATER 		= 'plugin-update.png'		
ICON_UPDATER_NEW 		= 'plugin-update-new.png'

ART    		= 'art-default.png'
ICON   		= 'icon-default.png'
NAME		= 'TuneIn2017'
MENU_ICON 	=  	{'menu-lokale.png', 'menu-musik.png', 'menu-sport.png', 'menu-news.png',
					 'menu-talk.png', 'menu-audiobook.png', 'menu-pod.png', 
				}

# ab 18.04.2018, Version 1.1.9: Inhalte von Webseite statt opml-Browse-Call,
#	zusätzliche API-Calls: api.tunein.com/categories, api.tunein.com/profiles.
#	opml-Calls weiter verwendet für Fav's, Folders, audience_url, Account-Queries.
#	formats=mp3,aac,ogg,flash,html - festgelegt in Main
# alte ROOT_URL 	= 'https://opml.radiotime.com/Browse.ashx?formats=%s'
BASE_URL	= 'https://tunein.com'
ROOT_URL 	= 'https://tunein.com/radio/home/'						
USER_URL 	= 'https://opml.radiotime.com/Browse.ashx?c=presets&partnerId=RadioTime&username=%s'
RECENTS_URL	= 'https://api.tunein.com/categories/recents?formats=%s&serial=%s&partnerId=RadioTime&version=3.31'

REPO_NAME		 	= 'Kodi-Addon-TuneIn2017'
GITHUB_REPOSITORY 	= 'rols1/' + REPO_NAME
REPO_URL 			= 'https://github.com/{0}/releases/latest'.format(GITHUB_REPOSITORY)

# Globale Variablen für Tunein:
# partnerId		= 'RadioTime'	ab 19.07.2019 auf akt. Wert erweitert 
partnerId		= 'RadioTime&version=3.34&itemUrlScheme=secure&reqAttempt=1'

# Start-Variablen aus Plex-Version
UrlopenTimeout = 3			# Timeout sec, 18.10.2017 von 6 auf 3
SearchWeb = True			# z.Z. Websuche statt opml-Call

PLog('Addon: lade Code')
PluginAbsPath 	= os.path.dirname(os.path.abspath(__file__))			# abs. Pfad für Dateioperationen
RESOURCES_PATH	=  os.path.join("%s", 'resources') % PluginAbsPath
ADDON_ID      	= 'plugin.audio.tunein2017'
SETTINGS 		= xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME    	= SETTINGS.getAddonInfo('name')
SETTINGS_LOC  	= SETTINGS.getAddonInfo('profile')
ADDON_PATH    	= SETTINGS.getAddonInfo('path').decode('utf-8')
ADDON_VERSION 	= SETTINGS.getAddonInfo('version')
PLUGIN_URL 		= sys.argv[0]
HANDLE			= int(sys.argv[1])

PLog("ICON: " + R(ICON))
TEMP_ADDON		= xbmc.translatePath("special://temp")
USERDATA		= xbmc.translatePath("special://userdata")
ADDON_DATA		= os.path.join("%s", "%s", "%s") % (USERDATA, "addon_data", ADDON_ID)
PLog("ADDON_DATA: " + ADDON_DATA)

M3U8STORE 		= os.path.join("%s/m3u8") % ADDON_DATA
DICTSTORE 		= os.path.join("%s/Dict") % ADDON_DATA
PLog(M3U8STORE); PLog(DICTSTORE); 

check 			= check_DataStores()	# Check /Initialisierung / Migration 
PLog('check: ' + str(check))
										
from platform import system, architecture, machine, release, version	# Debug
OS_SYSTEM = system()
OS_ARCH_BIT = architecture()[0]
OS_ARCH_LINK = architecture()[1]
OS_MACHINE = machine()
OS_RELEASE = release()
OS_VERSION = version()
OS_DETECT = OS_SYSTEM + '-' + OS_ARCH_BIT + '-' + OS_ARCH_LINK
OS_DETECT += ' | host: [%s][%s][%s]' %(OS_MACHINE, OS_RELEASE, OS_VERSION)
KODI_VERSION = xbmc.getInfoLabel('System.BuildVersion')

PLog('Addon: ClearUp')
ARDStartCacheTime = 300						# 5 Min.	
 
# Dict: Simpler Ersatz für Dict-Modul aus Plex-Framework
days = int(SETTINGS.getSetting('DICT_store_days'))
Dict('ClearUp', days)				# Dict bereinigen 
	
																		
####################################################################################################		
# Auswahl Sprachdatei / Browser-locale-setting	
# Locale-Probleme unter Plex s. Plex-Version
# 	hier Ersatz der Plex-Funktion Locale.LocalString durch einfachen Textvergleich - 
#	s. util.L
# Kodi aktualisiert nicht autom., daher Aktualsierung jeweils in home.

def ValidatePrefs():	
	PLog('ValidatePrefs:')
			
	try:
		lang =  SETTINGS.getSetting('language').split('/') # Format Bsp.: "Danish/da/da-DA/Author Tommy Mikkelsen"
		loc  = str(lang[1])				# da
		if len(lang) >= 2:
			loc_browser = str(lang[2])	# da-DA
		else:
			loc_browser = loc			# Kennungen identisch
	except Exception as exception:
		PLog(repr(exception))
		loc 		= 'en'				# Fallback (Problem Setting)
		loc_browser = 'en-US'
				
	loc_file =  os.path.join("%s", "%s", "%s") % (RESOURCES_PATH, "Strings", '%s.json' % loc)
	PLog(loc_file)	
	
	if os.path.exists(loc_file) == False:	# Fallback Sprachdatei: englisch
		loc_file =  os.path.join("%s", "%s", "%s") % (RESOURCES_PATH, "Strings", 'en.json')
		
	Dict('store', 'loc', loc) 	
	Dict('store', 'loc_file', loc_file) 		
	Dict('store', 'loc_browser', loc_browser)
	
	PLog('loc: %s' % loc)
	PLog('loc_file: %s' % loc_file)
	PLog('loc_browser: %s' % loc_browser)

####################################################################################################
def Main():
	PLog('Main:')
	
#-----------------------------										# 1. Init
	# nützliche Debugging-Variablen:
	PLog('Addon-Version: ' + VERSION); PLog('Addon-Datum: ' + VDATE)	
	PLog(OS_DETECT)	
	PLog('Addon-Python-Version: %s'  % sys.version)
	PLog('Kodi-Version: %s'  % KODI_VERSION)
	
	ValidatePrefs()
	if Dict('load', 'PID'):											# PID-Liste initialisieren, 
		pass														# 	falls leer
	else:
		PID = []		
		Dict('store', 'PID', PID)

	username = SETTINGS.getSetting('username')						# Privat - nicht loggen
	passwort = SETTINGS.getSetting('passwort')						# dto.
	PLog("%s | %s" % (len(username), len(passwort)))				# nur Länge - Debug
	serial = Dict('load','serial')
	if not serial:
		serial = serial_random()									# eindeutige serial-ID für Tunein für Favoriten u.ä.
		Dict('store','serial', serial)
		PLog('serial-ID erzeugt')									# 	wird nach Löschen Plugin-Cache neu erzeugt				
	PLog('serial-ID: %s' % str(Dict('load','serial')))
	SETTINGS.setSetting('serialid', serial)												
	                  		
	if 	not SETTINGS.getSetting('MyRadioStations'):						# mit Muster vorbelegen
		MyRadioStations =  os.path.join("%s", "myradiostations-Mix.txt") % RESOURCES_PATH
		SETTINGS.setSetting('MyRadioStations', MyRadioStations)
		
#-----------------------------										# 2. Menü
	# title = L('Durchstoebern')									# Plex: oc-title2
			
	li = xbmcgui.ListItem()
	li = home(li)													# Home-Button / Refresh	
	
	title = L('Suche')
	tagline = L('Suche Station / Titel')							# Suche
	fparams="&fparams={'query': ''}"
	addDir(li=li, label=title, action="dirList", dirID="Search", 
		fanart=R(ICON_SEARCH), thumb=R(ICON_SEARCH), tagline=tagline, fparams=fparams)
		
	if len(username) > 0:
		my_title = u'%s' % L('Meine Favoriten')
		my_url = USER_URL % username								# nicht serial-ID! Verknüpfung mit Account kann fehlen
		Dict('store','my_url', my_url)								# Verwend. in Favourit
		if SETTINGS.getSetting('StartWithFavourits') == "true":		# Favoriten-Menü direkt + Updater-Modul einbinden
			li, cnt = GetContent( url=my_url, title=my_title, offset=0, li=li)
			li 		= Menu_update(li)
			xbmcplugin.endOfDirectory(HANDLE)						# Ende
		else:														# Favoriten-Button
			fparams="&fparams={'url': '%s', 'title': '%s', 'offset': '0'}"  %\
				(urllib2.quote(my_url), urllib2.quote(my_title))
			addDir(li=li, label=my_title, action="dirList", dirID="GetContent", 
				fanart=R('icon-tunein2017.png'), thumb=R('icon-tunein2017.png'), fparams=fparams)
		
	MyRadioStations = SETTINGS.getSetting('MyRadioStations')		# eigene Liste mit Radiostationen, 
	PLog('MyRadioStations: ' + str(MyRadioStations))				# (Muster in Resources)
	if  SETTINGS.getSetting('UseMyRadioStations')	== 'true':
		MyRadioStations = MyRadioStations.strip()	
		if os.path.exists(MyRadioStations):
				title = L("Meine Radiostationen")
				summ = os.path.basename(MyRadioStations)
				fparams="&fparams={'path': '%s'}" % urllib2.quote(MyRadioStations)
				addDir(li=li, label=title, action="dirList", dirID="ListMRS", 
					fanart=R(ICON_MYRADIO), thumb=R(ICON_MYRADIO), summary=summ, fparams=fparams)
				
				# nur MyRadioStations + Updater-Modul einbinden
				if SETTINGS.getSetting('StartWithMyRadioStations') == "true":	# Nachrang hinter StartWithFavourits 								
					li = Menu_update(li)
					xbmcplugin.endOfDirectory(HANDLE)				# Ende						
		else:				
			msg1 = L("Meine Radiostationen") + ': ' + L("Datei nicht gefunden")	
			msg2 = MyRadioStations
			msg3 = L('Bitte den Eintrag in Einstellungen ueberpruefen!')
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
				
	formats = 'mp3,aac,ogg,flash,html,hls'
	PLog(SETTINGS.getSetting('PlusAAC'))								
	if  SETTINGS.getSetting('PlusAAC') == "false":					# Performance, aac nicht bei allen Sendern 
		formats = formats.replace(',aac', '')
	Dict('store', 'formats', formats) 								# Verwendung: Trend, opml- und api-Calls

	page, msg = RequestTunein(FunctionName='Main', url=ROOT_URL)	# Hauptmenü von Webseite
	PLog(len(page))

	page = stringextract('"homeMenuItem"', 'leftSide__authContainer', page)
	items = blockextract('common__link', page)
	if len(items) > 0:												# kein Abbruch, weiter mit MyRadioStations + Fav's
		del items[0]			# Home löschen
	else:
		msg1 = L('Fehler')
		msg2 = ROOT_URL
		msg3 = L('Ursache unbekannt')								# ohne Tunein-Menüs weiter
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li
			
	PLog(len(items))
	for item in items:												# Tunein-Menüs + Icons zeigen
		# PLog('item: ' + item)
		url = 'https://tunein.com' + stringextract('href="', '"', item)	#  Bsp. href="/radio/local/"
		key = url[:-1].split('/')[-1]
		thumb = getMenuIcon(key)
		PLog(url);	PLog(key);	PLog(thumb);	
		try:	
			title = re.search('">(.*)</a>', item).group(1)			# Bsp. data-reactid="64">Local Radio</a>
			PLog("title: " + title)
		except:
			title = key.title()
		title = title.replace('\u002F', '/')
		title = unescape(title)
		
		#if title == 'Premium':										# zu Testzwecken wieder eingeblendet
		#	continue
		
		categories = 'Category'
		if key == 'recents':										# Recents: Url-Anpassung erforderlich
			categories = None
			url = RECENTS_URL  										# % (formats, serial) in GetContent
		fparams="&fparams={'url': '%s', 'title': '%s', 'offset': '0'}"  %\
			(urllib2.quote(url), urllib2.quote(title))
		addDir(li=li, label=title, action="dirList", dirID="GetContent", 
			fanart=thumb, thumb=thumb, fparams=fparams)
		
#-----------------------------	
	PLog(SETTINGS.getSetting('UseRecording'))						# Check laufende Aufnahmen 
	pid = Dict('load', 'PID')
	PLog(pid)
	if SETTINGS.getSetting('UseRecording') == "true":	# Recording-Option: Aufnahme-Menu bei aktiven Aufnahmen einbinden
		if len(pid) > 0 and pid != False:						
			title = L("Laufende Aufnahmen")
			fparams="&fparams={'title': '%s'}"  % urllib2.quote(title)
			addDir(li=li, label=title, action="dirList", dirID="RecordsList", 
				fanart=R(MENU_RECORDS), thumb=R(MENU_RECORDS), fparams=fparams)
						       
#-----------------------------	
#	li = Menu_update(li)											# Updater-Modul einbinden

	repo_url = 'https://github.com/{0}/releases/'.format(GITHUB_REPOSITORY)
	call_update = False
	if SETTINGS.getSetting('InfoUpdate') == 'true': 	# Updatehinweis beim Start des Addons 
		ret = updater.update_available(VERSION)
		int_lv = ret[0]			# Version Github
		int_lc = ret[1]			# Version aktuell
		latest_version = ret[2]	# Version Github, Format 1.4.1
		
		if int_lv > int_lc:								# Update-Button "installieren" zeigen
			call_update = True
			title = L('neues Update vorhanden') +  ' - ' + L('jetzt installieren')
			summary = L('Plugin Version:') + " " + VERSION + ', Github Version: ' + latest_version
			# Bsp.: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/download/0.5.4/Kodi-Addon-ARDundZDF.zip
			url = 'https://github.com/{0}/releases/download/{1}/{2}.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)
			fparams="&fparams={'url': '%s', 'ver': '%s'}" % (urllib.quote_plus(url), latest_version) 
			addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", fanart=R(ICON_UPDATER_NEW), 
				thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary)
			
	if call_update == False:							# Update-Button "Suche" zeigen	
		title = L('Plugin Update') + " | " + L('Plugin Version:') + VERSION + ' - ' + VDATE 	 
		summary=L('Suche nach neuen Updates starten')
		tagline=L('Bezugsquelle') + ': ' + REPO_URL			
		fparams="&fparams={'title': 'Addon-Update'}"
		addDir(li=li, label=title, action="dirList", dirID="SearchUpdate", fanart=R(ICON_MAIN_UPDATER), 
			thumb=R(ICON_MAIN_UPDATER), fparams=fparams, summary=summary, tagline=tagline)
					
#-----------------------------	
	# Lang_Test=True					# Menü-Test Plugin-Sprachdatei
	Lang_Test=False		
	if Lang_Test:
		fparams="&fparams={}"  
		addDir(li=li, label='LangTest', action="dirList", dirID="LangTest", 
			fanart=R('lang_gnome.png'), thumb=R('lang_gnome.png'), summary='LangTest', fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
						
####################################################################################################
# LangTest testet aktuelle Plugin-Sprachdatei, z.B. en.json (Lang_Test=True).
#	Ausgabe von Buttons: Titel = Deutsch, summary = gewählte Sprache
def LangTest():										
	PLog('LangTest:')	
	title = 'LangTest: %s' % Dict('load', 'loc')
	li = xbmcgui.ListItem(NAME)
	
	loc = Dict('load', 'loc') 
	verz = os.path.join("%s", 'Strings', '%s.json') % (RESOURCES_PATH, loc)	
	loc_strings = RLoad(verz, abs_path=True)		
	
	loc_strings = loc_strings.split('\n')
	for string in loc_strings:
		string = string.split(':')[0]				# 1. Paar-Teil
		string = string.replace('"', '')
		string = string.replace('}', '')
		string = string.replace('{', '')
		string = string.strip()
		PLog(string)
		if string:
			title = string
			summ = L(title)	
			summ = "%s\n\n%s" % (summ, SETTINGS.getSetting('language'))										
			fparams="&fparams={}"
			addDir(li=li, label=title, action="dirList", dirID="dummy", 
				fanart=R("lang_gnome.png"), thumb=R("lang_gnome.png"), summary=summ, fparams=fparams)
	
	xbmcplugin.endOfDirectory(HANDLE)
#----------------------------------------------------------------
def dummy():
	li = xbmcgui.ListItem()
	li = home(li)						# Home-Button
	msg1 = L('Hinweis')
	msg2 = 'dummy-Funktion OK'
	xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
	
	xbmcplugin.endOfDirectory(HANDLE)

#----------------------------------------------------------------
def home(li):							# Home-Button
	PLog('home:')	
	title = 'Home / Refresh' 	
	fparams="&fparams={}"
	addDir(li=li, label=title, action="dirList", dirID="Main", 
		fanart=R('home.png'), thumb=R('home.png'), summary=title, tagline=NAME, fparams=fparams)
	
	return li
#-----------------------------	
def getMenuIcon(key):	# gibt zum key passendes Icon aus MENU_ICON zurück	
	icon = ''			#
	for icon in MENU_ICON:
		if key == 'local':
			icon = R('menu-lokale.png')
		if key == 'recents':
			icon = R('menu-kuerzlich.png')
		if key == 'trending':
			icon = R('menu-trend.png')
		elif key == 'music':
			icon = R('menu-musik.png')
		elif key == 'sports':
			icon = R('menu-sport.png')
		elif key == 'News-c57922':
			icon = R('menu-news.png')
		elif key == 'talk':
			icon = R('menu-talk.png')
		elif key == 'podcasts':
			icon = R('menu-pod.png')
		elif key == 'regions':
			icon = R('menu-orte.png')
		elif key == 'languages':
			icon = R('menu-sprachen.png')
		elif key == 'premium':
			icon = R('menu-pro.png')
	return icon	
#-----------------------------
def Search(query=''):
	PLog('Search: ' + str(query))
	oc_title2 = L('Suche nach')
	
	if  query == '':
		query = get_keyboard_input()	# Modul util
		if  query == None or query.strip() == '':
			return ""	
	
	li = xbmcgui.ListItem()
	li = home(li)						# Home-Button
	
	query = query.strip()
	oc_title2 = L('Suche nach') + ' >%s<' % query
	PLog(SearchWeb)
	if SearchWeb == True:
		query = urllib2.quote(query)										# Web-Variante
		url = 'https://tunein.com/search/?query=%s' % query		
		PLog('url: ' + url)
		li, cnt = GetContent(url=url, title=oc_title2, offset=0, li=li)
	else:		
		query = query.replace(' ', '+')										# opml-Variante
		url = 'http://opml.radiotime.com/Search.ashx?query=%s&formats=%s' % (query,Dict('load', 'formats'))	
		query = urllib2.quote(query, "utf-8")
		PLog('url: ' + url)
		li, cnt = GetContentOPML(url=url, title=oc_title2, offset=0, li=li)			
	
	if cnt == 0:
		title = L('Keine Suchergebnisse zu')
		msg1 = L(title) 
		msg2 = urllib2.unquote(query)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li		
		
	xbmcplugin.endOfDirectory(HANDLE)	
#-----------------------------

# SetLocation (Aufruf GetContent): Region für Lokales Radiomanuell setzen/entfernen
def SetLocation(url, title, region, myLocationRemove):	
	PLog('SetLocation: %s' % region)
	PLog('myLocationRemove: ' + myLocationRemove)

	if myLocationRemove == 'True':
		Dict('store', 'myLocation', None)
		msg1 = L('Lokales Radio entfernt') + ' | '	 + L('neu setzen im Menue Orte')
	else:
		Dict('store', 'myLocation', url) 
		msg1 = L('Lokales Radio gesetzt auf') + ': %s' % region
	xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
	return

#-----------------------------
# GetContentOPML wie in letzter Plex-Version nicht verwendet
#	GetContentOPML wertete opml-Calls aus (Ergenisse im xml-
#	Format).
# def GetContentOPML(title, url, offset=0, li=''):
#-----------------------------

# GetContent aufgerufen via Browser-Url, nicht via opml-Request (s. GetContentOPML)
# 	Die Auswertung erfolgt mittels Stringfunktionen, da die Ausgabe weder im xml- noch im json-Format
#		erzwungen werden kann.
#	Bei Recents wird statt des opm-Calls ein api-Call verwendet. Der Output unterscheidet sich in den
#		Anfangsbuchstaben der Parameter - s. uppercase / lowercase.
#	Unterscheidung Link / Station mittels mytype ("type")
#
def GetContent(url, title, offset=0, li=''):
	PLog('GetContent:'); PLog(url); PLog(offset); PLog(title); PLog(li);
	offset = int(offset)
	title = UtfToStr(title)
	title_org = title
	oc_title2 = title
	url_org = url
	
	if li == '':								# eigene Liste 
		endOfDirectory = True 
		li = xbmcgui.ListItem()
		li = home(li)							# Home-Button
	else:										# Aufrufer-Liste
		endOfDirectory = False	
	PLog(endOfDirectory);	

	if url == None or url == '':
		msg1 = 'GetContent: Url ' + L("nicht gefunden")	
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li
	if offset:
		oc_title2 = title_org + ' | %s...' % offset			

	serial = Dict('load', 'serial')
	username = SETTINGS.getSetting('username')
	local_url=''; callNoOPML=False

	max_count = int(SETTINGS.getSetting('maxPageContent'))	# max. Anzahl Einträge ab offset

	# ------------------------------------------------------------------	
	# Favoriten-Ordner,  Custom Url											Favoriten-Ordner
	# ------------------------------------------------------------------
	if "c=presets" in url:
		PLog("c=presets: " + url)
		li = FolderMenuList(url=url, title=title, li=li)
		
		if SETTINGS.getSetting('UseFavourites') == "true":
			PLog('Folder + Custom Menues')
			title = L('Neuer Ordner fuer Favoriten') 
			foldername = str(SETTINGS.getSetting('folder'))
			if foldername != 'None':
				summ = L('Name des neuen Ordners') + ': ' + foldername
				fparams="&fparams={'ID': 'addFolder', 'title': '%s', 'foldername': '%s', 'folderId': 'dummy'}"  %\
					(urllib2.quote(title), urllib2.quote(foldername))
				addDir(li=li, label=title, action="dirList", dirID="Folder", 
					fanart=R(ICON_FOLDER_ADD), thumb=R(ICON_FOLDER_ADD), summary=summ, fparams=fparams)						
		
			title = L('Ordner entfernen') 
			summ = L('Ordner zum Entfernen auswaehlen')
			fparams="&fparams={'ID': 'removeFolder', 'title': '%s', 'preset_id': 'dummy'}"  %\
				(urllib2.quote(title))
			addDir(li=li, label=title, action="dirList", dirID="FolderMenu", 
				fanart=R(ICON_FOLDER_REMOVE), thumb=R(ICON_FOLDER_REMOVE), summary=summ, fparams=fparams)						
			

	# ------------------------------------------------------------------	 Custom Url	
			# Button für Custom Url 
			# Einstellungen:  Felder Custom Url/Name müssen ausgefüllt sein, Custom Url mit http starten
			#	Custom Url wird hier nur hinzugefügt - Verschieben + Löschen erfolgt als Favorit in
			#		StationList 
			# Achtung: Entfernen der Custom Url nicht einzeln möglich, nur zusammen mit einem Ordner dto.
			#			Web).
				
			customUrl 	= SETTINGS.getSetting('customUrl').strip()
			customName = SETTINGS.getSetting('customName').strip()
			if customUrl or customName: 								# ungeprüft!
				# Custom Url/Name - ausgefüllt 
				sidExist,foldername,guide_id,foldercnt = SearchInFolders(preset_id=customUrl, ID=customUrl) 
				PLog(sidExist)
				PLog('customUrl: ' + customUrl); PLog(customName)
				if customUrl == '' or customName == '':
					error_txt = L("Custom Url") + ': ' + L("Eintrag fehlt fuer Url oder Name")
					PLog(msg1)
					xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
					return li
				
				if customUrl.startswith('http') == False: 
					error_txt = L('Custom Url muss mit http beginnen')
					PLog(msg1)
					xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
					return li
						
				if sidExist == False:									# schon vorhanden?
					title = L('Custom Url') + ' ' + L('hinzufuegen')	# hinzufuegen immer in Ordner General	
					summ = customName + ' | ' + customUrl
					fparams="&fparams={'ID': 'addcustom', 'preset_id': '%s', 'folderId': '%s'}"  %\
						(urllib2.quote(customUrl), urllib2.quote(customName))
					addDir(li=li, label=title, action="dirList", dirID="Favourit", 
						fanart=R(MENU_CUSTOM_ADD), thumb=R(MENU_CUSTOM_ADD), summary=summ, fparams=fparams)
						
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)
		return		# ohne return weiter trotz endOfDirectory!

	# ------------------------------------------------------------------	
	# Anpassung RECENTS_URL an Formate (Einstellungen) und serial-ID		RECENTS_URL
	# ------------------------------------------------------------------
	if 'categories/recents' in url:
		formats = Dict('load', 'formats'); serial = Dict('load', 'serial')
		# PLog(formats); PLog(serial);
		url = url % (formats, serial)
	# ------------------------------------------------------------------	
	# Anpassung Url Local Radio: Title2 oc, Url setzen, Remove-Button		Local Radio
	# ------------------------------------------------------------------
	skip_SetLocation = False; myLocationRemove = False
	if url.endswith('/radio/local/'):			# Local Radio
		if SETTINGS.getSetting('UseMyLocation') == "true":	
			if Dict('load', 'myLocation'):				# Region gesetzt - Url anpassen
				url = Dict('load', 'myLocation')		
				skip_SetLocation = True
				myLocationRemove = True
				region = stringextract('/radio/', '-r', url)
				oc_title2 = oc_title2 + ' (%s)' % region
				oc_title2=UtfToStr(oc_title2)
				PLog("region: %s, oc_title2: %s" % (region, oc_title2) )
	
	if myLocationRemove:							# Local Radio: Remove-Button
		if SETTINGS.getSetting('UseMyLocation') == "true":	
			if Dict('load', 'myLocation'):			# Region gesetzt
				summ = L('neu setzen im Menue Orte')
				thumb=R(ICON_MYLOCATION_REMOVE)
				info_title = L('entferne Lokales Radio') + ': >%s<' % region
							
				fparams="&fparams={'url': '%s', 'title': '%s', 'region': '%s', 'myLocationRemove': 'True'}"  %\
					(urllib2.quote(url), urllib2.quote(info_title), urllib2.quote(region))
				addDir(li=li, label=info_title, action="dirList", dirID="SetLocation", 
					fanart=thumb, thumb=thumb, summary=summ, tagline=oc_title2, fparams=fparams)
							
	# ------------------------------------------------------------------
	# Anpassungen für UseMyLocation: Set-Button								UseMyLocation
	# ------------------------------------------------------------------	
	if SETTINGS.getSetting('UseMyLocation') == "true" and skip_SetLocation == False:					
		url_split = url.split('-')[-1]				# Bsp. ../radio/Africa-r101215/
		try:
			url_id = re.search('(\d+)', url_split).group(1)
		except:
			url_id = None
		PLog("UseMyLocation: " + url_split); PLog(url_id)	
		if  url_id and url_split.startswith('r'):	# show myLocation-button to set region manually
			# summ = L('neu setzen im Menue Orte')
			summ = ''
			thumb=R(ICON_MYLOCATION) 
			region = stringextract('/radio/', '-r', url)
			info_title = L('setze Lokales Radio auf') + ': >%s<' % region
			fparams="&fparams={'url': '%s', 'title': '%s', 'region': '%s', 'myLocationRemove': 'False'}"  %\
				(urllib2.quote(url), urllib2.quote(info_title), region)
			addDir(li=li, label=info_title, action="dirList", dirID="SetLocation", 
				fanart=thumb, thumb=thumb, summary=summ, tagline=oc_title2, fparams=fparams)
	
	# ------------------------------------------------------------------	
	# 																		Get Content
	# ------------------------------------------------------------------	
	PLog('url: ' + url)	
	page, msg = RequestTunein(FunctionName='GetContent', url=url)
	if page == '':	
		msg1 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li

	# Hinw.: Seite nicht ab initialStateEl begrenzen - fehlt bei api-Ausgaben (Bsp. Recents) 
	#if '"users":' in page:
	#	page = page [:page.find('"users":')]
	PLog('pagelen: ' + str(len(page)))	
	PLog(page[:80])
	# RSave('/tmp/x.txt', page)		# Debug: Save Content	
	# PLog(page)
	link_list = blockextract('guide-item__guideItemLink', page) # Link-List außerhalb json-Bereich
	
	if 'doctypehtml' not in page:								# api-call: Uppercase für Parameter im json-Inhalt
		page = (page.replace('"Title"','"title"').replace('"Image"','"image"').replace('"Category"','"category"')
			.replace('"FollowText"','"followText"').replace('"ShareText"','"shareText"').replace('"Id"','"id"')
			.replace('Type','type').replace('ContainerType','containerType').replace('Token','token')
			.replace('Subtitle','subtitle').replace('Index','index').replace('GuideId','guideId').replace('"Url"','"url"')
			.replace('Duration','duration'))			

	indices = blockextract('"index":', page)
	page_cnt = len(indices)
	PLog('indices: %d, max_count: %d, offset: %d' % (page_cnt, max_count, offset))
	if 	max_count:									# '' = 'Mehr..'-Option ausgeschaltet?
		delnr = min(page_cnt, offset)
		del indices[:delnr]
		PLog(delnr)				
	PLog(len(indices))
		
	subtitle=''; 	
	li_cnt=0										# Anzahl items in loop - (getrennt für Links + Stations)
	for index in indices:		
		# PLog('index: ' + index)		
		# einleitenden Container überspringen, dto. hasButtonStrip":true / "hasIconInSubtitle":false /
		#	"expandableDescription" / "initialLinesCount" / "hasExpander":true
		#	Bsp. Bill Burr's Monday Morning Podcast
		if "children" in index:									# ohne eigenen Inhalt, children folgen
			PLog('skip: "children" in index')
			continue
		if	'"hasProgressBar":true' in index:					
			PLog('skip: "hasProgressBar":true in index')
			continue
			
		index = index.replace('\\"', '*')							# Bsp. Die \"beste\" Erfindung..
		title		= stringextract('"title":', '",', index)		# Sonderbhdl. wg. "\"Sticky Fingers\" ...
		title		= title[1:].replace('\\"', '"')	
		title		= title.replace('\u002F', '/')
		subtitle	= stringextract('"subtitle":"', '"', index)		# Datum lokal
		subtitle	= (subtitle.replace('\u002F', '/').replace('\u003E', '').replace('\u003C', ''))
		publishTime	= stringextract('"publishTime":"', '"', index)	# Format 2017-10-26T16:50:58
		seoName		= stringextract('"seoName":"', '"', index)		# -> url-Abgleich
		if '"description"' in index:
			descr		= stringextract('"description":"', '"', index)	
		else:
			descr		= stringextract('"text":"', '"', index)		# description
		descr	= (descr.replace('\u002F', '/').replace('\u003E', '').replace('\u003C', '')
			.replace('\\r\\n', ' '))
		duration	= stringextract('"duration":"', '"', index)

		#if 'Religious Music' in index:									# Debug: Datensatz
		#	PLog(index)
		
		myindex	= stringextract('"index":"', '"', index)	
		mytype	= stringextract('"type":"', '"', index)	
		image	= stringextract('"image":"', '"', index)		# Javascript Unicode escape \u002F
		image	= image.replace('\u002F', '/')					# Standard-Icon für Kategorie
		if image == '':
			image=R(ICON)
		FollowText	= stringextract('"followText":"', '"', index)
		ShareText	= stringextract('"shareText":"', '"', index)
		preset_id 	= stringextract('"id":"', '"', index)		# dto. targetItemId, scope, guideId -> url
		guideId 	= stringextract('"guideId":"', '"', index)	# Bsp. t121001218 -> opml-url zum mp3-Quelle
		path 		= stringextract('"path":"', '"', index)		# -> url_title - url-Abgleich
		linkfilter 	= stringextract('"filter":"', '"', index)	# dto.
		linkfilter	= 'filter%3D' + linkfilter
		
		play_part	= stringextract('"play"', '}', index)		# Check auf abspielbaren Inhalt in Programm
		# PLog(play_part)
		sec_gId		=  stringextract('"guideId":"', '"', play_part)# macht ev. Programm/Category zur Station		
		if sec_gId.startswith('t') or  sec_gId.startswith('s'):
			 guideId = sec_gId
			 
			
		PLog('Vars:') 	
		PLog("%s | %s | %s | %s | %s | %s | %s"	% (myindex,mytype,title,subtitle,publishTime,seoName,FollowText))
		PLog("%s | %s | %s | %s | %s | %s | %s"	% (ShareText,descr,linkfilter,preset_id,guideId,path,duration))
			
		if title in ShareText or subtitle in ShareText:		# Ergänzung: Höre .. auf TuneIn
			ShareText = ''			
		if seoName in title:				# seoName = Titel
			seoName = ''
											
		mytype = mytype.title()
		title=UtfToStr(title); title=repl_json_chars(title) 
	# ------------------------------------------------------------------	
	# 																	Callback Link
	# ------------------------------------------------------------------	
		if mytype == 'Link' or mytype == 'Category' or mytype == 'Program':		# Callback Link
			# die Url im Datensatz ist im Plugin nicht verwendbar ( api-Call -> profiles)
			# 	daher verwenden wir die fertigen Links aus dem linken Menü der Webseite ('guide-item__guideItemLink
			#	Die Links mixt Tunein mit preset_id, guideId, linkfilter. 
			#	Zusätzl. Problem: die Link-Sätze enthalten Verweis auf Folgesatz mit preset_id 
			#	(Bsp. data-nextGuideItem="c100000625")
			# Bisher sicherste Identifizierung (vorher über den Titel = title): Abgleich mit preset_id am
			#	Ende des Links. Bei Sprachen verwendet Tunein (außer bei Bashkirisch) nur linkfilter im Link.
			# Sätze überspringen (url == local_url) - Link zu Station zwar möglich (dann in guideId), aber 
			#	Stream häufig nicht verfügbar (künftige od. zeitlich begrenzte Sendung). 
			# 				
			url_found = False
			if preset_id == 'languages':		# nur mit linkfilter suchen (bei Tunein nur bei Languages)
				url_title = linkfilter
			else:
				url_title = "-%s/" % preset_id
																	
			PLog('url_title: ' + url_title)
			for link in link_list:
				local_url = BASE_URL + stringextract('href="', '"', link)
				if url_title in local_url:			
					PLog('url_found: ' + local_url)
					url_found = True
					link_list.remove(link)								# Sätze mit ident. linkfilter möglich
					break
					
			if not url_found: 					# Tunein-Info, übersetzt -  mögl.: will be available on ..
				msg1 = ('skip: no preset_id in link for: %s | %s' % (title,preset_id)) 
				PLog(msg1); PLog(preset_id); PLog(local_url)
				if 'index":1,"type":"Prompt"' in page:
					pos = page.find('index":1,"type":"Prompt"')
					PLog(pos)
					msg2 = page[pos:pos+200]
					msg2 = stringextract('title":"', '"', msg2)
					msg1 = title
					PLog(msg2)
					xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')	
				continue
											
			PLog('Link_url: %s, url_org: %s' % (local_url, url_org)); # PLog(image);	# Bei Bedarf
			if url == local_url:					# Rekursion vermeiden
				'''
				PLog('try_with_guideId')			# nicht genutzt - viele nicht verfügbare Stationen
				if guideId:							# wie Tunein-Web: erneuter Versuch mit guideId
					url = 'https://api.tunein.com/profiles/%s/contents?formats=mp3,aac,ogg,hls&serial=%s&partnerId=%s' % (guideId, serial, partnerId)	
					GetContent(url=url, title=title_org, li=li)
					return	
				else:
				'''
				PLog('skip: url=local_url')									
				continue
		
			if url == local_url:					# Rekursion vermeiden
				PLog('skip: url=local_url')
				continue
				
				
			if local_url == '':					# bei Programmcontainern möglich 
				PLog('skip: empty local_url')
				continue			
			
			link_offset = offset				# Reset offset bei Verzeichniswechsel
			if local_url != url_org:			
				link_offset = 0
				
			summ 	= 	subtitle			# summary -> subtitle od. FollowText
			summ_mehr = L('Mehr...')
			fparams="&fparams={'url': '%s', 'title': '%s', 'offset': '%s'}"  %\
				(urllib2.quote(local_url), urllib2.quote(title), link_offset)
			addDir(li=li, label=title, action="dirList", dirID="GetContent", 
				fanart=R(ICON), thumb=R(ICON), summary=summ_mehr, fparams=fparams)
			li_cnt = li_cnt + 1	
	# ------------------------------------------------------------------	
	# 																	Callback Station
	# ------------------------------------------------------------------	
		if mytype == 'Station' or mytype == 'Topic':					
			if preset_id.startswith('p'):
				preset_id = guideId				# mp3-Quelle in guideId., Bsp. t109814382
			# local_url = 'http://opml.radiotime.com/Tune.ashx?id=%s&formats=%s' % (preset_id, Dict('load', 'formats'))
			# 19.07.2019: nach IP-Sperre Call erweitert mit serial + partnerId - s. StationList
			local_url = 'http://opml.radiotime.com/Tune.ashx?id=%s&formats=%s&serial=%s&partnerId=%s' % (preset_id, Dict('load', 'formats'), serial, partnerId)
			#PLog('Station_url: ' + local_url);	# PLog(image);	# Bei Bedarf
			
			summ 	= 	subtitle			# summary -> subtitle od. FollowText
			if len(summ) < 11 and descr:	# summary: falls Datum mit description ergänzen
				summ = summ + ' | %s' % descr
				
			tagline = FollowText			# Bsp. 377,5K Favoriten od. 16:23 (Topic)
			if duration:
				tagline = ' %s | %s' % (duration, FollowText)
			if title == '':					# Bsp. Lokale Nachrichten / Das Magazin
				title = seoName
					
			if tagline.endswith('| '): tagline = tagline[:-3]	# Ende:   | löschen
			summ = summ.replace(' |', '')						# Start:  | löschen
			
			summ = UtfToStr(summ); local_url=UtfToStr(local_url);		# title s.o.
			image=UtfToStr(image); preset_id=UtfToStr(preset_id);
			
			summ=repl_json_chars(summ); 
				
			PLog('Satz_Station/Topic:') 								
			# bitrate: dummy 	
			fparams="&fparams={'url': '%s', 'title': '%s', 'summ': '%s', 'image': '%s', 'typ': 'Station', 'bitrate': 'unknown',  'preset_id': '%s'}"  %\
				(urllib2.quote(local_url), urllib2.quote(title), urllib2.quote(summ), urllib2.quote(image), preset_id)
			addDir(li=li, label=title, action="dirList", dirID="StationList", 
				fanart=image, thumb=image, summary=summ, tagline=tagline, fparams=fparams)
						
			li_cnt = li_cnt + 1										
				
		if max_count:
			# Mehr Seiten anzeigen:		
			cnt = li_cnt + offset		# 
			PLog('Mehr_Test: %s | %s | %s | %s' % (max_count, li_cnt, cnt, page_cnt) )
			if cnt >= page_cnt:			# Gesamtzahl erreicht - Abbruch
				offset=0
				break					# Schleife beenden
			elif li_cnt+1 >= max_count:	# Mehr, wenn max_count erreicht
				offset = offset + max_count 
				title = L('Mehr...') + title_org
				summ_mehr = L('Mehr...') + '(max.: %s)' % page_cnt
				title_org=UtfToStr(title_org);
				
				fparams="&fparams={'url': '%s', 'title': '%s', 'offset': '%s'}"  %\
					(urllib2.quote(url), urllib2.quote(title_org), offset)
				addDir(li=li, label=title, action="dirList", dirID="GetContent", 
					fanart=R(ICON_MEHR), thumb=R(ICON_MEHR), summary=summ_mehr, fparams=fparams)
				break					# Schleife beenden		
								
		# break	# Debug Stop
	PLog('li_cnt: ' + str(li_cnt))	
	if endOfDirectory == True:
		if li_cnt == 0:
			if subtitle:					# Hinweis auf künftige Sendung möglich (keine akt. Sendung)
				title_org = title_org + " | %s" % subtitle	
			msg1 = L('keine Eintraege gefunden') + ": " + title_org 
			msg1 = UtfToStr(msg1)
			PLog(msg1)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
			return li						# verursacht zwar Directory-Error, bleibt aber in der Liste.
		xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True) 
	else:
		return li, li_cnt	
	
#-----------------------------
# RequestTunein: die sprachliche Zuordnung steuern wir über die Header Accept-Language und 
#	CONSENT (Header-Auswertung Chrome).
#		
# Kodi-Version: User-Agent erforderlich (entfiel beim HTTP.Request in Plex).
# 2-stufiger Ablauf: 1. urllib2.Request (check_hostnam =False), 2. urllib2.Request mit Zertifikat
#	notwendig, da trotz identischer URL-Basis die SSL-Kommunikation ablaufen kann.
# Das Problem "Moved Temporarily" im Location“-Header-Feld wird hier nicht behandelt (bisher nicht notwendig),
#	s. get_pls -> Zertifikate-Problem.
#
#	Ab 29.04.2018: 3. Stufe - mit Zertifikatecheck (linux-Zertifikat, s. get_pls)
#		Alternative: user-definiertes Zertifikat (Einstellungen) - z.B. fullchain.pem von Let's Encrypt 
#
#
def RequestTunein(FunctionName, url, GetOnlyHeader=None):
	PLog('RequestTunein: ' + url)

	msg=''
	loc = Dict('load', 'loc')						# Bsp. fr, 	loc_browser nicht benötigt
	PLog('loc: ' + loc)	

	msg=''
	PLog('page1:')			
	try:																# Step 1: urllib2.Request
		PLog("RequestTunein, step 1, called from %s" % FunctionName)
		req = urllib2.Request(url)	
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3')
		# Quelle Language-Werte: Chrome-HAR
		# req.add_header('Accept-Language',  'da_DK, en;q=0.9, da_DK;q=0.7')	# Debug
		req.add_header('Accept-Language',  '%s, en;q=0.9, %s;q=0.7'	% (loc, loc))
			
		req.add_header('CONSENT', loc)				# loc_browser ebenfalls nicht benötigt
		gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  
		gcontext.check_hostname = False
		gcontext.verify_mode = ssl.CERT_NONE
		ret = urllib2.urlopen(req, context=gcontext, timeout=UrlopenTimeout)
		
		if GetOnlyHeader:
			PLog("GetOnlyHeader:")
			page = getHeaders(ret)		# Dict
			PLog(page) 
			return page, ''
		else:
			compressed = ret.info().get('Content-Encoding') == 'gzip'
			PLog("compressed: " + str(compressed))
			page = ret.read()
			PLog(len(page))
			if compressed:
				buf = StringIO(page)
				f = gzip.GzipFile(fileobj=buf)
				page = f.read()
				PLog(len(page))
			ret.close()
			PLog(page[:160])
	except Exception as exception:
		error_txt = "RequestTunein: %s-1: %s" % (FunctionName, repr(exception))
		error_txt = error_txt + ' | ' + url				 			 	 
		msg =  error_txt
		PLog(msg)
		# msg = L('keine Eintraege gefunden') + " | %s" % msg	
		page=''
		
	if page == '':	
		PLog('page2:')			
		msg=''			
		try:																# Step 2: urllib2.Request mit Zertifikat
			PLog("RequestTunein, step 2, called from %s" % FunctionName)
			cafile = os.path.join("%s", "xbmc_cacert.pem") % RESOURCES_PATH # 
			if SETTINGS.getSetting('UseSystemCertifikat') == "true":	# Bsp. "/etc/certbot/live/rols1.xxx.de/fullchain.pem"
				if os.path.exists(SETTINGS.getSetting('SystemCertifikat')) == "true":	
					cafile = SETTINGS.getSetting('SystemCertifikat')		# Vorabtest path.exists in Main
				
			PLog(cafile)
			req = urllib2.Request(url)			
			req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3')
			req.add_header('Accept-Language',  '%s, en;q=0.9, %s;q=0.7'	% (loc, loc))
			req.add_header('CONSENT', loc)
			ret = urllib2.urlopen(req, cafile=cafile, timeout=UrlopenTimeout)
			
			if GetOnlyHeader:
				PLog("GetOnlyHeader:")
				page = getHeaders(ret)		# Dict
				PLog(page)  # Bei Bedarf, nicht kürzen
				return page, ''
			else:
				page = ret.read()
		except Exception as exception:
			error_txt = "RequestTunein: %s-2: %s" % (FunctionName, repr(exception)) 
			error_txt = error_txt + ' | ' + url				 			 	 
			msg =  error_txt
			PLog(msg)
			# msg = L('keine Eintraege gefunden') + " | %s" % msg	
			page=''	
					
	PLog(page[:100])								# bei Bedarf
	return page, msg
	
#-----------------------------
# Auswertung der Streamlinks. Aufrufe ohne Playliste starten mit Ziffer 4:
#	1. opml-Info laden, Bsp. http://opml.radiotime.com/Tune.ashx?id=s24878
#	2. Test Inhalt von Tune.ashx auf Playlist-Datei (.pls) -
#		2.1. Playlist (.pls oder/und .m3u) laden, bei Problemen mittels urllib2 + Zertifikat
#		2.2. Streamlinks aus Playlist extrahieren -> in url-Liste
#		2.3. Doppler entfernen
#	3. Test Inhalt von Tune.ashx auf .m3u-Datei (Ergebnis überschreibt url-Liste, falls vorh.)
#		Ablauf wie .pls-Url, aber ohne urllib2 (nicht erforderl. bisher)
#	4. Behandlung der url-Liste:
#		4.1. .mp3-Links markieren (ohne Metaprüfung)
#		4.2. Prüfung der Metadaten (getStreamMeta - zeitaufwendig) 
#			4.2.1 Ermittlung Bitrate, Song - falls leer, mit tunein-Daten ergänzen
#			4.2.2 Prüfung auf angehängte Portnummer - url-Ergänzung mit ';' oder '/;'
#			4.2.3 Prüfung auf Endung '.fm/' - url-Ergänzung mit ';' 
#		4.3. letzte Doppler in der url-Liste entfernen
#	5. Erzeugung Listitems mit den einzelnen Url's der Liste
#	5.1. Bei Option UseRecording: 	zusätzlich Erstellung Recording- und Stop-Button
#	5.2. Bei Option UseFavourites: 	zusätzlich Erstellung Favorit hinzufügen/Löschen
#									(Löschen abhängig von Ergebnis SearchInFolders)
#
# Hinw. TV-Links: die gelisteten TV-Links, werden beim opml-Call mit Error 400 abgewiesen. Im Web
#	wird "ein Problem" angezeigt - laut dev-Tools wird der master.m3u8-Link ermittelt, aber der 
#	enthaltene Audio-Link nicht.
#
def StationList(url, title, image, summ, typ, bitrate, preset_id):
	PLog('StationList: ' + url)
	
	# Callback-Params für PlayAudio, RecordStart, RecordStop
	title=UtfToStr(title); summ = UtfToStr(summ);
	fparams="{'url': '%s', 'title': '%s', 'summ': '%s', 'image': '%s', 'typ': '%s', 'bitrate': 'unknown',  'preset_id': '%s'}"  %\
				(urllib2.quote(url), urllib2.quote(title), urllib2.quote(summ), urllib2.quote(image), typ, preset_id)
	Dict('store', 'Args_StationList', fparams)				

	PLog(title);PLog(image);PLog(summ);PLog(typ);PLog(bitrate);PLog(preset_id)
	title_org=title; summ_org=summ; bitrate_org=bitrate; 					# sichern
	typ_org=typ; url_org=url		
	
	li = xbmcgui.ListItem()
	li = home(li)							# Home
			
	if summ:
		if 'No compatible stream' in summ or 'Does not stream' in summ: 	# Kennzeichnung + mp3 von TuneIn 
			if 'Tune.ashx?' in url == False:								# "trozdem"-Streams überspringen - s. GetContent
				url = R('notcompatible.enUS.mp3') # Bsp. 106.7 | Z106.7 Jackson
				fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sid': '0'}" %\
					(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(image), urllib.quote_plus(summ))
				addDir(li=li, label=title, action="dirList", dirID="PlayAudio_pre", fanart=image, thumb=image, 
					fparams=fparams, summary=summ, mediatype='music')
				xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	
	

	if 'Tune.ashx?' in url:						# normaler TuneIn-Link zur Playlist o.ä.
		cont, msg = RequestTunein(FunctionName='StationList, Tune.ashx-Call', url=url)
		if cont == '':
			msg1 = msg
			PLog(msg1)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			xbmcplugin.endOfDirectory(HANDLE)
			return li
		if ': 400' in cont:				# passiert (manchmal) bei 'neuer Versuch' (mit preset_id)
			# Check TV-Sender? Falls ja, liefert Call master.m3u8 im json-Format 
			#	format: hls notwendig, sonst notcompatible-Error
			# Hinw.: nach ca. 5 fehlerhaften Calls  war meine IP-Adresse (nicht nur serial-ID) für weitere 
			# 	opml-Calls gesperrt. opml-Calls in GetContent waren erst wieder nach Erweiterung des  Calls
			#	mit serial + aktueller partnerId möglich. Test nach ca. 1 Std. ohne Erweit.: Sperre dauert an.
			#
			# Bsp.: China CRI Hit FM  - #STATUS: 400, tvaudio-Call ergibt json mit m3u8-Url
			#	Verwertbare Streams geben wir direkt aus, ohne Headercheck. 
			# Bei vielen chinesischen Sendern ergibt der tvaudio-Call notcompatible.enUS.mp3 - diesen geben wir
			#	NICHT als audio aus, da häufig durch Firewall verursacht.
			serial = Dict('load', 'serial')	
			audience = '%3Ball%3BVZ_Altice%3B'	# unquote:	;all;VZ_Altice; (ganzer Call aus chrome-dev-tools)		
			tvaudio_url = 'https://opml.radiotime.com/Tune.ashx?audience=%s&id=%s&render=json&formats=mp3,aac,ogg,hls&type=station&serial=%s&partnerId=%s' % (audience, preset_id, serial, partnerId)
			cont, msg = RequestTunein(FunctionName='StationList, tvaudio-Call', url=tvaudio_url)
			# PLog(cont)
			if 'url":' in cont:  											# json auswerten 
				json_url = stringextract('url": "', '"', cont) 				# mp3, m3u8 (auch andere?)
				PLog("json_url: " + json_url)
				if 'Audio/notcompatible' in  json_url:						# nach 400er-Error keine Audioausgabe
					audio_url = ''
				else:														# verm. mp3
					audio_url = json_url
				if "master.m3u8" in json_url or '.m3u8' in json_url: 		# m3u8 weiter auswerten
					audio_url = get_tv_audio_url(url=json_url)				
				if audio_url:
					return PlayAudio(url=audio_url, title=title, thumb=image, Plot=summ, CB='')	# direkt
				else:
					url = url_org					# Fehler-Url: Tunein-Url
					cont = title_org

			msg1 = L("keinen Stream gefunden zu") 
			msg2 = url
			msg3 = 'Tunein: %s' % cont
			PLog(msg1); PLog(msg2); PLog(msg3);
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
			return li

		PLog('Tune.ashx_content: ' + cont)
	else:										# ev. CustomUrl - key="presetUrls"> (direkter Link zur Streamquelle),
		cont = url								# sowie url's aus GetContent- 
		PLog('custom_content: ' + cont)
		
	# .pls-Auswertung ziehen wir vor, auch wenn (vereinzelt) .m3u-Links enthalten sein können
	if '.pls' in cont:					# Tune.ashx enthält häufig Links zu Playlist (.pls, .m3u)				
		cont = get_pls(cont)
		if cont.startswith('get_pls-error'): 	# Bsp. Rolling Stones by Radio UNO Digital, pls-Url: 
			msg1 = cont							# http://radiounodigital.com/Players-Tunein/rollingstones.pls
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			return li
	
	# if line.endswith('.m3u'):				# ein oder mehrere .m3u-Links, Bsp. "Absolut relax (Easy Listening Music)"
	if '.m3u' in cont:						# auch das: ..playlist/newsouth-wusjfmmp3-ibc3.m3u?c_yob=1970&c_gender..
		cont = get_m3u(cont)
		PLog('m3u-cont: ' + cont)
		if cont == '':
			msg1 = L('keinen Stream gefunden zu') 
			msg2 = "%s %s" % (msg, title)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li
			
												# Bsp.: Space Station Soma - mehrere Stream-Urls, die 
	if '&render=json' in cont:					# 	auf eine json-Datei verweisen, die Details + Audio-
		cont = get_ice_json(cont)					#	Url enthält
		PLog('ice_json: ' + cont)
		if cont == '':
			msg1 = L('keinen Stream gefunden zu') 
			msg2 = "%s %s" % (msg, title)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li			

	#	StreamTests ausgelagert zur Mehrfachnutzung (ListMRS)
	url_list, err_flag = StreamTests(cont,summ_org)	
	PLog("url_list: " + str(url_list))	
	if len(url_list) == 0:
		if err_flag == True:					# detaillierte Fehlerausgabe vorziehen, aber nur bei leerer Liste
			msg1 = L('keinen Stream gefunden zu') 
			msg2 = title
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li
		else:
			msg1 = L('keinen Stream gefunden zu') + ": %s" % title
			msg2 = L("Bitte den Eintrag in Einstellungen ueberpruefen!")
			msg3 = L('Minimale Bitrate')
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
			return li

	i=1; 
	for line in url_list:
		PLog(line)
		url   = line.split('|||')[0]
		summ  = line.split('|||')[1]
		server = url[:80] + '...'
		summ  = '%s | %s' % (summ, server)
		if summ.strip().startswith('|'):
			summ = summ[2:]
		
		fmt='mp3'								# Format nicht immer  sichtbar - Bsp. http://addrad.io/4WRMHX. Ermittlung
		if 'aac' in url:						#	 in getStreamMeta (contenttype) hier bisher nicht genutzt
			fmt='aac'
		title = title_org + ' | Stream %s | %s'  % (str(i), fmt)
		i=i+1
		title=UtfToStr(title); summ = UtfToStr(summ);
		PLog(url); PLog(summ); 
																		# Play-Button
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'sid': '%s', 'CB': 'StationList'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(image), urllib2.quote(summ), preset_id)
		addDir(li=li, label=title, action="dirList", dirID="PlayAudio_pre", fanart=image, thumb=image, 
			fparams=fparams, summary=summ)
		PLog("fparams: " + fparams)	
			
	if SETTINGS.getSetting('UseRecording') == "true":			# Aufnahme- und Stop-Button
		title = L("Aufnahme") + ' ' + L("starten")		
		fparams="&fparams={'url': '%s', 'title': '%s', 'title_org': '%s', 'image': '%s', 'summ': '%s', 'typ': '%s', 'bitrate': '%s'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title),  urllib.quote_plus(title_org),urllib.quote_plus(image), 
			urllib.quote_plus(summ), typ_org, bitrate_org)
		addDir(li=li, label=title, action="dirList", dirID="RecordStart", fanart=R(ICON_RECORD), thumb=R(ICON_RECORD), 
			fparams=fparams, summary=summ)

		title = L("Aufnahme") + ' ' + L("beenden")		
		fparams="&fparams={'url': '%s', 'title': '%s', 'summ': '%s', 'CB': 'StationList'}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title),  urllib.quote_plus(summ))
		addDir(li=li, label=title, action="dirList", dirID="RecordStop", fanart=R(ICON_STOP), thumb=R(ICON_STOP), 
			fparams=fparams, summary=summ)
			
	if SETTINGS.getSetting('UseFavourites') == "true":	# Favorit hinzufügen/Löschen
		if preset_id != None:			# None möglich - keine Einzelstation, Verweis auf Folgen, Bsp.:
										# # http://opml.radiotime.com/Tune.ashx?c=pbrowse&id=p680102 (stream_type=download)
			sidExist,foldername,guide_id,foldercnt = SearchInFolders(preset_id, ID='preset_id') # vorhanden, Ordner?
			PLog('sidExist: ' + str(sidExist))
			PLog('foldername: ' + foldername)
			PLog('foldercnt: ' + foldercnt)
			PLog(summ)
			if sidExist == False:		
				title = L("Favorit") + ' ' + L("hinzufuegen")	# hinzufuegen immer in Ordner General	
				fparams="&fparams={'ID': 'add', 'preset_id': '%s', 'folderId': 'dummy'}" % preset_id
				addDir(li=li, label=title, action="dirList", dirID="Favourit", fanart=R(ICON_FAV_ADD), thumb=R(ICON_FAV_ADD), 
					fparams=fparams, summary=summ)
					
			if sidExist == True:	
				summ =title_org	+ ' | ' + L('Ordner') + ': ' + 	foldername	# hier nur Station + Ordner angeben,
				title = L("Favorit") + ' ' + L("entfernen")					#  Server + Song entfallen
				fparams="&fparams={'ID': 'remove', 'preset_id': '%s', 'folderId': 'dummy'}" % preset_id
				addDir(li=li, label=title, action="dirList", dirID="Favourit", fanart=R(ICON_FAV_REMOVE), 
					thumb=R(ICON_FAV_REMOVE), fparams=fparams, summary=summ)

				title = L("Favorit") + ' ' + L("verschieben")	# preset_number ist Position im Ordner
				summ = L('Ordner zum Verschieben auswaehlen')				
				fparams="&fparams={ 'title': '%s', 'ID': 'moveto', 'preset_id': '%s'}" %\
					(urllib.quote_plus(title), preset_id)
				addDir(li=li, label=title, action="dirList", dirID="FolderMenu", fanart=R(ICON_FAV_MOVE), 
					thumb=R(ICON_FAV_MOVE), fparams=fparams, summary=summ)
											
	PLog(len(url_list))		
	url_list = repl_dop(url_list)				# Doppler entfernen	
	PLog(len(url_list))		
		
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

#-----------------------------
# Wrapper für getStreamMeta. Nutzung durch StationList + ListMRS
#	Für jede Url erfolgt in getStreamMeta eine Headerauswertung; falls erforderlich wird die Url angepasst 
#		(Anhängen von ";" oder "/;"), falls vorhanden werden bitrate + song für summary gespeichert. 
#	Rückgabe: Liste der aktualisierten Url mit summary-Infos.
#	url_list = Liste von Streamlinks aus Einzel-Url, .m3u- oder .pls-Dateien.
#	
def StreamTests(url_list,summ_org):
	PLog('StreamTests:');
	summ = ''
	
	max_streams = int(SETTINGS.getSetting('maxStreamsPerStation'))	# max. Anzahl Streams per Station
	PLog('max_streams: ' + str(max_streams))
	
	lines = url_list.splitlines()
	err_flag = False; err=''					# Auswertung nach Schleife	
	url_list = []
	line_cnt = 0								# Einzelzählung
	for line in lines:
		line_cnt = line_cnt + 1			
		PLog('line %s (max. %s): %s' % (line_cnt, str(max_streams), line))
		url = line

		if url.startswith('http'):				# rtpm u.ä. ignorieren
			if url.endswith('.mp3'):			# .mp3 bei getStreamMeta durchwinken
				st=1; ret={}
			else:
				ret = getStreamMeta(url)		# Sonderfälle: Shoutcast, Icecast usw. Bsp. http://rs1.radiostreamer.com:8020,
				PLog(ret)						# 	http://217.198.148.101:80/
				st = ret.get('status')	
			PLog('ret.get.status: ' + str(st))
			
			if st == 0:							# nicht erreichbar, verwerfen. Bsp. http://server-uk4.radioseninternetuy.com:9528
				err = ret.get('error')			# Bsp.  City FM 92.9 (Taichung, Taiwan):
				err = err + '\r\n' + url		#	URLError: timed out, http://124.219.41.230:8000/929.mp3
				err_flag = True
				PLog(err)
				# xbmcgui.Dialog().ok(ADDON_NAME, msg1=err, '', '') # erst nach Durchlauf der Liste, s.u.
				continue							
			else:
				if ret.get('metadata'):					# Status 1: Stream ist up, Metadaten aktualisieren (nicht .mp3)
					metadata = ret.get('metadata')
					PLog('metadata:'); PLog(metadata)						
					bitrate = metadata.get('bitrate')	# bitrate aktualisieren, falls in Metadaten vorh.
					if bitrate == None:
						bitrate = '0'					# wird nicht gegen Settings geprüft 
					PLog(bitrate)
					if int(bitrate) <  int(SETTINGS.getSetting('minBitrate')):	# Bitrate-Settings berücksichtigen
						continue
					
					try:
						song = metadata.get('song')		# mögl.: UnicodeDecodeError: 'utf8' codec can't decode..., Bsp.
						song = song.decode('utf-8')		# 	'song': 'R\r3\x90\x86\x11\xd7[\x14\xa6\xe1k...
						song = unescape(song)
					except:
						song=''
						
					PLog('song: ' + str(song)); PLog('bitrate: ' + str(bitrate))	# mind. bei bitrate None möglich
					if song.find('adw_ad=') == -1:		# ID3-Tags (Indiz: adw_ad=) verwerfen
						if bitrate and song:							
							summ = 'Song: %s | Bitrate: %s KB' % (song, bitrate) # neues summary
						if bitrate and song == '':	
							summ = '%s | Bitrate: %s KB' % (summ_org, bitrate)		# altes summary ergänzen
					PLog('summ: ' + summ)		
				if  ret.get('hasPortNumber') == 'true': # auch SHOUTcast ohne Metadaten möglich, Bsp. Holland FM Gran Canaria,
					if url.endswith('/'):				#	
						url = '%s;' % url
					else:								# Stream mit Portnummer, aber ohne / am Urlende - Berücksichtigung
						#  Icecast-Server. :
						PLog('ret.get shoutcast: ' + ret.get('shoutcast'))
						if 'Icecast' in ret.get('shoutcast'): 			# Bsp.  Sender Hi On Line,
							pass										# 		http://mediaserv33.live-streams.nl:8036
						else:											#  Bsp. Holland FM Gran Canaria,
							url = '%s/;' % url							# 		http://stream01.streamhier.nl:9010	
				else:	
					if url.endswith('.fm/'):			# Bsp. http://mp3.dinamo.fm/ (SHOUTcast-Stream)
						url = '%s;' % url
					else:								# ohne Portnummer, ohne Pfad: letzter Test auf Shoutcast-Status 
						#p = urlparse(url)				# Test auf url-Parameter nicht verlässlich
						#if 	p.params == '':	
						url_split = url.split('/')		
						PLog(len(url_split))
						if len(url_split) <= 4:			# Bsp. http://station.io, http://sl64.hnux.com/
							if url.endswith('/'):
								url = url[:len(url)-1]	# letztes / entfernen 
							# 27.09.2018 Verzicht auf "Stream is up"-Test. Falls keine Shoutcast-Seite, würde der
							#	Stream geladen, was hier zum Timeout führt. Falls erforderlich, hier Test auf 
							#  	ret.get('shoutcast') voranstellen.
							#cont = HTTP.Request(url).content# Bsp. Radio Soma -> http://live.radiosoma.com
							#if 	'<b>Stream is up' in cont:			# 26.09.2018 früheres '.. up at' manchmal zu lang
							#PLog('Shoutcast ohne Portnummer: <b>Stream is up at')
							shoutcast = str(ret.get('shoutcast'))
							PLog(ret.get('shoutcast'))
							if 'shoutcast' in shoutcast.lower(): # an Shoutcast-url /; anhängen
								url = '%s/;' % url	
																		
			PLog('append: ' + url)	
			PLog(summ); 					
			url_list.append(url + '|||' + summ)		# Liste für PlayAudio_pre	
				
			if max_streams:							# Limit gesetzt?
				if line_cnt >= max_streams:
					break 
	return url_list, err_flag
#-----------------------------
def get_pls(url):               # Playlist extrahieren
	PLog('get_pls: ' + url)
	url_org = url
	
	# erlaubte Playlist-Formate - Endungen oder Fragmente der Url:
	#	Bsp. http://www.asfradio.com/launch.asp?p=pls
	format_list = ['.pls', '.m3u', '=pls', '=m3u', '=ram', '=asx']
	
	urls =url.splitlines()	# mehrere möglich, auch SHOUTcast- und m3u-Links, Bsp. http://64.150.176.192:8043/

	pls_cont = []
	for url in urls:
		# PLog(url)
		cont = url.strip()
		if url.startswith('http') == False:		# Sicherung, falls Zeile keine Url enthält (bisher aber nicht gesehen)
			continue
		isInFormatList = False	
		for pat in format_list:					# Url mit Playlists
			if pat in url:	
				isInFormatList = True		
				break
												# 1. Versuch (2-step)
		if 	isInFormatList:	# .pls auch im Pfad möglich, Bsp. AFN: ../AFNE_WBN.pls?DIST=TuneIn&TGT=..
			cont, msg = RequestTunein(FunctionName='get_pls - isInFormatList', url=url)
		cont = cont.strip()
		if '.ts?sd=' in cont:					# skip Einzelstream: m3u8-Datei mit ts-Segmenten, 
			pls = url_org						# 	Aufruf aus ListMRS möglich
			PLog('skip m3u8 mit ts-Segmenten')
			return pls	

		PLog('cont1: ' + cont)
		
		# Zertifikate-Problem (vorwiegend unter Windows):
		# Falls die Url im „Location“-Header-Feld eine neue HTTPS-Adresse enthält (Moved Temporarily), ist ein Zertifikat erforderlich.
		# 	Performance: das große Mozilla-Zertifikat cacert.pem tauschen wir gegen /etc/ssl/ca-bundle.pem von linux (ca. halbe Größe).
		#	Ab 29.04.2018: alternativ user-definiertes Zertifikat (Einstellungen) - wie RequestTunein
		#	Aber: falls ssl.SSLContext verwendet wird, schlägt der Request fehl.
		#	Hinw.: 	gcontext nicht mit	cafile verwenden (ValueError)
		#	Bsp.: KSJZ.db SmoothLounge, Playlist http://smoothlounge.com/streams/smoothlounge_128.pls
		# Ansatz, falls dies unter Windows fehlschlägt: in der url-Liste nach einzelner HTP-Adresse (ohne .pls) suchen
		
		if cont == '':							# 2. Versuch
			try:
				req = urllib2.Request(url)
				cafile = os.path.join("%s", "xbmc_cacert.pem") % RESOURCES_PATH
				if SETTINGS.getSetting('SystemCertifikat') == "true": # Bsp. "/etc/certbot/live/rols1.xxx.de/fullchain.pem"	
					cafile = SETTINGS.getSetting('SystemCertifikat')
				PLog(cafile)
				req = urllib2.urlopen(req, cafile=cafile, timeout=UrlopenTimeout) 
				# headers = getHeaders(req)			# bei Bedarf
				# PLog(headers)
				cont = req.read()
			except Exception as exception:	
				error_txt = 'get_pls-error: ' + str(exception)	# hier nicht repr() verwenden
				# Rettungsversuch - hilft bei SomaFM-Stationen:
				# HTTP Error 302: Found - Redirection to url 'itunes://somafm.com/xmasrocks130.pls?bugfix=safari7' is not allowed
				if 'itunes://' in error_txt:	# Bsp. http://api.somafm.com/xmasrocks130.pls
					PLog(url)
					PLog(str(exception))
					url=stringextract('\'', '\'', str(exception))
					url=url.replace('itunes://', 'http://')
					PLog('neue itunes-url: ' + url)
					req = urllib2.Request(url)		# 3. Versuch
					req = urllib2.urlopen(req, cafile=cafile, timeout=UrlopenTimeout) 
					cont = req.read()					
					PLog(cont)
					if '[playlist]' in cont:		# nochmal gut gegangen
						pass
					else:
						error_txt = 'get_pls-error: itunes-Url not supported by this plugin.' + ' | ' + str(exception)
						return error_txt
				else:	
					error_txt = error_txt + ' | ' + url
					error_txt = error_txt.decode(encoding="utf-8")
					PLog(error_txt)
					return error_txt
												
		if cont:									# Streamlinks aus Playlist extrahieren 
			lines =cont.splitlines()	
			for line in lines:						# Bsp. [playlist] NumberOfEntries=1 File1=http://s8.pop-stream.de:8650/
				line = line.strip()
				if line.startswith('http'):
					pls_cont.append(line)
				if '=http' in line:					# Bsp. File1=http://195.150.20.9:8000/..
					line_url = line.split('=')[1]
					pls_cont.append(line_url)						
		 			 	 		   
	pls = pls_cont
	if pls == '':
		PLog('pls leer')
		return pls
	lines = repl_dop(pls)
	pls = '\n'.join(lines)
	pls = pls.strip()
	PLog(pls[:100])
	return pls
    
#-----------------------------
def get_m3u(url):               # m3u extrahieren - Inhalte mehrerer Links werden zusammengelegt,
	PLog('get_m3u: ' + url)		#	Details/Verfügbarkeit holt getStreamMeta
	urls =url.splitlines()	
	
	m3u_cont = []
	for url in urls:	
		# Bsp. http://icy3.abacast.com/progvoices-progvoicesmp3-32.m3u?source=TuneIn
		#	oder Radio Soma http://www.radiosoma.com/RadioSoma_107.9_MHz.m3u
		if url.startswith('http') and '.m3u' in url:	
			try:									
				req, msg = RequestTunein(FunctionName='get_m3u', url=url)
				req = urllib2.unquote(req).strip()	
				# PLog(req)	
			except: 	
				req=''
			lines =req.splitlines()				# Einzelzeilen oder kompl. m3u-Datei
			for line in lines:
				if line.startswith('http'):			# skip #EXTM3U, #EXTINF
					m3u_cont.append(line)			# m3u-Inhalt anhängen
		
	pls = m3u_cont	
	lines = repl_dop(pls)					# möglich: identische Links in verschiedenen m3u8-Inhalten, 
	pls = '\n'.join(lines) # 				# Coolradio Jazz: coolradio1-48.m3u, coolradio1-128.m3u, coolradio1-hq.m3u
	pls = pls.strip()
	PLog(pls[:100])
	return pls
    
#-----------------------------
def get_ice_json(url):               # Streamdetails aus json-Datei ermitteln
	PLog('get_ice_json: ' + url)		
	urls =url.splitlines()	
	
	stream_urls = []
	for url in urls:
		if url.startswith('http') and '&render=json' in url:
			try:									
				req, msg = RequestTunein(FunctionName='get_ice_json', url=url)
				req = urllib2.unquote(req).strip()	
				# PLog(req)	
			except: 	
				req=''
			stream_url = stringextract('"Url": "', '",', req)		# 1. Treffer, mehrere möglich
			if stream_url.startswith('http'):
				stream_urls.append(stream_url)	
	
	stream_urls = '\n'.join(stream_urls)	
	PLog(stream_urls[:100])
	return stream_urls
			
#-----------------------------
# Aufruf: StationList nach #STATUS: 400
# get_tv_audio_url: extrahiert aus master.m3u8-Datei die Audio-Url -
#	wir nehmen den ersten Treffer (2 bei 3sat vorhanden, ohne Detailinfo)
# 22.07.2019 Auswertung von BANDWIDTH auf CODECS umgestellt (wg. unter-
#	schiedlicher Bandbreiten)
#	TV: 	CODECS="avc1.77.30, mp4a.40.2"
#	Audio:	CODECS="mp4a.40.2"
#	
def get_tv_audio_url(url):
	PLog('get_tv_audio_url:')
	page, msg = RequestTunein(FunctionName='get_tv_audio_url', url=url)
	lines = page.splitlines()
	lines.pop(0)		# 1. Zeile entfernen (#EXTM3U)
	
	i = 0; audio_url=''
	for line in lines:
		if 'CODECS=' in line:
			Codecs = stringextract('CODECS="', '"', line)
			PLog(Codecs)
			try:
				if Codecs.startswith("mp4a"): 				#  "mp4a.40.2"
					audio_url = lines[i + 1]
					PLog(audio_url)
					if audio_url.startswith('http'): 		# Check
						return audio_url
					else:
						return ''							# möglich: chunklist_w1000637126.m3u8 
			except Exception as exception:	
				audio_url=''				
				PLog(str(exception))
		i = i + 1
				
	return audio_url

#-----------------------------
def get_details(line):		# line=opml-Ergebnis im xml-Format, mittels Stringfunktionen extrahieren 
	# PLog('get_details')	# 
	typ='';local_url='';text='';image='';key='';subtext='';bitrate='';preset_id='';guide_id='';playing=''
	
	typ 		= stringextract('type="', '"', line)
	local_url 	= stringextract('URL="', '"', line)
	text 		= stringextract('text="', '"', line)
	image 		= stringextract('image="', '"', line)
	if image == '':
		image = R(ICON) 
	key	 		= stringextract('key="', '"', line)
	subtext 	= stringextract('subtext="', '"', line)		
	bitrate 	= stringextract('bitrate="', '"', line)		
	preset_id  = stringextract('preset_id="', '"', line)	# Test auf 'u..' in FolderMenuList,
	guide_id 	= stringextract('guide_id="', '"', line)	# Bsp. "f3"
	playing 	= stringextract('playing="', '"', line)
	if 	playing == subtext:									# Doppel summ. + tagline vermeiden
		playing = ''
	is_preset  = stringextract('is_preset="', '"', line)	# true = Custom-Url
	
	local_url 	= unescape(local_url)
	text 		= unescape(text)
	subtext 	= unescape(subtext)
	playing 	= unescape(playing)
	if playing == '':
		playing = 'unknown'
		
	text		= text.decode(encoding="utf-8")
	subtext		= subtext.decode(encoding="utf-8")
	playing		= playing.decode(encoding="utf-8")
	
	return typ,local_url,text,image,key,subtext,bitrate,preset_id,guide_id,playing,is_preset
	
#-----------------------------
# CreateTrackObject entfällt in Kodi (-> PlayAudio)
# Codecs, Protocols ... s. Framework/api/constkit.py
#	DirectPlayProfiles s. Archiv/TuneIn2017/00_Hinweis.txt
#	sid = Station-ID (für opml-Call in PlayAudio)
# 05.12.2018 **kwargs entfernt + nach Tests wieder hinzugefügt. I.G.z. Shoutcast läuft Tunein2017 
#	mit + ohne **kwargs - tested hosted Web app  3.69.1, extern Web app  3.79.0, Android App
# 	
# def CreateTrackObject(url, title, summary, fmt, thumb, sid, include_container=False):

#-----------------------------
# PlayAudio_pre (in PMS-Version PlayAudio): diverse url-Tests einschl.
#	Header (Dict), falls OK: 
#		1. opml-Call mit sid zur Aufnahme in Recent (außer MyRadioStatios)
#		2. Sprung  zu PlayAudio
# 	CB enthält den Callback für PlayAudio (Verhinderung CGUIMediaWindow-Error)
#
def PlayAudio_pre(url, title, thumb, Plot, header=None, url_template=None, FavCall='', sid=None, CB=''):
	PLog('PlayAudio_pre:'); PLog(title); PLog(url); PLog(sid); PLog(Plot);

	if url is None or url == '':			# sollte hier nicht vorkommen
		PLog('Url fehlt!')
		url=GetLocalUrl()					# lokale mp3-Nachricht,  s.u. GetLocalUrl
		return PlayAudio(url, title, thumb, Plot, header, url_template, FavCall, CB)
		
	# Falsche Custom-Url,  Stream-Kennzeichnung von TuneIn
	if "/myradio.com/stream.mp3" in url:	# Scherzkeks: Einstellungen-Beispiel kopiert
		url =  os.path.join("%s", 'Sounds', 'tonleiter_harfe.mp3') % (RESOURCES_PATH)			
		return PlayAudio(url, title, thumb, Plot, header, url_template, FavCall, CB)	# Ausgabe Tonleiter

	if 'notcompatible.enUS' in url or 'nostream.enUS' in url:
		#url =  os.path.join("%s", 'Sounds', 'notcompatible.enUS.mp3') % (RESOURCES_PATH)			
		# 30.09.2019 einige nichtkompatible Streams sind via Websuche erreichbar
		# daher hier neuer Versuch - s. Settings
		if SETTINGS.getSetting('trynewsearch') == "true":
			query = title.split(' - ')[0]
			msg1 = L('Suche kompatible Streams fuer')
			msg2 = query
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			url = 'https://tunein.com/search/?query=%s' % query		
			PLog('url: ' + url)
			Search(query)			
			return
		else:
			return PlayAudio(url, title, thumb, Plot, header, url_template, FavCall, CB)	# Ausgabe not_available
		
	# Header-Check  
	#	page hier Dict, PLog s. RequestTunein
	page, msg = RequestTunein(FunctionName='PlayAudio_pre, Header-Check', url=url,GetOnlyHeader=True)

	if 'currently unavailable' in str(page):			# Bsp. icy-notice2: The resource requested is ..
		url=GetLocalUrl()	
		PLog('currently unavailable')
	elif 'text/html' in str(page):
		PLog('Error: Textpage ' + url)					# mp3: not a stream - this is a text page
		url =  os.path.join("%s", 'Sounds', 'textpage.mp3') % (RESOURCES_PATH)			
	elif 'HTTP Error' in msg or 'HTTPError' in msg:		# beliebiger HTTP-error
		url=GetLocalUrl()
		PLog('HTTP Error in msg')
		
	elif 'content-type' in str(page):
		try:									# möglich: 'HTTPHeaderProxy' object has no attribute 'get'
			stype = page.get('content-type')
			if 	'video/x-ms-asf' in page:
				PLog('Header: video/x-ms-asf')	
				url=GetLocalUrl()	
		except Exception as exception:
			error_txt = "error get content-type: " + repr(exception) 
			PLog(error_txt)
			url=GetLocalUrl()	
	
	# Ausgabe not_available:	
	if RESOURCES_PATH in url:							# audience-Call entfällt
		return PlayAudio(url, title, thumb, Plot, header, url_template, FavCall, CB) 
	
			
	# Checks überstanden -> audience-Call + -> Kodi-Player 
	#	page hier Dict, PLog s. RequestTunein
			
	if sid == None:							# Bsp. Der Feinmann-Translator http://www.dradio.de/wurf-tracks/112586.1420.mp3
		sid = '0'
	PLog('sid: ' + sid)
	if sid.startswith('s') and len(sid) > 1:			# '0' = MyRadioStatios + notcompatible stations
		# audience-opml-Call dient der Aufnahme in Recents - nur stations (Bsp. s202726, p799140 nicht - kein Lifestream).
		#	aus Chrome-Analyse - siehe Chrome_1Live_Curl.txt - Wiedergabe des Streams allein reicht tunein nicht für Recent!
		#	Custom-Url ausschließen, Bsp. sid: "u21"
		#	
		audience_url='https://opml.radiotime.com/Tune.ashx?audience=Tunein2017&id=%s&render=json&formats=%s&type=station&serial=%s&partnerId=RadioTime&version=3.31'
		audience_url = audience_url % (sid, Dict('load', 'formats'),Dict('load', 'serial'))
		PLog('audience_url: ' + audience_url)
		page, msg = RequestTunein(FunctionName='PlayAudio, audience_url', url=audience_url)
		PLog(page[:30])									# falls OK: "status": "200"
		if page == '':
			PLog('audience-opml-Call fehlgeschlagen: ' + msg)							
	
	# reguläre Ausgabe:
	return PlayAudio(url, title, thumb, Plot, header, url_template, FavCall, CB)

#-------------------------------------------------------
# convBase64 dekodiert base64-String für ShowFavs bzw. gibt False zurück
#	Base64 füllt den String mittels padding am Ende (=) auf ein Mehrfaches von 4 auf.
# aus https://stackoverflow.com/questions/12315398/verify-is-a-string-is-encoded-in-base64-python	
def convBase64(s):
	PLog('convBase64:')
	try:
		if len(s.strip()) % 4 == 0:
			return base64.decodestring(s)
	except Exception:
		pass
	return False
			
#-----------------------------
#	Google-Translation-Url (lokalisiert) - funktioniert mit PMS nicht
#		in Kodi bisher nicht getestet.
def GetLocalUrl(): 						# lokale mp3-Nachricht, übersetzt,  - nur für PlayAudio
	loc = Dict('load', 'loc')
	
	# en: Sorry, this station is not available
	# de: Dieser Sender ist leider nicht verfügbar
	# fr: Désolé, cette station n'est pas disponible
	# da: Beklager, denne station er ikke tilgængelig	
	# uk: а жаль, ця станція недоступна
	# pl: Przepraszamy, ta stacja nie jest dostępna
	
	url =  os.path.join("%s", 'Sounds', 'not_available_%s.mp3') % (RESOURCES_PATH, loc)	
	return url
	
####################################################################################################
#									Favoriten-/Ordner-Funktionen
####################################################################################################
#-----------------------------
# Rückgabe True, Ordnernamen, guide_id, foldercnt - True, falls ein Favorit mit preset_id existiert
# Problem: der opml-Call liefert nicht alle Fav's (vermutlich nur Stationen, z.B. fehlen Podcasts).
#	Alternative: Web-Auswertung https://tunein.com/user/{username}/favorites/ - json-Format, vollst.
#		Inhalt. Authentif. ist noch zu klären
#	
def SearchInFolders(preset_id, ID):	
	PLog('SearchInFolders:')
	preset_id = str(preset_id)			# None-Schutz (sollte hier nicht mehr vorkommen)
	PLog('preset_id: ' + preset_id)
	PLog('ID: ' + ID)
	serial = Dict('load', 'serial')	
	
	username = SETTINGS.getSetting('username')
	url = 'http://opml.radiotime.com/Browse.ashx?c=presets&partnerId=RadioTime&serial=%s' % serial	
	page, msg = RequestTunein(FunctionName='SearchInFolders: Ordner-Liste laden', url=url)
	if page == '':
		msg1 = msg
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')	
	PLog(page[:10])
	
	foldercnt = page.count('guide_id="f')
	foldername = ''
	guide_id = ''
	if foldercnt == 0:			# Ordnerübersicht entw. ohne oder mind.2 (General + x)
		foldercnt = 1
		guide_id = 'f1'
		foldername = 'General'
		if ID == 'foldercnt':
			return True, foldername, guide_id, str(foldercnt)
		if ID == 'preset_id' or ID == 'customUrl':		# ID='customUrl': preset_id=customUrl			
			if preset_id in page:
				return True, foldername, guide_id, str(foldercnt)
			else:
				return False, foldername, guide_id, str(foldercnt)
	else:							# einz. Ordner abklappern
		if ID == 'foldercnt':
			return True, foldername, guide_id, str(foldercnt)
			
		if ID == 'preset_id' or ID == 'customUrl':		# 	Fav's preset_id od. customUrl in den Ordnern vorhanden?
			outlines = blockextract('outline type="link"', page)
			for outline in outlines:
				ordner_url = stringextract('URL="', '"', outline)
				ordner_url = unescape(ordner_url) 
				foldername = stringextract('title=', '&', ordner_url)
				guide_id = stringextract('guide_id=', '&', ordner_url)
				page, msg = RequestTunein(FunctionName='SearchInFolders: Ordner-Inhalt laden', url=ordner_url)
				if preset_id in page:
					return True, foldername, guide_id, str(foldercnt)				
		
	return False, foldername, guide_id, str(foldercnt)	
	
#-----------------------------
# ermittelt Inhalte aus den Profildaten
#	ID='favoriteId': Rückgabe der FavoriteId (kennzeichnet die Position des Fav mit preset_id im Profil),
#					Abgleich erfolgt mit "Id"
#					falls preset_id mit u startet (Bsp. u21), handelt es sich um eine Custom Url,
#					Abgleich erfolgt mit "FavoriteId" (preset_id ohne u)
#	
def SearchInProfile(ID, preset_id):	
	PLog('SearchInProfile')
	PLog('preset_id: ' + preset_id)
	custom = False
	if preset_id.startswith('u'):			# custom-url: u entfernen für Abgleich mit FavoriteId
		preset_id = preset_id[1:]
		custom = True
	
	PLog('ID: ' + ID)
	serial = Dict('load', 'serial')

	sidExist,foldername,guide_id,foldercnt = SearchInFolders(preset_id, ID='preset_id') # vorhanden, Ordner-ID?
	# url: Profil laden, Filter: Ordner favoriteId - nur json-Format möglich
	url = 'https://api.tunein.com/profiles/me/follows?folderId=%s&filter=favorites&formats=%s&serial=%s&partnerId=RadioTime' %\
		(guide_id, Dict('load', 'formats'), serial)	
		
	favoriteId = guide_id
	if ID == 'favoriteId':
		page, msg = RequestTunein(FunctionName='SearchInProfile: favoriteId suchen', url=url)
		if page == '':
			msg1 = msg
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			return li
		PLog(page[:10])				
		
		indices = blockextract('"Index"', page)
		for index in indices:
			# PLog(index)	# bei Bedarf
			if  custom:			# custom-url
				Id = stringextract('FavoriteId":"', '"', index)
			else:
				Id = stringextract('"Id":"', '"', index)
			# PLog(Id);PLog(preset_id);
			if Id == preset_id:
				favoriteId = stringextract('"FavoriteId":"', '"', index)
				PLog('Profil-Index: ' + favoriteId)
				return favoriteId
				
	return favoriteId	# leer - Fehlschlag
	
#-----------------------------
# Favorit hinzufügen/löschen/verschieben
#	SETTINGS.getSetting('UseFavourites') bereits in StationList geprüft
#	Tunein verhindert selbst mehrfaches Hinzufügen 
#	Hinzufügen ohne Ordnerauswahl wie in Tunein - Zielordner ist autom. General, 
#		anschl. Verschieben: Button in StationList -> SearchInFolders -> 
#		FolderMenu -> Favourit (hier zusätzl. SearchInProfile erforderlich)
def Favourit(ID, preset_id, folderId):		
	PLog('Favourit:')
	PLog('ID: ' + ID); PLog('preset_id: ' + preset_id); PLog('folderId: ' + folderId);
	serial = Dict('load', 'serial')
	loc_browser = str(Dict('load', 'loc_browser'))
	username = str(SETTINGS.getSetting('username'))	# ev. None (Plex)
	password = str(SETTINGS.getSetting('passwort'))
	username = username.strip()						# Blanks verhindern
	password = password.strip()						
			
	headers = {'Accept-Language': "%s, en;q=0.8" % loc_browser}
	
	if not SETTINGS.getSetting('username')  or not SETTINGS.getSetting('passwort'):
		msg1 = L('Username und Passwort sind fuer diese Aktion erforderlich')
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return

	# Query prüft, ob der Tunein-Account bereits mit der serial-ID verknüpft ist, Rückgabe username falls OK 
	#	verknüpfte Geräte: https://tunein.com/devices/
	query_url = 'https://opml.radiotime.com/Account.ashx?c=query&partnerId=%s&serial=%s' % (partnerId,serial)
	# PLog(query_url)
	page, msg = RequestTunein(FunctionName='Favourit - association-test', url=query_url)	# 1. Query
	if page == '':							# Netzwerk-Problem
		msg1 = msg
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')							
		return	

	PLog('Fav-Query: ' + page[:10])				 
	tname  = stringextract('text="', '"', page)	# Bsp. <outline type="text" text="testuser"/>
	is_joined = False
	if tname == SETTINGS.getSetting('username'):				
		is_joined = True						# Verknüpfung bereits erfolgt
	if "<fault>" in page:						# trotzdem weiter, Call zur Verknüpfung folgt
		fault =  stringextract('<fault>', '</fault>', page) # Bsp. "No associated account"
		PLog(fault)
		
	PLog('is_joined: ' + str(is_joined))	
	if is_joined == False:
		# Join verknüpft Account mit serial-ID. Vorhandene Presets werden eingebunden
		# 	Ersetzung: partnerId, username, password, serial
		join_url = ('https://opml.radiotime.com/Account.ashx?c=join&partnerId=%s&username=%s&password=%s&serial=%s' 
					% (partnerId,username,password,serial))

		page, msg = RequestTunein(FunctionName='Favourit - join', url=join_url)				# 2. Join (is_joined=False)
		if page == '':	
			msg1 = msg
			PLog(msg1)
			PLog('Join-Call fehlgeschlagen')
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			# return
									
		# PLog('Fav-Join: ' + page)	# bei Bedarf
		
		status  = stringextract('<status>', '</status>', page)
		PLog(status)
		if '200' not in status:								# 
			title  = stringextract('<title>', '</title>', page)
			if title == '':
				title  = 'status ' + status
			msg = L('Problem mit Username / Passwort') 
			msg1 = msg
			PLog(msg1)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			return
			
	# Favoriten hinzufügen/Löschen - ID steuert ('add', 'remove', moveto)
	#		 Custom  Url nur einfügen - danach Behandlung als Favorit 
	#	Angabe des Ordners (folderId) nur für  moveto erf. 
	# 	Ersetzung bei 'moveto': ID,favoriteId,folderId,serial,partnerId
	# 	Ersetzung bei 'add', 'remove': ID,preset_id,serial,partnerId
	#	Sonderbehandlung bei Custom  Url: url=preset_id=customUrl , name=folderId=customName -
	#		urllib.quote(folderId) für Leer- u.a. Zeichen in name
	
	if ID == 'addcustom':						# Custom  Url einfügen
		folderId = urllib.quote(folderId)
		fav_url = ('https://opml.radiotime.com/Preset.ashx?render=xml&c=add&name=%s&url=%s&render=xml&formats=%s&serial=%s&partnerId=%s'
				% (folderId, preset_id, Dict('load', 'formats'), serial, partnerId))	

	if ID == 'moveto':
		folderId 	= folderId.split('f')[1]	# führendes 'f' entfernen, preset_number immer numerisch
		favoriteId 	= SearchInProfile(ID='favoriteId', preset_id=preset_id) # Wert ist bereits numerisch
		if favoriteId == '':					# 'Wahrscheinlichkeit gering			
			msg1 = L('verschieben') + ' ' + L('fehlgeschlagen')
			PLog(msg1)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			return 
		ID = 'move'		# Korrektur
		fav_url = ('https://opml.radiotime.com/favorites.ashx?render=xml&c=%s&favoriteId=%s&folderId=%s&formats=%s&serial=%s&partnerId=%s'
				% (ID, favoriteId, folderId, Dict('load', 'formats'), serial, partnerId))
				
	if ID == 'add' or ID == 'remove':
		fav_url = ('https://opml.radiotime.com/favorites.ashx?render=xml&c=%s&id=%s&formats=%s&serial=%s&partnerId=%s' 
				% (ID, preset_id, Dict('load', 'formats'), serial, partnerId))

	page, msg = RequestTunein(FunctionName="Favourit - ID=%s" % ID, url=fav_url)		# 3. Add / Remove
	if page == '':	
		msg1 = msg
		PLog(msg1)
		PLog('%s - Render-Call fehlgeschlagen' % ID)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return 
	# PLog('Fav add/remove: ' + page)
	
	status  = stringextract('<status>', '</status>', page)				# Ergebnisausgabe
	if '200' != status:	
		title  = stringextract('<title>', '</title>', page)
		if title == '':
			title  = 'status ' + status
		msg1 = L('fehlgeschlagen') + ' | Tunein: ' + title			
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return 
	else:
		if ID == 'add':											# 'add'
			msg1 = L("Favorit") + ' ' + L("hinzugefuegt")
		if ID == 'addcustom':									# 'addcustom'
			msg1 = L("Custom Url") + ' ' + L("hinzugefuegt")
		elif  ID == 'remove':	 								# 'remove'
			msg1 = L("Favorit") + ' ' + L("entfernt")	
		elif  ID == 'move':	 									# 'move'
			msg1 = L("Favorit") + ' ' + L("verschoben")
				
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')

#-----------------------------
# Direktaufruf von GetContent (mit li) oder rekursiv (ohne li), falls 
# 	get_details als typ=link ermittelt
# 
# ID = folderId, url mit serial-id vorbelegt	
def FolderMenuList(url, title, li=''):	
	PLog('FolderMenuList:')
	
	if li == '':								# eigene Liste
		endOfDirectory = True 
		li = xbmcgui.ListItem()
		li = home(li)							# Home
	else:
		endOfDirectory = False					# Aufrufer-Liste
	
	page, msg = RequestTunein(FunctionName='FolderMenu: Liste laden', url=url)	
	if page == '':
		msg1 = msg
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li
	PLog(len(page))
	PLog(page[:100])
	
	title	= stringextract('<title>', '</title>', page)
	title = unescape(title)
	title = title.decode(encoding="utf-8")

	items = blockextract('outline type', page)
	PLog(len(items))
	for item in items:
		# PLog('item: ' + item)	
		typ,local_url,text,image,key,subtext,bitrate,preset_id,guide_id,playing,is_preset = get_details(line=item)	
		PLog('Satz_FolderMenuList:')		
		PLog('%s | %s | %s |%s | %s' % (typ,text,subtext,playing,bitrate))
		PLog('%s | %s | %s |%s' % (preset_id,guide_id,local_url,image))

		text=UtfToStr(text); subtext = UtfToStr(subtext); local_url=UtfToStr(local_url);
		bitrate=UtfToStr(bitrate); preset_id=UtfToStr(preset_id);
		playing=UtfToStr(playing);
		subtext=repl_json_chars(subtext); text=repl_json_chars(text); 
		
		if preset_id.startswith('u'):				# Custom-Url -> Station
			typ = 'audio'
				
		if typ == 'link':							# Ordner
			image = R(ICON)	
			fparams="&fparams={'url': '%s', 'title': '%s'}"  %\
				(urllib2.quote(local_url), urllib2.quote(text))
			addDir(li=li, label=text, action="dirList", dirID="FolderMenuList", 
				fanart=image, thumb=image, fparams=fparams)
			
		if typ == 'audio':							# Station
			 						
			fparams="&fparams={'url': '%s', 'title': '%s', 'summ': '%s', 'image': '%s', 'typ': 'Station', 'bitrate': '%s', 'preset_id': '%s'}"  %\
				(urllib2.quote(local_url), urllib2.quote(text), urllib2.quote(subtext), urllib2.quote(image),
				bitrate, preset_id)
			addDir(li=li, label=text, action="dirList", dirID="StationList", 
				fanart=image, thumb=image, summary=subtext, tagline=playing, fparams=fparams)			
						
	if endOfDirectory == True:
		xbmcplugin.endOfDirectory(HANDLE)
	else:
		return li	
#-----------------------------
# Ordner hinzufügen/löschen
#	ID steuert: 'addFolder' / 'removeFolder' 
def Folder(ID, title, foldername, folderId):
	PLog('Folder:')
	PLog(ID); PLog(title); PLog(foldername); PLog(folderId);
	serial = Dict('load', 'serial')
	foldername = UtfToStr(foldername); 
		
	loc_browser = str(Dict('load', 'loc_browser'))			
	headers = {'Accept-Language': "%s, en;q=0.8" % loc_browser}
	
	if foldername == 'None' or foldername == '':
		msg1 = L('Ordnername fehlt') 
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return
	
	if foldername == 'General':
		msg1 = L('Ordner kann nicht entfernt werden')
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return
	
	# 	Ersetzung: c=ID, name=foldername, serial=serial, partnerId=partnerId
	#	
	if ID == 'addFolder':
		folder_url = ('https://opml.radiotime.com/favorites.ashx?render=xml&c=%s&name=%s&formats=%s&serial=%s&partnerId=%s' 
					% (ID,urllib2.quote(foldername), Dict('load', 'formats'), serial, partnerId))	
	else:
		# bei 'removeFolder' wird name=foldername ersetzt durch folderId=folderId 
		#
		folderId = folderId.split('f')[1]	# führendes 'f' entfernen
		folder_url = ('https://opml.radiotime.com/favorites.ashx?render=xml&c=%s&folderId=%s&formats=%s&serial=%s&partnerId=%s' 
					% (ID, folderId, Dict('load', 'formats'), serial, partnerId))	
						
	page, msg = RequestTunein(FunctionName='Folder: %s' % ID, url=folder_url)
	if page == '':
		msg1 = msg
		PLog(msg1)
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return
	# PLog('Fav-Join: ' + page)

	status  = stringextract('<status>', '</status>', page)				# Ergebnisausgabe
	if '200' != status:	
		title  = stringextract('<title>', '</title>', page)
		msg1 = L('fehlgeschlagen') + ' | Tunein: ' + title			
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
	else:
		if ID == 'addFolder':							# 'add'
			msg1 = L("Ordner") + ' ' + L("hinzugefuegt")
		else:											# 'remove'
			msg1 = L("Ordner") + ' ' + L("entfernt")	
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')

	my_title = u'%s' % L('Meine Favoriten')								# -> Menü Favoriten
	my_url = Dict('load','my_url')
	PLog("my_url: " + my_url)
	GetContent( url=my_url, title=my_title, offset=0)

	return
#-----------------------------
# Ordner auflisten - ID steuert Kennzeichnung:
#	ID='removeFolder' -> Ordner entfernen (Löschbutton in GetContent)
#	ID='moveto' -> Favorit in Ordner verschieben (UseFavourites in StationList)
#	preset_id nur für moveto erforderlich (Kennz. für Favoriten)
#
def FolderMenu(title, ID, preset_id, checkFiles=None):	
	PLog('FolderMenu:')
	PLog('ID: ' + ID)
	preset_id = UtfToStr(preset_id)
	serial = Dict('load', 'serial')
	
	li = xbmcgui.ListItem()
	li = home(li)							# Home-Button	
	
	preset_url = 'http://opml.radiotime.com/Browse.ashx?c=presets&partnerId=RadioTime&serial=%s' % serial
	page, msg = RequestTunein(FunctionName='FolderMenu: ID %s, Liste laden' % ID, url=preset_url)	
	if page == '':
		msg1 = msg
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li
				
	rubriken = blockextract('<outline type="link"', page)		# Ordner-Übersicht
	PLog(len(rubriken))	
	if len(rubriken) > 1:										# 1. Ordner (General) ohne Ordner-Urls
		for rubrik in rubriken:
				foldername 	= stringextract('text="', '"', rubrik)		# 1. Ordner immer General
				folderId 	= stringextract('guide_id="', '"', rubrik)	# Bsp. "f3"
				furl 		=  stringextract('URL="', '"', rubrik)
				furl		= unescape(furl)							# wie in SearchInFolders
				page, msg = RequestTunein(FunctionName='FolderMenu: %s, Inhalt laden' % foldername, url=furl)	
				items_cnt =  len(blockextract('URL=', page))		# outline unscharf
				PLog(items_cnt)
				
				if ID == 'removeFolder':	# -> Ordner entfernen
					title = foldername + ': ' + L('Ordner entfernen') + ' | ' + L('ohne Rueckfrage!')
					summ = L('Anzahl der Eintraege') + ': ' + str(items_cnt)
					thumb = R(ICON_FOLDER_REMOVE)
					if foldername == 'General':
						title = foldername + ': ' + L('Ordner kann nicht entfernt werden')
						thumb = R(ICON_FOLDER_ADD)	
					fparams="&fparams={'ID': 'removeFolder', 'title': '%s', 'foldername': '%s', 'folderId': '%s'}"  %\
						(urllib2.quote(title), urllib2.quote(foldername), folderId)
					addDir(li=li, label=title, action="dirList", dirID="Folder", 
						fanart=thumb, thumb=thumb, summary=summ, fparams=fparams)						
					
				else:	         			# 'moveto' -> Favorit in Ordner verschieben, preset_id=preset_number	
					if 	preset_id in page:	# Fav enthalten - Ordner nicht listen	
						pass
					else:
						title = foldername + ': ' + L('hierhin verschieben') 
						summ = L('Anzahl der Eintraege') + ': ' + str(items_cnt)
						thumb = R(ICON_FAV_MOVE)
						fparams="&fparams={'ID': 'moveto', 'preset_id': '%s', 'folderId': '%s'}"  %\
							(urllib2.quote(preset_id), urllib2.quote(folderId))
						addDir(li=li, label=title, action="dirList", dirID="Favourit", 
							fanart=thumb, thumb=thumb, summary=summ, fparams=fparams)						

			
	xbmcplugin.endOfDirectory(HANDLE)

####################################################################################################
#							   Funktionen für Meine Radiostationen
####################################################################################################
# ListMRS lädt eigene Datei "Meine Radiostationen" + listet die enthaltenen Stationen mit
#	Name + Url. Der Button führt zu SingleMRS (trackobject nach Auswertung in StreamTests).
#	path = lokale Textdatei
#	Test  os.path.exists  bereits in Main erfolgt.
# 
def ListMRS(path):										
	PLog('ListMRS:'); PLog(path) 
	title = L("Meine Radiostationen")
	
	li = xbmcgui.ListItem()
	li = home(li)						# Home-Button
	
	try:
		content = RLoad(path, abs_path=True)
	except:
		content = ''
		
	if content == '' or content == None:
		msg1 = L("nicht gefunden") + ': '
		msg2 = path
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')

	max_streams=0										# Limit default
	lines = content.splitlines()
	i=0
	for line in lines:
		i=i+1
		line = line.strip()
		if line.startswith('#') or line == '':			# skip comments
			continue
		try:
			if '#' in line:
				line = line.split('#')[0]				# Kommentar Zeilenende
			name,url = line.split('|')
			name = name.strip(); url = url.strip() 
			name =  name.decode('utf-8')
		except:
			name=''; url=''
		
		name = UtfToStr(name)
		PLog(name); PLog(url); 
		
		if name=='' and url=='':
			msg1 = L("fehlerhafte Datei")
			msg2 = path
			msg3 = 'in line %s' % str(i)
			PLog(msg1); PLog(msg2);  PLog(msg3);
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		
		thumb = R(ICON_MYRADIO)
		fparams="&fparams={'url': '%s', 'name': '%s', 'max_streams': '%s', 'image': '%s'}"  %\
			(urllib2.quote(url), urllib2.quote(name), max_streams, urllib2.quote(thumb))
		addDir(li=li, label=name, action="dirList", dirID="SingleMRS", 
			fanart=thumb, thumb=thumb, summary=url, fparams=fparams)			
	
	xbmcplugin.endOfDirectory(HANDLE)
#----------------------------------------------------------------
#	Einzelstation zu ListMRS - Meta-Auswertung hier - Timeout möglich in ListMRS (Plex). 
#	sid='0' für audience-opml-Call in PlayAudio_pre: Einzelstationen ev. tunein-inkompatibel
#
def SingleMRS(name, url, max_streams, image):										
	PLog('SingleMRS:'); PLog(url) 
	
	# Callback-Params für PlayAudio -z.Z. nicht genutzt (Rekursion bei gestörten Streams
	#	beobachtet)
	name=UtfToStr(name);
	fparams="{'name': '%s', 'url': '%s',  'max_streams': '%s', 'image': '%s'}"  %\
				(urllib2.quote(name), urllib2.quote(url), max_streams, urllib2.quote(image))
	Dict('store', 'Args_SingleMRS', fparams)				

	li = xbmcgui.ListItem()
	li = home(li)						# Home-Button
	
	if url.startswith('http') == False: 
		msg1 =  L('Custom Url muss mit http beginnen') 
		msg2 = url
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li
							
	if 'Tune.ashx?' in url:						# TuneIn-Link ebenfalls ermöglichen, Inhalt laden
		try:
			url_list, msg = RequestTunein(FunctionName='SingleMRS', url=url)
		except Exception as exception:			
			url_list = ''
		if url_list == '' or 'error' in url_list:
			msg1 = 'My Radiostations - url error:' 
			msg2 = url
			PLog(msg1); PLog(msg2)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
			return li
			
		PLog(url_list)	
		url_list = get_pls(url_list)		
	else:
		url_list = get_pls(url)				# Streamlinks extrahieren, ev. mit Zertifikat
		
	PLog(url_list); 
	if url_list == '':
		msg1 = L('keinen Stream gefunden zu') 
		msg2 = name
		msg3 = url
		PLog(msg1); PLog(msg3); 
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
		return li
		
	if url_list.startswith('get_pls-error'): 					# z.B: Redirection to url ..  is not allowed, einschl.
		msg1 = url_list.decode(encoding="utf-8")				# itunes-Url not supported by this plugin	
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return li
	
	url_list, err_flag =  StreamTests(url_list,summ_org='')
	if len(url_list) == 0:
		if err_flag == True:					# detaillierte Fehlerausgabe vorziehen, aber nur bei leerer Liste
			msg1 = L('keinen Stream gefunden zu') 
			msg2 = name
			msg3 = url
			PLog(msg1); PLog(msg3); 
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, msg3)
			return li
	
	i=1;
	for line in url_list:
		PLog(line)
		url   = line.split('|||')[0]
		server = url[:80] + '...'
		try:
			summ  = line.split('|||')[1]
		except:
			summ = url
		summ  = '%s | %s' % (summ, server)
		summ = summ.decode('utf-8')		# ev. für song erforderlich
		if summ.strip().startswith('|'):
			summ = summ[3:]
		
		fmt='mp3'								# Format nicht immer  sichtbar - Bsp. http://addrad.io/4WRMHX. Ermittlung
		if 'aac' in url:						#	 in getStreamMeta (contenttype) hier bisher nicht genutzt
			fmt='aac'
		if url.endswith('.asf') or '=asf' in url: # Achtung: www.asfradio.com
			fmt='asf'
		if url.endswith('.ogg') : 				# .ogg in http://mp3.radiox.ch:8000/standard.ogg.m3u
			fmt='ogg'
		title = name + ' | Stream %s | %s'  % (str(i), fmt)
		i=i+1

		Plot = summ
		url=UtfToStr(url); Plot=UtfToStr(Plot); title=UtfToStr(title); image=UtfToStr(image);
		summ=UtfToStr(summ);
		
		PLog('Satz:')
		PLog(url)
		# z.Z. ohne Callback (s.o.)
		fparams="&fparams={'url': '%s', 'title': '%s', 'thumb': '%s', 'Plot': '%s', 'CB': ''}" %\
			(urllib.quote_plus(url), urllib.quote_plus(title), urllib.quote_plus(image), urllib.quote_plus(Plot))
		addDir(li=li, label=title, action="dirList", dirID="PlayAudio_pre", fanart=image, thumb=image, fparams=fparams, 
			summary=summ)
	
	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=True)	

####################################################################################################
#									Recording-Funktionen
####################################################################################################
# 
def RecordStart(url,title,title_org,image,summ,typ,bitrate, CB=''):		# Aufnahme Start 
	PLog('RecordStart')
	PLog(sys.platform)
	
	p_prot, p_path = url.split('//')	# Url-Korrektur für streamripper bei Doppelpunkten in Url (aber nicht mit Port) 
	PLog(p_path)							#	s. https://sourceforge.net/p/streamripper/discussion/19083/thread/300b7a0f/
										#	dagegen wird ; akzeptiert, Bsp. ..tunein;skey..
	p_path = (p_path.replace('id:', 'id%23').replace('secret:', 'secret%23').replace('key:', 'key%23'))	# ev.  ergänzen
	url_clean = '%s//%s'	% (p_prot, p_path)
	
	AppPath	= SETTINGS.getSetting('StreamripperPath')
	PLog('AppPath: ' + AppPath)	 
	AppExist = False
	if AppPath:										# Test: PRG existent?
		PLog(os.path.exists(AppPath))
		if 'linux' in sys.platform:					# linux2, weitere linuxe?							
			if os.path.exists(AppPath):				
				AppExist = True
		else:										# für andere, spez. Windows kein Test (os.stat kann fehlschlagen)
			AppExist = True		
	else:
		AppExist = False
	if AppExist == False:
		msg1 = 'Streamripper' + ' ' + L("nicht gefunden")
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		return 		
	
	DestDir = SETTINGS.getSetting('DownloadDir')	# bei leerem Verz. speichert Streamripper ins Heimatverz.
	PLog('DestDir: ' + DestDir)	 
	if DestDir:
		DestDir = DestDir.strip()
		if os.path.exists(DestDir) == False:
			msg1 = L('Download-Verzeichnis') + ' ' + L("nicht gefunden")
			PLog(msg1)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			return 		
					
	# cmd-Bsp.: streamripper http://addrad.io/4WRMHX --quiet -d /tmp -u Mozilla/5.0
	#	30.05.2018 UserAgent hinzugefügt (Error: Access Forbidden (try changing the UserAgent)) -
	#	einige Sender verweigern den Download beim Default Streamripper/1.x
	#	Konfig-Alternative:  /var/lib/plexmediaserver/.config/streamripper/streamripper.ini	
	#	MP3-Problem: streamripper speichert .mp3 im incomplet-Verz. und geht in Endlosschleife -
	#		Versuch mit Titel -> Dateiname plus Timestamp abgebrochen (Endlosschleife bleibt,
	#		streamripper verwendet weiter unterschiedl. Verz., abhängig  von Url) - Code
	#		s. __init__.py_v1.2.5_mp3-download
	UserAgent = "Mozilla/5.0"
	cmd = "%s %s --quiet -d %s -u %s"	% (AppPath, url_clean, DestDir, UserAgent)		
	PLog('cmd: ' + cmd)
				
	PLog(sys.platform)
	if sys.platform == 'win32':							
		args = cmd
	else:
		args = shlex.split(cmd)							# ValueError: No closing quotation (1 x, Ursache n.b.)
	PLog(len(args))
	PLog(args)

	PID_lines = Dict('load', 'PID')
	PLog(PID_lines)
	if PID_lines:
		for PID_line in PID_lines:							# Prüfung auf exist. Aufnahme
			PLog(PID_line)									# Aufbau: Pid|Url|Sender|Info
			pid_url = PID_line.split('|')[1]
			if pid_url == url:	
				pid = PID_line.split('|')[0]		
				summ = PID_line.split('|')[3]	
				title_new = title_org + ': ' + L('Aufnahme') +  ' ' + L('gestartet')
				msg1 =  '%s:\n%s | %s | PID: %s' % (title_new, title_org, url, pid)	
				PLog(OS_DETECT)	
				PLog('Test existing Record: ' + msg1)
				PLog(msg1)
				xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
				return 		

	# Popen-Objekt mit Pid außerhalb nicht mehr ansprechbar (call.pid). Daher speichern wir im Dict die Prozess-ID direkt.
	# PHT-Problem (Linux + Windows): return ObjectContainer nach Dict['PID'].append führt PHT direkt wieder hierher 
	# 	(vor append OK) - Problem der Stackverwaltung im Framwork? Den erneuten Durchlauf von PHT fangen wir oben in 
	#	Prüfung auf exist. Aufnahme ab.
	# PHT-Problem  in Kodi nicht existent
	call=''
	try:
		PLog(OS_DETECT)	
		call = subprocess.Popen(args, shell=False)		# shell=False erfordert shlex-Nutzung	
		# output,error = call.communicate()				# klemmt hier (anders als im ARD-Plugin)
		PLog('call: ' + str(call))						# Bsp. <subprocess.Popen object at 0x7f16fad2e290>
		if str(call).find('object at') > 0:  			# subprocess.Popen object OK
			PID_line = '%s|%s|%s|%s'	% (call.pid, url, title_org, summ) 	# Muster: 																
			PLog(PID_line)	
			PID = Dict('load', 'PID')					# [] vorbelegt in Main
			PID.append(PID_line)						# 
			PLog(PID)
			Dict('store', 'PID', PID)
			title_new = L('Aufnahme') + ' ' + L('gestartet')
			msg1 =  '%s: \n %s | %s | PID: %s' % (title_new, title_org, url, call.pid)
			PLog(msg1)
			xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
			return 		
							
	except Exception as exception:
		msg1 = L('Aufnahme fehlgeschlagen')
		msg2 = str(exception)
		PLog(msg1); PLog(msg2)		
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return 		
		
	msg1 = L('Aufnahme') + ' ' + L('fehlgeschlagen') + '\n' + L('Ursache unbekannt')
	PLog(msg1)	
	xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
#	return 		
	 	
#-----------------------------
def RecordStop(url,title,summ, CB=''):					# Aufnahme Stop
	PLog('RecordStop:')
	
	pid = ''
	PID_lines = Dict('load', 'PID')
	PLog(PID_lines)
	for PID_line in PID_lines:							# Prüfung auf exist. Aufnahme
		PLog(PID_line)									# Format: call|url|title_org|summ
		pid_url = PID_line.split('|')[1]
		if pid_url == url:
			pid = PID_line.split('|')[0]
			PLog(pid)
			break
			
	if pid == '' or int(pid) == 0:
		msg1 = url + ': ' + L('keine laufende Aufnahme gefunden')
		PLog(msg1)
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, '', '')
		# if CB:	Callback(CB)		# nicht genutzt
		return			
			
	# Problem kill unter Linux: da wir hier Popen aus Sicherheitsgründen ohne shell ausführen, hinterlässt kill 
	#	einen Zombie. Dies ist aber zu vernachlässigen, da aktuelle Distr. Zombies nach wenigen Sekunden autom.
	#	entfernen. 
	#	Auch call.terminate() in einem Thread (Thread StreamripperStop wieder entfernt) hinterlässt Zombies.
	#	Alternative (für das Plugin Overkill) wäre die Verwendung von psutil (https://github.com/giampaolo/psutil) 
	pid = int(pid)
	try:
		os.kill(pid, signal.SIGTERM)	# Verzicht auf running-Abfrage os.kill(pid, 0)
		time.sleep(1)
		if 'linux' in sys.platform:		# Windows: 	object has no attribute 'SIGKILL'						
			os.kill(pid, signal.SIGKILL)	
		pidExist = True
	except OSError as err:
		pidExist = False
		error='Error: ' + str(err)
		PLog(error)
						
	if pidExist == False:
		msg1 = str(err) 
		msg2 =  '%s:\n%s | %s | PID: %s' % (title, url, pid)	
	else:
		msg1 = L('Aufnahme') + ' ' + L('beendet')
		msg2 =  '%s | %s | PID: %s' % (title, url, pid)
			
	PID_lines.remove(PID_line)		# Eintrag Prozessliste entfernen - unabhängig vom Erfolg
	PLog(PID_lines)
	Dict('store', 'PID', PID_lines)	
	xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
	return 		
					
#-----------------------------
# Liste laufender Aufnahmen mit Stop-Button - Prozess wird nicht geprüft!
def RecordsList(title):			# title=L("laufende Aufnahmen")
	PLog('RecordsList')
	li = xbmcgui.ListItem()
	li = home(li)						# Home-Button
	
	# Callback-Params für RecordStop
	title=UtfToStr(title); 
	fparams="{'title': '%s'}"  % (urllib2.quote(title))
	Dict('store', 'Args_RecordsList', fparams)				
	
	
	PID_lines = Dict('load', 'PID')	
	for PID_line in PID_lines:							# Prüfung auf exist. Aufnahme
		PLog(PID_line)									# Aufbau: Pid|Url|Sender|Info
		pid 	= PID_line.split('|')[0]
		pid_url = PID_line.split('|')[1]
		pid_sender = PID_line.split('|')[2]
		pid_summ = PID_line.split('|')[3]
		title_new = L('beenden') + ': ' + pid_sender 
		if not 'unknown' in pid_summ:
			title_new = title_new + ' | ' + pid_summ
		summ_new = pid_url + ' | ' + 'PID: ' + pid	
				
		pid_sender = UtfToStr(pid_sender); pid_summ = UtfToStr(pid_summ);  		
		fparams="&fparams={'url': '%s', 'title': '%s', 'summ': '%s', 'CB': 'RecordsList'}" %\
			(urllib.quote_plus(pid_url), urllib.quote_plus(pid_sender),  urllib.quote_plus(pid_summ))
		addDir(li=li, label=title_new, action="dirList", dirID="RecordStop", fanart=R(ICON_STOP), thumb=R(ICON_STOP), 
			fparams=fparams, summary=summ_new)
	
	xbmcplugin.endOfDirectory(HANDLE)

####################################################################################################
#								Hilfsfunktionen - weitere in Modul util
####################################################################################################

def SearchUpdate(title):		
	PLog('SearchUpdate:')
	li = xbmcgui.ListItem()

	ret = updater.update_available(VERSION)	
	#PLog(ret)
	if ret[0] == False:		
		msg1 = L("Github ist nicht errreichbar")
		msg2 = 'update_available: False'
		PLog("%s | %s" % (msg1, msg2))
		xbmcgui.Dialog().ok(ADDON_NAME, msg1, msg2, '')
		return li			

	int_lv = ret[0]			# Version Github
	int_lc = ret[1]			# Version aktuell
	latest_version = ret[2]	# Version Github, Format 1.4.1
	summ = ret[3]			# Changes
	tag = ret[4]			# tag, Bsp. 029
	
	# Bsp.: https://github.com/rols1/Kodi-Addon-ARDundZDF/releases/download/0.5.4/Kodi-Addon-ARDundZDF.zip
	url = 'https://github.com/{0}/releases/download/{1}/{2}.zip'.format(GITHUB_REPOSITORY, latest_version, REPO_NAME)

	PLog(int_lv); PLog(int_lc); PLog(latest_version); PLog(summ);  PLog(url);
	
	if int_lv > int_lc:		# zum Testen drehen (akt. Addon vorher sichern!)			
		title = L('neues Update vorhanden') +  ' - ' + L('jetzt installieren')
		summary = L('Plugin Version:') + " " + VERSION + ', Github Version: ' + latest_version
		tagline = cleanhtml(summ)
		thumb = R(ICON_UPDATER_NEW)
		fparams="&fparams={'url': '%s', 'ver': '%s'}" % (urllib.quote_plus(url), latest_version) 
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", 
			fanart=R(ICON_UPDATER_NEW), thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary, 
			tagline=cleanhtml(summ))
			
		title = L('Update abbrechen')
		summary = L('weiter im aktuellen Plugin')
		thumb = R(ICON_UPDATER_NEW)
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="Main", fanart=R(ICON_UPDATER_NEW), 
			thumb=R(ICON_UPDATER_NEW), fparams=fparams, summary=summary)
	else:	
		title = L('Plugin aktuell') + " | Home"
		summary = 'Plugin Version ' + VERSION + ' ' + L('ist die neueste Version')
		summ = summ.splitlines()[0]		# nur 1. Zeile changelog
		tagline = tag
		thumb = R(ICON_OK)
		fparams="&fparams={}"
		addDir(li=li, label=title, action="dirList", dirID="Main", fanart=R(ICON_OK), 
			thumb=R(ICON_OK), fparams=fparams, summary=summary, tagline=tagline)

	xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)
#-----------------------------
def presentUpdate(li,start):
	PLog('presentUpdate:' + start)
	ret = resources.lib.updater.update_available(VERSION)		# bei Github-Ausfall 3 x None
	PLog(ret)
	int_lv = ret[0]			# Version Github
	int_lc = ret[1]			# Version aktuell
	latest_version = ret[2]	# Version Github, Format 1.4.1

	if ret[0] == None or ret[0] == False:
		return li, 'no_connect'
		
	zip_url = ret[5]	# erst hier referenzieren, bei Github-Ausfall None
	url = zip_url
	summ = ret[3]		# History, replace ### + \r\n in get_latest_version, summ -> summary, 
	tag = summ.decode(encoding="utf-8")  			# History -> tag
	PLog(latest_version); PLog(int_lv); PLog(int_lc); PLog(tag); PLog(zip_url); 
	
	if int_lv > int_lc:								# 2 Update-Button: "installieren" + "abbrechen"
		available = 'true'
		title = L('neues Update vorhanden') +  ' - ' + L('jetzt installieren')
		summary = L('Plugin Version:') + " " + VERSION + ', Github Version: ' + latest_version
		fparams="&fparams={'url': '%s', 'ver': '%s'}"  % (urllib2.quote(url), latest_version)
		addDir(li=li, label=title, action="dirList", dirID="resources.lib.updater.update", 
			fanart=R(ICON_UPDATER_NEW), thumb=R(ICON_UPDATER_NEW), summary=summary, tagline=tag, fparams=fparams)					
			
		if start == 'false':						# Option Abbrechen nicht beim Start zeigen
			fparams="&fparams={}" 
			addDir(li=li, label=title, action="dirList", dirID="Main", 
				fanart=R(ICON_UPDATER_NEW), thumb=R(ICON_UPDATER_NEW), summary=summary, fparams=fparams)					
				
	else:											# Plugin aktuell -> Main
		available = 'false'
		if start == 'false':						# beim Start unterdrücken
			fparams="&fparams={}" 
			addDir(li=li, label=title, action="dirList", dirID="Main", 
				fanart=R(ICON_OK), thumb=R(ICON_OK), summary=summary,  tagline=tagline, fparams=fparams)					

	return li,available

####################################################################################################
#									Streamtest-Funktionen
####################################################################################################
# getStreamMeta ist Teil von streamscrobbler-python (https://github.com/dirble/streamscrobbler-python),
#	angepasst für dieses Plugin (Wandlung Objekte -> Funktionen, Prüfung Portnummer, Rückgabe Error-Wert).
#	Originalfunktiom: getAllData(self, address).
#	
#	getStreamMeta wertet die Header der Stream-Typen und -Services Shoutcast, Icecast / Radionomy, 
#		Streammachine, tunein aus und ermittelt die Metadaten.
#		Zusätzlich wird die Url auf eine angehängte Portnummer geprüft.
# 	Rückgabe 	Bsp. 1. {'status': 1, 'hasPortNumber': 'false', 'shoutcast': 'false', 'metadata': false, error': error}
#				Bsp. 2.	{'status': 1, 'hasPortNumber': 'true',  'shoutcast': 'true', 'error': error, 
#						'metadata': {'contenttype': 'audio/mpeg', 'bitrate': '64', 
#						'song': 'Nasty Habits 41 - Senza Filtro 2017'}}
#		
def getStreamMeta(address):
	PLog('getStreamMeta: ' + address)
	# import httplib2 as http	# hier nicht genutzt
	# import pprint				# hier nicht genutzt
	# import re					# bereits geladen
	# import urllib2			# bereits geladen
	# from urlparse import urlparse # bereits geladen
				
	shoutcast = False
	status = 0

	# Test auf angehängte Portnummer = zusätzl. Indikator für Stream, Anhängen von ; in StationList
	#	aber nur, wenn Link direkt mit Portnummer oder Portnummer + / endet, Bsp. http://rs1.radiostreamer.com:8020/
	hasPortNumber='false'
	p = urlparse(address)
	if p.port and p.path == '':	
		hasPortNumber='true'		
	if p.port and p.path:
		if address.endswith('/'):		# als path nur / erlaubt
			hasPortNumber='true'
	PLog('hasPortNumber: ' + hasPortNumber)	
	
	request = urllib2.Request(address)
	user_agent = 'iTunes/9.1.1'
	request.add_header('User-Agent', user_agent)
	request.add_header('icy-metadata', 1)
	gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1) 	# 08.10.2017 SSLContext für https://hr-youfm-live.sslcast.addradio.de
	gcontext.check_hostname = False
	gcontext.verify_mode = ssl.CERT_NONE
	
	try:
		response = urllib2.urlopen(request, context=gcontext, timeout=UrlopenTimeout)	
		headers = getHeaders(response)
		# PLog(headers)
				   
		if "server" in headers:
			shoutcast = headers['server']
		elif "X-Powered-By" in headers:
			shoutcast = headers['X-Powered-By']
		elif "icy-notice1" in headers:
			shoutcast = headers['icy-notice2']
		else:
			shoutcast = bool(1)

		if isinstance(shoutcast, bool):
			if shoutcast is True:
				status = 1
			else:
				status = 0
			metadata = False;
		elif "SHOUTcast" in shoutcast:
			status = 1
			metadata = shoutcastCheck(response, headers, False)
		elif "Icecast" or "137" in shoutcast:
			status = 1
			metadata = shoutcastCheck(response, headers, True)
		elif "StreamMachine" in shoutcast:
			status = 1
			metadata = shoutcastCheck(response, headers, True)
		elif shoutcast is not None:
			status = 1
			metadata = shoutcastCheck(response, headers, True)
		else:
			metadata = False
		response.close()
		error=''
		return {"status": status, "metadata": metadata, "hasPortNumber": hasPortNumber, "shoutcast": shoutcast, "error": error}

	except urllib2.HTTPError as e:	
		error='Error, HTTP-Error = ' + str(e.code)
		PLog(error)
		return {"status": status, "metadata": None, "hasPortNumber": hasPortNumber, "shoutcast": shoutcast, "error": error}

	except urllib2.URLError as e:						# Bsp. RANA FM 88.5 http://216.221.73.213:8000
		error='Error, URL-Error: ' + str(e.reason)
		PLog(error)
		return {"status": status, "metadata": None, "hasPortNumber": hasPortNumber, "shoutcast": shoutcast, "error": error}

	except Exception as err:
		error='Error: ' + str(err)
		PLog(error)
		return {"status": status, "metadata": None, "hasPortNumber": hasPortNumber, "shoutcast": shoutcast, "error": error}
#----------------------------------------------------------------  
#	Hilfsfunktionen für getStreamMeta
#----------------------------------------------------------------  
def parse_headers(response):
	headers = {}
	int = 0
	while True:
		line = response.readline()
		if line == '\r\n':
			break  # end of headers
		if ':' in line:
			key, value = line.split(':', 1)
			headers[key] = value.rstrip()
		if int == 12:
			break;
		int = int + 1
	return headers
#---------------------------------------------------
def getHeaders(response):
	if is_empty(response.headers.dict) is False:
		headers = response.headers.dict
	elif hasattr(response.info(),"item") and is_empty(response.info().item()) is False:
		headers = response.info().item()
	else:
		headers = parse_headers(response)
	return headers
#---------------------------------------------------
def is_empty(any_structure):
	if any_structure:
		return False
	else:
		return True       
#----------------------------------------------------------------  
def stripTags(text):
	finished = 0
	while not finished:
		finished = 1
		start = text.find("<")
		if start >= 0:
			stop = text[start:].find(">")
			if stop >= 0:
				text = text[:start] + text[start + stop + 1:]
				finished = 0
	return text
#----------------------------------------------------------------  
def shoutcastCheck(response, headers, itsOld):
	if itsOld is not True:
		if 'icy-br' in headers:
			bitrate = headers['icy-br']
			bitrate = bitrate.rstrip()
		else:
			bitrate = None

		if 'icy-metaint' in headers:
			icy_metaint_header = headers['icy-metaint']
		else:
			icy_metaint_header = None

		if "Content-Type" in headers:
			contenttype = headers['Content-Type']
		elif 'content-type' in headers:
			contenttype = headers['content-type']
			
	else:
		if 'icy-br' in headers:
			bitrate = headers['icy-br'].split(",")[0]
		else:
			bitrate = None
		if 'icy-metaint' in headers:
			icy_metaint_header = headers['icy-metaint']
		else:
			icy_metaint_header = None

	if headers.get('Content-Type') is not None:
		contenttype = headers.get('Content-Type')
	elif headers.get('content-type') is not None:
		contenttype = headers.get('content-type')
				

	if icy_metaint_header is not None:
		metaint = int(icy_metaint_header)
		PLog("icy metaint: " + str(metaint))
		read_buffer = metaint + 255
		content = response.read(read_buffer)
		# RSave("/tmp/icy_content", content)	# Debug

		start = "StreamTitle='"
		end = "';"

		try: 
			title = re.search('%s(.*)%s' % (start, end), content[metaint:]).group(1)
			title = re.sub("StreamUrl='.*?';", "", title).replace("';", "").replace("StreamUrl='", "")
			title = re.sub("&artist=.*", "", title)
			title = re.sub("http://.*", "", title)
			title.rstrip()
		except Exception as err:
			PLog("songtitle error: " + str(err))
			title = content[metaint:].split("'")[1]

		return {'song': title, 'bitrate': bitrate, 'contenttype': contenttype.rstrip()}
	else:
		PLog("No metaint")
		return False
#---------------------------------------------------
##################################### Routing ##############################################################
def router(paramstring):
	# paramstring: Dictionary mit
	# {<parameter>: <value>} Elementen
	paramstring = urllib.unquote_plus(paramstring)
	PLog(' router_params1: ' + paramstring)
		
	if paramstring:		
		params = dict(parse_qsl(paramstring[1:]))
		PLog(' router_params_dict: ' + str(params))
		try:
			if params['content_type'] == 'video':		# Auswahl im Addon-Menü
				Main()
			PLog(' router action: ' + params['action']) # hier immer action="dirList"
			PLog(' router dirID: ' + params['dirID'])
			PLog(' router fparams: ' + params['fparams'])
		except Exception as exception:
			PLog(str(exception))

		if params['action'] == 'dirList':			# Aufruf Directory-Listing
			newfunc = params['dirID']
			func_pars = params['fparams']

			# Funktionsaufrufe + Parameterübergabe via Var's 
			#	s. 00_Migration_PLEXtoKodi.txt
			# Modulpfad immer ab resources - nicht verkürzen.
			if '.' in newfunc:						# Funktion im Modul, Bsp.:
				l = newfunc.split('.')				# Bsp. resources.lib.updater.update
				PLog(l)
				newfunc =  l[-1:][0]				# Bsp. updater
				dest_modul = '.'.join(l[:-1])
				PLog(' router dest_modul: ' + str(dest_modul))
				PLog(' router newfunc: ' + str(newfunc))
			
				func = getattr(sys.modules[dest_modul], newfunc)		
			else:
				func = getattr(sys.modules[__name__], newfunc)	# Funktion im Haupt-PRG OK		

			PLog(' router func_getattr: ' + str(func))		
			if func_pars != '""':		# leer, ohne Parameter?	
				# PLog(' router func_pars: Ruf mit func_pars')
				# func_pars = urllib.unquote_plus(func_pars)		# quotierte url auspacken - entf.
				PLog(' router func_pars unquote_plus: ' + str(func_pars))
				try:
					# Problem (spez. Windows): Parameter mit Escapezeichen (Windows-Pfade) müssen mit \\
					#	behandelt werden und werden dadurch zu unicode-Strings. Diese benötigen in den
					#	Funktionen eine UtfToStr-Behandlung.
					# Keine /n verwenden (json.loads: need more than 1 value to unpack)
					func_pars = func_pars.replace("'", "\"")		# json.loads-kompatible string-Rahmen
					func_pars = func_pars.replace('\\', '\\\\')		# json.loads-kompatible Windows-Pfade
					# func_pars = func_pars.decode(encoding="utf-8")# entf. in Kodi
					
					PLog("json.loads func_pars: " + func_pars)
					PLog('json.loads func_pars type: ' + str(type(func_pars)))
					# func_pars = func_pars.encode("utf-8")			# entf. in Kodi
					mydict = json.loads(func_pars)
					PLog("mydict: " + str(mydict)); PLog(type(mydict))
				except:
					mydict = ''
				
				# PLog(' router func_pars: ' + str(type(mydict)))
				if 'dict' in str(type(mydict)):				# Url-Parameter liegen bereits als dict vor
					mydict = mydict
				else:
					mydict = dict((k.strip(), v.strip()) for k,v in (item.split('=') for item in func_pars.split(',')))			
				PLog(' router func_pars: mydict: %s' % str(mydict))
				func(**mydict)
			else:
				func()
		else:
			PLog('router action-params: ?')
	else:
		# Plugin-Aufruf ohne Parameter
		Main()

#---------------------------------------------------------------- 
PLog('Addon_URL: ' + PLUGIN_URL)		# sys.argv[0], plugin://plugin.video.ardundzdf/
PLog('ADDON_ID: ' + ADDON_ID);
PLog(ADDON_PATH);PLog(ADDON_VERSION);
PLog('HANDLE: ' + str(HANDLE))

PluginAbsPath = os.path.dirname(os.path.abspath(__file__))
PLog('PluginAbsPath: ' + PluginAbsPath)

# Callbackadressen für PlayAudio, Ablage der Args jeweils in den Funktionen
Modul_Main = sys.modules[__name__]
PLog(Modul_Main)
fadr = getattr(Modul_Main, 'StationList')	
Dict('store', 'StationList', fadr)
fadr = getattr(Modul_Main, 'SingleMRS')	
Dict('store', 'SingleMRS', fadr)
fadr = getattr(Modul_Main, 'RecordsList')	
Dict('store', 'RecordsList', fadr)
fadr = getattr(Modul_Main, 'RecordStart')	
Dict('store', 'RecordsList', fadr)
fadr = getattr(Modul_Main, 'RecordStop')	
Dict('store', 'RecordsList', fadr)

PLog('Addon: Start')
if __name__ == '__main__':
	try:
		router(sys.argv[2])
	except Exception as e: 
		msg = str(e)
		PLog('network_error: ' + msg)
		# xbmcgui.Dialog().ok(ADDON_NAME, 'network_error', msg)

		
