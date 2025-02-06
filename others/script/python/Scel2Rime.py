import os
import requests
import glob
import datetime

def download_newest_scel_file(file_name):
    """从搜狗词库下载最新的 scel 文件"""
    url = 'https://pinyin.sogou.com/d/dict/download_cell.php?id=4&name=%E7%BD%91%E7%BB%9C%E6%B5%81%E8%A1%8C%E6%96%B0%E8%AF%8D%E3%80%90%E5%AE%98%E6%96%B9%E6%8E%A8%E8%8D%90%E3%80%91'
    r = requests.get(url)
    with open(file_name, 'wb') as f:
        f.write(r.content)

def convert_scel_to_rime():
    """使用 ImeWlConverterCmd.dll 进行转换"""
    scel_md5_files = glob.glob("*.scel")

    # 获取环境变量或默认值
    rime_freq = os.getenv('RIME_FREQ', '100')
    scel_output_file = 'sogou_popular.dict.yaml'  # 始终输出为 sogou_popular.dict.yaml

    if scel_md5_files:
        scel_files_str = " ".join(scel_md5_files)
        command = f'''dotnet /tmp/imewlconverter/publish/ImeWlConverterCmd.dll -i:scel {scel_files_str} -r:{rime_freq} -ft:"rm:eng|rm:num|rm:space|rm:pun" -o:rime "{scel_output_file}"'''
        os.system(command)
    else:
        print("未找到 .scel 文件")

def update_yaml_file(dict_name, scel_output_file):
    """更新 Rime 词库的 YAML 文件格式"""
    data1 = '''# Rime dictionary
# encoding: utf-8
#
#sogou 输入法网络流行新词
#https://pinyin.sogou.com/dict/detail/index/4
# 部署位置：
# ~/.config/ibus/rime  (Linux ibus)
# ~/.config/fcitx/rime  (Linux fcitx)
# ~/Library/Rime  (Mac OS)
# %APPDATA%\\Rime  (Windows)
#
# 于重新部署后生效
#
---
'''

    # 创建名称
    data2 = "name: " + dict_name + "\n"

    # 创建时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data3 = "version: \"" + now + "\"\n"

    data4 = '''
sort: by_weight
use_preset_vocabulary: false
columns:
  - text # 第一列字／词
  - code # 第二列码
  - weight # 第三列字／词频
...
'''

    # 打开目标文件并写入数据
    with open(scel_output_file, "r+") as output_file:
        old = output_file.read()
        output_file.seek(0)
        output_file.write(data1)
        output_file.write(data2)
        output_file.write(data3)
        output_file.write(data4)
        output_file.write(old)

def main():
    file_name = 'sogou_popular.scel'
    
    # 下载最新的 scel 文件
    download_newest_scel_file(file_name)

    # 转换 scel 为 Rime 词库
    convert_scel_to_rime()

    # 更新 YAML 文件
    dict_name = "sogou_popular"  # 请根据实际情况设置字典名称
    scel_output_file = 'sogou_popular.dict.yaml'
    update_yaml_file(dict_name, scel_output_file)

if __name__ == '__main__':
    main()
