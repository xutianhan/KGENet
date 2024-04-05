import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
import csv
import re


# 下载停用词列表（如果之前没有下载过的话）
nltk.download('stopwords')
nltk.download('punkt')

# 加载英文停用词列表
stop_words = set(stopwords.words('english'))
# 添加自定义停用词
custom_stopwords = {'admission', 'date', 'discharge', 'birth', 'sex', 'patient', 'year', 'years','month', 'months',
                    'day', 'days', 'hour', 'hours','morning', 'afternoon', 'evening', 'night','job', 'units', 'times'}
stop_words.update(custom_stopwords)

inpath = './train_50.csv'
outpath = './train_50_entities.csv'

# 加载 en_core_sci_sm 模型
scism = spacy.load("en_core_sci_sm")

# 加载spaCy的医学模型
med7 = spacy.load("en_core_med7_trf")


# 打开输入和输出文件
with open(inpath, 'r', newline='', encoding='utf-8') as infile, \
     open(outpath, 'w', newline='', encoding='utf-8') as outfile:
    # 创建CSV读写对象
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # 读取并写入表头
    header = next(reader)
    writer.writerow(header)

    # 逐行处理数据并写入输出文件
    for row in reader:
        # 在这里对TEXT字段进行所需的操作
        ehr_text = row[2]
        # 使用正则表达式替换所有标点符号为空字符串
        ehr_text = re.sub(r'[^\w\s]', '', ehr_text)
        # 分词
        words = word_tokenize(ehr_text)

        # 添加以 "name" 开头的词为停用词
        name_starting_words = [word for word in words if word.startswith('name')]
        stop_words.update(name_starting_words)
        # 去除停用词
        filtered_words = [word for word in words if word.lower() not in stop_words]

        # 输出处理后的文本
        filtered_text = ' '.join(filtered_words)

        # scism进行NER
        scism_res = scism(filtered_text)
        # med7进行药物NER
        med7_res = med7(filtered_text)

        entity_set = set()

        # 识别后结果加入set
        for ent in scism_res.ents:
            entity_set.add(ent.text)
        for ent in med7_res.ents:
            entity_set.add(ent.text)
        entity_text = ' '.join(entity_set)

        # 写入
        writer.writerow([row[0], row[1], entity_text, row[3], row[4]])
