# -*- coding:utf-8 -*-
"""
"""
import csv
import numpy as np
import networkx as nx

def findrange(icd,level,parient_child):

    for item in level:
        if '-' in item:
            tokens=item.split('-')
            if icd.startswith('E') or icd.startswith('V'):
                if int(icd[1:]) in  range(int(tokens[0][1:]),int(tokens[1][1:])+1):
                    parient_child.append((item,icd))
                    return item
            else:
                # 不是以E或者V开头的
                print(icd,tokens[0],tokens[1])
                if int(icd) in  range(int(tokens[0]),int(tokens[1])+1):
                    parient_child.append((item,icd))
                    return item
        else:
            if icd.startswith('E') or icd.startswith('V'):
                if int(icd[1:])==int(item[1:]):
                    #parient_child.append((item,icd))
                    return False
            else:
                # 不是以E或者V开头的
                if int(icd)==int(item):
                    #parient_child.append((item,icd))
                    return False

def build_tree(filepath):

    level2 = ['001-009', '010-018', '020-027', '030-041', '042', '045-049', '050-059', '060-066', '070-079', '080-088',
              '090-099', '100-104', '110-118', '120-129', '130-136', '137-139', '140-149', '150-159', '160-165',
              '170-176',
              '176', '179-189', '190-199', '200-208', '209', '210-229', '230-234', '235-238', '239', '240-246',
              '249-259',
              '260-269', '270-279', '280-289', '290-294', '295-299', '300-316', '317-319', '320-327', '330-337', '338',
              '339', '340-349', '350-359', '360-379', '380-389', '390-392', '393-398', '401-405', '410-414', '415-417',
              '420-429', '430-438', '440-449', '451-459', '460-466', '470-478', '480-488', '490-496', '500-508',
              '510-519',
              '520-529', '530-539', '540-543', '550-553', '555-558', '560-569', '570-579', '580-589', '590-599',
              '600-608',
              '610-611', '614-616', '617-629', '630-639', '640-649', '650-659', '660-669', '670-677', '678-679',
              '680-686',
              '690-698', '700-709', '710-719', '720-724', '725-729', '730-739', '740-759', '760-763', '764-779',
              '780-789',
              '790-796', '797-799', '800-804', '805-809', '810-819', '820-829', '830-839', '840-848', '850-854',
              '860-869',
              '870-879', '880-887', '890-897', '900-904', '905-909', '910-919', '920-924', '925-929', '930-939',
              '940-949',
              '950-957', '958-959', '960-979', '980-989', '990-995', '996-999']
    level2_E=['E000-E899', 'E000', 'E001-E030', 'E800-E807', 'E810-E819', 'E820-E825', 'E826-E829', 'E830-E838',
              'E840-E845', 'E846-E849', 'E850-E858', 'E860-E869', 'E870-E876', 'E878-E879', 'E880-E888', 'E890-E899',
              'E900-E909', 'E910-E915', 'E916-E928', 'E929', 'E930-E949', 'E950-E959', 'E960-E969', 'E970-E978',
              'E980-E989', 'E990-E999']
    level2_V=['V01-V91', 'V01-V09', 'V10-V19','V20-V29','V30-V39', 'V40-V49', 'V50-V59', 'V60-V69', 'V70-V82', 'V83-V84',
              'V85', 'V86', 'V87', 'V88', 'V89','V90','V91']

    allICDS=[] # 保存所有的icds
    with open(filepath,'r') as f:
        for row in f:
            array = row.split('\t')
            icd = array[0]
            allICDS.append(icd)

    allICDS_=list(set(allICDS))
    allICDS_.sort(key=allICDS.index)
    print('all icd codes:', len(allICDS_))

    #针对EHR中出现的每个icd code 找到它的所有父节点，以(parient,child)形式保存
    parient_child=[]
    hier_icds={}
    print('循环开始：针对EHR中出现的每个icd code 找到它的所有父节点')
    for icd in allICDS_:
        hier_icd=[icd]
        # 先判断icd中是否包含E ,例如：E939.58 or E824.1
        if icd.startswith('E'):
            # 先判断是否包含小数点：
            if '.' in icd:
                tokens = icd.split('.')
                # 再判断小数点后有几位
                if len(tokens[1])==1:
                    # 去掉小数点之后会得到第一个父节点 （E824,E824.1）
                    parient_child.append((tokens[0],icd))
                    hier_icd.insert(0,tokens[0])
                    # 找到E824 对应的范围
                    parient=findrange(tokens[0],level2_E,parient_child)
                    if parient!=False:
                        hier_icd.insert(0, parient)

                elif len(tokens[1])==2:
                    #去掉小数点后得到会得到三层的父节点
                    parient_child.append((icd[:-1],icd)) #（E939.5，E939.58）
                    hier_icd.insert(0, icd[:-1])
                    parient_child.append((tokens[0],icd[:-1])) #（E939，E939.5）
                    hier_icd.insert(0, tokens[0])
                    parient=findrange(tokens[0],level2_E,parient_child)
                    if parient!=False:
                        hier_icd.insert(0, parient)

        # 先判断icd中是否包含V ,例如：V85.54 or V86.0
        elif icd.startswith('V'):
            # 先判断是否包含小数点：
            if '.' in icd:
                tokens = icd.split('.')
                # 再判断小数点后有几位
                if len(tokens[1]) == 1:
                    # 去掉小数点之后会得到第一个父节点 （V86.0,V86）
                    parient_child.append((tokens[0], icd))
                    hier_icd.insert(0, tokens[0])
                    # 找到E824 对应的范围
                    parient=findrange(tokens[0], level2_V, parient_child)
                    if parient!=False:
                        hier_icd.insert(0, parient)


                elif len(tokens[1]) == 2:
                    # 去掉小数点后得到会得到三层的父节点
                    parient_child.append((icd[:-1], icd))  # （E939.5，E939.58）
                    hier_icd.insert(0, icd[:-1])
                    parient_child.append((tokens[0], icd[:-1]))  # （E939，E939.5）
                    hier_icd.insert(0, tokens[0])
                    parient=findrange(tokens[0], level2_V, parient_child)
                    if parient!=False:
                        hier_icd.insert(0, parient)

        else:
            # 先判断是否包含小数点：
            if '.' in icd:
                tokens = icd.split('.')
                # 再判断小数点后有几位
                if len(tokens[1]) == 1:
                    # 去掉小数点之后会得到第一个父节点 （824,824.1）
                    parient_child.append((tokens[0], icd))
                    hier_icd.insert(0, tokens[0])
                    # 找到824 对应的范围
                    parient=findrange(tokens[0], level2, parient_child)
                    if parient!=False:
                        hier_icd.insert(0, parient)

                elif len(tokens[1]) == 2:
                    # 去掉小数点后得到会得到三层的父节点
                    parient_child.append((icd[:-1], icd))  # （E939.5，E939.58）
                    hier_icd.insert(0, icd[:-1])
                    parient_child.append((tokens[0], icd[:-1]))  # （E939，E939.5）
                    hier_icd.insert(0, tokens[0])
                    parient=findrange(tokens[0], level2, parient_child)
                    if parient!=False:
                        hier_icd.insert(0, parient)
            else: #疾病中不包含小数点
                # 找到824 对应的范围
                parient=findrange(icd, level2, parient_child)
                if parient!=False:
                    hier_icd.insert(0, parient)

        if icd not in hier_icds:
            hier_icds[icd]=hier_icd

    print('循环结束')
    # 将层级的labels转换为id
    node2id={}
    hier_labels_init=hier_icds.copy()

    for icd,hier_icd in hier_icds.items():
        #当hier_icdIds不满足长度为4的话 使用父节点进行填充
        if len(hier_icd)<5:
            hier_icd=hier_icd+[hier_icd[-1]]*(5-len(hier_icd))
        hier_icds[icd]=hier_icd
        #路径上的每个node 分配一个节点
        for item in hier_icd:
            if item not in node2id:
                node2id[item]=len(node2id)
    hier_labels_init_new={}
    for icd, hier_icd in hier_labels_init.items():
        icdId = node2id.get(icd)
        hier_icdIds = [node2id.get(item) for item in hier_icd]
        hier_labels_init_new[icdId]=hier_icdIds

    node2id['ROOT'] = len(node2id)
    # 将字符路径转换为id型路径
    level0 = set()
    level1 = set()
    level2 = set()
    level3 = set()

    # 根据parient_child 生成一个邻接矩阵，用来方便寻找每个子节点的孩子
    parient_child = []
    adj = np.zeros((len(node2id), len(node2id)))

    hier_dicts={}
    
    print('循环开始：沿着树路径，创建adj')
    for icd, hier_icd in hier_icds.items():
        print('hier_icd:', hier_icd)
        icdId=node2id.get(icd)
        hier_icdIds=[node2id.get(item) for item in hier_icd]
        #hier_dicts_init[icdId]=hier_icdIds.copy()

        hier_icdIds.insert(0,node2id.get('ROOT'))
        hier_dicts[icdId]=hier_icdIds
        level0.add(hier_icdIds[1])
        level1.add(hier_icdIds[2])
        level2.add(hier_icdIds[3])
        level3.add(hier_icdIds[4])
        # 沿着树路径 创建adj
        for i in range(len(hier_icdIds)-1):
            for j in range(i+1,i+2):
                print('hier_icdIds[i]:',hier_icdIds[i])
                print('hier_icdIds[j]:',hier_icdIds[j])
                adj[hier_icdIds[i]][hier_icdIds[j]]=1
                parient_child.append([hier_icdIds[i],hier_icdIds[j]])

    print('循环结束！')
    # 统计最大的孩子个数
    children_num = [len(np.argwhere(row)) for row in adj]
    max_children_num = max(len(level0), max(children_num))
    min_children_num = min(len(level0), min(children_num))
    # print('max_childeren_num:', max_children_num)
    # return parient_child,list(level0),list(level1),list(level2),list(level3),adj,node2id,hier_dicts,hier_labels_init_new ,max_children_num
    return parient_child, list(level0), list(level1), list(level2), list(level3), adj, node2id, hier_dicts, hier_labels_init_new, max_children_num

def build_brothers(filepath,node2id,hier_labels,parent_children_adj):
    brother_adj = np.zeros((len(node2id), len(node2id)))
    with open(filepath,'r') as f:
        reader=csv.reader(f)
        next(reader)
        data=[row[-1] for row in reader]
        for row in data:
            icds=row.split(';')
            icds=[node2id.get(icd) for icd in icds if len(icd)>0]
            labels=[hier_labels.get(icd) for icd in icds]
            #为每个样本的每一层建立brother关系
            for level in range(1,5):
                tmp=[row[level] for row in labels]
                for i in range(len(tmp)-1):
                    for j in range(i+1,len(tmp)):
                        # 判断tmp[i]与tmp[j]是否是兄弟关系，即二者是否拥有同一个父亲
                        brotherFlag=isbrother(tmp[i],tmp[j],parent_children_adj)
                        if brotherFlag:
                            brother_adj[tmp[i]][tmp[j]] += 1
                            brother_adj[tmp[j]][tmp[i]] += 1
    return brother_adj

def isbrother(label_a,label_b,parent_children_adj):
    parent_a=np.argwhere(parent_children_adj[:,label_a]>0)
    parent_b=np.argwhere(parent_children_adj[:,label_b]>0)
    if parent_a.any()==parent_b.any():
        brotherFlag=True
    else:
        brotherFlag=False
    return brotherFlag


# 根据值查询键的函数
def get_key_by_value(dictionary, target_value):
    # 遍历字典的键值对
    for key, value in dictionary.items():
        # 如果值匹配目标值，则返回对应的键
        if value == target_value:
            return key
    # 如果未找到匹配的值，则返回 None 或者其他指定的默认值
    return None

def generate_graph(parent_child,node2id):
    # 将parient-child中的每条边转换成id
    # 根据关系创建图
    G = nx.Graph()
    G.add_nodes_from(node2id.keys())
    parent_child_new = []
    for p_c in parent_child:
        parient_id = p_c[0]
        child_id = p_c[1]
        parent_node = get_key_by_value(node2id, parient_id)
        child_node = get_key_by_value(node2id, child_id)
        if (parent_node is not None) and (child_node is not None):
            parent_child_new.append([parent_node, child_node])
    G.add_edges_from(parent_child_new)
    print('number of hierarchical nodes:', G.number_of_nodes())
    print('number of hierarchical edges:', G.number_of_edges())
    return G

# def generate_graph(parient_child, label_node, hier_dicts):
#     # Create an empty graph
#     G = nx.Graph()
#
#     # Add label nodes to the graph
#     for label in label_node:
#         G.add_node(label)
#
#     # Add edges to the graph
#     for parent, child in parient_child:
#         # Only add edges between label nodes
#         if parent in hier_dicts.values() and child in hier_dicts.values():
#             G.add_edge(parent, child)
#     print('number of hierarchical nodes:', G.number_of_nodes())
#     print('number of hierarchical edges:', G.number_of_edges())
#     return G
