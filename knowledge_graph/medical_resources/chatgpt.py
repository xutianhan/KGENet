import openai
import time

def get_query(query_index, disease_name):
    template_list = [
        "What is \"%s\"?",
        "What are the symptoms of \"%s\"?",
        "What are the physical signs of \"%s\"?",
        "What are the causes and risk factors for \"%s\"?",
        "What tests are needed to diagnose \"%s\"?",
        "What treatments are available for \"%s\"?",
        "What drugs are commonly used to treat \"%s\"?",
        "Which hospital department to visit for \"%s\"?"
    ]
    query = template_list[query_index] % disease_name
    return query

def process(icd_file, out_path):
    file_index = 0
    disease_index = 0
    with open(icd_file) as f_icd:
        for line in f_icd:
            print(disease_index)
            if file_index == 0 and disease_index == 0:
                file_name = out_path + "part-%s.txt" % str(file_index)
                out_f = open(file_name, 'w')
            line = line.strip()
            if line == '':
                continue
            arr = line.split(',')
            if len(arr) < 4:
                continue
            icd_code = arr[1].replace('"', '').strip()
            short_title = arr[2].replace('"','').replace(',', '').strip()
            long_title = arr[3].replace('"','').replace(',', '').strip()
            out_list = []
            out_list.append(icd_code)
            out_list.append(short_title)
            out_list.append(long_title)

            for query_index in range(0, 8):
                query = get_query(query_index, long_title)
                res = chat_gpt(query)
                time.sleep(2)
                out_list.append(res)

            out_line = '\t'.join(out_list) + "\n"
            out_f.write(out_line)
            disease_index += 1
            if disease_index % 200 == 0:
                out_f.close()
                file_index += 1
                file_name = out_path + "part-%s.txt" % str(file_index)
                out_f = open(file_name, 'w')
            if disease_index == 1001:
                out_f.close()
                print("get response end!")
    f_icd.close()

def chat_gpt(query):
    openai.api_key = ""
    res_str = 'null'
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=query,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )
        if response['choices'][0]['finish_reason'] == 'stop':
            res_str = str(response['choices'][0]['text'])
            res_str = res_str.strip()
            res_str = res_str.replace("\n", ".").replace("\t", ",")
    except BaseException as err:
        print(err)
        time.sleep(60)
        res_str = 'null'
    return res_str


if __name__ == '__main__':
    icd_file = '/preprocess/Key-algo/key1.csv'
    out_path = '~/healthcare-code/ICD-coding-baseline/KEGNet/preprocess/gpt-response/key1/'
    process(icd_file, out_path)



