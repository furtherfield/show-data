# process_pages.py - Extract show information from downloaded html
#
# Copyright 2015 Furtherfield.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import codecs, itertools, json, os, re
import unicodecsv
from BeautifulSoup import BeautifulSoup

INPUT_ROOT = 'furtherfield.org'
OUTPUT_ROOT = 'data'
URL_ROOT = 'http://furtherfield.org'
EXHIBITION_DIRS = [os.path.join(INPUT_ROOT, 'exhibitions'),
                   os.path.join(INPUT_ROOT, 'programmes', 'exhibition')]
INDEX_DIR = os.path.join(INPUT_ROOT, 'programmes')
JSONDIR = 'json'
SHOWS_HEADER = 'index,show,venue,date,url'
ARTISTS_HEADER = 'show,artist'

ARTISTS_OVERRIDES = json.load(codecs.open('artists-overrides.json', 'r',
                                          'utf-8'))
ARTIST_OVERRIDES = json.load(codecs.open('artist-overrides.json', 'r',
                                         'utf-8'))

show_count = 1

def file_soup(filepath):
    with codecs.open(filepath, 'r', 'utf-8') as filehandle:
        text = filehandle.read()
    return BeautifulSoup(text)

def list_shows():
    shows = []
    for dir in EXHIBITION_DIRS:
        shows += [os.path.join(dir, show) for show in os.listdir(dir)
                  if not '?' in show]
    return shows

def list_shows_in_order():
    index_pages = [page for page in os.listdir(INDEX_DIR)
                   if 'exhibitions' in page]
    index_pages.sort()
    index_pages.reverse()
    shows = []
    for index_page in index_pages:
        soup = file_soup(os.path.join(INDEX_DIR, index_page))
        page_listings = []
        for listing in soup.findAll('div', {'class':re.compile('.*listing.*')}):
            page_listings.append(listing.find('a').get('href'))
        page_listings.reverse()
        shows += page_listings
    return shows

def sub_artists(artists):
    artists = re.sub(r'\band\b', ',', artists)
    for override in ARTIST_OVERRIDES:
        left = override[0]
        right = override[1]
        artists = re.sub(left, right, artists)
    return artists

def get_artists(soup, show):
    try:
        artist_string = soup.find('h2', {'class':'artist'}).text
    except:
        try:
            artist_string = ARTISTS_OVERRIDES[show]
        except:
            print 'Need artists for: %s.' % show
    artist_string = sub_artists(artist_string)
    artists = re.findall(r'[^,/&]+', artist_string)
    artists = [artist.strip() for artist in artists]
    artists = [artist for artist in artists if artist != '']
    return artists

def get_show(soup):
    return soup.find('div', {'id':'main'}).find('h1').text

def get_listings(soup):
    return soup.find('div', {'class':'listings'})

def get_date(soup):
    listings = get_listings(soup)
    return listings.findAll('span', {'class':'i'})[0].text

def get_venue(soup):
    listings = get_listings(soup)
    return listings.findAll('span', {'class':'i'})[1].text

def print_show_csv(showsfile, show_index, show_url, show, venue, date):
    showsfile.writerow((show_index, show, venue, date, show_url))

def print_artists_csv(artistsfile, show_index, artists):
    for artist in artists:
        artistsfile.writerow((show_index, artist))

def print_show_json(jsondir, show_index, show_url, show, venue, date, artists):
    with codecs.open(os.path.join(OUTPUT_ROOT, jsondir,
                                  '%i.json' % (show_index)),
                     'w', 'utf-8') as outfile:
        json.dump({'id':show_index, 'show':show, 'uri':show_url,
                   'venue':venue, 'date':date, 'artists':artists},
                  outfile)

def process_show_file(show_index, show_url, show_page_text,
                      showsfile, artistsfile):
    soup = BeautifulSoup(show_page_text)
    show = get_show(soup)
    venue = get_venue(soup)
    date = get_date(soup)
    artists = get_artists(soup, show)
    print_show_csv(showsfile, show_index, show_url, show, venue, date)
    print_artists_csv(artistsfile, show_index, artists)
    print_show_json(JSONDIR, show_index, show_url, show, venue, date, artists)

def process_shows():
    showsfile = open(os.path.join(OUTPUT_ROOT, 'shows.csv'), 'w')
    print >>showsfile, SHOWS_HEADER
    showswriter = unicodecsv.writer(showsfile, encoding='utf-8')
    artistsfile = open(os.path.join(OUTPUT_ROOT, 'artists.csv'), 'w')
    artistswriter = unicodecsv.writer(artistsfile, encoding='utf-8')
    print >>artistsfile, ARTISTS_HEADER
    shows = list_shows_in_order()
    show_index = 1
    for show in shows:
        try:
            with open(INPUT_ROOT + show) as show_file:
                show_text = show_file.read()
            show_url = URL_ROOT + show
            process_show_file(show_index, show_url, show_text,
                              showswriter, artistswriter)
            show_index += 1
        except IOError, e:
            print "Couldn't find show: %s" % show

if __name__ == '__main__':
    process_shows()
