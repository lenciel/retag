#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tinytag import TinyTag


def recreate_tag(filename):
    tag_info = TinyTag.get(unicode(filename, 'utf8'))
    tag_title = recreate_encoding(tag_info.title)
    tag_artist = recreate_encoding(tag_info.artist)
    tag_album = recreate_encoding(tag_info.album)

    print('This track is by %s.and title is %s, it is in album %s'
          % (tag_artist, tag_title, tag_album))
    print('It is %f seconds long.' % tag_info.length)


def recreate_encoding(tag_entry):
    # if it is unicode in unicode
    if repr(tag_entry)[3:4] == 'u':
        return tag_entry
    # if it is gbk in unicode (i know, wtf...-_-')
    else:
        tag_entry_gbk = repr(tag_entry)[1:].replace(" ", "").decode('string_escape').replace("'", "")
        return tag_entry_gbk.decode('gbk').encode('utf-8').decode('utf-8')

songs = ["/Users/lenciel/Music/iTunes/iTunes Media/Music/Lenka/Lenka/Anything I'M Not.mp3",
         '/Users/lenciel/Music/iTunes/iTunes Media/Music/蔡健雅/T-time/03 Â·¿Ú.mp3',
         '/Users/lenciel/Music/Collection/一生所爱.mp3']
for song in songs:
    recreate_tag(song)