import string, re, urllib, urllib2, json, xml.dom.minidom, cookielib

# http://nlds119.cdnak.neulion.com/nlds_vod/tsn/vod/2012/12/22/4/1_4_can_swe_2012_h_whole_1_3000.mp4.m3u8

class wjhc:
    
    def __init__(self):
        """
        Initialize some constants needed later on
        """
        self.LOGIN_URI = 'https://worldjuniors.tsn.ca/tsn/secure/login'
        self.GAMES_URI = 'http://worldjuniors.tsn.ca/tsn/servlets/games'
        self.PUBLISH_URI = 'http://worldjuniors.tsn.ca/tsn/servlets/publishpoint'
        self.LOGIN_USER = 'username'
        self.LOGIN_PASS = 'password'
        self.GAME_ID = 'id'
        self.GAME_TYPE = 'gt'
        self.GAME_TYPE_CONDENSED = 'condensed'
        self.GAME_TYPE_ARCHIVE = 'archive'
        self.GAME_TYPE_LIVE = 'live'

    def login(self, user, password):
        
        values = { self.LOGIN_USER : user,
                   self.LOGIN_PASS : password }
        
        jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
        form_data = urllib.urlencode(values)
        
        resp = opener.open(self.LOGIN_URI, form_data)

        data = resp.read()
        dom = xml.dom.minidom.parseString(data)
        
        result_node = dom.getElementsByTagName('result')[0]
        code_node = result_node.getElementsByTagName('code')[0]
        
        if code_node.firstChild.nodeValue != 'loginsuccess':
            print "ERROR: Login failure."
            return False
        
        self.jar = jar
        
        return True
    
    def getGames(self):
        
        req = urllib2.Request(self.GAMES_URI)
        
        try:
            resp = urllib2.urlopen(req)
        except:
            print "ERROR: Unable to get games list."
            return None
        
        data = resp.read()
        result = json.loads(data)
        
        return result['games']
    def getLiveGame(self, id):
        """
        Get a live game
        """
        base_live = self.getGame(id, self.GAME_TYPE_LIVE)
        
        match = re.search('.*/tsn/(.*?)/.*', base_live, re.IGNORECASE)
        if match != None:
            try:
                hd = base_live.replace('android.m3u8', 's_' + match.group(1) + '_live_game_hd.m3u8')
                req = urllib2.Request(hd)
                resp = urllib2.urlopen(req)
                if resp.getcode() == 200:
                    return hd
            except:
                return base_live

        return base_live


        
        return base_live

    def getCondensedGame(self, id):
        """
        Get a condensed game
        """
        return self.getGame(id, self.GAME_TYPE_CONDENSED)
    
    def getArchivedGame(self, id):
        """
        Get an archived game
        """
        return self.getGame(id, self.GAME_TYPE_ARCHIVE)
        
    def getGame(self, id, gt):
        """
        Get a game by its it and type
        """
        values = { 'type' : 'game',
                   'nt' : '1',
                   self.GAME_ID : str(id),
                   self.GAME_TYPE : gt }
        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        opener.addheaders = [('User-agent', 'Android Mobile')]

        form_data = urllib.urlencode(values)
        resp = opener.open(self.PUBLISH_URI, form_data)

        # get the path node CDATA from teh result tag.
        dom = xml.dom.minidom.parseString(resp.read())
        result_node = dom.getElementsByTagName('result')[0]
        code_node = result_node.getElementsByTagName('path')[0]
        
        # return a cleaned up URI
        return code_node.firstChild.data.strip().split('?')[0].replace('_android','')
