import hashlib
import json
import mimetypes
import os
import re
import sys
from datetime import datetime
from random import random
from shutil import copy
from time import time


def rmlastslash(rspath):
    rsplis = rspath.split(os.sep)
    if rsplis[-1] == '':
        rspath = os.sep.join(rsplis[:-1])
    return rspath


class InfoHolder(object):
    def __init__(self, bkuptz=0):
        self.__bkuptz = bkuptz
        self.rsdict = {}

    def _timefmter(self, timestamp=None):
        if timestamp == None:
            return datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'Z'
        else:
            timestamp = timestamp - self.__bkuptz * 60 * 60
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'Z'

    def _rshash(self, rspath, confuse=False):
        if confuse == True:
            hashstr = f'{str(rspath)}{str(random())}{str(time())}'
        else:
            hashstr = rspath
        return hashlib.md5(hashstr.encode('utf8')).hexdigest()

    def _initinfo(self, rspath, isroot=False):
        print(f'------rspath: {rspath}')
        self._path = rspath
        self._name = os.path.split(rspath)[-1].split('.')[0]
        self._id = self._rshash(rspath, True)
        if isroot == True:
            self._parent_id = ''
        else:
            try:
                self._parent_id = self.rsdict[self._rshash(
                    os.path.dirname(rspath))]['id']
            except KeyError:
                self._parent_id = ''
        self._created_time = self._timefmter()
        self._updated_time = self._timefmter()
        self._source_url = ''
        self._mime = ''
        self._file_extension = ''
        if os.path.isfile(rspath):
            self._mime = mimetypes.guess_type(rspath)[0]
            self._file_extension = os.path.splitext(rspath)[-1][1:]

    def _updateinfo(self, rspath, name='', isroot=False):
        self._initinfo(rspath, isroot)
        if not name == '':
            self._name = name

    def updatersdict(self, rspath, rstype=None, name='', isroot=False):
        rspath = rmlastslash(rspath)
        self._updateinfo(rspath, name, isroot)
        rsinfo = {'path': self._path,
                  'name': self._name,
                  'id': self._id}
        if rstype == 1:
            des = f'''
id: {self._id}
parent_id: {self._parent_id}
created_time: {self._created_time}
updated_time: {self._updated_time}
is_conflict: 0
latitude: 0.00000000
longitude: 0.00000000
altitude: 0.0000
author:
source_url:{self._source_url}
is_todo: 0
todo_due: 0
todo_completed: 0
source: joplin-desktop
source_application: net.cozic.joplin-desktop
application_data:
order: 0
user_created_time: {self._created_time}
user_updated_time: {self._updated_time}
encryption_cipher_text:
encryption_applied: 0
markup_language: 1
is_shared: 0
type_: 1'''
        if rstype == 2:
            des = f'''{rsinfo['name']}

id: {self._id}
created_time: {self._created_time}
updated_time: {self._updated_time}
user_created_time: {self._created_time}
user_updated_time: {self._updated_time}
encryption_cipher_text:
encryption_applied: 0
parent_id: {self._parent_id}
is_shared: 0
type_: 2'''
        if rstype == 4:
            des = f'''{rsinfo['name']}

id: {self._id}
mime: {self._mime}
filename:
created_time: {self._created_time}
updated_time: {self._updated_time}
user_created_time: {self._created_time}
user_updated_time: {self._updated_time}
file_extension: {self._file_extension}
encryption_cipher_text:
encryption_applied: 0
encryption_blob_encrypted: 0
size: {os.path.getsize(rspath)}
is_shared: 0
type_: 4'''
        rsinfo['des'] = des
        self.rsdict[self._rshash(rspath)] = rsinfo


class InfoHolderYNote(InfoHolder):
    def __init__(self, bkuptz=0):
        super(InfoHolderYNote, self).__init__(bkuptz)

    def _updateinfo(self, rspath, name='', isroot=False):
        self._initinfo(rspath, isroot)
        if not name == '':
            self._name = name
        rspathse = os.path.splitext(rspath)
        if rspathse[-1] == '.md':
            if not os.path.exists(rspathse[0] + '.json'):
                return
            with open(rspathse[0] + '.json', 'r') as jfile:
                jdic = json.load(jfile)
            self._name = os.path.splitext(jdic['fileEntry']['name'])[0]
            self._source_url = jdic['fileMeta']['sourceURL']
            self._created_time = self._timefmter(
                jdic['fileEntry']['createTimeForSort'])
            self._updated_time = self._timefmter(
                jdic['fileEntry']['modifyTimeForSort'])


class Md2Jex(object):
    def __dir_md_list(self, root_dir):
        dfs_list = []
        for root, dirs, files in os.walk(root_dir):
            if not f'{root_dir}/md_resources' in root:
                dfs_list.append((root, 'd'))
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.splitext(file_path)[-1] == '.md':
                        dfs_list.append((file_path, '-'))
        return sorted(dfs_list)

    def __initinfo(self, f_root_dir, t_root_dir, extinfo='', bkuptz=0):
        self.f_root_dir = rmlastslash(f_root_dir)
        self.t_root_dir = rmlastslash(t_root_dir)
        if not os.path.exists(self.t_root_dir):
            os.makedirs(self.t_root_dir)
        if not os.path.exists(self.t_root_dir + '/resources'):
            os.makedirs(self.t_root_dir + '/resources')
        self.dfs_list = self.__dir_md_list(self.f_root_dir)
        if extinfo == '':
            self.ifhd = InfoHolder(bkuptz)
        elif extinfo == 'YNote':
            self.ifhd = InfoHolderYNote(bkuptz)

    def __rsinfoget(self, rspath, ext='', subdir=''):
        phash = self.ifhd._rshash(rspath)
        rsinfo = self.ifhd.rsdict[phash]
        rsinfo['phash'] = phash
        rsinfo['rs2path_main'] = os.sep.join(
            [self.t_root_dir, rsinfo['id'] + '.md'])
        if subdir != '':
            rsinfo['rs2path_res'] = os.sep.join(
                [self.t_root_dir, subdir, rsinfo['id'] + ext])
        return rsinfo

    def __t2proc(self, rspath, name='', isroot=False):
        self.ifhd.updatersdict(rspath, 2, name, isroot)
        rsinfo = self.__rsinfoget(rspath)
        content = rsinfo['des']
        with open(rsinfo['rs2path_main'], 'w') as f:
            f.write(content)
        print(f"--t2-- writed file {rsinfo['rs2path_main']}")
        self.ifhd.rsdict[rsinfo['phash']] = {'id': rsinfo['id']}

    def __t4proc(self, rspath, name=''):
        self.ifhd.updatersdict(rspath, 4, name)
        rsinfo = self.__rsinfoget(
            rspath, os.path.splitext(rspath)[-1], 'resources')
        content = rsinfo['des']
        with open(rsinfo['rs2path_main'], 'w') as f:
            f.write(content)
        print(f"--t4-- writed file {rsinfo['rs2path_main']}")
        copy(rspath, rsinfo['rs2path_res'])
        print(f"--t4-- copied {rspath} to {rsinfo['rs2path_res']}")
        rsid = rsinfo['id']
        del self.ifhd.rsdict[rsinfo['phash']]
        return rsid

    def __picproc(self, matched):
        picstr = matched.group('piclinked')
        pic_info = picstr[2:-1].split('](')
        if os.path.exists(pic_info[-1]):
            rsid = self.__t4proc(pic_info[-1], pic_info[0])
            return f'![{pic_info[0]}](:/{rsid})'
        else:
            return picstr

    def __t1proce(self, rspath):
        self.ifhd.updatersdict(rspath, 1)
        rsinfo = self.__rsinfoget(rspath)
        with open(rspath, 'r') as f:
            content = f.read()
        regex_pic = re.compile(r'(?P<piclinked>!\[(.+?)\))')
        content = regex_pic.sub(self.__picproc, content)
        content = rsinfo['name'] + '\n' + '\n' + content + '\n' + rsinfo['des']
        with open(rsinfo['rs2path_main'], 'w') as f:
            f.write(content)
        print(f"--t1-- writed file {rsinfo['rs2path_main']}")
        del self.ifhd.rsdict[rsinfo['phash']]

    def md2jex(self, f_root_dir, t_root_dir, extinfo='', nbname='JoplinNote transformed by dir2jex', bkuptz=0):
        self.__initinfo(f_root_dir, t_root_dir, extinfo, bkuptz)
        self.__t2proc(self.dfs_list[0][0], nbname, True)
        for i in self.dfs_list[1:]:
            if i[-1] == 'd':
                self.__t2proc(i[0])
            elif i[-1] == '-':
                self.__t1proce(i[0])


if __name__ == '__main__':
    f_root_dir = './notes-md'
    t_root_dir = './notes-jex'
    extinfo = 'YNote'
    nbname = 'YNoteOut'
    bkuptz = 8
    transer = Md2Jex()
    transer.md2jex(f_root_dir, t_root_dir, extinfo, nbname, bkuptz)
