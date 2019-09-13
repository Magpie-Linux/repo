#!/usr/bin/env python
# coding: utf-8
import os
import sqlite3
import subprocess
import sys
from glob import glob
from random import choice as randomChoice
from time import sleep
from urllib import request

from bs4 import BeautifulSoup

Packages_Location_With_Name: str = 'x86_64/*.pkg.tar.xz'
Database_Location_With_Name: str = 'AurScrapDB.sqlite3'


class AurScrapper:

    def __init__(self):
        # Variables ↓
        self.__localPkgLoc: str = Packages_Location_With_Name
        self.__rand: tuple = (0.01, 0.01)
        # Database Operations ↓
        self.__dbLoc: str = Database_Location_With_Name
        self.__conn = sqlite3.connect(self.__dbLoc)

    def __scrap(self, pkgName: str):
        sleep(randomChoice(self.__rand))
        url: str = 'https://aur.archlinux.org/packages/{0}/'.format(pkgName)
        page = request.urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        nameVer = soup.find('div', attrs={'id': 'pkgdetails'})
        nameVer = nameVer.find('h2')
        nameVer = nameVer.text
        # git: str = soup.find('table', attrs={'id': 'pkginfo'}).find('a')
        return {
            "name": pkgName,
            "version": nameVer.split(' ').pop(),
            "url": url,
            "git": 'https://aur.archlinux.org/{0}.git'.format(pkgName)
        }

    def aurDbUpdate(self):
        cusror_One = self.__conn.cursor()
        cusror_Two = self.__conn.cursor()
        cusror_One.execute("SELECT aur_pkg_name FROM AUR")
        row = cusror_One.fetchone()
        while row:
            pkgName = row[0]
            data = self.__scrap(pkgName)
            print(data)
            sql: str = """
                UPDATE AUR
                SET aur_pkg_version = ?,
                aur_pkg_url = ?,
                aur_pkg_git = ?
                WHERE aur_pkg_name = ?
            """
            sqlVar: tuple = (data.get('version'), data.get('url'), data.get('git'), data.get('name'))
            cusror_Two.execute(sql, sqlVar)
            row = cusror_One.fetchone()
        self.__conn.commit()

    def localDbUpdate(self):
        cursor = self.__conn.cursor()
        # noinspection SqlWithoutWhere
        cursor.execute("DELETE FROM Repository")
        for i in glob(self.__localPkgLoc):
            tmp = os.path.basename(i)
            tmp = tmp.replace('-any.pkg.tar.xz', '')
            tmp = tmp.replace('-x86_64.pkg.tar.xz', '')
            tmp = tmp.split('-')
            pkgName: str = '-'.join(tmp[:-2])
            pkgVersion: str = '-'.join(tmp[-2:])
            sql: str = "INSERT INTO Repository (local_pkg_name, local_pkg_version) VALUES (?, ?)"
            sqlVar: tuple = (pkgName, pkgVersion)
            print(sqlVar)
            cursor.execute(sql, sqlVar)
        self.__conn.commit()

    def check(self):
        cursor = self.__conn.cursor()
        sql: str = """
            SELECT AUR.local_pkg_name,
                AUR.aur_pkg_version,
                AUR.aur_pkg_name,
                Repository.local_pkg_version,
                AUR.aur_pkg_url,
                AUR.aur_pkg_git
            FROM AUR
            INNER JOIN Repository ON Repository.local_pkg_name = AUR.local_pkg_name AND
                                     Repository.local_pkg_version != AUR.aur_pkg_version;
        """
        cursor.execute(sql)
        data = cursor.fetchall()
        for i in range(len(data)):
            print(
                "{0}.\n"
                "\tPackage name: {1}\n"
                "\tPackage version: {2}\n"
                "\tAUR name: {3}\n"
                "\tAUR version: {4}\n"
                "\tAUR link: {5}\n"
                "\tAUR Git Link: {6}".format(i + 1,
                                             data[i][0],
                                             data[i][3],
                                             data[i][2],
                                             data[i][1],
                                             data[i][4],
                                             data[i][5],
                                             )
            )
        print("\nTotal %d package need to be updated.\n" % len(data))

    def close(self):
        self.__conn.close()


def main():
    aurScrapper = AurScrapper()
    try:
        while True:
            print(
                "Choose your option:"
                "\n\t1. Update info from AUR for Db Packages"
                "\n\t2. Update info of Local Repo to Db"
                "\n\t3. Check updates"
                "\n\t4. Check all 1,2,3 one serially"
                "\n\t5. Clear screen"
                "\n\t6. Exit"
            )
            ans: str = input('Execute task no: ').strip()
            if ans == '1':
                aurScrapper.aurDbUpdate()
                continue
            elif ans == '2':
                aurScrapper.localDbUpdate()
                continue
            elif ans == '3':
                aurScrapper.check()
                break
            elif ans == '4':
                aurScrapper.aurDbUpdate()
                aurScrapper.localDbUpdate()
                aurScrapper.check()
                break
            elif ans == '5':
                subprocess.run('clear')
                continue
            elif ans == '6':
                aurScrapper.close()
                break
            else:
                print('Wrong input')
                continue
        aurScrapper.close()
        sys.exit('Exited')
    except KeyboardInterrupt:
        aurScrapper.close()
        print()
        sys.exit(-1)
    except Exception as e:
        aurScrapper.close()
        sys.exit(e)


if __name__ == '__main__':
    main()
