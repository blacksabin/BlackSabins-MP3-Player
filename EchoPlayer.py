import pygame, os, random, time
from ast import literal_eval
from pygame.locals import *
from PGLib import Box
from PGLib import TextBox


Library = {}            #Library; aka where the mp3 names and tags are
CONFIG = {'debug'           :   False,  #Holds all the configurations and settings
          'path'            :   os.path.expanduser('~\Music'),
          'backgroundColor' :   (5,5,5),
          'foregroundColor' :   (20,20,20),
          'fontColor'       :   (255,255,255),
          'whitelistColor'  :   (0,255,0),
          'blacklistColor'  :   (255,0,0),
          'font'            :   'Calibri',
          'height'          :   400,
          'width'           :   400}
TuplesNeeded = ['backgroundColor','foregroundColor','fontColor','whitelistColor','blacklistColor']
debug_buffer = []               #For when its loading the settings and you don't want a log
Tags = []                       #Holds the whole list of tags
SONG_END = pygame.USEREVENT + 1 #Makes the event for when a song finishes

gridLayout = (3,3)              #Used to organize the screen's grid layout

#################################################################################
#################################################################################

def log(string, *strings): #Instead of using print(), log() will put everything in the log.txt
    string = str(string) #Makes it a strig
    if strings is not None: #Extra arguments?
        for i in strings:
            string = string + str(i) #Make them all one string
    if CONFIG['debug'] is True:
        #print(string)
        file = open('log.txt','a') #Append the log file, don't overwrite it
        file.write(time.strftime('%x,%X') + ': ' + string + '\n') #Make it look nice
        file.close() #Dreadfully important to close this.
    else:
        debug_buffer.append(string)

def refresh():
    pygame.display.update()

def TBox(self,key,text,pos,size,**kwargs):
    w = self.surface.get_width() #Screen width
    h = self.surface.get_height() #Screen height
    mx,my = gridLayout #Master X, Master Y. These are the "new" positions
    wIncrement = w / mx
    hIncrement = h / my
    x,y = pos
    x = x - 1
    y = y - 1
    a,b = size
    defaults = {'color'     : CONFIG['foregroundColor'],
                'font_color': CONFIG['fontColor'],
                'font_size' : 'dynamic'}
    for kwarg in kwargs:
        if kwarg in defaults:
            defaults[kwarg] = kwarg[kwarg]
    self.Elements[key]= TextBox(text,
                                [(x*wIncrement,y*hIncrement),(a*wIncrement,b*hIncrement)],
                                **defaults)

#################################################################################
#################################################################################

def makeConfigs():
    log('Making config file')
    file = open('config.txt','w')
    for key in CONFIG:
        file.write(key + ' = ' + str(CONFIG[key]) + '\n')
    file.close()
    log('Config file created')

def loadConfigs():
    if os.path.exists('config.txt'): #If the file exists
        log('Config file found')
        file = open('config.txt','r')#Start reading
        for line in file:#For each line (or setting)
            line = line.rstrip('\n')#Get rid of the newline character
            try:
                var,val = line.split(' = ')#setting , value
                CONFIG[var] = val #Assigns it
                if val == '':#If the setting doesn't have a value
                    log('Empty variable found. Remaking config file.')
                    makeConfigs()
                    loadConfigs()
                    break
                elif val.lower() == 'true':#Makes sure statements like tRuE are evaluated as True
                    val = True
                elif val.lower() == 'false':#Same as True but with False
                    val = False
                if (var == 'font') or (var == 'path'):
                    CONFIG[var] = val
                else:
                    CONFIG[var] = literal_eval(val)
                log(var,' : ',val)#Logs it
            except ValueError:#If there is an error, ignore it. This keeps inappropriate settings from loading.
                pass
        if CONFIG['debug'] is True:#Debugging just lets log() make a file. Otherwise, you won't see anything.
            file = open('log.txt','w')#Make the log file
            file.close()#Close it; we're not the ones writing to it, thats log()'s job
            for key in debug_buffer:#We couldn't log shit before, so lets catch up
                log(key)
        try:
            os.path.exists(CONFIG['path'])#This needs to not crash, so a try statement.
        except:
            log('Something wrong with the config file. Remaking it.')
            makeConfigs()
            loadConfigs()
            pass
        file.close()
    else:
        log('Config file not found')
        makeConfigs()
        log('Attempting to load configs again...')
        loadConfigs()

def loadData():
    if os.path.exists('data.txt'):
        file = open('data.txt','r')
        log('Data file found')
        for line in file:
            line = line.rstrip('\n')
            try:
                var,val = line.split(" | ")
                lst = val.split(',')
                Library[var]=lst
                log('Mp3 loaded: ',var,Library[var])
            except ValueError:
                pass
        log(str(len(Library)),' mp3s found')
        file.close()
    else:
        log('Data file not found')

def loadTags():
    log('Loading Tags')
    for key in Library:
        for item in Library[key]:
            if item not in Tags:
                log('Tag found: ',item)
                Tags.append(item)

def findMusic():
    log('Searching for new music...')
    i = 0
    for file in os.listdir(CONFIG['path']):
        if file.endswith('.mp3'):
            file = os.path.splitext(file)[0]
            if Library.get(file) is None:
                i += 1
                Library[file] = ['tagme']
                log('Found new mp3:',file)
    log(i, ' new mp3s added')
    if i > 0:
        log('Updating data file')
        file = open('data.txt','w')
        for key in Library:
            string = ''
            for q in Library[key]:
                string = string + q.rstrip('\n')
            file.write(str(key + ' | ' + string + '\n'))
            log(key, ' added')
        file.close()

#################################################################################
#################################################################################

def playSong(song): #Plays the song, takes the raw name!
    try:
        pygame.mixer.music.load(str(CONFIG['path']+'\\' + song + '.mp3')) #Puts together the file path
        pygame.mixer.music.play() #This plays it
        log('Playing ', song)
    except pygame.error: #Only in the event of an invalid song name
        log('Error 404: Song file not found.')
        pass

def pickRandomSong(master):
    log('Picking random song')
    if master == None:
        raise IndexError('Master is None')
    else:
        return random.choice(master)
        
#################################################################################
#################################################################################

loadConfigs()
loadData()
findMusic()
loadTags()
log('Initializing PyGame')
pygame.init()
pygame.mixer.init()
Screen = pygame.display.set_mode((CONFIG['width'],CONFIG['height']),HWSURFACE|DOUBLEBUF|RESIZABLE)
done = False

#################################################################################
#################################################################################

class MP3Player():

    Elements = {}           #These are the items that need to be rendered
    Whitelist = []          #The selected tag to play
    Blacklist = []          #The selected tags to not play
    Playlist = []           #The Playlist of mp3s made from the selected tag
    Buffer = []             #List of what just played, in order to go back
    Queue = []              #List of whats next on the Playlist
    NowPlaying = 'N/A'      #Whats now playing
    TagSelected = Tags[0]   #This is the first tag
    Paused = False          #If the song is Paused

    def __init__(self,surf):
        self.surface = surf
        
        ###Display now playing
        TBox(self,'NowPlayingLabel','Now Playing:',(1,1),(1,1))
        TBox(self,'NowPlaying',self.NowPlaying,(2,1),(2,1))
        ###Tag controller
        TBox(self,'Tag_Previous','<',(1,2),(1,1))
        TBox(self,'Tag_Selected',self.TagSelected.title(),(2,2),(1,1))
        TBox(self,'Tag_Next','>',(3,2),(1,1))
        ###Previous, Play/Pause, Skip
        TBox(self,'Previous_Song','<',(1,3),(1,1))
        TBox(self,'Play','V',(2,3),(1,1))
        TBox(self,'Next_Song','>',(3,3),(1,1))

        self.Whitelist.append(self.TagSelected) #Starts the whitelist with the selected tag(s)
        self.update_Playlist() #We just started, so we have no playlist. Make one.
        self.draw() #We're pretty, now show the user

    def keypress(self,button):
        log(button,' was pressed')
        if button == 'Play':   #Play button was pressed
            if not self.Paused: #Pause the party
                self.pause()
            elif self.Paused: #Now let it rollll
                self.play()
        elif button == 'Next_Song': #Skip, duh.
            log('Skipping song')
            self.play_next()
        elif button == 'Previous_Song': #Go back, that was my jam!
            log('Playing last song')
            self.play_previous()
        elif button == 'Tag_Next':
            log('Selecting Next Tag')
            self.tag_next()
        elif button == 'Tag_Previous':
            log('Selecting Previous Tag')
            self.tag_previous()
        elif button == 'Tag_Selected':
            log('Manipulating White/Blacklist')
            self.tag_press()

    def play(self):
        log('Unpausing...')
        pygame.mixer.music.unpause()
        self.Paused = False

    def pause(self):
        log('Pausing...')
        pygame.mixer.music.pause()
        self.Paused = True

    def update_Playlist(self):
        log('Updating Playlist')
        pygame.mixer.music.stop()
        self.Buffer = []
        self.Queue = []
        if self.Whitelist == 'all': #If the tag is all, just use the whole Library
            log('All tag detected. Including full library.')
            self.Playlist = list(Library.keys()) #Just use the whole library.
        else:
            self.NowPlaying = 'N/A'
            self.Playlist = [] #Empty the playlist. We're updating, so blank it.
            for key in Library: #For each song
                if (bool(set(Library[key]).intersection(self.Whitelist))) and not (bool(set(Library[key]).intersection(self.Blacklist))): #If the tag in whitelist matches that of the song
                    log(key,' added to playlist.')
                    self.Playlist.append(key) #Add the song to the playlist.
            if not self.Playlist: #If the playlist is empty by the end of it all,
                log('Invalid tags or no tags found. Including full library.')
                self.Playlist = list(Library.keys()) #Just use the whole library.
        log('Successfully updated library.')

    def update_NowPlaying(self): #Updates the NowPlaying label
        log('Updating NowPlaying')
        TBox(self,'NowPlaying',self.NowPlaying,(2,1),(2,1))
        self.Elements['NowPlaying'].draw(self.surface)
        refresh()

    def update_TagSelected(self):
        log('Updating TagSelected')
        target = self.Elements['Tag_Selected']
        TBox(self,'Tag_Selected',self.TagSelected.title(),(2,2),(1,1))
        target.caption = self.TagSelected.title()
        if self.TagSelected in self.Whitelist:
            target.color = CONFIG['whitelistColor']
        elif self.TagSelected in self.Blacklist:
            target.color = CONFIG['blacklistColor']
        target.draw(self.surface)
        refresh()

    def tag_next(self): #Selects the next tag in the list
        log('Grabbing next tag')
        i = Tags.index(self.TagSelected) #Finds it's index
        i += 1
        if i >= len(Tags): #If the tag index is now greater than the list,
            i = 0 #reset it
        self.TagSelected = Tags[i] #Select the new tag
        self.update_TagSelected()

    def tag_previous(self): #Selects the previous tag in the list; tag_next backwards
        log('Grabbing previous tag')
        i = Tags.index(self.TagSelected)
        i -= 1
        if i < 0:
            i = len(Tags) - 1
        self.TagSelected = Tags[i]
        self.update_TagSelected()
        
    def tag_press(self): #When someone clicks on the tag so it modifies the whitelists
        log('Tag button pressed')
        if self.TagSelected in self.Whitelist:
            log('Tag ', self.TagSelected, ' moved to blacklist')
            self.Whitelist.remove(self.TagSelected)
            self.Blacklist.append(self.TagSelected)   #Add to blacklist            
        elif self.TagSelected in self.Blacklist:
            log('Tag ', self.TagSelected, ' removed from blacklist')
            self.Blacklist.remove(self.TagSelected)      #Don't give it a designation
        else:
            log('Tag ', self.TagSelected, ' added to whitelist')
            self.Whitelist.append(self.TagSelected)   #Add to whitelist
        self.update_TagSelected()
        self.update_Playlist()
                   
    def play_next(self):
        log('Playing next song')
        self.Buffer.append(self.NowPlaying) #Put the song we're skipping on the backburner
        pop = None #So the (if pop) statement doesn't have issues
        try:
            pop = self.Queue.pop() #Grab the next song
        except:
            pass #If we don't have a next song, don't crash
        if pop is not None:
            playSong(pop) #Play the song in Queue
            self.NowPlaying = pop
        else:
            choice = pickRandomSong(self.Playlist) #Pick a song!
            playSong(choice)
            self.NowPlaying = choice
        pygame.mixer.music.set_endevent(SONG_END) #Let the system know when we end playing
        self.update_NowPlaying() #Update the "now playing"

    def play_previous(self): #play_next, but the opposite direction.
        log('Playing previous song')
        self.Queue.append(self.NowPlaying)
        pop = None
        try:
            pop = self.Buffer.pop()
        except:
            pass
        if pop is not None:
            playSong(pop)
            self.NowPlaying = pop
        else:
            choice = pickRandomSong(self.Playlist)
            playSong(choice)
            self.NowPlaying = choice
        pygame.mixer.music.set_endevent(SONG_END)
        self.update_NowPlaying()
        
    def draw(self): #Put everything on the screen
        log('Drawing Player')
        Screen.fill(CONFIG['backgroundColor']) #Start with a blank sheet
        for key in self.Elements:
            self.Elements[key].draw(self.surface) #Draw onto the screen
        refresh() #Update le' screen

#################################################################################
#################################################################################

Player = MP3Player(Screen) #Make an instance of our MP3Player

while not done: #Main loop
    for event in pygame.event.get(): #Grab everything thats going on
        #log(event)
        if event.type == QUIT: #User clicked the X!
            log('Closing! Please wait...')
            done = True
            break
        elif event.type == MOUSEBUTTONDOWN: #The user clicked!
            log('Mouse clicked')
            for key in Player.Elements:
                if Player.Elements[key].rect.collidepoint(event.pos): #Check if the click was a button
                    Player.keypress(key) #Push a button!
                    break
        elif event.type == KEYDOWN: #The user pressed a key!
            if event.key == K_ESCAPE: #That key was escape!
                log('Escape!')
                done = True
                break
            else:
                log('Key pressed: ', event.key)
        elif event.type == SONG_END: #When the song ends (duh)
            log('Song ended, playing next')
            Player.play_next()
        elif event.type == VIDEORESIZE:
            log('Window size changed to ',event.size)
            WIDTH, HEIGHT = event.size
            CONFIG['width'] = WIDTH
            CONFIG['height'] = HEIGHT
            Screen = pygame.display.set_mode((WIDTH,HEIGHT),HWSURFACE|DOUBLEBUF|RESIZABLE)
            Player.__init__(Screen)

pygame.quit()
