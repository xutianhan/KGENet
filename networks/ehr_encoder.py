import sys
sys.path.append('/')
from transformers import LongformerModel
from transformers import LongformerTokenizerFast
import torch as th
import torch.nn as nn

class EHREncoder():
    def __init__(self, model_name):
        # 加载 Clinical-Longformer 模型和分词器
        self.tokenizer = LongformerTokenizerFast.from_pretrained(model_name)
        self.model = LongformerModel.from_pretrained(model_name)


    # 加载KG的文本属性描述
    def load_data(self, train_file):
        ehr_list = []
        with open(train_file, 'r') as f1:
            for line in f1:
                line = line.strip()
                array = line.split('\t')
                if len(array) < 4:
                    continue
                ehr_text = array[2]
                labels = array[3]
                data = (ehr_text, labels)
                ehr_list.append(data)
        return ehr_list


    def compute_ehr_embedding(self, ehr_text):
        # 对文本进行编码
        inputs = self.tokenizer(ehr_text, return_tensors="pt", padding="max_length", truncation=True, max_length=4096)
        # Get the input embeddings
        input_embeddings = self.model.get_input_embeddings()

        token_embeddings = input_embeddings(inputs['input_ids'])
        # print("Clinical Longformer embeddings shape:", token_embeddings.shape)
        return token_embeddings

    def batch_ehr_embeddings(self, batch_ehr_text):
        embedding_list = []
        for ehr_text in batch_ehr_text:
            ehr_embedding = self.compute_ehr_embedding(ehr_text)
            embedding_list.append(ehr_embedding)
        W = th.cat(embedding_list, dim=0)
        batch_ehr_embeddings = nn.Embedding.from_pretrained(W, freeze=True)
        return batch_ehr_embeddings


if __name__ == "__main__":
    print('start!')
    model_name = "yikuan8/Clinical-Longformer"
    # train_file = '/Users/guyixun/Documents/PHD/healthcare-code/ICD-coding-baseline/mimicdata/icd_knowledge/core-attribute/train_50_entities.csv'
    ehr_text = "costal margin tenofovir disoproxil fumarate ill contacts bilirubin lactate urinalysis toxic repeated sputum complains hospital stay exposure venous distention subcutaneously levoxyl access issues fibrosis states medquist36 number primaquine clindamycin clindamycin epivir movements transferred hospital ward tenofovir noninvasive positive pressure ventilation bronchoscopy sweats physical examination electrocardiogram surveillance afebrile stitle visit right upper quadrant ultrasound primary care medications multivitamin blood pressure staphylococcus aureus strength extremities status discharged home instructions weeks codeine guaifenesin empiric pneumocystis negative levoxyl exertion mouth issue system problems air percussion regimen acyclovir fluconazole carinii pneumonia respiratory rate diagnosed antibiotics sleep multivitamin penicillin pulmonary issues emergency room nitrogen creatinine lamivudine alcohol illicit drugs increased positive bowel sounds improved mcg every levoxyl mcg lower extremity edema intravenous nasal cannula diabetes twice subcutaneously regular insulin sliding scale gram positive cocci pairs twice per lantus respiratory status liters oxygen saturation issues child location elevated anicteric mucous membranes viral pneumonia mg nausea family history family history drug use thorax intact neutrophils tapered time lantus aspartate aminotransferase allergies vancomycin laboratory values blood cultures clearance secondary respiratory distress room air blood sugars discharged lantus tricuspid valve obscured dry extraocular medication regimen steroid drugs medical history sentences cachectic prednisone saline clindamycin one female liver biopsy cranial nerves noncontributory chemistries intravenously sinus tachycardia unchanged chest x ray valvular abnormalities class cirrhosis right atrium chest x ray total course subcutaneously sliding scale primaquine vancomycin therapy cardiovascular examination tablets cytosis saturate metabolic disease sinusoidal symptoms clinic inserted sulfa dapsone heart rate three mg neurologic examination tachycardia murmurs xii intact low viral load pertinent abdomen husband cd4 hepatomegaly alkaline phosphatase total bilirubin fevers fluconazole taper house dyspnea cc cc aztreonam esophagogastroduodenoscopy insulin general ill toxic week course tuberculosis cirrhosis cholangitis pneumonia decreased codeine guaifenesin syrup cholelithiasis gallbladder wall zantac rash dapsone chest x ray tapered blood sugars blood urea room noninvasive positive pressure ventilation normal saline time blood cultures didanosine fatigue bilateral dapsone klonopin bile duct followup alanine aminotransferase alkalosis secondary highly active hypothyroidism temperature increasing mild diffuse tenderness sliding scale emergency department presentation low pao2 hospital ward arterial blood gas acyclovir pneumocystis two lung hospital diflucan q 6h leukocyte esterase dictated interstitial opacities oxygen saturations social history lives intensive care unit improve tolerated medications tablet lantus subcutaneously sliding scale allergies intravenous antibiotics illness air liters secondary lantus subcutaneously viread right upper quadrant ultrasound transfusions grew methicillin diabetes mellitus sulfa drugs shortness breath cough human immunodeficiency virus bacteremia white blood cell"
    encoder = EHREncoder(model_name)
    embeddings = encoder.compute_ehr_embedding(ehr_text)
    print('end!')



