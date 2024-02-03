# 搜狗词库scel格式转换为Rime词库yaml格式

import struct
import datetime
import requests
import os

NO_REPEAT_WORD_COUNT_OFFSET = 0x120  # 不重复词数位移
PIN_YIN_OFFSET = 0x1540  # 拼音表位移
WORD_OFFSET = 0x2628  # 汉语词组表位移

PinYinDict = {}
WordList = []


def read_uint(data):
    return struct.unpack('H', data)[0]


def read_scel_file(file_name):
    with open(file_name, 'rb') as f:
        data = f.read()
        f.close()
    return data


def byte_to_str(data):
    length = len(data)
    res = u''
    for index in range(0, length, 2):
        t = chr(read_uint(data[index:index + 2]))
        if t == u'\r':
            res += u'\n'
        elif t != u' ':
            res += t
    return res


def get_pin_yin_dict(data):
    pin_yin_dict = {}
    table_size = read_uint(data[0:2])
    # print("拼音表长度:", table_size)
    data = data[4:]
    i = 0
    for _ in range(0, table_size):
        index_buffer = data[i:i + 2]
        index = read_uint(index_buffer)

        i += 2
        pin_yin_len_buffer = data[i:i + 2]
        pin_yin_len = read_uint(pin_yin_len_buffer)

        i += 2
        pin_yin_buffer = data[i:i + pin_yin_len]
        pin_yin = byte_to_str(pin_yin_buffer)

        pin_yin_dict[index] = pin_yin

        i += pin_yin_len
    return pin_yin_dict


def get_word(data, pin_yin_dict):
    word_list = []
    no_repeat_word_count = read_uint(data[NO_REPEAT_WORD_COUNT_OFFSET:NO_REPEAT_WORD_COUNT_OFFSET + 2]) + \
                           read_uint(data[NO_REPEAT_WORD_COUNT_OFFSET + 2:NO_REPEAT_WORD_COUNT_OFFSET + 4])
    index = 0
    data = data[WORD_OFFSET:]
    for _ in range(0, no_repeat_word_count):
        same_num = read_uint(data[index:index + 2])
        # print("同音词数量:", same_num)

        index += 2
        pin_yin_index_length = read_uint(data[index:index + 2])
        # print("拼音索引长度:", pin_yin_index_length)

        index += 2
        pin_yin_list = []
        for j in range(0, pin_yin_index_length, 2):
            pin_yin_list.append(pin_yin_dict[read_uint(data[index + j:index + j + 2])])
        # print("拼音索引:", pin_yin_array)

        index += pin_yin_index_length
        for _ in range(0, same_num):
            word_length = read_uint(data[index:index + 2])
            # print("词组长度:", word_length)

            index += 2
            word = byte_to_str(data[index:index + word_length])
            # print("词组:", word)

            index += word_length
            order_length = read_uint(data[index:index + 2])
            # print("排序序号长度:", order_length)

            index += 2
            order = read_uint(data[index:index + 2]) + struct.unpack('H', data[index + 2:index + 4])[0]
            # print("order:", order)

            word_list.append((word, pin_yin_list, order))
            index += order_length
    return word_list, index


def get_black_list(data):
    # 前12个字节为黑名单标志: DELTBL
    word_count = read_uint(data[12:14])
    data = data[14:]
    index = 0
    for _ in range(0, word_count):
        word_length = read_uint(data[index:index + 2])
        index += 2
        # print("黑词:", byte2str(data[index:index + word_length * 2]))
        index += word_length * 2


def write_rime_file(data):
    data.sort(key=lambda x: x[2])
    name = "sogou_popular"
    rime_file_name = name + ".dict.yaml"
    version = datetime.datetime.now().strftime('%Y.%m.%d')
    with open(rime_file_name, 'w', encoding='utf-8') as f:
        f.write(f'''---\nname: {name}\nversion: "{version}"\nsort: by_weight\nuse_preset_vocabulary: false\n...\n\n''')
        for i in data:
            f.write(i[0] + '\t' + ' '.join(i[1]) + '\t1\n')


def download_newest_scel_file(file_name):
    # 从搜狗词库下载最新的scel文件
    url = 'https://pinyin.sogou.com/d/dict/download_cell.php?id=4&name=%E7%BD%91%E7%BB%9C%E6%B5%81%E8%A1%8C%E6%96%B0%E8%AF%8D%E3%80%90%E5%AE%98%E6%96%B9%E6%8E%A8%E8%8D%90%E3%80%91'
    r = requests.get(url)
    with open(file_name, 'wb') as f:
        f.write(r.content)
        f.close()


def delete_scel_file(file_name):
    os.remove(file_name)


def main():
    file_name = 'sogou_popular.scel'
    # 下载最新的scel文件
    download_newest_scel_file(file_name)

    # 读取scel文件
    data = read_scel_file(file_name)

    # 获取拼音表
    pin_yin_dict = get_pin_yin_dict(data[PIN_YIN_OFFSET:WORD_OFFSET])

    # 获取词组表
    word_list = get_word(data, pin_yin_dict)

    # 写入文件
    write_rime_file(word_list[0])

    # 删除scel文件
    # delete_scel_file(file_name)


if __name__ == '__main__':
    main()

#     # print("不重复词数：", read_uint(data[0x120:0x122]) + read_uint(data[0x122:0x124]))
#     # print("重复词数：", read_uint(data[0x124:0x126]))
#     # print("重复词数：", read_uint(data[0x126:0x128]))
#     # print ("备注：", byte2str(data[0x540:0xD40]))
#     # print ("词库示例：", byte2str(data[0xD40:0x1540]))
#     # print ("地点：", byte2str(data[0x338:0x540]))
#     # print ("词库名：", byte2str(data[0x130:0x338]))
