#!/usr/bin/env python3

import json
import os
import sys
import urllib
import urllib.error
import urllib.request
from os import listdir
from os.path import isfile, join
from pprint import pprint


def open_main_json_file():
    # Open the main json file and save it as dictionary.
    with open("AurScrapDB.json", 'r', encoding='UTF-8') as main_file:
        datafile: dict = json.loads(main_file.read())  # Use as main dictionary through out the whole code.

    return datafile


def update_main_json_file(datafile):
    with open("AurScrapDB.json", 'w', encoding='UTF-8') as updated_file:
        json.dump(datafile, updated_file, indent=2, sort_keys=True)


def set_data(f_str, datafile, filenames_list):
    for f_name in filenames_list:
        if f_str in f_name:
            existing_version = f_name.replace((f_str + "-"), "")
            datafile[f_str]['version'] = str(existing_version)  # Set existing version, as in directory.
            url: str = "https://aur.archlinux.org/packages/"
            datafile[f_str]['aur_link'] = url + str(datafile[f_str]['aur_name']) + "/"  # Set aur_link.


def parse_json(aur_name):
    try:
        url: str = 'https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={0}'.format(aur_name)
        response: str = urllib.request.urlopen(url).read().decode('UTF-8')  # Get response from URL

    except urllib.error.HTTPError:
        print("HTTP Error!")

    else:
        return json.loads(response)['results'][0]['Version']


def update_local(datafile):
    # Find the name of files in the package directory.
    directory_name = "x86_64"
    filenames_list: list = [((filename.replace(".pkg.tar.xz", "")).replace("-any", "")).replace("-x86_64", "")
                            for filename in listdir(directory_name)
                            if isfile(join(directory_name, filename))]
    # Set the main info like version and aur_link in the datafile(main dictionary file).
    for key in datafile.keys():
        set_data(key, datafile, filenames_list)
    return datafile


def update_from_api(datafile):
    # Parse 'aur_version' from API.
    it: int = 1
    total: int = len(datafile.keys())
    for key in datafile.keys():
        sys.stdout.write("\r" + "Processing: {0}/{1}".format(it, total))
        datafile[key]['aur_version'] = str(parse_json(datafile[key]['aur_name']))
        it += 1
        sys.stdout.flush()
    print()
    return datafile


def match_versions(datafile):
    # Check whether 'version' and 'aur_version' is same or not.
    for key in datafile.keys():
        if datafile[key]['version'] != datafile[key]['aur_version']:
            pprint(datafile[key])  # print particular info under this key.
        else:
            pass
    return datafile


def do_everything():
    datafile: dict = open_main_json_file()
    update_main_json_file(match_versions(update_from_api(update_local(datafile))))


def main():
    print("Your options:")
    print("\t1. Update Local Version")
    print("\t2. Update Version From AUR")
    print("\t3. Compare Version")
    print("\t4. Update All")
    print("\t5. Clear Screen")
    print("\t6. Exit")
    c: int = int(input("Enter Your Choice: "))

    if c is 1:
        print()
        datafile: dict = open_main_json_file()
        update_main_json_file(update_local(datafile))
        print("File Updated Locally\n")
        main()
    elif c is 2:
        print()
        datafile: dict = open_main_json_file()
        update_main_json_file(update_from_api(datafile))
        print("File Updated From API\n")
        main()
    elif c is 3:
        print()
        datafile: dict = open_main_json_file()
        update_main_json_file(match_versions(datafile))
        main()
    elif c is 4:
        print()
        do_everything()
        print("Everything Updated!\n")
        main()
    elif c is 5:
        os.system('clear')
        print("\nCleared\n")
        main()
    elif c is 6:
        print("\nExited")
        sys.exit(0)


if __name__ == "__main__":
    main()
