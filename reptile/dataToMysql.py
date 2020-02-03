import pymysql
import os
import pandas as pd
import tqdm

######################################################################################

#导入item_data数据到数据库

data = pd.read_csv('../data/item_data.csv')
data = data[['item_id', 'title', 'price', 'pic_file', 'pic_url', 'type', 'sales']]
rows = len(data)
print(data.head())
# data.to_csv('../data/item_data.csv', index=False)

db = pymysql.connect(host='localhost',
	                 user='root',
	                 password='root',
	                 port=3306,
	                 db='curdesign',
	                 charset='gbk')
cursor = db.cursor()

# sql = """INSERT INTO items_item(item_id, title, price, pic_file, pic_url, type, sales) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

error_list = []


def itemToMysql(value):
	db = pymysql.connect(host='localhost',
	                     user='root',
	                     password='root',
	                     port=3306,
	                     db='curdesign',
	                     charset='gbk')
	cursor = db.cursor()
	sql = """INSERT INTO items_item(item_id, title, price, pic_file, pic_url, type, sales) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
	# print(sql)
	try:
		cursor.execute(sql, (value[0], value[1], value[2], value[3], value[4], value[5], value[6]))
		db.commit()
	except:
		try:
			cursor.execute(sql, (value[0], value[1], value[2], value[3], value[4], value[5], value[6]))
			db.commit()
		except:
			db.rollback()
			print('保存失败')
	cursor.close()
	db.close()


# s = """DETELE FROM items_item WHERE id={}""".format(1)
# print(s)
# try:
# 	cursor.execute(s)
# 	db.commit()
# except:
# 	db.rollback()
# 	print('保存失败')
# insert(('dsf', 'erigj', 21.0, 'uihuih', 'http://g-search1.alicdn.c', 'ejdfn', 1254))
# q = ('19_170', '味滋源 零食坚果大礼包一整箱休闲小吃散装三只年货礼盒送礼松鼠', 54.9, 'data/零食/零食_170.jpg', 'http://g-search3.alicdn.com/img/bao/uploaded/i4/i1/3171123884/O1CN01wMgSnl1eYutEtslMe_!!0-item_pic.jpg', '零食', 3086)
# insert(q, 1)


for i in range(rows):
# for i in range(1):
	q = data.iloc[i, :].values
	q = tuple(q)
	itemToMysql(q)
	# print(value)
	# try:
	# 	print(q)
	# 	cursor.execute(sql, q)
	# 	db.commit()
	# except:
	# 	db.rollback()
	# 	print('保存失败')
	# 	error_list.append(i)


print(len(error_list))




'''
#sql命令
load data infile 'C:/ProgramData/MySQL/MySQL Server 5.7/Uploads/data.csv'
into table items_item
character set gbk
Fields Terminated By ',' Enclosed By '"' Escaped By '"' Lines Terminated By '\r\n'
ignore 1 lines;
'''


###########################################################################################

#导入user_item_data数据到数据库

# data = pd.read_csv('../data/user_item_data.csv')
# rows = len(data)
# print(data.head())
# print(data.info())
#
# db = pymysql.connect(host='localhost',
# 	                 user='root',
# 	                 password='root',
# 	                 port=3306,
# 	                 db='curdesign',
# 	                 charset='gbk')
# cursor = db.cursor()
#
# sql = "INSERT INTO analytics_rating(id, user_id,item_id, rating, rating_timestamp, type) VALUES (%d, %s, %s, %s, %s, %s)"
#
# error_list = []
#
# def insert(value, i):
# 	try:
# 		cursor.execute(sql, tuple(value))
# 		db.commit()
# 	except:
# 		db.rollback()
# 		print('保存失败')
# 		error_list.append(i)
#
#
# # q = (3999, '19_67', 1, '2014-11-29 09', '零食')
# # insert(q, 1)
#
#
# for i in range(rows):
# # for i in range(1):
# 	q = list(data.iloc[i, :].values)
# 	qq = [i+1]
# 	q = tuple(qq+q)
# 	# print(value)
# 	try:
# 		print(q)
# 		cursor.execute(sql, q)
# 		print(i)
# 		db.commit()
# 	except:
# 		db.rollback()
# 		print('保存失败')
# 		error_list.append(i)
# 	# insert(q, i)
#
# print(len(error_list))
#
# cursor.close()
# db.close()

# data = pd.read_csv('C:/ProgramData/MySQL/MySQL Server 5.7/Uploads/user_item_data.csv')
# data['id'] = range(1, len(data)+1)
# data = data[['id', 'user_id', 'item_id', 'rating', 'rating_timestamp' ,'type']]
# data.to_csv('C:/ProgramData/MySQL/MySQL Server 5.7/Uploads/user_item_data.csv', index=False)

'''
load data infile 'C:/ProgramData/MySQL/MySQL Server 5.7/Uploads/user_item_data.csv'
into table analytics_rating
character set utf8
Fields Terminated By ',' Enclosed By '"' Escaped By '"' Lines Terminated By '\r\n'
ignore 1 lines;
'''
