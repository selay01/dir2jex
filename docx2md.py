import os
import sys
from shutil import copy


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


def docxs2md(f_root_dir, t_root_dir, media_dir=None, pdcpath='./pandoc'):
    if media_dir == None:
        media_dir = t_root_dir
    media_dir = os.path.realpath(media_dir)
    dfs_list = dir_file_list(f_root_dir)
    for i in dfs_list:
        j0 = i[0].replace(f_root_dir, t_root_dir)
        if i[1] == 'd' and (not os.path.exists(j0)):
            os.mkdir(j0)
        elif i[1] == '-' and os.path.splitext(i[0])[-1] == '.docx':
            file_out = os.path.splitext(j0)[0] + '.md'
            file_name = os.path.split(os.path.splitext(j0)[0])[-1]
            pdcCMD = f'{pdcpath} -o "{file_out}" \
                -t commonmark \
                --extract-media="{media_dir}/md_resources/{file_name}" \
                "{i[0]}"'
            os.system(pdcCMD)
            print(f"converted {i[0]} to md format.")
            copy(os.path.splitext(i[0])[0] +
                 '.json', os.path.dirname(file_out))
            print(f"copied {os.path.splitext(i[0])[0] + '.json'}")


if __name__ == '__main__':
    f_root_dir = './notes-docx'
    t_root_dir = './notes-md'
    if sys.argv[-1] == '--test':
        media_dir = os.path.dirname(t_root_dir)
    else:
        media_dir = None
    pdcpath = './pandoc'
    docxs2md(f_root_dir, t_root_dir, media_dir, pdcpath)
