from mutagen.id3 import ID3
import os, os.path

import re
from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')

def slugify(text, delim=u'_'):
    """Generates an slightly worse ASCII-only slug.
    http://stackoverflow.com/questions/9042515/normalizing-unicode-text-to-filenames-etc-in-python
    Jan 28 '12 at 3:11
    by julio.alegria """
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))

class Song(object):
    def __init__(self, filename, artist, album, title, date, trackno):
        self.filename = filename
        self.artist = artist
        self.album = album
        self.title = title
        self.date = date
        self.trackno = trackno
        self.new_filename = None
        self.new_path = None

    def move(self, directory):
        try:
            os.makedirs(os.path.join(directory, self.new_path))
        except OSError:
            pass
        os.rename(self.filename, os.path.join(self.new_path, self.new_filename))


    def plong(self):
        print "file: %s" % self.filename
        if self.new_path:
            print "new_path: %s" % self.new_path
        if self.new_filename:
            print "new_filename: %s" % self.new_filename
        print "artist: %s" % self.artist
        print "album: %s" % self.album
        print "title: %s" % self.title
        print "date: %s" % self.date
        print "trackno: %s" % self.trackno

    def pshort(self):
        print self.filename
        print "%s: %s - %s - %s (%s)" % (self.trackno,
                                         self.artist,
                                         self.album,
                                         self.title,
                                         self.date)
class Album(object):
    def __init__(self, directory):
        self.songs = []
        self.compilation = False

    def check_compilation(self):
        artist = None
        for song in self.songs:
            if not artist:
                artist = song.artist
            elif song.artist != artist:
                self.compilation = True
                return
            else:
                artist = song.artist
        self.compilation = False



def get_param(id3, param):
    a = id3.get(param)
    if not a:
        return ''
    else:
        return a.text[0]

def get_tracks(directory, albums, single_tracks):
    for path, dnames, fnames in os.walk(directory):
        for fname in fnames:
            id3 = ID3(os.path.join(path, fname))
            artist = get_param(id3, 'TPE1')
            album = get_param(id3, 'TALB')
            title = get_param(id3, 'TIT2')
            date = get_param(id3, 'TDRC')
            trackno = get_param(id3, 'TRCK')

            if not artist:
                artist = u'unknown'
            if not title:
                title = u'unknown'
            if not trackno.isdigit():
                temp = u''
                for char in trackno:
                    if char.isdigit():
                        temp += char
                    else:
                        break
                trackno = temp

            song = Song(os.path.join(path, fname), artist, album, title, date, trackno)

            if albums.get(album) == None:
                albums[album] = Album(directory)
            if not trackno:
                single_tracks.append(song)
            else:
                albums[album].songs.append(song)

def separate_compilations(albums, compilations):
    for name, album in albums.items():
        if album.compilation:
            compilations[name] = albums.pop(name)



def main():
    raw_input("This program will touch and move all of your files in this directory and "\
            "directories beneath this one. Press Ctrl+C to cancel or enter to continue.")

    albums = {}
    compilations = {}

    directory = os.getcwd()
    ext = ".mp3"
    single_tracks = []

    get_tracks(directory, albums, single_tracks)

    if albums.get(''):
        temp = albums.pop('')
        for song in temp.songs:
            single_tracks.append(song)

    for album in albums.values():
        album.check_compilation()

    separate_compilations(albums, compilations)

    # Create new file names for each song in each container
    for song in single_tracks:
        song.new_path = os.path.join(directory,
                                    slugify(song.artist))
        song.new_filename = "%s-%s%s" % (slugify(song.artist),
                                        slugify(song.title),
                                        ext)

    for album in albums.values():
        for song in album.songs:
            song.new_path = os.path.join(directory,
                                        slugify(song.artist),
                                        slugify(song.album))
            song.new_filename = "%s-%02d-%s%s" % (slugify(song.artist),
                                                int(slugify(song.trackno)),
                                                slugify(song.title),
                                                ext)

    for album in compilations.values():
        for song in album.songs:
            song.new_path = os.path.join(directory,
                                            "various_artists",
                                            slugify(song.album))
            song.new_filename = os.path.join("%02d-%s-%s%s" % (int(slugify(song.trackno)),
                                            slugify(song.artist),
                                            slugify(song.title),
                                            ext))

    # move and rename each file
    for song in single_tracks:
        song.move(directory)
    for album in albums.values():
        for song in album.songs:
            song.move(directory)
    for album in compilations.values():
        for song in album.songs:
            song.move(directory)

    # find and remove empty directories
    to_remove = []
    for path, dname, fname in os.walk(directory):
        if not dname:
            to_remove.append(path)
        elif not fname:
            to_remove.append(path)
    for path in to_remove:
        try:
            os.removedirs(path)
        except OSError:
            pass

if __name__ == '__main__':
    main()
