import zipfile
from pathlib import Path
import shutil
import sys


def unzip(origin_file, target_dir):
    '''
    解压zip格式压缩包
    '''
    with zipfile.ZipFile(origin_file) as zf:
        zf.extractall(target_dir)


def zip(folder_path, zip_path):
    '''
    以zip格式压缩文件夹和文件，文件结构不变
    '''
    folder_path = Path(folder_path)
    zip_path = Path(zip_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in folder_path.glob('**/*'):
            if file.is_file():
                zf.write(file, file.relative_to(folder_path))
            else:
                zf.write(file, file.relative_to(folder_path) / '')

def transfer(target_dir):
    '''
    将文件夹下的数据格式转换成Fiddler的格式
    '''
    # 获取目录下下所有文件夹
    dirs = [x for x in Path(target_dir).iterdir() if x.is_dir()]
    # 按照文件夹名排序(文件夹名为整数)
    dirs.sort(key=lambda x: int(x.name))
    length = len(str(len(dirs)))

    # 创建新文件夹raw
    raw = Path(target_dir) / 'raw'
    raw.mkdir()

    # 对每个文件夹下的文件进行处理
    for dir in dirs:
        # 获取request.hcy和response.hcy文件
        request_file = dir / 'request.hcy'
        response_file = dir / 'response.hcy'

        # 生成新文件名(*_c.txt和*_s.txt，*为dir的名称，长度为length，不足在前面补0)
        request_file_new = dir.name.zfill(length) + '_c.txt'
        response_file_new = dir.name.zfill(length) + '_s.txt'


        # 将request.hcy和response.hcy文件移动到raw，并重命名
        shutil.move(request_file, raw / request_file_new)
        shutil.move(response_file, raw / response_file_new)

    # 删除所有文件夹
    for dir in dirs:
        shutil.rmtree(dir)


def main():
    # 获取输入参数
    args = sys.argv[1:]
    if len(args) == 1:
        file = args[0]
    else:
        file = input('请输入HttpCanary的抓包文件(zip格式)：')

    # 如果文件后缀不是zip，则添加后缀
    if not file.endswith('.zip'):
        file += '.zip'

    # 判断文件是否存在
    if not Path(file).exists():
        print('文件不存在')
        return

    # 如果已经存在tmp文件夹，则删除tmp及其下的所有文件和文件夹
    if Path('tmp').exists():
        shutil.rmtree('tmp')

    # 解压HttpCanary的抓包文件
    unzip(file, 'tmp')

    # 转换文件
    transfer('tmp')

    target_file = file.split('.')[0] + '_Fiddler.saz'
    # 压缩文件夹
    zip('tmp', target_file)

    # 删除tmp文件夹
    shutil.rmtree('tmp')

    # 判断是否转换成功
    if Path(target_file).exists():
        print('转换成功')
    else:
        print('转换失败')
    input('按任意键退出')


if __name__ == '__main__':
    main()