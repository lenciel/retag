#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import fnmatch
import shutil
import argparse
import re
import urllib
import urllib2
import xml.dom.minidom
import glob

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


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


def get_id3_by_search(music_file, id3_info):
    # Get the Artist and Title from id3_info to make the query
    _artist = id3_info["artist"][0]
    _title = id3_info["title"][0]

    # Query the MusicBrainz web service
    try:
        query = {'query': 'artist:' + _artist + ' AND recording:' + _title}
        response = urllib2.urlopen(
            'http://musicbrainz.org/ws/2/recording?' + urllib.urlencode(query))
        x = xml.dom.minidom.parse(response)

        recording_list = x.getElementsByTagNameNS('http://musicbrainz.org/ns/mmd-2.0#',
                                 'recording-list')[0]
        recording = recording_list.getElementsByTagName('recording')[0]
        if recording.nodeType == 1 and recording.attributes.get(
                'ext:score').value == '100':
            id3_info["tracknumber"] = get_track_number(str(int(
                recording.getElementsByTagName('track-list')[0].attributes.get(
                    'offset').value) + 1))
            id3_info["artist"] = recording.getElementsByTagName('name')[
                0].firstChild.nodeValue
            id3_info["title"] = recording.getElementsByTagName('title')[
                0].firstChild.nodeValue

            # Check for multiple releases containing the title
            release_list = recording.getElementsByTagName('release-list')[0]
            releases = release_list.getElementsByTagName('release')

            release_opts = []

            for release in releases:
                release_title = release.getElementsByTagName('title')[
                    0].firstChild.nodeValue

                if release_title not in release_opts:
                    release_opts.append(release_title)

            if len(release_opts) > 1:
                # Ask the user which option they'd prefer
                print music_file + " has multiple options:"
                index = 0
                print "0) Ignore file and discard edits."
                for opt in release_opts:
                    index += 1
                    print str(index) + ") " + opt

                choice = input("Choice: ")

                if choice == 0:
                    print "You chose to ignore the file."
                else:
                    id3_info["album"] = release_opts[choice - 1]
                    id3_info["tracknumber"] = get_track_number(str(int(
                        releases[choice - 1].getElementsByTagName('track-list')[
                            0].attributes.get('offset').value) + 1))
            else:
                id3_info["album"] = release_opts[0]

            id3_info.save()
    except:
        print sys.exc_info()[0]

    return id3_info


def get_album_artwork(artist, album):
    query = {
        'method': 'album.getinfo',
        'api_key': '<Your API Key>',
        'artist': artist,
        'album': album
    }

    response = urllib2.urlopen(
        'http://ws.audioscrobbler.com/2.0/?' + urllib.urlencode(query))
    x = xml.dom.minidom.parse(response)

    image_url = ""

    images = x.getElementsByTagName('image')
    for image in images:
        if image.getAttribute('size') == 'extralarge':
            image_url = image.firstChild.nodeValue
            break

    print image_url


def move(output, music_file, dir_match):
    audio = MP3(music_file)

    # Add ID3 tag if none exist
    try:
        audio.add_tags()
    except:
        pass

    audio.save()

    id3_info = EasyID3(music_file)

    try:
        _track_number = get_track_number(id3_info["tracknumber"][0])
        _artist = id3_info["artist"][0]
        _title = id3_info["title"][0]
        _album = id3_info["album"][0]
    except KeyError:
        if dir_match:
            id3_info = get_id3_by_file(music_file, id3_info)
        else:
            id3_info = get_id3_by_search(music_file, id3_info)

        _track_number = id3_info["tracknumber"][0]
        _artist = id3_info["artist"][0]
        _title = id3_info["title"][0]
        _album = id3_info["album"][0]

    output_dir = output + "/" + _artist + "/" + _album + "/"
    output_file = _track_number + ". " + _artist + " - " + _title + ".mp3"

    print "Saving file ", output_dir + output_file

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    shutil.move(music_file, output_dir + output_file)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--directory', nargs=1, required=True, help='')
    parser.add_argument('-o', '--output', nargs=1, required=True, help='')

    args = parser.parse_args()

    directory = os.path.abspath(args.directory[0])
    output = os.path.abspath(args.output[0])

    dir_match = (directory == output)

    for root, subFolders, file_names in os.walk(directory):
        for file_name in fnmatch.filter(file_names, '*.mp3'):
            move(output, os.path.join(root, file_name), dir_match)

    # Build a list of all the album directories
    dir_list = glob.glob(os.path.join(output, '*', '*'))
    dir_list = filter(lambda f: os.path.isdir(f), dir_list)

    for albumDir in dir_list:
        album = albumDir.split("/")
        get_album_artwork(album[-2], album[-1])


main()