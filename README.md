**依赖：**

  Python3 和 pandoc；

  下载 [pandoc 2.9.2](https://github.com/jgm/pandoc/releases/tag/2.9.2) 平台对应的文件,解压,
  并把 pandoc 文件放于此文件(即README.MD)所在目录下；

  对于linux可直接[点此：pandoc 2.9.2](https://github.com/jgm/pandoc/releases/download/2.9.2/pandoc-2.9.2-linux-amd64.tar.gz)下载压缩包

**基本功能及用法：**

  将 ‘由 .docx文件 及 .json信息文件 构成的目录’ 转换为 用于导入Joplin的 ‘RAW-Joplin导出目录’。

  目前支持 有道云笔记的 .json信息文件。

  将放有docx文件的目录放于此文件(即README.MD)所在目录下,并重命名为 notes-docx,然后执行以下命令：

    python docx2md.py # 将创建 ./notes-md 目录,并放置转换出来的所有 md 文件 及 资源文件

    python md2jex.py # 将创建 ./notes-jex 目录,并放置转换出来的可用于导入Joplin的所有文件

  导入方法：

    打开 Joplin,文件-->导入-->RAW-Joplin导出目录；选择目录 notes-jex,点击确定

  消除渲染后多余行：

    打开 Joplin,工具-->选项-->插件-->勾选 启动软中断-->确定

**附加功能及用法：**

  按照笔记目录下载 有道云笔记 所有笔记的 xml/docx格式内容 + json笔记信息 到对应层级的目录。

    python YNoteGet.py 用户名 密码  ./notes-xml              # 下载 xml版本和json 信息

    python YNoteGet.py 用户名 密码  ./notes-docx docx        # 下载 docx版本和json 信息


  修改自 [YoudaoNoteExport](https://github.com/wesley2012/YoudaoNoteExport)；python3 适用

    限制：不能 下载笔记的相关附件

    增强：下载失败时,下次运行将下载剩余可下载项，不下载已下载项

**缘起及技术实现过程与思路：**

  有道云笔记 老用户,用久了累积了不少不爽,想找个替代,发现数据导出格式***！细思极？,发现了 Joplin,

  开源软件,数据导出格式透明简单,客户端丰富,支持多种云端同步,于是...

  最好,一步一步进行,互补影响,功能就可以单独被提取使用,于是：

    YNoteGet.py 用于导出 有道云笔记的所有笔记

  由于 Joplin 默认支持的是(?commonmark?)的md, 导入md目录 功能不对图片等资源导入,(怎么同步,我就不知道了)
  并且 pandoc 转换时 的资源目录(?只能使用绝对路径?),于是：

    docx2md.py 用于将 目录下的 docx 转换为 commonmark 格式,并复制同名json文件（如果有的话）,
    并保持了 目录结构,资源按照文件名（有道的笔记抓下来文件名大概不会相同,也就不用hash了）放于 md_resources 目录,
    因为 md文件中的资源使用了绝对路径,所有转换出来的目录不能改变位置（中间产物,也就不计较了）

    md2jex.py 用于将 docx2md.py 的转换产物 转换为 Joplin 的 RAW-Joplin导出目录（资源终于能被导入了）

**技术细节：**

    YNoteGet.py docx2md.py md2jex.py 每个都单独完成自己的任务,里面有一些信息,遇到问题,里面可能有答案
    低频使用工具,懒得详细写了,用得人多了再说吧

***测试参数：***

  ubuntu 18.04, x86_64；
  Python 3.7.3；
  [pandoc 2.9.2](https://github.com/jgm/pandoc/releases/download/2.9.2/pandoc-2.9.2-linux-amd64.tar.gz)；
  [Joplin-1.0.193(AppImage)](https://github.com/laurent22/joplin/releases/download/v1.0.193/Joplin-1.0.193.AppImage)

***要在win下使用(未测试)：***

  安装 Python3；

  下载 [pandoc 2.9.2](https://github.com/jgm/pandoc/releases/tag/2.9.2) win平台对应的文件,解压,
  并把 pandoc 文件放于此文件(即README.MD)所在目录下；

  [Joplin-1.0.193](https://github.com/laurent22/joplin/releases/tag/v1.0.193) win平台对应的文件
