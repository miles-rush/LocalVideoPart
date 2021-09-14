from gooey import Gooey, GooeyParser
import requests
import json
import os
import ffmpy
import time


# 全局变量
# 数据请求接口
fix = "/base/list"
# ffpath = 'D:\\KingRainGrey\\Download\\ffmpeg\\ffmpeg\\bin\\ffmpeg.exe'


@Gooey(
    richtext_controls=True,
    program_name="单机问卷系统本地工具",
    encoding="utf-8",
    language='chinese',
    # 再次执行，清除之前执行的日志
    clear_before_run=True,
    image_dir='./imgs',
    menu=[{
        'name': '功能',
        'items': [{
            'type': 'AboutDialog',
            'menuTitle': '使用说明',
            'name': '单机版问卷工具包',
            'description': '提供本地心理测评使用，提供包括问卷记录，视频统计分析等功能',
            'version': '0.0.1',
            'copyright': '2021',
            'website': 'http://81.69.223.15:7913/#/home',
            'developer': 'KingRainGrey、',
            'license': '口头授权'
        }, {
            'type': 'Link',
            'menuTitle': '打开问卷',
            'url': 'http://81.69.223.15:7913/#/home'
        },{
            'type': 'MessageDialog',
            'menuTitle': '帮助',
            'caption': '帮助',
            'message': '若有部分功能未响应，请使用管理员权限运行此程序。\n使用该程序必须保证ffmepg库运行正常\n此外使用该程序出现任何问题，可以联系计算机楼A513实验室。'
        },]
    }],
)
def main():
    parser = GooeyParser(description="本工具配合单机问卷系统联合使用")
    parser.add_argument('input', metavar='视频保存文件夹', help="选择回答卷时保存视频的本地文件夹", widget="DirChooser")
    parser.add_argument('out', metavar='视频输出文件夹', help="分割后的视频片段将会保存在该路径", widget="DirChooser")
    parser.add_argument('ffpath', metavar='ffmpeg路径', help="视频分割依赖ffmpage,请配置ffmpeg.exe路径",default='./ffmpeg/bin/ffmpeg.exe', widget="FileChooser")
    parser.add_argument('url', metavar="服务器地址", help="下行数据的服务器地址",default="http://81.69.223.15:7945",widget="TextField")
    args = parser.parse_args()


    print(args, flush=True)
    # 输入文件夹
    inputFilePath = args.input
    # 输出文件夹
    outFilePath = args.out
    # ffmpeg配置路径
    ffpath = args.ffpath
    url = '' + args.url + fix
    res = requests.get(url)
    res_dict = res.json()
    if res_dict['code'] == 200:
        print('-----数据下载成功-----')
        print('-----服务器数据-----')
        print(json.dumps(res_dict, indent=2, sort_keys=True, ensure_ascii=False))
        # 读取input文件夹内视频
        print('-----输入文件夹视频路径-----')
        inputFileList = get_all_path(inputFilePath)
        print(inputFileList)
        print('-----开始匹配分割-----')
        for path in inputFileList:
            arr = path.split("\\")
            # xxxxxxx.mkv
            filename = arr[len(arr)-1]
            # 提取到无格式的原始名
            filenamewithoutmkv = filename.split(".")[0]
            # 原始名与服务器数据进行比较
            datalist = res_dict['data']
            for data in datalist:
                name = data['content']['videoName']
                times = data['timePoint']
                if filenamewithoutmkv == name:
                    # 匹配到了
                    # 开始分割pre
                    print('-----' + '文件名:' + filename + '匹配到了服务器数据，开始分割' + '-----')

                    # 对时间进行取整处理
                    newtimeslist = []
                    for t in times:
                        if t == 0:
                            pass
                        else:
                            newt = int (t/1000)
                            newtimeslist.append(newt)
                    print('-----分割时间点-----')
                    print(newtimeslist)
                    print('-----按时间点开始分割-----')
                    pretime = 0
                    partname = 1
                    for t in newtimeslist:
                        # clip = VideoFileClip(path).subclip(pretime, t)
                        stime = time.strftime('%H:%M:%S', time.gmtime(pretime))
                        etime = time.strftime('%H:%M:%S', time.gmtime(t))
                        print('开始时间:' + stime)
                        print('结束时间:' + etime)
                        mkdir(outFilePath  + '\\' + filenamewithoutmkv + '\\')
                        outputfile = outFilePath  + '\\' + filenamewithoutmkv + '\\' + str(partname) + '.mp4'
                        print('输出文件:' + outputfile)
                        ff = ffmpy.FFmpeg(
                            executable= ffpath,
                            inputs={path:None},
                            outputs={outputfile : [
                                '-ss', stime,
                                '-t', etime,
                            ]}
                        )
                        ff.run()
                        # clip_video(path, outputfile, pretime, t)
                        pretime = t
                        partname = partname + 1

    else:
        print('-----数据下载失败-----')
        return
    print('-----运行结束-----')


def mkdir(path):
    # 引入模块
    import os

    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        return False

def get_all_path(open_file_path):
    rootdir = open_file_path
    path_list = []
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        com_path = os.path.join(rootdir, list[i])
        #print(com_path)
        if os.path.isfile(com_path):
            path_list.append(com_path)
        if os.path.isdir(com_path):
            path_list.extend(get_all_path(com_path))
    #print(path_list)
    return path_list


def success_print(text):
    print(f'\033[35m{text}\033[0m')

if __name__ == '__main__':
    # success_print('123')
    main()
