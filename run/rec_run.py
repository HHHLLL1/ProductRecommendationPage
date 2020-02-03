import os
import numpy as np
import pymysql

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RecSysInItem.settings")
import django
django.setup()

from collections import defaultdict

from analytics.models import Rating, Rec_Items

from urils import load_all_ratings, dfToDict, get_user_item_matrix
from recommend.bpr import BayesianPersonalizationRanking
from recommend.ItemBasedCF import ItemCF_Norm, ItemCF, ItemIUF
from recommend.UserBasedCF import UserCF, UserIIF, MostPopular, adjustrecommend
from recommend.svdCF import svd_predict, SVD


def resitemToMysql(value):
	db = pymysql.connect(host='localhost',
	                     user='root',
	                     password='root',
	                     port=3306,
	                     db='curdesign',
	                     charset='gbk')
	cursor = db.cursor()
	sql_create = """INSERT INTO analytics_rec_items(user_id, rec_item) VALUES (%s,%s)"""
	sql_update = """UPDATE analytics_rec_items SET rec_item = %s WHERE user_id = %s"""
	# print(sql)
	try:
		cursor.execute(sql_create, (value[0], value[1]))
		db.commit()
	except:
		try:
			cursor.execute(sql_update, (value[1], value[0]))
			db.commit()
		except:
			db.rollback()
			print('保存失败')
	cursor.close()
	db.close()


if __name__ == '__main__':


	data = load_all_ratings()
	user_id = list(data['user_id'].value_counts().index)
	n = 20
	# print(len(user_id))


	#基于SVD的协同过滤算法
	svdcf = SVD(data)
	svdcf.train()


	#基于物品的协同过滤算法测试
	data = dfToDict(data)
	mp = MostPopular(data, 5, n)
	itemcf = ItemCF_Norm(data, 5, n)
	usercf = UserIIF(data, 5, n)

	# item_rank = []
	for i in user_id[:10]:
		svd_pre = svdcf.predict(int(i), n)
		mp_pre = mp(int(i))
		item_pre = itemcf(int(i))
		user_pre = usercf(int(i))
		it = defaultdict(float)
		for uid, scr in mp_pre:
			it[uid] += scr
		for uid, scr in svd_pre:
			it[uid] += scr
		for uid, scr in item_pre:
			it[uid] += scr
		for uid, scr in user_pre:
			it[uid] += scr
		# print(it)

		r = list(sorted(it.items(), key=lambda x:x[1], reverse=True))
		value = (str(i), str(r))
		# print(value)
		resitemToMysql(value)
		# item_rank.append((str(i), str(r)))


# #基于用户的协同过滤算法测试
# data = load_all_ratings()
# data = dfToDict(data)
# print(data)
# r = UserCF(data, 5, 5)
# print(r(1))



#基于SVD的协同过滤算法
# data = load_all_ratings()
# # data = get_user_item_matrix(data)
# # columns = data.columns
# # print(len(columns))
# # data = np.asmatrix(data)
# #
# # N_arr = np.nonzero(data[1, :] == 0)[1]
# # print(len(N_arr))
# # print(columns[N_arr[2]])
#
# # # print(data)
# # # print(data.info())
# # r = svd_predict(data, 1552, 5)
# # print(r)
#
# svddf = SVD(data)
# svddf.train()
# r = svddf.predict(1, 5)
# print(r)


