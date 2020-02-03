import numpy as np
import pandas as pd
from tqdm import tqdm
import os


###############################################################################

#抽取出一部分用户-商品数据

#user_item_data = pd.read_csv('../fresh_comp_offline/tianchi_fresh_comp_train_user.csv')
#print(user_item_data.head())
#
#
##user_item_data['item_count'] = user_item_data.groupby('item_id')['item_id'].transform('count')
#user_item_data.index = user_item_data['item_id']
#item_id  = user_item_data.item_id.value_counts()[:4334].index
#user_item_data = user_item_data.loc[item_id, :]
#
#user_item_data.index = user_item_data.user_id
#user_id = user_item_data.user_id.value_counts()[:4000].index
#user_item_data = user_item_data.loc[user_id, :]
#
#user_item_data = user_item_data[['user_id', 'item_id', 'behavior_type', 'time']]
#user_item_data.to_csv('../data/user_item_data.csv', index=False)


#################################################################################

#替换用户-商品数据集中的用户id和商品id，加入商品类型，和爬取的数据保持一致

# item_data = pd.read_csv('../data/item_data.csv')
# user_item_data = pd.read_csv('../data/user_item_data.csv')
#
#
# user_item_data['behavior_type'].loc[user_item_data['behavior_type']==3] = 2
# user_item_data['behavior_type'].loc[user_item_data['behavior_type']==4] = 3

              
# item_id = user_item_data.item_id.value_counts().index
# item_dict = {}
# for i in tqdm(range(len(item_id))):
#     item_dict[item_id[i]] = item_data.item_id[i]
# user_item_data.item_id = user_item_data.item_id.replace(item_dict)
#
#
# user_id = user_item_data.user_id.value_counts().index
# user_dict = {}
# for i in tqdm(range(len(user_id))):
#     user_dict[user_id[i]] = i
# user_item_data.user_id = user_item_data.user_id.replace(user_dict)
                                            

path = '../data/'
file_list = os.listdir(path)
file_list = [i for i in file_list if i[-4:] != '.csv']                                          
file_dict = {}
x = 1
for i in file_list:
    file_dict[x] = i
    x += 1
print(file_dict)
# user_item_data['type'] = user_item_data.apply(lambda x: file_dict[int(x['item_id'].split('_')[0])], axis=1)
# user_item_data = user_item_data.drop_duplicates()
# user_item_data['id'] = range(1, len(user_item_data)+1)
# user_item_data = user_item_data[['id', 'user_id', 'item_id','rating', 'rating_timestamp', 'type']]
# user_item_data.to_csv('../data/user_item_data.csv', index=False)




