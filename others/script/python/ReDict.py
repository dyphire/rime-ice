import argparse
import re

def compare_and_remove_duplicates(base_file, additional_file, output_file):
    def extract_chinese_characters(line):
        # 使用正则表达式提取每行中的汉字
        chinese_characters = re.findall(r'[\u4e00-\u9fa5]+', line)
        return chinese_characters

    try:
        with open(base_file, 'r', encoding='utf-8') as basefile:
            base_lines = basefile.readlines()
            
        with open(additional_file, 'r', encoding='utf-8') as additionalfile:
            additional_lines = additionalfile.readlines()
            
        # 提取每行的汉字并进行比较
        base_characters = set(''.join(extract_chinese_characters(line)) for line in base_lines)
        
        # 找到在额外词库中出现但不在基础词库中出现的行
        unique_lines = [line for line in additional_lines if not any(char in base_characters for char in extract_chinese_characters(line))]
        
        # 写入结果到输出文件
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.writelines(unique_lines)
            
        print(f"行内容对比和去重完成，结果保存在 {output_file}")
        
    except Exception as e:
        print(f"出现错误: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="比较两个 Rime 词库中汉字并去重")
    parser.add_argument("base_file", help="基础词库文件路径")
    parser.add_argument("additional_file", help="额外词库文件路径")
    parser.add_argument("output_file", help="输出词库文件路径")

    args = parser.parse_args()
    
    compare_and_remove_duplicates(args.base_file, args.additional_file, args.output_file)
