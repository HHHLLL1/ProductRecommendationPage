# -*-coding:utf-8-*-


import MySQLdb
from numpy import *  # 导入numpy的库函数
import numpy as np
from urils import load_all_ratings, dfToDict
import math


#基于商品的协同过滤算法

def cos_distance( v1, v2):
    # 计算余弦距离
    a1 = np.array(v1, dtype=int)
    a2 = np.array(v2, dtype=int)
    a3 = multiply(a1, a2)
    return sum(a3) * 1.0 / (sqrt(sum(a1)) + sqrt(sum(a2)))


class ItemBasedCF:
    book_id = ''
    def __init__(self, bi):
        self.book_id = bi
        # self.book_tags = self.get_tag_vec(bi)
        # self.rec_books = self.get_k_neighbor(5,self.book_tags)

    def get_k_neighbor(self,k, vector1):
        nearest_books = dict()
        # 计算得到物品id,距离
        # get data from mysql
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='blog', port=3306)
            cur = conn.cursor()
            cur.execute('select * from book_tag')
            results = cur.fetchall()
            all_booktag = dict()
            for row in results:
                book_id = row[1]
                book_tag = row[2:7]
                # changge book_tag to 01 array
                bt = [0 for i in range(0, 15)]
                for i in range(0, 5):
                    bt[book_tag[i] - 1] = 1
                cur_dis = cos_distance(vector1, bt)

                # print cur_dis
                nearest_books[book_id] = cur_dis

            cur.close()
            conn.close()
        except (MySQLdb.Error, e):
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        # sorted(d.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        return sorted(nearest_books.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)[1:k+1]

    def get_tag_vec(self,book_id):
        try:
            conn = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='blog', port=3306)
            cur = conn.cursor()

            sql = 'select * from book_tag where book_id='+str(book_id)
            # print sql
            cur.execute(sql)
            cur_book_tag = cur.fetchone()[2:7]
            # print data
            cur.close()
            conn.close()
            bt = [0 for i in range(0, 15)]
            for i in range(0, 5):
                bt[cur_book_tag[i] - 1] = 1
            return bt
        except (MySQLdb.Error, e):
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))




# 1. 基于物品余弦相似度的推荐
def ItemCF(train, K, N):
    '''
    :params: train, 训练数据集
    :params: K, 超参数，设置取TopK相似物品数目
    :params: N, 超参数，设置取TopN推荐物品数目
    :return: GetRecommendation, 推荐接口函数
    '''
    # 计算物品相似度矩阵
    sim = {}
    num = {}
    for user in train:
        items = train[user]
        for i in range(len(items)):
            u = items[i]
            if u not in num:
                num[u] = 0
            num[u] += 1
            if u not in sim:
                sim[u] = {}
            for j in range(len(items)):
                if j == i: continue
                v = items[j]
                if v not in sim[u]:
                    sim[u][v] = 0
                sim[u][v] += 1
    for u in sim:
        for v in sim[u]:
            sim[u][v] /= math.sqrt(num[u] * num[v])

    # 按照相似度排序
    sorted_item_sim = {k: list(sorted(v.items(), \
                                      key=lambda x: x[1], reverse=True)) \
                       for k, v in sim.items()}

    # 获取接口函数
    def GetRecommendation(user):
        items = {}
        seen_items = set(train[user])
        for item in train[user]:
            for u, _ in sorted_item_sim[item][:K]:
                if u not in seen_items:
                    if u not in items:
                        items[u] = 0
                    items[u] += sim[item][u]
        recs = list(sorted(items.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs

    return GetRecommendation


# 2. 基于改进的物品余弦相似度的推荐
def ItemIUF(train, K, N):
    '''
    :params: train, 训练数据集
    :params: K, 超参数，设置取TopK相似物品数目
    :params: N, 超参数，设置取TopN推荐物品数目
    :return: GetRecommendation, 推荐接口函数
    '''
    # 计算物品相似度矩阵
    sim = {}
    num = {}
    for user in train:
        items = train[user]
        for i in range(len(items)):
            u = items[i]
            if u not in num:
                num[u] = 0
            num[u] += 1
            if u not in sim:
                sim[u] = {}
            for j in range(len(items)):
                if j == i: continue
                v = items[j]
                if v not in sim[u]:
                    sim[u][v] = 0
                # 相比ItemCF，主要是改进了这里
                sim[u][v] += 1 / math.log(1 + len(items))
    for u in sim:
        for v in sim[u]:
            sim[u][v] /= math.sqrt(num[u] * num[v])

    # 按照相似度排序
    sorted_item_sim = {k: list(sorted(v.items(), \
                                      key=lambda x: x[1], reverse=True)) \
                       for k, v in sim.items()}

    # 获取接口函数
    def GetRecommendation(user):
        items = {}
        seen_items = set(train[user])
        for item in train[user]:
            for u, _ in sorted_item_sim[item][:K]:
                # 要去掉用户见过的
                if u not in seen_items:
                    if u not in items:
                        items[u] = 0
                    items[u] += sim[item][u]
        recs = list(sorted(items.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs

    return GetRecommendation


# 3. 基于归一化的物品余弦相似度的推荐
def ItemCF_Norm(train, K, N):
    '''
    :params: train, 训练数据集
    :params: K, 超参数，设置取TopK相似物品数目
    :params: N, 超参数，设置取TopN推荐物品数目
    :return: GetRecommendation, 推荐接口函数
    '''
    # 计算物品相似度矩阵
    sim = {}
    num = {}
    for user in train:
        items = train[user]
        for i in range(len(items)):
            u = items[i]
            if u not in num:
                num[u] = 0
            num[u] += 1
            if u not in sim:
                sim[u] = {}
            for j in range(len(items)):
                if j == i: continue
                v = items[j]
                if v not in sim[u]:
                    sim[u][v] = 0
                sim[u][v] += 1
    for u in sim:
        for v in sim[u]:
            sim[u][v] /= math.sqrt(num[u] * num[v])

    # 对相似度矩阵进行按行归一化
    for u in sim:
        s = 0
        for v in sim[u]:
            s += sim[u][v]
        if s > 0:
            for v in sim[u]:
                sim[u][v] /= s

    # 按照相似度排序
    sorted_item_sim = {k: list(sorted(v.items(), \
                                      key=lambda x: x[1], reverse=True)) \
                       for k, v in sim.items()}

    # 获取接口函数
    def GetRecommendation(user):
        items = {}
        seen_items = set(train[user])
        for item in train[user]:
            for u, _ in sorted_item_sim[item][:K]:
                if u not in seen_items:
                    if u not in items:
                        items[u] = 0
                    items[u] += sim[item][u]
        recs = list(sorted(items.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs

    return GetRecommendation


# data = load_all_ratings()
# data = dfToDict(data)
# r = ItemCF_Norm(data, 5, 5)
# print(r(1))

