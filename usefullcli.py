import json
import os


def dir_file_list(root_dir, tocsv=False, csvfn='dfs_list'):
    dfs_list = []
    for root, dirs, files in os.walk(root_dir):
        dfs_list.append((root, 'd'))
        for file in files:
            file_path = os.path.join(root, file)
            dfs_list.append((file_path, '-'))
    dfs_list = sorted(dfs_list)
    if tocsv == True:
        with open(csvfn + '.csv', 'w') as f:
            for i in dfs_list:
                f.write(i[0]+','+str(i[1])+'\n')
    return dfs_list


def rm_json(f_root_dir):
    dfs_list = dir_file_list(f_root_dir)
    count = 0
    for i in dfs_list:
        if i[1] == '-' and os.path.splitext(i[0])[-1] == '.json':
            pdcCMD = f'rm "{i[0]}"'
            os.system(pdcCMD)
            count += 1
            print(f'removed: {i[0]}')
    return count


def rm_directory(f_root_dir='./'):
    print(f"rm_directory under: {os.path.abspath(f_root_dir)}")
    dfs_list = dir_file_list(f_root_dir)
    count = 0
    for i in dfs_list:
        if i[1] == '-' and os.path.split(i[0])[-1] == '.directory':
            pdcCMD = f'rm "{i[0]}"'
            os.system(pdcCMD)
            count += 1
    return count


print('rmcount_directory: ', rm_directory())


# 根据 去除文件名缀后 的所有文件，返回 仅出现单数次 的文件的列表
def getungeted(f_root_dir):
    dfs_list = dir_file_list(f_root_dir)
    uglist = ['']
    for i in dfs_list:
        if i[1] == '-':
            pse_i = os.path.splitext(i[0])[0]
            pse_l = os.path.splitext(uglist[-1])[0]
            if pse_i == pse_l:
                uglist.pop()
            else:
                uglist.append(i[0])
    del uglist[0]
    return uglist


# only for YNote .json file
def getinfo(jflis):
    idinfo = {}
    for i in jflis:
        if os.path.splitext(i)[-1] == '.json':
            info = {}
            with open(i, 'r') as jfile:
                jdic = json.load(jfile)
            info['name'] = jdic['fileEntry']['name']
            info['url'] = jdic['fileMeta']['sourceURL']
            info['ctm'] = jdic['fileEntry']['createTimeForSort']
            info['mtm'] = jdic['fileEntry']['modifyTimeForSort']
            idinfo[jdic['fileEntry']['id']] = info
    return idinfo


if __name__ == '__main__':
    # print('rmcount_json: ', rm_json('./notes-docx'))
    print('rmcount_directory: ', rm_directory('./notes-docx'))
    uglist = getungeted('./notes-docx')
    idinfo = getinfo(uglist)
    print(uglist)
    print(idinfo)
