#!/usr/bin/python3
import sys, os, glob, re
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date

class GIG_plot():
    def __init__(self, gig_data):
        self.gig_data = gig_data
        self.n_graphs = 0
        self.colour1  = '#153E7E' # blue
        self.colour2  = '#C9BE62' # yellow
        self.colour3  = '#CCCCCC' # grey
        self.colour4  = 'red'     # red
        self.year     = datetime.today().year
    def top_venue_growth(self,top_n=5,dest=None):
        self.n_graphs += 1

        fig, ax = plt.subplots()
        venues = self.gig_data.get_unique_venues()[0:top_n]
        first_date = self.gig_data.get_unique_years()[0][1][0].date
        all_dates = [ first_date ]
        vnames = []
        for (v,gs) in venues:
            vnames.append(v)
            for g in gs:
                all_dates.append(g.date)

        all_dates.sort()

        for (v,gs) in venues:
            counts = []
            for d in all_dates:
                counts.append(0)

            for g in gs:
                indx = all_dates.index(g.date)
                for i in range(indx,len(all_dates)):
                    counts[i] += 1
            plt.plot(all_dates,counts,linewidth=2)

        ax.legend(vnames,'upper left')
        ax.set_xlim(datetime(all_dates[0].year-1,1,1),datetime(all_dates[-1].year+1,1,1))
        ax.set_ylim(-1,len(venues[0][1])+1)
        ax.set_axisbelow(True)
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')

        plt.title("Venue Growth (Top %d)" % top_n)
        fig.canvas.set_window_title("Figure %d" % self.n_graphs)

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
            plt.show()
    def top_venues(self,top_n=5,dest=None):
        self.n_graphs += 1

        fig, ax = plt.subplots()
        venues = self.gig_data.get_unique_venues()[0:top_n]

        names = [ v[0] for v in venues ]
        counts = [ len(v[1]) for v in venues ]
        ind = list(range(len(counts)))

        bar1 = ax.bar( ind, counts, align='center', color=self.colour1 )

        plt.xticks(ind,names,rotation='vertical')

        ax.set_axisbelow(True)
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')

        plt.title("Top Venues (Top %d)" % top_n)
        fig.canvas.set_window_title("Figure %d" % self.n_graphs)

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
            plt.show()
    def artist_growth(self,dest=None,end_date=None):
        fig, ax = plt.subplots()

        self.n_graphs += 1

        y_gigs = self.gig_data.get_unique_years()
        y_gigs.sort()
        years = []
        n_artists = []
        n_new_artists = []
        all_artists = []
        n_new_headliners = []

        max_y_axis = 90

        for (y,c) in y_gigs:
            y_artists = []
            years.append(y)
            n_artists.append(0)
            n_new_artists.append(0)
            n_new_headliners.append(0)
            for g in c:
                if end_date and g.date > end_date:
                    continue
                set_index = 0
                for s in g.sets:
                    if s.artist in y_artists:
                        pass
                    else:
                        y_artists.append(s.artist)
                        n_artists[-1] += 1

                    if s.artist in all_artists:
                        pass
                    else:
                        all_artists.append(s.artist)
                        n_new_artists[-1] += 1
                        if set_index == 0:
                            n_new_headliners[-1] += 1
                    set_index += 1
        
        ind = range(1,len(years)+1)
        bar1 = ax.bar( ind, n_artists,        align='center', color=self.colour1 )
        bar2 = ax.bar( ind, n_new_artists,    align='center', color=self.colour2 )
        bar3 = ax.bar( ind, n_new_headliners, align='center', color=self.colour3 )
        plt.xticks(ind,[str(xx)[2:4] for xx in years])

        if not end_date:
            plt.legend((bar1[0], bar2[0], bar3[0]), \
                       ('Total artists', 'New artists', 'New headliners'), \
                       'upper left')

        ax.set_axisbelow(True)
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')
        if end_date:
            plt.ylim( [ 0, max_y_axis ] )

        plt.xlim( [0, len(years)+1] )

        #plt.title("Total artists seen per year")
        fig.canvas.set_window_title("Figure %d" % self.n_graphs)

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
    def month_growth(self,dest=None):
        self.n_graphs += 1
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        month_totals = [0] * 12
        curr_totals = [0] * 12
        year_months = []

        for (y,c) in self.gig_data.get_unique_years():
            y_totals = [0] * 12
            for gig in c:
                i = int(gig.date.strftime("%m"))
                if gig.date.year == self.year:
                    curr_totals[i-1] += 1
                month_totals[i-1] += 1
                y_totals[i-1] += 1
            year_months.append(y_totals)

        month_maxima = []
        for x in range(0,12):
            month_maxima.append( max( [ y[x] for y in year_months ] ) )

        fig, ax = plt.subplots()
        ind = range(1,len(months)+1)

        bar1 = ax.bar( ind, month_totals,  align='center', color=self.colour1 )
        #bar2 = ax.bar( ind, month_maxima,  align='center', color=self.colour3 )
        bar3 = ax.bar( ind, curr_totals,   align='center', color=self.colour2 )

        plt.xticks(ind,months)
        ax.set_axisbelow(True)
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')
        plt.xlim([0,len(ind)+1])
        # plt.legend( (bar1[0],bar3[0],bar2[0]), \
        #             ('Events in month', '%d events' % self.year, 'Month max'), \
        #             'upper left' )
        plt.legend( (bar1[0],bar3[0]), \
                    ('Events in month', '%d events' % self.year), \
                    'upper left' )

        #plt.title("Month histogram")
        fig.canvas.set_window_title("Figure %d" % self.n_graphs)

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
    def days_growth(self,dest=None):
        self.n_graphs += 1

        days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        day_totals = [0] * 7
        curr_totals = [0] * 7
        for gig in self.gig_data.get_past_gigs():
            i = int(gig.date.strftime("%w"))
            if gig.date.year == self.year:
                curr_totals[i-1] += 1
            day_totals[i-1] += 1

        fig, ax = plt.subplots()
        ind = range(1,len(day_totals)+1)
        bar1 = ax.bar( ind, day_totals, align='center', color=self.colour1 )
        bar2 = ax.bar( ind, curr_totals, align='center', color=self.colour2 )
        plt.xticks(ind,days)
        ax.set_axisbelow(True)
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')
        plt.legend((bar1[0], bar2[0]), ('Events in day','%d events' % self.year), 'upper left')
        fig.canvas.set_window_title("Figure %d" % self.n_graphs)

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
    def year_growth(self,dest=None,end_date=None):
        self.n_graphs += 1

        fig, ax = plt.subplots()
        y_gigs = self.gig_data.get_unique_years(True)
        y_gigs.sort()

        yday = datetime.today().timetuple().tm_yday
        if end_date:
            yday = end_date.timetuple().tm_yday
        years = []
        total_counts = []
        relative_counts = []
        future_counts = []  # total + future

        max_y_axis = 45

        for (y,c) in y_gigs:
            years.append(y)
            relative_counts.append(0)
            total_counts.append(0)
            future_counts.append(0)
            for g in c:
                if end_date and g.date > end_date:
                    continue
                future_counts[-1] += 1
                if not g.future:
                    total_counts[-1] += 1
                    if g.date.timetuple().tm_yday <= yday:
                        relative_counts[-1] += 1
            if y == self.year:
                break

        ind = range(1,len(years)+1)
        if not end_date:
            bar0 = ax.bar( ind, future_counts,   align='center', color=self.colour3 )
        bar1 = ax.bar( ind, total_counts,    align='center', color=self.colour1 )
        bar2 = ax.bar( ind, relative_counts, align='center', color=self.colour2 )
        plt.xticks(ind,[str(xx)[2:4] for xx in years])

        today = datetime.today()
        ordinal = lambda n: str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))
        datestr = str(ordinal(today.day)) + today.strftime(" %b")
        plt.legend((bar1[0],), ('Events up to %s' % datestr,), 'upper left')

        if not end_date:
            plt.legend((bar1[0], bar2[0], bar0[0]), ('Total events', \
                'Events up to %s' % datestr, \
                'Projected total' ), 'upper left' )

        ax.set_axisbelow(True)
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')
        if end_date:
            plt.ylim( [ 0, max_y_axis ] )

        plt.xlim( [0, len(years)+1] )

        #plt.title("Year Histogram")
        fig.canvas.set_window_title("Figure %d" % self.n_graphs)

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
    def venue_growth(self,dest=None,end_date=None):
        fig, ax = plt.subplots()

        self.n_graphs += 1

        y_gigs = self.gig_data.get_unique_years()
        y_gigs.sort()
        years = []
        n_venues = []
        n_new_venues = []
        all_venues = []
        all_cities = []
        n_new_cities = []

        max_y_axis = 30

        for (y,c) in y_gigs:
            y_venues = []
            years.append(y)
            n_venues.append(0)
            n_new_venues.append(0)
            n_new_cities.append(0)
            for g in c:
                if end_date and g.date > end_date:
                    continue
                if g.venue in y_venues:
                    pass
                else:
                    y_venues.append(g.venue)
                    n_venues[-1] += 1
                    if g.city in all_cities:
                        pass
                    else:
                        all_cities.append(g.city)
                        n_new_cities[-1] += 1

                if g.venue in all_venues:
                    pass
                else:
                    all_venues.append(g.venue)
                    n_new_venues[-1] += 1

        ind = range(1,len(years)+1)
        bar1 = ax.bar( ind, n_venues,     align='center', color=self.colour1 )
        bar2 = ax.bar( ind, n_new_venues, align='center', color=self.colour2 )
        bar3 = ax.bar( ind, n_new_cities, align='center', color=self.colour3 )
        plt.xticks(ind,[str(xx)[2:4] for xx in years])
        if end_date:
            plt.ylim( [ 0, max_y_axis ] )

        if not end_date:
            plt.legend((bar1[0], bar2[0], bar3[0]), \
                       ('Total venues', 'New venues', 'New cities'), \
                       'upper left')

        ax.set_axisbelow(True)
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')

        plt.xlim( [0, len(years)+1] )

        #plt.title("Total venues seen per year")
        fig.canvas.set_window_title("Figure %d" % self.n_graphs)

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
    def freq_dist(self,dest=None):
        self.n_graphs += 1

        fig, ax = plt.subplots()
        a_gigs = self.gig_data.get_unique_artists()

        freq = [ 0 ] * len(a_gigs[0][1] )

        for (a,c) in a_gigs:
            freq[ len(c) - 1 ] += 1

        ind = range(1,len(freq)+1)
        bar1 = ax.bar( ind, freq, align='center', color=self.colour1 )
        plt.xticks(ind, [ str(i+1) if freq[i] > 0 else "" for i in range(0,len(freq)) ] )
        plt.legend((bar1[0],), ('Artist frequency distribution',), 'upper right')
        ax.set_axisbelow(True)
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')

        #plt.title("Frequency Distribution of Artists")
        fig.canvas.set_window_title("Figure %d" % self.n_graphs)

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
            plt.show()
    def relative_progress(self,dest=None):
        self.n_graphs += 1

        yday = datetime.today().timetuple().tm_yday

        gig_counts = []
        gig_years = []

        gigs_by_year = self.gig_data.get_unique_years()
        gigs_by_year.sort()

        for (y,c) in gigs_by_year:
            gig_years.append(y)
            gig_counts.append(0)
            for g in c:
                if g.date.timetuple().tm_yday <= yday:
                    gig_counts[-1] += 1
            
        #print( "gig_counts: %s" % ",".join( str(x) for x in gig_counts ) )

        fig, ax = plt.subplots()

        ind = range(1,len(gig_counts)+1)
        bar1 = ax.bar( ind, gig_counts, align='center', color=self.colour1 )
        plt.xticks(ind, [str(xx)[2:4] for xx in gig_years] )

        today = datetime.today()
        ordinal = lambda n: str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))
        datestr = str(ordinal(today.day)) + today.strftime(" %b")
        plt.legend((bar1[0],), ('Events up to %s' % datestr,), 'upper left')

        #plt.title("Relative Progress")
        fig.canvas.set_window_title("Figure %d" % self.n_graphs)
        plt.ylim([0,max(gig_counts)+1])
        ax.set_axisbelow(True)
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
            plt.show()
    def total_progress(self,dest=None,end_date=None):
        self.n_graphs += 1

        gigs_by_year = self.gig_data.get_unique_years()
        gigs_by_year.sort()

        running_total = 0
        totals = []
        dates = []
        years = []

        max_y_axis = 420

        for (y,c) in gigs_by_year:
            # running_total += 1 # comment this out for cumulative annual count
            years.append(datetime.strptime(str(y),"%Y"))
            for g in c:
                if end_date and g.date > end_date:
                    continue
                running_total += 1
                totals.append(running_total)
                dates.append(g.date)
            
        #print( "gig_counts: %s" % ",".join( str(x) for x in gig_counts ) )
        fig, ax = plt.subplots()

        line1 = plt.plot(dates,totals,color=self.colour1) #,linewidth=2.0)
        plt.xticks(years,[xx.strftime("%y") for xx in years])

        if not end_date:
            plt.legend((line1[0],), ('Cumulative event count',), 'upper left')

        ax.set_axisbelow(True)
        ax.fill_between(dates, 0, totals, color=self.colour1)

        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')
        plt.xlim([datetime.strptime(str(years[0].year-1),"%Y"),
                  datetime.strptime(str(years[-1].year+1),"%Y")])
        if end_date:
            plt.ylim( [ 0, max_y_axis ] )

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
            plt.show()
    def total_progress_by_year(self,dest,year):
        gigs = None

        for (y,c) in self.gig_data.get_unique_years(True):
            if y == year:
                gigs = c

        running_total = 0
        totals = []
        dates = []
        bob_totals = []
        bob_dates = []
        future_dates = []
        future_totals = []
        
        if gigs == None:
            return False

        for g in gigs:
            running_total += 1
            if 'Bob Dylan' in g.get_artists():
                bob_totals.append(running_total)
                bob_dates.append(g.date)
            if g.future:
                future_dates.append(g.date)
                future_totals.append(running_total)
            else:
                totals.append(running_total)
                dates.append(g.date)
                future_dates = [ g.date ]
                future_totals = [ running_total ]

        months = [ date(year=year, month=x, day=1) for x in range(1,13) ]

        fig, ax = plt.subplots()

        if len(dates) > 1:
            line1 = plt.plot(dates,totals,color=self.colour1) #,linewidth=2.0)
        if len(future_dates) > 1:
            line2 = plt.plot(future_dates,future_totals,color=self.colour1,ls='--')
        dots1 = plt.plot(dates,totals,color=self.colour2,marker='o',ls='')
        dots2 = plt.plot(bob_dates,bob_totals,color=self.colour4,marker='o',ls='')

        plt.xticks(months, [x.strftime(" %b") for x in months], ha='left')
        if running_total <= 10:
            plt.yticks(range(1,11))

        #ax.set_axisbelow(True)
        ax.fill_between(dates, 0, totals, color=self.colour1)

        plt.xlim([ date(year=year, month=1, day=1), date(year=year, month=12, day=31) ])
        plt.ylim([0,45])
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')

        fig.savefig(dest, bbox_inches='tight')
        plt.close()

        return True
    def song_breakdown(self,artist,events,unique_songs,dest=None):
        event_idx = list(range(1,len(events)+1))
        new_songs = [0 for event in events]
        
        for song in unique_songs:
            index = 0
            for event in events:
                if event in song['events']:
                    new_songs[index] += 1
                    break
                index += 1

        for i in range(1,len(events)):
            new_songs[i] += new_songs[i-1]

        #print(event_idx)
        #print(new_songs)

        fig, ax = plt.subplots()
        ax.set_axisbelow(True)
        ax.margins(0.05)

        line1 = plt.plot(event_idx,new_songs,marker='.')

        # plotting against date rather than index breaks something in plt:
        #dates = [e.date.date() for e in events]
        #line1 = plt.plot(dates,new_songs,marker='.')

        plt.legend((line1[0],), ('Unique song count',), 'upper left')
        plt.grid(b=True, which='both')
        plt.xlim( 0, len(events)+1 )

        if dest:
            fig.savefig( dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
            plt.show()
    def song_freq_dist(self,unique_songs,dest=None):
        counts = [ len(s['events']) for s in unique_songs ]
        max_count = max(counts)

        fig, ax = plt.subplots()
        ax.set_axisbelow(True)
        
        index = []
        f_dist = []
        for x in range(1,max_count+1):
            index.append(x)
            f_dist.append( counts.count(x) )

        bar1 = ax.bar( index, f_dist, align='center', color=self.colour1 )
        plt.xticks(index)

        if len(index) > 10:
            for label in ax.xaxis.get_ticklabels()[::2]:
                label.set_visible(False)

        plt.legend( (bar1[0],), ('Freq dist',), 'upper right' )
        plt.grid(b=True, which='both') #, color='0.65',linestyle='-')
        fig.canvas.set_window_title("Figure %d" % self.n_graphs)

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
    def activity(self,dest=None):
        dates = [ x.date for x in self.gig_data.get_past_gigs() ]
        dates.sort()

        which = 'weeks'
        which = 'months'
        which = 'days'
        which = 'years'

        divisions = []
        gigcounts = []

        if which == 'days':
            cur_day = dates[0]
            last_day = dates[-1]

            divisions = []
            while cur_day <= last_day:
                divisions.append(cur_day)
                cur_day += timedelta(days=1)

            gigcounts = [0] * len(divisions)
            for d in dates:
                pos = divisions.index(d)
                gigcounts[pos] += 1
        elif which == 'weeks':
            weekstart = lambda d: d - timedelta(days=d.weekday())

            one_week = timedelta(days=7)
            cur_week = weekstart(dates[0])
            last_week  = weekstart(dates[-1])

            divisions = []
            while cur_week <= last_week:
                divisions.append(cur_week)
                cur_week += one_week

            gigcounts = [0] * len(divisions)
            for d in dates:
                pos = divisions.index(weekstart(d))
                gigcounts[pos] += 1
        elif which == 'months':
            monthstart = lambda d: date( year=d.year, month=d.month, day=1 )
            addmonth = lambda d: date( year = int(d.year + d.month / 12 ),
                                       month = d.month % 12 + 1, day = 1 )

            cur_month = monthstart(dates[0])
            last_month = monthstart(dates[-1])

            divisions = []
            while cur_month <= last_month:
                divisions.append(cur_month)
                cur_month = addmonth(cur_month)
            
            gigcounts = [0] * len(divisions)
            for d in dates:
                pos = divisions.index(monthstart(d))
                gigcounts[pos] += 1
        elif which == 'years':
            cur_year = dates[0].year
            last_year = dates[-1].year

            divisions = []
            while cur_year <= last_year:
                divisions.append(cur_year)
                cur_year += 1

            gigcounts = [0] * len(divisions)
            for d in dates:
                pos = divisions.index(d.year)
                gigcounts[pos] += 1
            
        fig, ax = plt.subplots()
        #bar1 = ax.bar(divisions, gigcounts, align='center', color=self.colour1 )
        line1 = plt.plot(divisions, gigcounts, color=self.colour1)
        ax.fill_between(divisions, 0, gigcounts, color=self.colour1)

        ax.set_axisbelow(True)
        plt.grid(b=True, which='both')

        if dest:
            fig.savefig(dest, bbox_inches='tight')
            plt.close()
        else:
            plt.show(block=False)
            plt.show()

class GIG_html():
    def __init__(self, gig_data, head, playlists = False):
        self.gig_data = gig_data
        self.head = head
        self.plotter = GIG_plot(gig_data)

        # optional extras:
        self.do_covers = True           # mark covers
        self.do_playlists = playlists   # add playlist links and index
        self.do_solo_sets = False       # mark solo sets
        self.do_songcount = True        # count song occurrences (SLOW)
        self.do_graphs    = True

        # do the work:
        self.years = [ str(y) for (y,c) in self.gig_data.get_unique_years(True) ]
        self.years.sort()
        if self.do_playlists:
            gig_data.fill_in_playlist_links()
        self.generate_html_files()

    # HTML Generation
    def id_of_artist(self,artist):
        counter = 0
        for (a,c) in self.gig_data.get_unique_artists():
            counter += 1
            if artist == a:
                break
        return str(counter).zfill(3)
    def id_of_venue(self,venue):
        counter = 0
        for (v,c) in self.gig_data.get_unique_venues():
            counter += 1
            if venue == v:
                break
        return str(counter).zfill(3)
    def id_of_city(self,city):
        counter = 0
        cities = self.gig_data.unique_cities()
        for (this_city,gigs_past,gigs_future) in cities:
            counter += 1
            if city == this_city:
                break
        return str(counter).zfill(3)
    def gig_prev(self,gigs,gig):
        g_prev = None
        for g in gigs:
            if gig.index == g.index:
                break
            g_prev = g
        return g_prev
    def gig_next(self,gigs,gig):
        g_next = None
        set_next = False
        for g in gigs:
            if set_next:
                g_next = g
                break
            if gig.index == g.index:
                set_next = True;
        if g_next != None and g_next.future:
            g_next = None
        return g_next
    def footnote_symbol(self,n):
        return '<sup>' + str(n) + '</sup>'
    def make_flag_note(self, ftype, force_title = None, force_symbol = None ):
        if ftype == 'solo':
            return '<div class=flag title="Solo performance">&sect;</div>'
        elif ftype == 'improv':
            return '<div class=flag title="Improvisation">&#8225;</div>' # double dagger
        elif ftype == 'debut':
            return '<div class=flag title="Live debut">@</div>'
        elif ftype == 'first_time':
            return ''
            # disabled as buggy and not very helpful...
            #return '<div class=flag title="First time I\'ve seen it!">!</div>'
        elif ftype == 'guest':
            return '<div class=flag title="' + force_title + '">' + force_symbol + '</div>'
        elif ftype == 'custom':
            force_title = force_title[0].upper() + force_title[1:].lower()
            return '<div class=flag title="' + force_title + '">*</div>'
        else:
            return ''
    def gig_setlist_string(self,gig,linkback = True, liszt = None, suffix = None ):
        # linkback means whether to add artist/venue links
        ordinal = lambda n: str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))
        day = int(gig.date.strftime("%d"))

        # list of all guesting artists (so we know whether we need footnotes):
        gig_guests = []
        for g in gig.sets:
            for s in g.songs:
                gig_guests += s.guests
        gig_guests = list(set(gig_guests))

        link_prev = ''
        link_next = ''

        if linkback:
            # compute next/previous links
            if liszt == None:
                g_prev = self.gig_prev(self.gig_data.gigs,gig)
                g_next = self.gig_next(self.gig_data.gigs,gig)
            else:
                g_prev = self.gig_prev(liszt,gig)
                g_next = self.gig_next(liszt,gig)

            fname_prev = '""'
            fname_next = '""'

            if g_prev != None:
                fname_prev = g_prev.link
                if suffix != None:
                    fname_prev += suffix
            if g_next != None:
                fname_next = g_next.link
                if suffix != None:
                    fname_next += suffix
            
            link_prev = '<a href=' + fname_prev + '.html>&lt;</a>'
            link_next = '<a href=' + fname_next + '.html>&gt;</a>'

        cf_fname = ''
        vg_fname = ''
        yg_fname = ''
        vsplits = gig.venue.split()
        if linkback:
            cf_fname = gig.link + '_c' + self.id_of_city(vsplits[0]) + '.html'
            vg_fname = gig.link + '_v' + self.id_of_venue(gig.venue) + '.html'
            yg_fname = gig.link + '.html'

        ccount = self.gig_data.gig_city_times(gig)
        vcount = self.gig_data.gig_venue_times(gig)
        ycount = self.gig_data.gig_year_times(gig)

        clink = '<a href=' + cf_fname + ' title="Citycount: ' + ccount + '">' + vsplits[0] + '</a>'
        vlink = '<a href=' + vg_fname + ' title="Venuecount: ' + vcount + '">' + " ".join(vsplits[1:]) + '</a>'
        ylink = '<a href=' + yg_fname + ' title="Yearcount: ' + ycount + '">' + gig.date.strftime("%Y") + '</a>' 
        setlist_string = '<div class=sl_title>\n' + clink + ' ' + vlink + '<br>' + \
                    link_prev + link_next + ' ' + \
                    ordinal(day) + gig.date.strftime(" %B, ") + ylink + '</div>' + '\n'

        # artists = [ x[0] for x in self.gig_data.get_unique_artists() ]

        main_artists = [ s.artist for s in gig.sets if not s.guest_only ]

        for g in gig.sets:
            art_songs = []
            if self.do_songcount:
                # Calculate the number of times I have seen the song.
                # This is very slow. We need to cache the song data.
                art_songs = self.gig_data.unique_songs_of_artist(g.artist)

            playlist_link = ''
            if self.do_playlists and g.playlist:
                playlist_link = '\n<a href="' + g.playlist + '">&raquo;</a>\n'

            if g.band_only:
                # if it's a dummy set for a band member, don't display it
                continue
            ag_fname = ''
            if linkback:
                ag_fname = gig.link + '_a' + self.id_of_artist(g.artist) + '.html'

            acount = self.gig_data.gig_artist_times(gig,g.artist)
            alink = '<a href=' + ag_fname + ' title="Artistcount: ' + acount + '">' + g.artist + '</a>'

            if g.solo and self.do_solo_sets:
               alink += ' ' + self.make_flag_note('solo')
            if g.guest_only:
                alink = '(' + alink + ')'

            asymbol = ''
            if g.artist in gig_guests:
                asymbol = self.footnote_symbol( gig.get_artists().index(g.artist) )

            if g.guest_only:
                continue
                #fn = self.make_flag_note( 'guest', "Only as a guest in another set", asymbol ) 
                #setlist_string += '\n<br> ' + alink + ' ' +  fn
            else:
                fn = self.make_flag_note( 'guest', "+ Guested in another set", asymbol ) 
                setlist_string += '\n<br> ' + alink + ' ' + fn

            setlist_string += playlist_link

            band_string = ''
            if g.band:
                band_links = []
                for b in g.band:
                    acount = self.gig_data.gig_artist_times(gig,b)
                    bg_fname = gig.link + '_a' + self.id_of_artist(b) + '.html'
                    blink = '<a href=' + bg_fname + ' title="Artistcount: ' + acount + '">' + b + '</a>'
                    band_links.append(blink)
                band_string = '\n<br><br>' + self.sp(3) + '[Featuring ' + ', '.join(band_links) + ']'
            setlist_string += band_string

            proc_guests = []
            for s in g.songs:
                for guest in s.guests:
                    if guest in main_artists:
                        continue
                    if guest in proc_guests:
                        continue
                    elif not proc_guests and not band_string:
                        setlist_string += '<br>'
                    a_indx = gig.get_artists().index(guest)
                    ag_fname = gig.link + '_a' + self.id_of_artist(guest) + '.html'
                    acount = self.gig_data.gig_artist_times(gig,guest)
                    glink = '<a href=' + ag_fname + ' title="Artistcount: ' + acount + '">' + guest + '</a>'
                    setlist_string += '\n<br>' + self.sp(3) + '[Guesting ' + glink + ' '
                    setlist_string += self.make_flag_note( 'guest', '+ ' + guest, 
                                                            self.footnote_symbol(a_indx) )
                    setlist_string += ']'
                    proc_guests.append(guest)

            list_tag = 'ol' if g.ordered else 'ul'

            if len(g.songs) > 0:
                setlist_string += '\n<' + list_tag + '>'

                for s in g.songs:
                    if self.do_songcount:
                        song_times = self.gig_data.gig_song_times(gig,s,art_songs)

                    sn = s.title if s.title else '???'
                    if sn == '???':
                        if s.quote != None:
                            sn = '<div title=' + s.quote + '>' + sn + '</div>'
                    elif self.do_songcount:
                        sn = '<div class=greyflag title="Songcount: ' + song_times + '">' + sn + '</div>'
                        #sn += ' [%d]' % n_times
                    if s.set_opener:
                        setlist_string += '\n<br><br>'
                    if s.medley:
                        joiner = '' # could be '&gt; ' or '+ '
                        setlist_string += '\n<br>' + joiner + sn + ' '
                    else:
                        setlist_string += '\n<li>' + sn + ' '
                    if s.improv:
                        setlist_string += self.make_flag_note('improv')
                    if s.solo:
                        setlist_string += self.make_flag_note('solo')
                    if s.debut:
                        setlist_string += self.make_flag_note('debut')
                    if s.first_time:
                        setlist_string += self.make_flag_note('first_time')
                    if s.cover and self.do_covers:
                        symbol = '&curren;'
                        symbol = '*'
                        setlist_string += '<div class=flag title="' + s.cover + \
                                          ' cover">' + symbol + '</div>'
                    for guest in s.guests:
                        if guest in gig.get_artists():
                            a_indx = gig.get_artists().index(guest)
                            setlist_string += ' ' + self.make_flag_note( 'guest', '+ ' + guest, 
                                                                   self.footnote_symbol(a_indx) )
                    if s.custom:
                        custom_text = ' / '.join(s.custom)
                        setlist_string += self.make_flag_note( 'custom', custom_text )
                    if s.youtube:
                        setlist_string += self.make_youtube_link(s.youtube)

                setlist_string += '\n</' + list_tag + '>'
            else:
                setlist_string += '<br>'

        return setlist_string
    def make_file( self, filename, years_string, gigs_string, setlist_string, img = ""):
        # writes lines to file
        fname_html = self.head + filename + '.html'
        img_string = ''
        if os.path.isfile('./html/' + img):
            img_string = '    <div id="img"><img src=./' + img + '></div>' 

        giglist_id = 'col_giglist'
        if setlist_string == '':
            giglist_id = 'col_onlylist'

        lines = [
            '<html lang="en">',
            '<head>',
            '    <title>Concert Diary</title>',
            '    <link rel="stylesheet" type="text/css" href="style.css">',
            '    <link rel="shortcut icon" href="img/thumb.ico" type="image/x-icon">',
            '</head>',
            '<body>',
            img_string,
            '    <div id="body">',
            '        <div id="header" class="cf"></div>',
            '        <div id="main" class="cf">',
            '            <div id="col_yearlist">',
                             years_string,
            '            </div>',
            '                <div id="' + giglist_id + '">',
                                 gigs_string,
            '                </div>',
            '                <div id="col_setlist">',
                                 setlist_string,
            '            </div>',
            '        </div>',
            '        <div id="footer" class="cf"> </div>',
            '    </div>',
            '</body>',
            '</html>',
            ]
        with open( fname_html, 'w') as the_file:
            for l in lines:
                the_file.write(l)
    def make_stylesheet(self):
        fname_html = self.head + 'style.css'

        col_maintext = 'gray'
        col_mainbg = 'black'
        col_boxbg = '#153E7E'
        col_border = '#C9BE62'
        col_highlight = '#990000'

        col_gigbg = col_mainbg
        col_setlbg = col_mainbg
        col_setltext = col_maintext
        col_gigtext = col_maintext

        # different colours for debugging:
        #col_setlbg = 'red'
        #col_gigbg = 'yellow'

        lines = [
            'html,body {',
            '    margin:0;',
            '    padding:0;',
            '    font-family: sans-serif;',
            '    color:' + col_maintext + ';',
            '    background:' + col_mainbg + ';',
            '    }',
            '#body {',
            '    margin:0 auto;',
            '    font-size: 1.6ex;',
            '    font-family: sans-serif;',
            '    color:' + col_maintext + ';',
            '    background:transparent;',
            '    }',
            '#img {',
            '    position: absolute;',
            '    float: right;',
            '    top: 50;',
            '    right: 60;',
            '    z-index: -1;',
            '    display: block;',
            '    }',
            '#header {',
            '    padding:10px;',
            '    background:transparent;',
            '    }',
            'ul {',
            '    list-style-type: square;',
            '    }',
            '#col_yearlist {',
            '    float:left;',
            '    padding-top:5px;',
            '    padding-left:2%;',
            '    background:transparent;',
            #'    position:fixed;',
            '    }',
            '#col_giglist {',
            '    float:left;',
            '    padding-left:5%;',
            '    width:40%;',
            '    background:transparent;',
            '    color:' + col_gigtext + ';',
            '    overflow: hidden;',
            '    }',
            '#col_onlylist {',
            '    float:left;',
            '    padding-left:5%;',
            '    width:80%;',
            '    background:transparent;',
            '    }',
            '#col_setlist {',
            '    float:left;',
            '    width:30%;',
            '    padding-top:5px;',
            '    padding-left:3%;',
            '    padding-right:5%;',
            '    background-colour:transparent;',
            '    color:' + col_setltext + ';',
            '    overflow: hidden;',
            '    }',
            '#footer {',
            '    padding:10px;',
            '    background:transparent;',
            '    }',
            '.cf {*zoom:1;}',
            '',
            '.yr {',
            '    width: 60px;',
            '    left: 0;',
            '    text-align: center;',
            '    background-color:' + col_boxbg + ';',
            '    display: float;',
            '    border: 1px ' + col_border + ' solid;',
            '    padding: 8px;',
            '    }',
            'a:link, a:visited {',
            '    text-decoration: none;',
            '    color: ' + col_border + ';',
            '    text-decoration: bold;',
            '    }',
            'a:hover {text-decoration: underline}',
            'a.future:link {',
            '    color: ' + col_maintext + ';',
            '    text-decoration: none;',
            '    font-style: italic;',
            '    }',
            'a.future:visited {',
            '    color: ' + col_maintext + ';',
            '    text-decoration: none;',
            '    font-style: italic;',
            '    }',
            'a.future:hover {',
            '    color: ' + col_maintext + ';',
            '    text-decoration: none;',
            '    font-style: italic;',
            '    }',
            'a.future:active {',
            '    color: ' + col_maintext + ';',
            '    text-decoration: none;',
            '    font-style: italic; }',
            '.sl_title {',
            '    display: block;',
            '    width:60%;',
            '    color: ' + col_border + ';',
            '    background-color:' + col_boxbg + ';',
            '    padding: 12px;',
            '    text-align: left;',
            '    border: 1px ' + col_border + ' solid;',
            '    }',
            'table {',
            '    font-size: 1.7ex;',
            '    border-collapse: collapse',
            '    }',
            '.date {',
            '    font-weight: bold;',
            '    font-family: "Courier new", monospace;',
            '    display: inline;',
            '    }',
            'a.highlight {',
            '    color:' + col_highlight + ';',
            '    font-weight: bold;',
            '    }',
            '.flag {',
            '    display: inline;',
            '    color:' + col_boxbg + ';',
            '    }',
            '.greyflag {',
            '    display: inline;',
            #'    color:' + col_boxbg + ';',
            '    }',
            '.yearplot {',
            '    width: 100%;',
            '    }',
            '.png {',
            '    width: 35em;', #500px;', #30%;',
            '    }',
            'pre {',
            '    font-family: "courier new", courier, monospace;',
            '    font-size: 14px;',
            '    }',
            'sup, sub {',
            '  vertical-align: baseline;',
            '  position: relative;',
            '  font-size: 8px;',
            '  top: -0.4em;',
            '}',
            'sub {',
            '  top: 0.4em;',
            '}',
        ]
        with open( fname_html, 'w') as the_file:
            for l in lines:
                the_file.write(l + '\n')
    def sp(self,n):
        # inserts a non-breaking space
        return '&emsp;' * n
    def row(self,entries, alignment = 'lll'):
        string = '\n<tr>'
        for entry in list( zip(entries,alignment) ):
            align = ''
            if entry[1] == 'r':
                align = ' align=right'
            elif entry[1] == 'c':
                align = ' align=center'
            string += '\n<td' + align + '>' + entry[0] + '</td>'
        string += '</tr>'
        return string
    def build_gigs_string(self,gigs,y=None,link_suffix=None,file_title=None,force_artist=None,match_id=0):
        gigs_string = "<br>"
        if file_title:
            gigs_string += file_title + ': <br> <br>'
        gigs_string += '\n<table>'
        i = 0
        for gig in gigs:
            if y == None or gig.date.year == y:
                i += 1
                # day = str(int(gig.date.strftime("%d"))) # removes leadings 0's
                # if len(day) == 1:
                #     # pad single digit with a space
                #     day = '&nbsp;' + day

                day = gig.date.strftime("%d")
                date_str = '<div class=date>' + day + \
                            gig.date.strftime(" %b %Y") + '</div>'

                name_str = gig.sets[0].artist

                if force_artist != None and force_artist != name_str:
                    name_str = '<i>' + force_artist + '</i>'

                if force_artist != None:
                    # force_artist => only for artist giglist
                    for s in gig.sets:
                        # list band rather than band member!
                        if s.band_only and s.artist == force_artist:
                            for ss in gig.sets:
                                if not ss.band_only and s.artist in ss.band:
                                    #name_str = '<i>' + ss.artist + '</i>'
                                    name_str = ss.artist
                                    break

                if not gig.future:
                    link = gig.link 
                    if link_suffix:
                        link += '_' + link_suffix
                    name_str2 = name_str
                    name_str = '<a '
                    if match_id == gig.index:
                        name_str += 'class=highlight '
                    acount = self.gig_data.gig_artist_times(gig,gig.sets[0].artist)
                    title = 'title="Artistcount: ' + acount + '"' 
                    name_str += 'href=' + link + '.html ' + title + '>' + name_str2 + '</a>'

                if gig.future:
                    gigs_string += self.row( [ '', name_str, date_str, gig.venue ], 'rlll' )
                else:

                    ccount = self.gig_data.gig_city_times(gig)
                    vcount = self.gig_data.gig_venue_times(gig)
                    venue_str  = '<div class=greyflag title="Citycount: '+ccount+'">'+ gig.city+'</div>'
                    venue_str += ' <div class=greyflag title="Venuecount: '+vcount+'">'+gig.venue_nocity+'</div>'
                    cols = [ str(i) + '.' + self.sp(1), name_str, date_str, venue_str ]
                    gigs_string += self.row( cols, 'rlll' )

        gigs_string += self.row( [ self.sp(3), self.sp(15), self.sp(9), '' ] )
        gigs_string += '\n</table>'
        return gigs_string
    def is_int(self,s):
        try:
            int(s)
            return True
        except TypeError:
            return False
        except ValueError:
            return False
    def is_highlight_year(self,h,y):
        if h == None or y == None:
            return False
        elif str(h) == str(y):
            return True
    def make_years_string(self,highlight_year=None):
        years_string = ''
        for y in self.years:
            if y == '':
                years_string += '\n<br>'
            else:
                if y[-1] == '0':
                    years_string += '\n<br>'
                years_string += '\n<div class=yr> <a '
                if self.is_highlight_year( highlight_year, y ):
                    years_string += 'class=highlight '
                years_string += 'href=' + str(y).lower() + '.html>' + str(y) + '</a> </div>'
        return years_string
    def make_artist_index_string(self,years_string_a):
        all_artists = self.gig_data.get_unique_artists()

        n_headliners = 0
        for (a,c) in all_artists:
            if self.gig_data.artist_is_support(a):
                pass
            else:
                n_headliners += 1

        artists_string = str(len(self.gig_data.get_past_gigs())) + ' events featuring ' + \
                str(len(all_artists)) + \
                ' artists [' + str(n_headliners) + ' headliners] ' + \
                '(those in italic were never headliners): ' + \
                '<br><br>\n<table>'

        n_gigs_for_last_artist = 0
        counter = 0

        for (a,c) in all_artists:
            counter += 1
            afname = 'a' + str(counter).zfill(3)

            all_agigs = self.gig_data.all_gigs_of_artist(a,True) # need to include future gigs here!
            artist_string = self.build_gigs_string( all_agigs, None, afname, None, a )

            breakdown = ''
            if len(c) > 1:
                unique_songs = self.gig_data.unique_songs_of_artist(a)

                events = [ x for x in c ]
                events.sort(key=lambda x: x.index)

                if len(c) > 3:
                    plot_fname = 'html/img/' + afname + '.png'
                    self.plotter.song_breakdown(a,events,unique_songs,plot_fname)
                    breakdown += '\n<br>\n<img class=png src="img/' + afname + '.png"><br>\n'
                    #plot_fname2 = 'html/img/' + afname + '_fd.png'
                    #self.plotter.song_freq_dist(unique_songs,plot_fname2)
                    #breakdown += '\n<br>\n<img class=png src="img/' + afname + '_fd.png"><br>\n'
                else:
                    breakdown += '\n<br> \n' + '='*50

                breakdown += '<br><br>Breakdown of %d songs across %d events (%.2f songs/event):<br>' \
                                % ( len(unique_songs), len(c), len(unique_songs) / float(len(c)) )
                breakdown += '\n<pre>'

                for song in unique_songs:
                    event_string = ""
                    for event in events:
                        if event in song['events']:
                            #event_string += 'X'
                            title = song['title'] + ' / ' + event.venue + \
                                                    ' / ' + event.date.strftime("%d %b %Y")
                            event_string += '<div class=greyflag title="' + title + '">X</div>'
                        else:
                            event_string += '-'
                    songtitle = song['title']
                    if song['obj'].cover:
                        songtitle += ' *'
                        # adding a hover title upsets the plain text alignment
                        #greyflag = '<div class=greyflag title="' + song['obj'].cover + '">*</div>'
                        #songtitle += ' ' + greyflag
                    breakdown += '<br>{0:3d} {1:50s} {2:30s}' \
                        . format( len(song['events']), songtitle, event_string )
                breakdown += '\n</pre>'

            self.make_file( afname, years_string_a, artist_string + breakdown, '' )

            for gig in c:
                suffix = '_a' + str(counter).zfill(3)
                link = gig.link + suffix
                artist_string_h = self.build_gigs_string( all_agigs, None, afname, None, a, gig.index )
                setlist_string = self.gig_setlist_string( gig, True, c, suffix)
                self.make_file( link, years_string_a, artist_string_h + breakdown, setlist_string, gig.img )

            link = '<a href=' + afname + '.html>' + a + '</a>'
            if self.gig_data.artist_is_support(a):
                link = '<i>' + link + '</i>'
            if len(c) == n_gigs_for_last_artist:
                artists_string += ', ' + link
            else:
                artists_string += '</td></tr>\n<tr><td align=right valign=top>' + str(len(c)) + \
                    '.' + self.sp(1) + '</td><td>' + link

            n_gigs_for_last_artist = len(c)

        artists_string += '\n</table>'
        
        return artists_string
    def make_venue_index_string(self,years_string_v):
        all_venues = self.gig_data.get_unique_venues()
        venues_string = str(len(self.gig_data.get_past_gigs())) + ' events at ' + \
                str(len(all_venues)) + ' venues:<br><br>\n<table>'
        n_gigs_for_last_venue = 0
        counter = 0
        for (v,c) in all_venues:
            counter += 1
            vfname = 'v' + str(counter).zfill(3)

            all_vgigs = self.gig_data.all_gigs_of_venue(v,True) # need to include future gigs here!
            venue_string = self.build_gigs_string( all_vgigs, None, vfname, v )
            self.make_file( vfname, years_string_v, venue_string, '' )

            for gig in c:
                suffix = '_' + vfname
                link = gig.link + suffix
                venue_string_h = self.build_gigs_string( all_vgigs, None, vfname, v, None, gig.index )
                setlist_string = self.gig_setlist_string( gig, True, c, suffix)
                self.make_file( link, years_string_v, venue_string_h, setlist_string, gig.img )

            link = '<a href=' + vfname + '.html>' + v + '</a>'

            if len(c) == n_gigs_for_last_venue:
                venues_string += ', ' + link
            else:
                venues_string += '</td></tr>\n<tr><td align=right valign=top>' + str(len(c)) + \
                    '.' + self.sp(1) + '</td><td>' + link
            n_gigs_for_last_venue = len(c)

        venues_string += '</table>'

        cities = self.gig_data.unique_cities()
        n_cities = 0
        for (city,gigs_past,gigs_future) in cities:
            if len(gigs_past) > 0:
                n_cities += 1

        venues_string += '\n<br> <br> ' + '='*50 + '\n<br><br>' + str(n_cities) + ' cities:' \
                + '<br>\n<table>'

        n_gigs_for_last_city = 0
        counter = 0

        for (city,gigs_past,gigs_future) in cities:
            #print( "%s %d %d" % ( city, len(gigs_past), len(gigs_future) ) )
            #venues_string += '\n<tr><td align=right valign=top>' + str(len(c)) + '.' + self.sp(1) + \
                    #'</td><td>' + ', '.join([ x[0] for x in c]) + '</td></tr>'
            counter += 1
            cfname = 'c' + str(counter).zfill(3)
            clink = '<a href=' + cfname + '.html>' + city + '</a>' 

            all_cgigs = gigs_past + gigs_future;

            city_string = self.build_gigs_string( all_cgigs, None, cfname, city )
            self.make_file( cfname, years_string_v, city_string, '' )

            for gig in all_cgigs:
                suffix = '_' + cfname
                link = gig.link + suffix
                city_string_h = self.build_gigs_string( all_cgigs, None, cfname, city, None, gig.index )
                setlist_string = self.gig_setlist_string( gig, True, all_cgigs, suffix )
                self.make_file( link, years_string_v, city_string_h, setlist_string, gig.img )

            if len(gigs_past) == 0:
                pass
            elif len(gigs_past) == n_gigs_for_last_city:
                venues_string += ', ' + clink
            else:
                venues_string += '</td></tr>\b<tr><td align=right valign=top>' + str(len(gigs_past)) + \
                        '.' + self.sp(1) + '</td><td>' + clink
            
            n_gigs_for_last_city = len(gigs_past)


        venues_string += '</table>'
        return venues_string
    def make_bootlegs_index_string(self):
        playlist_gigs = self.gig_data.playlist_gigs
        string = '\n<ul>'
        y = ""
        for p in playlist_gigs:
            if y != p.date.strftime("%Y"):
                string += '\n <br>' # '========'
            y = p.date.strftime("%Y")
            links = []
            for s in p.sets:
                if s.playlist:
                    link = '<a href="' + s.playlist + '">' + s.artist + '</a>'
                    links.append(link)
            string += '\n  <br> <div class=date>' + p.date.strftime("%Y-%b-%d") + \
                    '</div> &nbsp;' + " + ".join(links) + ' (' + p.venue + ')'
        string += '\n</ul>'
        return string
    def make_graphs_index_string(self):
        graphs = []

        self.plotter.year_growth('html/img/plot_year_growth.png')
        self.plotter.total_progress('html/img/plot_cumulative.png')
        self.plotter.month_growth('html/img/plot_month_growth.png')
        self.plotter.artist_growth('html/img/plot_artist_growth.png')
        self.plotter.venue_growth('html/img/plot_venue_growth.png')
        #self.plotter.relative_progress('html/img/plot_relative_progress.png')
        #self.plotter.days_growth('html/img/plot_days_growth.png')
        self.plotter.top_venue_growth(8,'html/img/plot_top_venue_growth.png')
        #self.plotter.freq_dist('html/img/plot_freq_dist.png')

        graphs.append('img/plot_year_growth.png')
        graphs.append('img/plot_cumulative.png')
        graphs.append('img/plot_month_growth.png')
        graphs.append('img/plot_artist_growth.png')
        graphs.append('img/plot_venue_growth.png')
        #graphs.append('img/plot_relative_progress.png')
        #graphs.append('img/plot_days_growth.png')
        graphs.append('img/plot_top_venue_growth.png')
        #graphs.append('img/plot_freq_dist.png')

        string = '<br> <br> <center>\n'
        count = 0

        for graph in graphs:
            count += 1
            string += '<img src="' + graph + '" style="width:30%;"><nbsp>'
            #if count % 2 == 0:
                #string += '<br>'
            string += '\n'

        string += '</center>\n'
        return string
    def make_calendar(self):
        # get future gigs
        pass
    def generate_html_files(self):
        self.make_stylesheet()

        extras = [ 'Artists', 'Venues' ]
        if self.do_playlists:
            extras += [ 'Tapes' ]
        if self.do_graphs:
            extras += [ 'Stats' ]
        self.years = extras + [ '' ] + self.years

        years_string   = self.make_years_string()
        years_string_a = self.make_years_string("Artists")
        years_string_v = self.make_years_string("Venues")

        index_string   = ''
        years_string_i = ''
         
        for (y,c) in self.gig_data.get_unique_years(True):
            gigs_string = self.build_gigs_string(self.gig_data.gigs,y)
            years_string_h = self.make_years_string(y)

            plot_string = ''
            year_plot_path = 'img/plot_%s.jpg' % str(y)
            if self.plotter.total_progress_by_year('html/' + year_plot_path,y):
                plot_string += '<img class=yearplot src="%s">' % year_plot_path

            # Set the index page to the date of the next future gig:
            if y == self.gig_data.first_unseen().date.year:
                index_string = gigs_string
                years_string_i = years_string_h

            self.make_file( str(y), years_string_h, gigs_string, plot_string )
            for gig in self.gig_data.gigs:
                if gig.date.year == y:
                    setlist_string = self.gig_setlist_string(gig)
                    gigs_string_h = self.build_gigs_string( self.gig_data.gigs, y, 
                                                            None, None, None, gig.index)
                    self.make_file( gig.link, 
                               years_string_h, gigs_string_h, setlist_string, gig.img)
            
        artists_string = self.make_artist_index_string(years_string_a)
        venues_string = self.make_venue_index_string(years_string_v)

        self.make_file( 'venues',    years_string_v,   venues_string,    '' )
        self.make_file( 'artists',   years_string_a,   artists_string,   '' )
        self.make_file( 'index',     years_string_i,   index_string,     '' )

        if self.do_playlists:
            years_string_b = self.make_years_string("Tapes")
            bootlegs_string = self.make_bootlegs_index_string()
            self.make_file( 'tapes',     years_string_b,   bootlegs_string,  '' )

        if self.do_graphs:
            years_string_g = self.make_years_string("Stats")
            graphs_string = self.make_graphs_index_string()
            self.make_file( 'stats',     years_string_g,   graphs_string,  '' )

        self.make_calendar()

        return
    def make_youtube_link(self,yt):
        link = '<a href="http://www.youtube.com/watch?v=' + yt + '">'
        link += '&bullet;'
        link += '</a>'
        return link

class GIG_gigs():
    def __init__(self,root):
        self.root = root
        self.gigs = []
        self.past_gigs = []

        self.unique_artists = None  # cached
        self.unique_artists_inc_future = None  # cached
        self.unique_venues = None   # cached
        self.unique_venues_inc_future = None   # cached
        self.unique_years = None    # cached
        self.unique_years_inc_future = None    # cached
        self.playlist_gigs = []

        self.build_gig_data()
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
                    song.guests += re.findall( '{([0-9A-Za-z- ]+)}', splits[1])
                if '[' in splits[1]:
                    #song.custom = re.findall( '\[([0-9A-Za-z- ]+)\]', splits[1])
                    for x in re.findall( '\[([0-9A-Za-z- ]+)\]', splits[1]):
                        if x == 'solo':
                            song.solo = True
                        elif x == 'debut':
                            song.debut = True
                        elif x == 'improv':
                            song.improv = True
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
                if '|' in splits[1]:
                    m = re.match( '.*\|(\w+)\|.*', splits[1] )
                    if m:
                        song.youtube = m.group(1)
            this_set.append_song(song)
    def process_venue_name(self,name):
        # This does nothing, but it would be nice to sort out underscores.
        #new_name = re.sub( r'_', '&nbsp;', name)
        return name
    def process_artist_name(self,n):
        # strip comments and remove definite articles
        name = n
        name = re.sub( '\s*---.*', '', name )
        name = name.strip()
        name = re.sub( '^The\s+', '', name )
        return name
    def identify_first_times(self):
        for (a,c) in self.get_unique_artists():
            for song in self.unique_songs_of_artist(a):
                first_id = min( [ x.index for x in song['events'] ] )
                for g in self.gigs:
                    if g.index == first_id:
                        for s in g.sets:
                            try:
                                pos = s.songs.index(song['title'])
                                if s.artist == a or a in s.songs[pos].guests:
                                    s.songs[pos].first_time = True
                                    break
                            except ValueError:
                                pass
    def fill_in_playlist_links(self):
        fname = self.root + '/playlists'
        lines = []
        with open(fname) as f:
            for l in f.read().splitlines():
                if True or os.path.exists(l):
                    lines.append(l)
        if len(lines) > 0:
            used_lines = []
            for g in self.gigs:
                for s in [ x for x in g.sets if not x.band_only ]:
                    date_string = g.date.strftime("%Y.%m.%d")
                    artist_words = s.artist.lower().split(' ')
                    for line in lines:
                        if line in used_lines:
                            pass
                        elif not date_string in line:
                            pass
                        else:
                            checked_all_names = True
                            if len(artist_words) == 2 and artist_words[1] == 'dylan':
                                checked_all_names = 'dylan' in line.lower()
                                pass
                            else:
                                for aw in artist_words:
                                    if aw.lower() == 'the':
                                        pass
                                    elif not aw in line.lower():
                                        checked_all_names = False
                                        break
                            if checked_all_names:
                                s.playlist = line
                                if len(self.playlist_gigs) == 0 or self.playlist_gigs[-1] != g:
                                    self.playlist_gigs.append(g)
                                    used_lines.append(line)
    def get_data_from_file(self,path):
        level = 0
        n_processed = 0
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
                    n_processed += 1
                    d = datetime.strptime( m1.group(1), date_regex )
                    ident = d.strftime( "%y" ) + '{0:02d}'.format(n_processed)
                    v = self.process_venue_name( m1.group(2) )
                    this_gig = GIG_gig( ident, d, v )
                else:
                    a = self.process_artist_name( mopen.group(1) )
                    this_set = GIG_set(a)
                    this_gig.append_set(this_set)
            elif mclose:
                last_blank = False
                level -= 1
                if level == 0 and not commented:
                    this_gig.add_dummy_sets_for_guests()
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
        self.gigs.sort(key=lambda x: x.index)
        self.identify_first_times()
        
    # Some utilities
    def artist_stats(self,artist):
        unique_songs = self.unique_songs_of_artist(artist)
        
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
                        artists = [ s.artist ] # + song.guests
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
    def unique_songs_of_artist(self,a):
        # this is quite slow. it could be cached!
        raw_songs = []
        artist = a + '$'
        for gig in self.gigs:
            for s in gig.sets:
                # look for song in artist's main set:

                main_set = False
                if re.search(artist, s.artist, re.IGNORECASE):
                    main_set = True
                elif s.band:
                    for b in s.band:
                        if re.search(artist, b, re.IGNORECASE):
                            main_set = True
                            break

                if main_set:
                    for song in s.songs:
                        got = False
                        if not song.title: # Untitled
                            continue
                        for got_song in raw_songs:
                            if got_song['title'] == song.title:
                                got_song['events'].append(gig)
                                got = True
                        if not got:
                            raw_songs.append( { 'title': song.title, 'events': [gig], 'obj': song } )
                else:
                    # look for song in other sets for which the artist is flagged:

                    for song in s.songs:
                        flagged = False
                        for guest in song.guests:
                            if re.search( artist, guest, re.IGNORECASE ):
                                flagged = True
                        if flagged:
                            got = False
                            for got_song in raw_songs:
                                if got_song['title'] == song.title:
                                    got_song['events'].append(gig)
                                    got = True
                            if not got:
                                raw_songs.append( { 'title': song.title, 'events': [gig], 'obj': song } )

        raw_songs = [ x for x in raw_songs if x['title'] ] # shouldn't be necessary
        raw_songs.sort(key=lambda x: (-len(x['events']),x['title']), reverse=True)
        raw_songs.reverse()
        return raw_songs
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
                if venue in gig.venue:
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
        for gig in self.gigs:
            if gig.sets[0].artist == a:
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
        yweek = yday % 7 if yday > 7 else 0
        current_count = 0
        previous_counts = []

        gigs_by_year = self.get_unique_years()
        gigs_by_year.sort()

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
                    if s.artist in all_artists:
                        pass
                    else:
                        n_new_artists += 1
                        all_artists.append(s.artist)

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
            songs = self.unique_songs_of_artist(a)
            songs = [ x['title'] for x in songs ]
            self.print_fuzzy_matches(songs,a)
        venues = self.get_unique_venues()
        venues = [ x[0] for x in venues ]

        self.print_fuzzy_matches(artists, 'Artists')
        self.print_fuzzy_matches(venues, 'Venues')
    def get_covers(self):
        artists = []
        csongs = []

        for g in self.gigs:
            for s in g.sets:
                for song in s.songs:
                    if song.cover:
                        event = '(%s, %s)' % (s.artist,g.date.strftime('%d-%b-%Y'))
                        #print( song.cover.ljust(20) + song.title.ljust(35) + event )
                        
                        idx = None
                        if song.cover in artists:
                            idx = artists.index(song.cover)
                        else:
                            artists.append(song.cover)
                            csongs.append([])
                            idx = len(artists) - 1
                        
                        csongs[idx].append( song.title.ljust(37) + event)

        zipped = [ [x[0], x[1]] for x in zip(artists,csongs) ]
        zipped.sort(key=lambda x: len(x[1]) )
        zipped.reverse()

        for a,s in zipped:
            print('%s (%d)' % (a,len(s)))
            s.sort()
            for song in s:
                print( '  ' + song )
                        

    # Gig counts
    def gig_artist_times(self,gig,artist):
        # gig is the nth event of artist
        for s in gig.sets:
            if s.artist == artist:
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
    def __init__(self, ident, date, venue):
        self.index  = ident
        self.date   = date
        self.venue  = venue
        self.city   = venue.split()[0]
        self.venue_nocity = " ".join(venue.split()[1:])
        self.sets   = []
        today = datetime.today()
        self.future = date > today or ( date.date() == today.date() and today.hour < 20 )
        self.link    = str(ident)
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
            string += "\n  Artist: " + s.artist
            for song in s.songs:
                string += "\n          > " + song.title if song.title else "???"
        string += "\n"
        return string
    def print_short(self):
        date = self.date.strftime('%d-%b-%Y')
        venue = self.venue
        artist_list = [ s.artist for s in self.sets ]
        artists = artist_list[0]
        if len(artist_list) > 1:
            artists += ' + ' + artist_list[1]
        if len(artist_list) > 2:
            artists += ' + ... '
        ident = '[' + self.index + ']'
        print( ' {0:8s} {1:15s} {2:30s} {3:20s}' . format( ident, date, venue, artists) )
    def append_set(self,s):
        self.sets.append(s)
    def add_dummy_sets_for_guests(self):
        # Adds empty sets for song guests
        # If guests appear in a songflag but not in a set of their own, we must
        # add a dummy set (marked "guest_only") to ensure they are included in
        # the artist statistics.

        addarts = []
        artists = [ x.artist for x in self.sets ]

        for s in self.sets:
            for song in s.songs:
                for g in song.guests:
                    if not g in artists and not g in addarts:
                        addarts.insert(0,g)

        # The footnote numbering will be derived from the index in setlists array,
        # so we always insert the guests at index 1 (immediately after the headliner),
        # which is usually all we need...

        for a in addarts:
            this_set = GIG_set(a)
            this_set.guest_only = True
            self.sets.insert(1,this_set)

        # Now we also add dummy sets for band members who are explicity named:

        band_artists = []
        for s in self.sets:
            for b in s.band:
                band_artists.append(b)

        for b in band_artists:
            this_set = GIG_set(b)
            this_set.band_only = True
            self.sets.insert(1,this_set)
    def get_artists(self):
        if not self.artists:
            self.artists = [ x.artist for x in self.sets ]
        return self.artists
    def stub(self):
        # short printer
        return "%s %s   %s" % (self.sets[0].artist.ljust(20), self.date.strftime("%d-%b-%Y (%a)"), self.venue )

class GIG_set():
    def __init__(self, artist):
        self.artist     = artist
        self.songs      = []
        self.band       = []
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
        self.solo        = False
        self.first_time  = False
        self.set_opener  = False
        self.debut       = False
        self.improv      = False
        self.quote       = None
        self.cover       = None
        self.youtube     = None
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
        