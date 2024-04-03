import re
def remove_punctuation(text):
    # 使用正则表达式替换所有标点符号为空字符串
    return re.sub(r'[^\w\s]', '', text)

f_out = open('50_attribute.txt', 'w')
with open('50_attribute_old.txt', 'r') as f_in:
    for line in f_in:
        line = line.strip()
        array = line.split('\t')
        icd_code = array[0]
        text = array[1]
        clean_text = remove_punctuation(text)
        new_line = icd_code + '\t' + clean_text + '\n'
        f_out.write(new_line)
f_out.close()

