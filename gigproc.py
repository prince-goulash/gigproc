#!/usr/bin/python3
import sys
import os
import glob
import re
import time
from datetime import datetime, timedelta, date
from gigproc.gigplot import GIG_plot
from gigproc.gightml import GIG_html

class GIG_artist():
    def __init__(self,name,index):
        self.name  = name
        self.index = index
        self.gigs  = []
        self.biog  = {}

    def age(self, date):
        age = None
        if self.biog and self.biog['dob']:
            dob = self.biog['dob']
            age = date.year - dob.year - ((date.month, date.day) < (dob.month, dob.day))
        return age

    def gender(self):
        gender = None
        if self.biog and self.biog['gender']:
            gender = self.biog['gender']
        return gender

class GIG_data():
    def __init__(self,root,verbose=False):
        self.root      = root
        self.verbose   = verbose
        self.gigs      = []
        self.past_gigs = []
        self.artists   = []

        self.artist_bios = {}
        self.last_artist_index = 0

        self.unique_artists = None  # cached
        self.unique_artists_inc_future = None  # cached
        self.unique_venues = None   # cached
        self.unique_venues_inc_future = None   # cached
        self.unique_years = None    # cached
        self.unique_years_inc_future = None    # cached
        self.unique_songs_of_artist = {} # cached
        self.playlist_gigs = []

        self.time = time.clock()
        self.build_gig_data()
        self.time = time.clock() - self.time
        if self.verbose:
            print("Generated gig data in %.2f seconds" % self.time)
    def __str__(self):
        # print summary of gig data
        nmax      = 30
        artists   = self.get_unique_artists()
        venues    = self.get_unique_venues()
        years     = self.get_unique_years()
        n_gigs    = len(self.get_past_gigs())
        n_venues  = str(len(venues))
        n_artists = str(len(artists))
        n_years   = " " + str(len(years))

        string = ( ""
         "\n          /---------------------\ "
         "\n          |                     | "
         "\n          |     %s years       | "
         "\n          |     %s gigs        | "
         "\n          |     %s venues      | "
         "\n          |     %s artists     | "
         "\n          |                     | "
         "\n          \---------------------/ "
         "\n"
         ) % ( n_years, n_gigs, n_venues, n_artists )

        for i in range(0,nmax-1):
            string += '\n {0:3d} {1:30s} {2:3d} {3:30s}' \
                . format( len(artists[i][1]), artists[i][0], \
                          len(venues[i][1]), venues[i][0])

        string += '\n'

        return string

    def get_artist_bios(self,name):
        if not self.artist_bios:
            lines = []
            path = self.root + '/artist_data'
            with open(path) as f:
                lines = f.readlines()

            for line in lines:
                bio = {
                    'dob'    : None,
                    'gender' : None,
                    'dod'    : None,
                    }
                splits = line.split(':')
                splits = [ x.strip() for x in splits ]

                artist = splits[0]

                if len(splits) > 1 and splits[1]:
                    bio['dob'] = datetime.strptime( splits[1], '%Y-%m-%d').date()

                if len(splits) > 2 and splits[2]:
                    bio['gender'] = splits[2]

                if len(splits) > 3 and splits[3]:
                    bio['dod'] = datetime.strptime( splits[3], '%Y-%m-%d').date()

                self.artist_bios[artist] = bio

        biog = {}
        if name in self.artist_bios.keys():
            biog = self.artist_bios[name]

        return biog
    def find_artist(self,name):
        artist = None
        for a in self.artists:
            if a.name == name:
                artist = a
                break
        if not artist:
            self.last_artist_index += 1
            artist = GIG_artist(name, self.last_artist_index)
            artist.biog = self.get_artist_bios(name)
            self.artists.append(artist)
        return artist

    # Functions to build gig data:
    def process_song_line(self,line,this_set,opener):
        # This function builds a GIG_song and appends it to this_set.
        # It also updates the set flags if necessary.

        splits = line.split('---')
        title = splits[0]
        title = re.sub( r"\s*---.*$", '', title)
        title = re.sub( r"\s*\*+\s*$", '', title)
        title = re.sub( r"\s*\^+\s*$", '', title)
        title = re.sub( r"\s*\~+\s*$", '', title)
        #title = re.sub( r"(?<=[^?])\?$", '\1', title)

        # capitalise each word:
        title = ' '.join(w[0].upper() + w[1:] for w in title.split()) 

        # uncapitalise conjunctions:
        # words = [ "And", "The", "Of", "In", "On" ]
        # for w in words:
        #     title = re.sub( ' (' + w + ') ', 
        #         lambda m: ' ' + m.group(1).lower() + ' ', title )

        if re.match('^\s*$', title):
            # process set flags
            title = None
            if len(splits) > 1:
                # set flags:
                if '[unordered]' in splits[1]:
                    this_set.ordered = False
                if '[solo]' in splits[1]:
                    this_set.solo = True
                # Comment out these two lines to suppress the band member processing
                if re.match( '.*{.*', splits[1] ):
                   this_set.band += re.findall( '{([0-9A-Za-z- ]+)}', splits[1])
                if '@' in splits[1]:
                    path = line.split('@')[1].strip()
                    path = r'/home/jpf/Music/' + path
                    this_set.playlist = path
                    if not os.path.exists(path):
                        print(path)
        else:
            # process song flags and append
            if re.match( '\?+', title ):
                title = None
            song = GIG_song(title)
            song.count = 1
            for oldsong in this_set.songs:
                if oldsong.title == song.title:
                    song.count += 1
            song.set_opener = opener
            if re.match( '^\s+', line )  :
                # if the line is indented, it's part of a medley
                song.medley = True;
            if len(splits) > 1:
                # song flags:
                if '{' in splits[1]:
                    #song.guests += re.findall( '{([0-9A-Za-z- ]+)}', splits[1])
                    for guest in re.findall( '{([0-9A-Za-z- ]+)}', splits[1]):
                        if guest[0] == '-':
                            song.missing.append(guest[1:])
                        else:
                            song.guests.append(guest)
                if '[' in splits[1]:
                    #song.custom = re.findall( '\[([0-9A-Za-z- ]+)\]', splits[1])
                    for x in re.findall( '\[([0-9A-Za-z- ]+)\]', splits[1]):
                        if x == 'solo':
                            song.solo = True
                        elif x == 'debut':
                            song.debut = True
                        elif x == 'improv':
                            song.improv = True
                        elif x == 'request':
                            song.request = True
                        else:
                            song.custom.append(x)
                if '<' in splits[1]:
                    m = re.match( '.*<(.*)>.*', splits[1] )
                    if m:
                        song.cover = m.group(1)
                if '"' in splits[1]:
                    m = re.match( '.*(".*").*', splits[1])
                    if m:
                        song.quote = m.group(1)
                # if '[solo]' in splits[1]:
                #     song.solo = True
                # if '[debut]' in splits[1]:
                #     song.debut = True
                # if '[improv]' in splits[1]:
                #     song.improv = True
            this_set.append_song(song)
    def process_artist_name(self,n):
        # strip comments and remove definite articles
        names = []
        splits = n.split('+')
        for split in splits:
            name = split
            name = re.sub( '\s*---.*', '', name )
            name = name.strip()
            name = re.sub( '^The\s+', '', name )
            names.append(name)

        artists = [ self.find_artist(n) for n in names ]

        return artists
    def identify_first_times(self):
        for (a,c) in self.get_unique_artists():
            for song in self.get_unique_songs_of_artist(a):
                first_id = min( [ x.index for x in song['events'] ] )
                for g in self.gigs:
                    if g.index == first_id:
                        for s in g.sets:
                            try:
                                pos = s.songs.index(song['title'])
                                if s.artists[0].name == a or a in s.songs[pos].guests:
                                    s.songs[pos].first_time = True
                                    break
                            except ValueError:
                                pass
    def load_playlists(self):
        fname = self.root + '/playlists'
        playlists = []
        with open(fname) as f:
            for line in f.readlines():
                playlist = {}
                splits = line.split('---')
                path = splits[0].strip()
                if path.startswith('~'):
                    path = os.path.expanduser(path)
                playlist["path"] = path
                playlist["artist"] = None
                playlist["artist_alt"] = None
                if len(splits) > 1:
                    playlist["artist"] = splits[1].strip()
                else:
                    splits = path.split('/')
                    playlist["artist"] = splits[5]
                    if ',' in splits[5]:
                        names = splits[5].split(',')
                        if len(names) == 2:
                            playlist["artist_alt"] = names[1].strip() + " " + names[0].strip()
                            #print(playlist["artist_alt"])

                playlists.append(playlist)
        return playlists
    def fill_in_playlist_links(self):
        playlists = self.load_playlists()
        if playlists:
            for g in self.gigs:
                for s in [ x for x in g.sets if not x.band_only ]:
                    if s.playlist:
                        continue
                    date_string = g.date.strftime("%Y.%m.%d")
                    artist = s.artists[0].name
                    #print(date_string + ' [%s]' % artist)
                    #print(artist)
                    #candidates = [ x for x in playlists if date_string in x["path"] ]
                    for i, pl in enumerate(playlists):
                        if not date_string in pl["path"]:
                            continue
                        #print(pl)
                        if pl["artist"] and pl["artist"] == artist:
                            s.playlist = pl["path"]
                            del playlists[i]
                        elif pl["artist_alt"] and pl["artist_alt"] == artist:
                            s.playlist = pl["path"]
                            del playlists[i]
                        elif artist in pl["path"]:
                            s.playlist = pl["path"]
                            del playlists[i]

        # Print playlists which have not been matched to a set:
        #for pl in playlists:
            #print(pl)

    def get_data_from_file(self,path):
        level = 0
        commented = False
        com_level = -1
        last_blank = False
        with open(path) as f:
            lines = f.read().splitlines()
        for line in lines:
            mopen = re.match('^\{\{\{ (.*)',line)
            mclose = re.match('^\}\}\}',line)
            mblank = re.match('^\s*$',line)
            mc = re.match('^\{\{\{\s*---',line)
            if mc:
                commented = True
                if com_level == -1:
                    com_level = level
            if mblank:
                last_blank = True
            elif mopen:
                last_blank = False
                level += 1
                m1 = re.match('^(\d\d-[A-Z][a-z][a-z]-\d\d\d\d) \[(.*)\]\s*$',mopen.group(1))
                date_regex = "%d-%b-%Y"
                if not m1:
                    m1 = re.match('^(\d\d\.\d\d\.\d\d\d\d) \[(.*)\]\s*$',mopen.group(1))
                    date_regex = "%d.%m.%Y"
                if commented:
                    pass
                elif m1:
                    d = datetime.strptime( m1.group(1), date_regex )
                    v = m1.group(2)
                    this_gig = GIG_gig( d, v )
                elif not this_gig:
                    # This can happen when the regex doesn't match (e.g. due to a missing "]"), 
                    # so we misinterpret a set as an event. 
                    raise ValueError("Malformed line? : " + line)
                else:
                    a = self.process_artist_name( mopen.group(1) )
                    for artist in a:
                        artist.gigs.append(this_gig)
                    this_set = GIG_set(a)
                    this_gig.append_set(this_set)
            elif mclose:
                last_blank = False
                level -= 1
                if level == 0 and not commented:
                    this_gig.add_dummy_sets_for_guests(self)
                    self.gigs.append(this_gig)
                    this_gig = None
                if commented and com_level == level:
                    com_level = -1
                    commented = False
            elif level == 2:
                self.process_song_line(line,this_set,last_blank)
                last_blank = False
    def build_gig_data(self):
        for f in glob.glob(self.root + '/*.gigs'):
            self.get_data_from_file(f)
        self.gigs.sort(key=lambda x: x.date)

        # fill in gig index
        i = 0
        lyear = 0
        for g in self.gigs:
            year = g.date.year
            if year != lyear:
                i = 0
                lyear = year
            g.index = int(str(year) + str(i+1).zfill(2))
            g.link  = str(year) + '_' + str(i+1).zfill(2)
            i += 1

        self.identify_first_times()
        
    # Some utilities
    def artist_stats(self,artist):
        unique_songs = self.get_unique_songs_of_artist(artist)
        
        raw_events = []
        for song in unique_songs:
            raw_events += song['events']
        
        events = list(set(raw_events))
        events.sort(key=lambda x: x.index) 
        
        print( "\n\n Profiling %d unique songs from %d events by %s:\n"  \
            % (len(unique_songs), len(events), artist) )
        
        for song in unique_songs:
            event_string = ""
            for event in events:
                if event in song['events']:
                    #title = song['title'] + ' / ' + event.venue + ' / ' + event.date.strftime("%d %b %Y")
                    #event_string += '<div class=greyflag title="' + title + '">X</div>'
                    event_string += 'X'
                else:
                    event_string += '-'
            print( '{0:3d} {1:50s} {2:30s}' \
                . format( len(song['events']), song['title'], event_string ) )
    def songs_performed_by_multiple_artists(self):
        raw_songs = [] # list of { song, artists, gigs }
        for g in self.gigs:
            for s in g.sets:
                for song in s.songs:
                    if song.title:
                        artists = [ s.artists[0].name ] # + song.guests
                        try:
                            i = [ x['title'] for x in raw_songs ].index(song.title)
                            for a in artists:
                                if a not in raw_songs[i]['artists']:
                                    raw_songs[i]['artists'].append(a)
                        except ValueError:
                            # add new song
                            new_song = { 'title': song.title, 'artists': artists }
                            raw_songs.append(new_song)
        raw_songs = [ x for x in raw_songs if len(x['artists']) > 1 ]
        for song in raw_songs:
            print( song['title'].ljust(30) + ' ' + ', '.join(song['artists']) )
    def get_unique_songs_of_artist(self,a):
        try:
            usoa = self.unique_songs_of_artist[a]
            return usoa
        except KeyError:
            usoa = []
            artist = a + '$'
            for gig in self.gigs:
                for s in gig.sets:
                    # look for song in artist's main set:

                    guest = False
                    main_set = False
                    if re.search(artist, s.artists[0].name, re.IGNORECASE):
                        main_set = True
                    elif s.band:
                        for b in s.band:
                            if re.search(artist, b, re.IGNORECASE):
                                main_set = True
                                guest = True
                                break

                    if main_set:
                        for song in s.songs:
                            got = False
                            if not song.title: # Untitled
                                continue
                            if guest and song.solo: # solo performance cannot contain guest
                                continue
                            if a in song.missing:
                                continue
                            for got_song in usoa:
                                if got_song['title'] == song.title:
                                    got_song['events'].append(gig)
                                    got = True
                            if not got:
                                usoa.append( { 'title': song.title, 'events': [gig], 'obj': song } )
                    else:
                        # look for song in other sets for which the artist is flagged:

                        for song in s.songs:
                            flagged = False
                            for guest in song.guests:
                                if re.search( artist, guest, re.IGNORECASE ):
                                    flagged = True
                            if flagged:
                                got = False
                                for got_song in usoa:
                                    if got_song['title'] == song.title:
                                        got_song['events'].append(gig)
                                        got = True
                                if not got:
                                    usoa.append( { 'title': song.title, 'events': [gig], 'obj': song } )

            usoa = [ x for x in usoa if x['title'] ] # shouldn't be necessary
            usoa.sort(key=lambda x: (-len(x['events']),x['title']), reverse=True)
            usoa.reverse()
            self.unique_songs_of_artist[a] = usoa
            return usoa
    def get_past_gigs(self):
        if not self.past_gigs:
            self.past_gigs = []
            for g in self.gigs:
                if not g.future:
                    self.past_gigs.append(g)
        return self.past_gigs
    def first_unseen(self):
        for gigs in self.gigs:
            if gigs.future:
                return gigs
    def calendar(self,verbose=False,month=None):
        start = datetime(2016,1,1) # leap year

        gig_days = 0

        dates = []
        gigs = []
        date_gig_counts = []

        for date in ( start + timedelta(days=n) for n in range(366) ):
            if month and date.month != month:
                continue

            dates.append(date)
            gigs.append([])

            years = []
            for gig in self.gigs:
                if gig.date.month == date.month and gig.date.day == date.day:
                    if not gig.future:
                        years.append(gig.date.year)
                    gigs[-1].append(gig)

            artists = ''
            if years:
                gig_days += 1
                artists = ', '.join([str(x) for x in years])

            date_gig_counts.append( len(years) )

            if verbose:
                print(date.strftime("%b %d") + " : " + artists)

        if verbose:
            print("\nGig days: %d/366 = %.1f%%" % (gig_days, gig_days/3.66))

        return dates, gigs
    def next_gig(self):
        for g in self.gigs:
            if g.future:
                return g

    # Queries on gig data:
    def all_gigs_of_artist(self,artist,inc_future=False):
        artgigs = []
        for gig in self.gigs:
            if not gig.future or inc_future:
                if artist in gig.get_artists():
                    artgigs.append(gig)
        
        artgigs.sort(key=lambda x: x.index)
        
        return artgigs
    def all_gigs_of_venue(self,venue,inc_future=False):
        vengigs = []
        for gig in self.gigs:
            if not gig.future or inc_future:
                if venue == gig.venue:
                    vengigs.append(gig)
        
        vengigs.sort(key=lambda x: x.index)
        return vengigs
    def generate_unique_artists(self,inc_future=False):
        artists = []
        artgigs = []
        for gig in self.gigs:
            if not gig.future or inc_future:
                for artist in gig.get_artists():
                    try:
                        i = artists.index(artist)
                        artgigs[i].append(gig)
                    except ValueError:
                        artists.append(artist)
                        artgigs.append([gig])
        
        for l in artgigs:
            l.sort(key=lambda x: x.index)
        
        zipped = list( zip( artists, artgigs ) )
        zipped.sort( key=lambda x: (-len(x[1]),x[0]), reverse = True ) 
        zipped.reverse()
        return zipped
    def get_unique_artists(self,inc_future=False):
        if inc_future:
            if not self.unique_artists_inc_future:
                self.unique_artists_inc_future = self.generate_unique_artists(inc_future)
            return self.unique_artists_inc_future
        else:
            if not self.unique_artists:
                self.unique_artists = self.generate_unique_artists(inc_future)
            return self.unique_artists
    def generate_unique_venues(self,inc_future=False):
        venues = []
        vengigs = []
        for gig in self.gigs:
            if not gig.future or inc_future:
                venue = gig.venue
                try:
                    i = venues.index(venue)
                    vengigs[i].append(gig)
                except ValueError:
                    venues.append(venue)
                    vengigs.append([gig])
        
        for l in vengigs:
            l.sort(key=lambda x: x.index)
        
        zipped = list( zip( venues, vengigs ) )
        zipped.sort( key=lambda x: (-len(x[1]),x[0]), reverse = True ) 
        zipped.reverse()
        return zipped
    def get_unique_venues(self,inc_future=False):
        if inc_future:
            if not self.unique_venues_inc_future:
                self.unique_venues_inc_future = self.generate_unique_venues(inc_future)
            return self.unique_venues_inc_future
        else:
            if not self.unique_venues:
                self.unique_venues = self.generate_unique_venues(inc_future)
            return self.unique_venues
    def unique_cities(self):
        cities = []
        city_gigs = []
        city_gigs_future = []
        for gig in self.gigs:
            try:
                pos = cities.index(gig.city)
            except ValueError:
                pos = len(cities)
                city_gigs.append([])
                city_gigs_future.append([])
                cities.append(gig.city)

            if gig.future:
                city_gigs_future[pos].append(gig)
            else:
                city_gigs[pos].append(gig)

        for l in city_gigs:
            l.sort(key=lambda x: x.index)
        for l in city_gigs_future:
            l.sort(key=lambda x: x.index)

        zipped = list( zip( cities, city_gigs, city_gigs_future ) )
        zipped.sort( key=lambda x: (-len(x[1]),x[0]), reverse = True ) 
        zipped.reverse()
        return zipped
    def get_unique_countries(self,inc_future=False):
        countries = {}
        path = self.root + '/venue_data'
        v_countries = {}
        with open(path) as f:
            for line in f.readlines():
                splits = line.split('#')
                if len(splits) == 2:
                    v_countries[splits[0].strip()] = splits[1].strip()
        for (city, gigs_past, gigs_future) in self.unique_cities():
            if city in v_countries.keys():
                country = v_countries[city]
                if not country in countries.keys():
                    countries[country] = []
                countries[country] += gigs_past
                if inc_future:
                    countries[country] += gigs_future
        return countries
    def generate_unique_years(self,inc_future=False):
        years = []
        ygigs = []
        for gig in self.gigs:
            if not gig.future or inc_future:
                y = gig.date.year
                try:
                    i = years.index(y)
                    ygigs[i].append(gig)
                except ValueError:
                    years.append(y)
                    ygigs.append([gig])
        
        for l in ygigs:
            l.sort(key=lambda x: x.index)
        
        zipped = list( zip( years, ygigs ) )
        zipped.sort( key=lambda x: (-len(x[1]),x[0]), reverse = True )
        zipped.reverse()
        return zipped
    def get_unique_years(self,inc_future=False):
        if inc_future:
            if not self.unique_years_inc_future:
                self.unique_years_inc_future = self.generate_unique_years(inc_future)
            return self.unique_years_inc_future
        else:
            if not self.unique_years:
                self.unique_years = self.generate_unique_years(inc_future)
            return self.unique_years
    def artist_is_support(self,a):
        support_only = True
        for gig in self.all_gigs_of_artist(a):
            if gig.sets[0].artists[0].name == a:
                support_only = False 
                break
        return support_only
    def longest_gap(self):
        gaps = []
        gigs = self.get_past_gigs()
        gigs = [ x for x in gigs if x.date.year >= 2010 ]
        for i in range(1,len(gigs)):
            gap = gigs[i].date.toordinal() - gigs[i-1].date.toordinal() 
            gaps.append( [ gap, gigs[i-1], gigs[i] ] )
        cur_gap = [ datetime.today().toordinal() - gigs[-1].date.toordinal(), 
                    gigs[-1], None ]
        print( "\n  Current gap is %d days (since %s)." % \
                ( cur_gap[0], cur_gap[1].date.strftime("%d-%b-%Y")) )
        gaps.append(cur_gap)
        ngaps = 20
        gaps.sort(key=lambda x: -x[0])
        gaps = gaps[:ngaps]
        print( "\n  Longest gaps since 2010:\n" )
        for gap in gaps:
            date1 = gap[1].date.strftime("%d-%b-%Y") if gap[1] else '           '
            date2 = gap[2].date.strftime("%d-%b-%Y") if gap[2] else '           '
            print( "   %s days (%s -> %s)" % ( str(gap[0]).rjust(4), date1, date2 ) )
    def longest_run(self):
        runs = []
        gigs = self.get_past_gigs()
        current_run = [gigs[0]]
        last_g = gigs[0]
        for g in gigs[1:]:
            if g.date.toordinal() - last_g.date.toordinal() == 1:
                current_run.append(g)
            elif len(runs) == 0 or len(current_run) > len(runs[0]):
                runs = [ current_run ]
                current_run = [g]
            elif len(current_run) == len(runs[0]):
                runs.append(current_run)
                current_run = [g]
            else:
                current_run = [g]

            # if we're at the end, maybe add current run:
            if g == gigs[-1] and len(current_run) == len(runs[0]):
                runs.append(current_run)
            elif g == gigs[-1] and len(current_run) > len(runs[0]):
                runs = [ current_run ]

            last_g = g
            
        print( "\n  Longest run was %d gigs, which occurred %d times:\n" % ( len(runs[0]), len(runs) ) )
        for run in runs:
            for g in run:
                print( "    " + g.stub() )
            print( "" )
    def relative_progress(self):
        year = datetime.today().year
        yday = datetime.today().timetuple().tm_yday
        yweek = 7 % yday
        current_count = 0
        previous_counts = []

        gigs_by_year = self.get_unique_years()
        gigs_by_year.sort()

        # need to add hour > 20 logic to this calculation:

        for (y,c) in gigs_by_year:
            if y == year:
                for g in c:
                    if g.date.timetuple().tm_yday <= yday:
                        current_count += 1
                    else:
                        break
            elif y < year:
                previous_counts.append(0)
                for g in c:
                    if g.date.timetuple().tm_yday < yday:
                        previous_counts[-1] += 1
                    else:
                        break

        print( "" )
        print( "  Days into %d:  %d" % (year, yday) )
        print( "  Weeks into %d: %d" % (year, yweek) )
        print( "  Current count:   %d" % current_count )
        print( "  Previous counts: %s" % ",".join( str(x) for x in previous_counts) )

        rank = len(previous_counts) + 1
        for x in previous_counts:
            if x < current_count:
                rank -= 1

        print( "  %d rank:       %d/%d" % ( year, rank, 1+len(previous_counts)) )
        print( "  %d gigs/week:  %f" % ( year, current_count/yweek ) )
        print( "" )
    def growth(self):
        gigs_by_year = self.get_unique_years()
        gigs_by_year.sort(key=lambda x: x[0])
        all_venues = []
        all_artists = []
        n_venues = []
        n_artists = []
        for (y,c) in gigs_by_year:
            n_new_venues = 0
            n_new_artists = 0
            
            for g in c:
                if g.venue in all_venues:
                    pass
                else:
                    n_new_venues += 1
                    all_venues.append(g.venue)

                for s in g.sets:
                    if s.artists[0].name in all_artists:
                        pass
                    else:
                        n_new_artists += 1
                        all_artists.append(s.artists[0].name)

            n_venues.append(n_new_venues)
            n_artists.append(n_new_artists)

        print( n_venues )
        print( n_artists )

        #print( years )
    def print_fuzzy_matches(self,items,category = ''):
        from difflib import SequenceMatcher as SM
        min_ratio = 0.8
        n_items = len(items)
        matches = []
        for i in range(0,n_items-1):
            ti = items[i]
            for j in range(i+1,n_items-1):
                tj = items[j]
                ratio = SM(None, ti, tj).ratio()
                if ratio > min_ratio:
                    # print( "(%d %d) (%s, %s) %f" % ( i, j, ti, tj, ratio ) )
                    matches.append( [ ti, tj ] )
        if len(matches) > 0:
            print( '\n  ' + category + ':' )
            for match in matches:
                print( '    ' + ', '.join(match) )
    def fuzzy_matcher(self):
        artists = self.get_unique_artists()
        artists = [ x[0] for x in artists ]
        for a in artists:
            songs = self.get_unique_songs_of_artist(a)
            songs = [ x['title'] for x in songs ]
            self.print_fuzzy_matches(songs,a)
        venues = self.get_unique_venues()
        venues = [ x[0] for x in venues ]

        self.print_fuzzy_matches(artists, 'Artists')
        self.print_fuzzy_matches(venues, 'Venues')
    def get_covers(self,verbose=False):
        covers = []

        for g in self.gigs:
            for s in g.sets:
                for song in s.songs:
                    if song.cover:
                        this_dict = None
                        for cover in covers:
                            if cover['cover_artist'] == song.cover:
                                this_dict = cover
                                break
                        if this_dict == None:
                            this_dict = { 'cover_artist': song.cover,
                                          'count': 0,
                                          'songs': [],
                                          'artists': [],
                                          'gigs': [],
                                          }
                            covers.append( this_dict )

                        this_dict['count'] += 1

                        if song.title in this_dict['songs']:
                            idx = this_dict['songs'].index(song.title)
                        else:
                            idx = len(this_dict['songs'])
                            this_dict['songs'].append(song.title)
                            this_dict['artists'].append([])
                            this_dict['gigs'].append([])

                        this_dict['artists'][idx].append(s.artists[0].name)
                        this_dict['gigs'][idx].append(g)

        covers = sorted(covers, key=lambda x: x['cover_artist'], reverse=False )
        covers = sorted(covers, key=lambda x: x['count'], reverse=True )

        if verbose:
            for cover in covers:
                print( '\n===== ' + cover['cover_artist'] + ' (%d)' % cover['count'] ) 
                for s, artists, gigs in zip( cover['songs'], cover['artists'], cover['gigs'] ):
                    versions = []
                    for a, g in zip(artists,gigs):
                        link = g.date.strftime('%d-%b-%Y')
                        versions.append( '[%s %s]' % ( link, a ) )
                    versions.sort()
                    print( '      ' + s )
                    for v in versions:
                        print( '        ' + v )

        return covers
    def get_untitled(self):
        for g in self.gigs:
            for s in g.sets:
                for song in s.songs:
                    if not song.title:
                        print("=====")
                        print(g.date.strftime("%Y-%b-%d"))
                        quote = song.quote if song.quote else ""
                        print(s.artists[0].name.ljust(30) + '"' + quote + '"')
    def get_live_debuts(self):
        debuts = []
        for g in self.gigs:
            for s in g.sets:
                for song in s.songs:
                    if song.debut:
                        debuts.append( [ song.title, s.artists[0].name, g ] )

        debuts.sort(key=lambda x: x[2].date)

        for debut in debuts:
            print( "%s %s : %s" % ( debut[1], debut[2].date.strftime("%Y-%b-%d"), debut[0] ) )

        return debuts

    # Gig counts
    def gig_artist_times(self,gig,artist):
        # gig is the nth event of artist
        for s in gig.sets:
            if s.artists[0].name == artist:
                if not s.artisttimes:
                    artist_count = 0
                    total = 0
                    record = True
                    for agig in self.all_gigs_of_artist(artist):
                        total += 1
                        if record:
                            artist_count += 1
                        if gig.index == agig.index:
                            record = False
                    s.artisttimes = "%s/%s" % ( artist_count, total )
                return s.artisttimes
        return None
    def gig_venue_times(self,gig):
        # gig is the nth event at venue
        if not gig.venuetimes:
            venue_count = 0
            total = 0
            record = True
            for agig in self.all_gigs_of_venue(gig.venue):
                total += 1
                if record:
                    venue_count += 1
                if gig.index == agig.index:
                    record = False
            gig.venuetimes = "%s/%s" % ( venue_count, total )
        return gig.venuetimes
    def gig_city_times(self,gig):
        # gig is the nth event in city
        if not gig.citytimes:
            cities = self.unique_cities()
            city_count = 0
            total = 0
            record = True
            for (this_city,gigs_past,gigs_future) in cities:
                if this_city == gig.city:
                    for g in gigs_past:
                        total += 1
                        if record:
                            city_count += 1
                        if g.index == gig.index:
                            record = False
            gig.citytimes = "%s/%s" % ( city_count, total )
        return gig.citytimes
    def gig_year_times(self,gig):
        # gig is the nth event of the year
        year_count = 0
        total = 0
        record = True
        for (y,c) in self.get_unique_years():
            if y == gig.date.year:
                for g in c:
                    total += 1
                    if record:
                        year_count += 1
                    if g.index == gig.index:
                        record = False
        return "%s/%s" % ( year_count, total )
    def gig_song_times(self,gig,song,artist_songs):
        # gig is the nth time I have seen the song
        # artist_songs is cached by the caller for performance
        n_times = 0
        total = 0
        record = True
        for usong in artist_songs:
            if song.title == usong['title']:
                for e in usong['events']:
                    total += 1
                    if record:
                        n_times += 1
                    if e.index == gig.index:
                        record = False
        n_times += song.count - 1
        return "%s/%s" % ( n_times, total )

    def animate_growth(self):
        import subprocess
        # need to count 
        for g in self.gigs:
            if g.date > datetime.today():
                break
            prefix = 'anim_%s' % str(g.index).zfill(3)
            # print('plotting ' + prefix)
            # plotter = GIG_plot(self)
            # plotter.year_growth(    'anim/' + prefix + '_y.png', g.date )
            # plotter.total_progress( 'anim/' + prefix + '_t.png', g.date )
            # plotter.artist_growth(  'anim/' + prefix + '_a.png', g.date )
            # plotter.venue_growth(   'anim/' + prefix + '_v.png', g.date )
            #joined = 'joined_%s.png' % str(g.index).zfill(3)
            #subprocess.call(['convert', '-append', 'anim/' + prefix + '_*.png', 'anim/' + joined ])
            #print(joined)

        subprocess.call(['convert','-delay','5','-loop','1','anim/joined_*.png','anim_joined.gif'])
        print('joined.png')

        # subprocess.call(['convert','-delay','5','-loop','1','anim/*_y.png','anim_y.gif'])
        # print('made anim_y.gif')
        # subprocess.call(['convert','-delay','5','-loop','1','anim/*_t.png','anim_t.gif'])
        # print('made anim_t.gif')
        # subprocess.call(['convert','-delay','5','-loop','1','anim/*_a.png','anim_a.gif'])
        # print('made anim_a.gif')
        # subprocess.call(['convert','-delay','5','-loop','1','anim/*_v.png','anim_v.gif'])
        # print('made anim_v.gif')

class GIG_gig():
    def __init__(self, date, venue):
        self.index  = 0
        self.date   = date
        self.venue  = venue.replace('_',' ')
        self.city   = venue.split()[0].replace('_',' ')
        self.country = None
        self.venue_nocity = " ".join(venue.split()[1:]).replace('_',' ')
        self.sets   = []
        today = datetime.today()
        self.future = date > today or ( date.date() == today.date() and today.hour < 20 )
        self.link    = ''
        self.citytimes = None
        self.venuetimes = None
        # self.img should really be the same as self.link 
        # (so multiple gigs per day can have individual images). 
        # But that would require renaming all the existing images.
        # More importantly, the images would need renaming every time 
        # a gig was added retrospectively (thus incrementing all subsequent gig indices).
        self.img     = 'img/' + date.strftime('%Y_%m_%d') + '.gif'
        self.artists = None # cached
    def __str__(self):
        # print formatter
        string = ""
        string += "\n    Date: " + self.date.strftime('%A %d %B, %Y')
        string += "\n   Venue: " + self.venue
        for s in self.sets:
            string += "\n  Artist: " + s.artists[0].name
            for song in s.songs:
                string += "\n          > " + song.title if song.title else "???"
        string += "\n"
        return string
    def print_short(self):
        date = self.date.strftime('%d-%b-%Y')
        venue = self.venue
        artist_list = [ s.artists[0].name for s in self.sets ]
        artists = artist_list[0]
        if len(artist_list) > 1:
            artists += ' + ' + artist_list[1]
        if len(artist_list) > 2:
            artists += ' + ... '
        ident = '[' + self.index + ']'
        print( ' {0:8s} {1:15s} {2:30s} {3:20s}' . format( ident, date, venue, artists) )
    def append_set(self,s):
        self.sets.append(s)
    def add_dummy_sets_for_guests(self,data):
        # Adds empty sets for song guests
        # If guests appear in a songflag but not in a set of their own, we must
        # add a dummy set (marked "guest_only") to ensure they are included in
        # the artist statistics.

        addarts = []
        artists = [ x.artists[0].name for x in self.sets ]

        for s in self.sets:
            for song in s.songs:
                for g in song.guests:
                    if not g in artists and not g in addarts:
                        addarts.append(g)

        # Remember that the footnote numbering will be derived from the index in setlist array!
        # Examples to check:
        #   2019_15 (Neil Young footnote in Bob Dylan guest appearance)
        #   2017_17 (John Cale guests)
        #   2017_30 (Matthew E. White guests)

        for a in addarts:
            aa = data.find_artist(a)
            this_set = GIG_set([aa])
            this_set.guest_only = True
            self.sets.append(this_set)

        # Now we also add dummy sets for band members who are explicity named:

        band_artists = []
        for s in self.sets:
            for b in s.band:
                band_artists.append(b)

        for b in band_artists:
            bb = data.find_artist(b)
            this_set = GIG_set([bb])
            this_set.band_only = True
            self.sets.append(this_set)
    def get_artists(self):
        if not self.artists:
            self.artists = []
            for s in self.sets:
                if not s.artists[0].name in self.artists:
                    self.artists.append(s.artists[0].name)
        return self.artists
    def stub(self):
        # short printer
        headliner = self.sets[0].artists[0].name
        date = self.date.strftime("%d-%b-%Y (%a)")
        return "%s %s   %s" % (headliner.ljust(20), date, self.venue )

class GIG_set():
    def __init__(self, artists):
        self.artists    = artists[0:1]
        self.songs      = []
        self.band       = [a.name for a in artists[1:]]
        # flags
        self.ordered    = True
        self.guest_only = False
        self.band_only  = False
        self.solo       = False
        self.playlist   = ''
        self.artisttimes = 0
    def append_song(self, song):
        self.songs.append(song)

class GIG_song():
    def __init__(self, title):
        self.title       = title
        # flags
        self.medley      = False
        self.guests      = []
        self.missing     = []
        self.solo        = False
        self.first_time  = False
        self.set_opener  = False
        self.debut       = False
        self.improv      = False
        self.request     = False
        self.quote       = None
        self.cover       = None
        self.custom      = []
        self.count       = 0

class GIG_query():
    def __init__(self,gig_data,opts):
        self.gig_data   = gig_data
        self.date     = None
        self.venue    = None
        self.artist   = None
        self.song     = None
        self.index    = None
        self.stats    = False
        self.empty    = True
        self.results  = None
        self.parse_query(opts)
        self.query_gigs()
    def parse_query(self,opts):
        if opts.artist:
            self.artist = opts.artist
            self.empty = False
        elif opts.venue:
            self.venue = opts.venue
            self.empty = False
        elif opts.song:
            self.song = opts.song
            self.empty = False
        elif opts.date:
            self.date = opts.date
            self.empty = False
        elif opts.index:
            self.index = opts.index
            self.empty = False
        elif opts.stats:
            self.stats = True
            self.empty = False
    def query_gigs(self):
        self.results = []
        for gig in self.gig_data.gigs:
            if gig.future:
                pass
            elif not self.index:
                match = True
                if match and self.date:
                    match = False
                    if self.date.isdigit() and len(self.date) == 4:
                        # it's a year
                        if gig.date.year == int(self.date):
                            match = True
                    if self.date.isalpha():
                        # it's a month
                        if re.search( self.date, gig.date.strftime("%B"),re.IGNORECASE): 
                            match = True
                if match and self.venue and not re.search(self.venue,gig.venue,re.IGNORECASE):
                    match = False
                if match and self.artist:
                    match = False
                    artists = gig.get_artists()
                    for a in artists:
                        if re.search(self.artist,a,re.IGNORECASE):
                            match = True
                            break
                if match and self.song:
                    match = False
                    titles = []
                    for s in gig.sets:
                        titles += [ x.title for x in s.songs if x.title ]
                    for t in titles:
                        if re.search(self.song,t,re.IGNORECASE):
                            match = True
                            break
                if match:
                    self.results.append(gig)
            elif self.index and self.index == gig.index:
                self.results.append(gig)
                break
    def print_results(self):
        if self.stats and self.artist:
            self.gig_data.artist_stats( self.artist )
        elif len(self.results) == 1:
            print(self.results[0])
        else:
            self.results.sort(key=lambda x: x.index)
            print( "\n %d matching events.\n" % len(self.results) )
            for gig in self.results:
                gig.print_short()
            print( '\n' )
        
