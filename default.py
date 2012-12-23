import xbmcplugin, xbmcgui, xbmcaddon
import string, urllib
from wjhc import wjhc

__settings__ = xbmcaddon.Addon(id='plugin.video.TSN2013WJHC')
__language__ = __settings__.getLocalizedString

def authenticate():
    # get the username    
    username = __settings__.getSetting("username")
    if len(username) == 0:
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30000), __language__(30001))
        xbmcplugin.endOfDirectory(handle = int(sys.argv[1]),
                                  succeeded=False)
        return None
    
    # get the password
    password = __settings__.getSetting("password")
    if len(password) == 0:
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30002), __language__(30003))
        xbmcplugin.endOfDirectory(handle = int(sys.argv[1]),
                                  succeeded=False)
        return None

    wj = wjhc()
    wj.login(username, password)
    
    return wj

def createMainMenu(wj):

    games = wj.getGames()
    is_live = True
    
    for game in games:
        title = game['awayTeamName'] + ' at ' + game['homeTeamName']
        
        # skip games that have not started yet
        if not game['progressTime']:
            continue

        if game['progressTime']:
            title += ' (' + game['progressTime'] + ")"
            if string.find(game['progressTime'], "FINAL") >= 0:
                is_live = False
        
        if not is_live:    
            url = sys.argv[0] + '?' + urllib.urlencode({'id' : str(game['id'])})
            print url
        else:
            url = ""

        li = xbmcgui.ListItem(title)
        li.setInfo( type='Video', infoLabels={'Title' : title })
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=url,
                                    listitem=li,
                                    isFolder=(not is_live))

    # end the list
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return None

def createFinishedMenu(id):
    games = wj.getGames()
    
    for game in games:
        if str(game['id']) == id:
            break
        
    title = __language__(30009) + ' ' + game['awayTeamName'] + ' at ' + game['homeTeamName']


    li = xbmcgui.ListItem(__language__(30010))
    li.setInfo( type='Video', infoLabels={'Title' :  title})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                url=wj.getCondensedGame(id),
                                listitem=li,
                                isFolder=False)
    
    li = xbmcgui.ListItem(__language__(30011))
    li.setInfo( type='Video', infoLabels={'Title' :  title})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                url=wj.getArchivedGame(id),
                                listitem=li,
                                isFolder=False)

    # end the list
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return None

wj = authenticate()

if (len(sys.argv[2]) == 0):
    createMainMenu(wj)
else:
    createFinishedMenu(sys.argv[2][4:])

