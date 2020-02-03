import pymysql
import os
import numpy as np
import pandas as pd


path = '../data/'
file_list = os.listdir(path)
file_list = [i for i in file_list if i[-4:] != '.csv']
print(file_list)

# #调整手机序号
# a = pd.read_csv('../data/手机.csv')
# a['序号'] -= 1
# a.to_csv('../data/手机.csv', index=False)

#处理部分数据序列问题
# l = ['图书', '电脑']
# for file_name in l:
# 	df = pd.read_csv(f'../data/{file_name}.csv')
# 	df['序号'] = range(len(df))
# 	df.rename(columns={'商品价格':'名称'}, inplace=True)
# 	df.to_csv(f'../data/{file_name}.csv', index=False)
# 	pic_file = os.listdir(f'../data/{file_name}')
# 	for i in pic_file:
# 		a = df['序号'].loc[df['名称'] == i[:-4]]
# 		if len(a) !=0:
# 			b = a.values[0]
# 			os.rename(f'../data/{file_name}/'+i, f'../data/{file_name}/{file_name}_{b}.jpg')
# 			print(b)






# #更改列名，更改商品id
# file_dict = {}
# x = 1
# for i in file_list:
# 	file_dict[i] = x
# 	x += 1
# for file_name in file_list[4:]:
# 	df = pd.read_csv(f'../data/{file_name}.csv')
# 	df.rename(columns={'序号':'item_id','价格':'price','名称':'title','图片URL':'pic_url','类型':'type','销量':'sales'}, inplace=True)
# 	df['item_id'] = df['item_id'].apply(lambda x: str(file_dict[file_name])+'_'+str(x))
# 	df.to_csv(f'../data/{file_name}.csv', index=False)



#合并数据集
# x = 0
# for file_name in file_list:
# 	if x == 0:
# 		df = pd.read_csv(f'../data/{file_name}.csv')
# 		x = 1
# 	else:
# 		a = pd.read_csv(f'../data/{file_name}.csv')
# 		df = pd.concat((df, a))
# df.to_csv('../data/item_data.csv', index=False)



#存储图片的本地路径
# data = pd.read_csv('../data/item_data.csv')
# print(data.info())
# data['pic_file'] = data.apply(lambda x: f'data/'+str(x['type'])+ '/' + str(x['type']) + '_' + x['item_id'].split('_')[1] + '.jpg', axis=1)
# data.to_csv('../data/item_data.csv', index=False)
# print(data.head())