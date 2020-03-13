# 修改自 https://github.com/wesley2012/YoudaoNoteExport；python3 适用
# 修复 获取docx时老旧笔记下载内容错误 的问题：忽略，不对其docx文件进行下载；下次运行可下载剩余可下载项
# 导出有道云笔记，保存为JSON和DOCX/XML文件。DOCX/XML文件是笔记的内容，DOCX包含图片，XML不包含图片，
# JSON文件是笔记的其它信息（包括标题、创建时间、修改时间等）
# 无法获取内容，可能因为无法在登录时输入验证码，使用 chrome 输入验证码 登录后，此脚本即可正常运行
# 无法下载 docx 是因为老旧笔记未被转化为新格式，使用 客户端 或 chrome 登录，打开那些笔记会自动转化，
# 等待一段（？可能需要十几个小时或一两天？）时间后再使用此脚本下载；此过程可反复尝试
# 20200310测试发现：win下客户端搜索功能不足，总是卡顿；此脚本无法下载的docx，
# 使用web下载会出现 服务器错误，需要等待一段（？可能需要十几个小时或一两天？）时间 再尝试
# 云笔记web上个别没有保存为word选项的笔记无法下载
# 注意：
#     python YNoteGet.py 用户名 密码  ./notes-xml              # 下载 xml版本和json 信息
#     python YNoteGet.py 用户名 密码  ./notes-docx docx        # 下载 docx版本和json 信息
#     此脚本对于包含附件的笔记不能导出附件


import hashlib
import json
import os
import sys
import time

import requests
from requests.cookies import create_cookie


def timestamp():
    return str(int(time.time() * 1000))


class YoudaoNoteSession(requests.Session):
    def __init__(self):
        requests.Session.__init__(self)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }

    def login(self, username, password):
        self.get('https://note.youdao.com/web/')

        self.headers['Referer'] = 'https://note.youdao.com/web/'
        self.get(
            'https://note.youdao.com/signIn/index.html?&callback=https%3A%2F%2Fnote.youdao.com%2Fweb%2F&from=web')

        self.headers['Referer'] = 'https://note.youdao.com/signIn/index.html?&callback=https%3A%2F%2Fnote.youdao.com%2Fweb%2F&from=web'
        self.get(
            'https://note.youdao.com/login/acc/pe/getsess?product=YNOTE&_=' + timestamp())
        self.get('https://note.youdao.com/auth/cq.json?app=web&_=' + timestamp())
        self.get(
            'https://note.youdao.com/auth/urs/login.json?app=web&_=' + timestamp())
        data = {
            "username": username,
            "password": hashlib.md5(password.encode('utf8')).hexdigest()
        }
        self.post('https://note.youdao.com/login/acc/urs/verify/check?app=web&product=YNOTE&tp=urstoken&cf=6&fr=1&systemName=&deviceType=&ru=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&er=https%3A%2F%2Fnote.youdao.com%2FsignIn%2F%2FloginCallback.html&vcode=&systemName=&deviceType=&timestamp=' + timestamp(), data=data, allow_redirects=True)
        self.get(
            'https://note.youdao.com/yws/mapi/user?method=get&multilevelEnable=true&_=' + timestamp())
        print(self.cookies)
        self.cstk = self.cookies.get('YNOTE_CSTK')

    def getRoot(self):
        data = {
            'path': '/',
            'entire': 'true',
            'purge': 'false',
            'cstk': self.cstk
        }
        response = self.post(
            'https://note.youdao.com/yws/api/personal/file?method=getByPath&keyfrom=web&cstk=%s' % self.cstk, data=data)
        rescontent = response.content.decode('utf8')
        if 'AUTHENTICATION_FAILURE' in rescontent:
            print('\n------Please login with Web or Client, then try again.------\n')
            return
        print('getRoot:' + rescontent)
        jsonObj = json.loads(rescontent)
        return jsonObj['fileEntry']['id']

    def getNote(self, id, saveDir):
        if os.path.exists('%s/%s.xml' % (saveDir, id)):
            return
        data = {
            'fileId': id,
            'version': -1,
            'convert': 'true',
            'editorType': 1,
            'cstk': self.cstk
        }
        url = 'https://note.youdao.com/yws/api/personal/sync?method=download&keyfrom=web&cstk=%s' % self.cstk
        response = self.post(url, data=data)
        with open('%s/%s.xml' % (saveDir, id), 'w') as fp:
            fp.write(response.content.decode('utf8'))
            print('Saved file: ', '%s/%s.xml' % (saveDir, id))

    def getNoteDocx(self, id, saveDir):
        if os.path.exists('%s/%s.docx' % (saveDir, id)):
            return
        url = 'https://note.youdao.com/ydoc/api/personal/doc?method=download-docx&fileId=%s&cstk=%s&keyfrom=web' % (
            id, self.cstk)
        response = self.get(url)
        if b'DATA_TRANSMISSION_FAILURE' in response.content:
            return
        else:
            with open('%s/%s.docx' % (saveDir, id), 'wb') as fp:
                fp.write(response.content)
                print('Saved file: ', '%s/%s.docx' % (saveDir, id))

    def getFileRecursively(self, id, saveDir, doc_type):
        data = {
            'path': '/',
            'dirOnly': 'false',
            'f': 'false',
            'cstk': self.cstk
        }
        url = 'https://note.youdao.com/yws/api/personal/file/%s?all=true&f=true&len=30&sort=1&isReverse=false&method=listPageByParentId&keyfrom=web&cstk=%s' % (
            id, self.cstk)
        lastId = None
        count = 0
        total = 1
        while count < total:
            if lastId == None:
                response = self.get(url)
            else:
                response = self.get(url + '&lastId=%s' % lastId)
            # print('getFileRecursively:' + response.content.decode('utf8'))
            jsonObj = json.loads(response.content)
            total = jsonObj['count']
            for entry in jsonObj['entries']:
                fileEntry = entry['fileEntry']
                id = fileEntry['id']
                name = fileEntry['name']
                # print('%s %s' % (id, name))
                if fileEntry['dir']:
                    subDir = saveDir + '/' + name
                    try:
                        os.lstat(subDir)
                    except OSError:
                        os.mkdir(subDir)
                    self.getFileRecursively(id, subDir, doc_type)
                else:
                    if not os.path.exists('%s/%s.json' % (saveDir, id)):
                        with open('%s/%s.json' % (saveDir, id), 'w') as fp:
                            fp.write(json.dumps(entry, ensure_ascii=False))
                            print('Saved file: ', '%s/%s.json' % (saveDir, id))
                    if doc_type == 'xml':
                        self.getNote(id, saveDir)
                    else:  # docx
                        self.getNoteDocx(id, saveDir)
                count = count + 1
                lastId = id

    def getAll(self, saveDir, doc_type):
        rootId = self.getRoot()
        self.getFileRecursively(rootId, saveDir, doc_type)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('args: <username> <password> [saveDir [doc_type]]')
        print('doc_type: xml or docx')
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    if len(sys.argv) >= 4:
        saveDir = sys.argv[3]
    else:
        saveDir = './YNotes'
    if len(sys.argv) >= 5:
        doc_type = sys.argv[4]
    else:
        doc_type = 'xml'
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    sess = YoudaoNoteSession()
    sess.login(username, password)
    sess.getAll(saveDir, doc_type)
