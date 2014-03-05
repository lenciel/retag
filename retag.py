#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from mutagen.easyid3 import EasyID3


def get_track_number(track):
    if track.find("/") > -1:
        return get_track_number(track[0:track.find("/")])
    elif track.isdigit():
        return track.zfill(2)


def get_id3_by_file(music_file, id3_info):
    music_file_name = os.path.basename(music_file)
    m = re.match(r"(?P<trackNumber>\d{2})\. (?P<artist>((?! -).)+) - (?P<title>[^\.]+)\.mp3",
        music_file_name)

    id3_info["tracknumber"] = m.group('track_number')
    id3_info["artist"] = m.group('artist')
    id3_info["title"] = m.group('title')
    id3_info["album"] = music_file.split('/')[-2]

    id3_info.save()
    return id3_info


def recreate_tag(music_file):
    # tag_info = TinyTag.get(unicode(filename, 'utf8'))
    # tag_title = recreate_encoding(tag_info.title)
    # tag_artist = recreate_encoding(tag_info.artist)
    # tag_album = recreate_encoding(tag_info.album)

    id3_info = EasyID3(music_file)
    print id3_info
    try:
        # _track_number = get_track_number(id3_info["tracknumber"][0])
        _artist = recreate_encoding(id3_info["artist"][0])
        _title = recreate_encoding(id3_info["title"][0])
        _album = recreate_encoding(id3_info["album"][0])
    except KeyError:
        pass
        # id3_info = get_id3_by_file(music_file, id3_info)
        #
        # _track_number = id3_info["tracknumber"][0]
        # _artist = id3_info["artist"][0]
        # _title = id3_info["title"][0]
        # _album = id3_info["album"][0]
    # print _track_number
    print _artist
    print _title
    print _album
    # tag_title = recreate_encoding(audio["title"])
    # tag_artist = recreate_encoding(audio["artist"])
    # tag_album = recreate_encoding(audio["album"])

    # print('This track is by %s.and title is %s, it is in album %s'
    #       % (tag_artist, tag_title, tag_album))


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