import argparse

def merge_rime_dictionaries(input_files, output_file):
    try:
        # 读取所有输入词库文件的内容
        merged_lines = []
        for input_file in input_files:
            with open(input_file, 'r', encoding='utf-8') as infile:
                merged_lines.extend(infile.readlines())

        # 写入结果到输出文件
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.writelines(merged_lines)

        print(f"合并完成，结果保存在 {output_file}")

    except Exception as e:
        print(f"出现错误: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="合并多个 Rime 词库文件")
    parser.add_argument("input_files", nargs='+', help="输入词库文件路径，可以指定多个文件")
    parser.add_argument("output_file", help="输出合并后的词库文件路径")

    args = parser.parse_args()

    merge_rime_dictionaries(args.input_files, args.output_file)
