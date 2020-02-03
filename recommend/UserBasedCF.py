# -*-coding:utf-8-*-
import math
from urils import load_all_ratings, dfToDict


#基于用户的协同过滤算法

class recommender:
    # 推荐 n 本书
    def __init__(self, data, k=5, n=5):
        self.k = k
        self.n = n
        self.fn = self.pearson
        self.data = data

    # 皮尔逊相关系数，计算相关性
    def pearson(self, rating1, rating2):
        sum_xy = 0
        sum_x = 0  # 相同书评论分数之和
        sum_y = 0
        sum_x2 = 0  # 平方和
        sum_y2 = 0
        n = 0
        for key in rating1:
            if key in rating2:
                n += 1  # 统计相同的选择个数
                x = rating1[key]  # 物品得分
                y = rating2[key]
                sum_xy += x * y  # 对于相同的选择计算得分乘积的和
                sum_x += x
                sum_y += y
                sum_x2 += pow(x, 2)
                sum_y2 += pow(y, 2)
        if n == 0:
            # 此时分母为0（即两个用户没有一本书相同，相关度为0）
            return 0
        den = math.sqrt(sum_x2 - pow(sum_x, 2) / n) * math.sqrt(sum_y2 - pow(sum_y, 2) / n)
        if den == 0:
            return 0
        else:
            return (sum_xy - (sum_x * sum_y) / n) / den

    def get_k_neighbor(self, username):
        # 计算获得相似的用户
        distances = []
        for instance in self.data:  # 对于每个用户
            if instance != username:  # 遍历用户还未结束的时候
                distance = self.fn(self.data[username], self.data[instance])  # 计算用户间的相关系数
                distances.append((instance, distance))
        # distance 中保存所有用户之间的相关程度  （用户名，相关得分）
        distances.sort(key=lambda cur_bookTuple: cur_bookTuple[1], reverse=True)
        return distances

    def recommend(self, users_score_item):
        recommendations = {}  # book:score
        # 计算出user与所有其他用户的相似度，返回一个list
        nearest = self.get_k_neighbor(users_score_item)
        userRatings = self.data[users_score_item]  # 获得该用户的所有投票
        totalDistance = 0.0
        # 最近的k个用户的距离之和
        for i in range(self.k):
            totalDistance += nearest[i][1]
        if totalDistance == 0.0:  # 避免分母为0（为了将权值映射到0-1之间）
            totalDistance = 1.0

        # 将与user最相近的k个人中user没有看过的书推荐给user，按照用户间的相似度进行加权
        for i in range(self.k):
            # 第i个人的与user的相似度，转换到[0,1]之间
            weight = nearest[i][1] / totalDistance
            name = nearest[i][0]
            neighborRatings = self.data[name]
            for cur_book in neighborRatings:
                if cur_book not in userRatings:  # 如果用户没有评价过
                    if cur_book not in recommendations:
                        recommendations[cur_book] = (neighborRatings[cur_book] * weight)
                    else:
                        # 按照相似度的权值加权
                        recommendations[cur_book] = (recommendations[cur_book] + neighborRatings[cur_book] * weight)

        recommendations = list(recommendations.items())
        recommendations.sort(key=lambda cur_bookTuple: cur_bookTuple[1], reverse=True)  # 按照得分排序
        return recommendations[:self.n], nearest


def adjustrecommend(users_score_item, user_name):
    bookid_list = []
    rec = recommender(users_score_item)
    k, nearuser = rec.recommend(bytes(user_name))
    for i in range(len(k)):
        bookid_list.append(k[i][0])
    return bookid_list, nearuser[:7]










# bookid_list, near_list = adjustrecommend("1Ws3SmK")
# print ("bookid_list:", bookid_list)
# print ("near_list:", near_list)





# 2. 热门推荐
def MostPopular(train, K, N):
    '''
    :params: train, 训练数据集
    :params: K, 可忽略
    :params: N, 超参数，设置取TopN推荐物品数目
    :return: GetRecommendation, 推荐接口函数
    '''
    items = {}
    for user in train:
        for item in train[user]:
            if item not in items:
                items[item] = 0
            items[item] += 1

    def GetRecommendation(user):
        # 随机推荐N个没见过的最热门的
        user_items = set(train[user])
        rec_items = {k: items[k] for k in items if k not in user_items}
        rec_items = list(sorted(rec_items.items(), key=lambda x: x[1], reverse=True))
        return rec_items[:N]

    return GetRecommendation




# 3. 基于用户余弦相似度的推荐
def UserCF(train, K, N):
    '''
    :params: train, 训练数据集
    :params: K, 超参数，设置取TopK相似用户数目
    :params: N, 超参数，设置取TopN推荐物品数目
    :return: GetRecommendation, 推荐接口函数
    '''
    # 计算item->user的倒排索引
    item_users = {}
    for user in train:
        for item in train[user]:
            if item not in item_users:
                item_users[item] = []
            item_users[item].append(user)

    # 计算用户相似度矩阵
    sim = {}
    num = {}
    for item in item_users:
        users = item_users[item]
        for i in range(len(users)):
            u = users[i]
            if u not in num:
                num[u] = 0
            num[u] += 1
            if u not in sim:
                sim[u] = {}
            for j in range(len(users)):
                if j == i: continue
                v = users[j]
                if v not in sim[u]:
                    sim[u][v] = 0
                sim[u][v] += 1
    for u in sim:
        for v in sim[u]:
            sim[u][v] /= math.sqrt(num[u] * num[v])

    # 按照相似度排序
    sorted_user_sim = {k: list(sorted(v.items(), \
                                      key=lambda x: x[1], reverse=True)) \
                       for k, v in sim.items()}

    # 获取接口函数
    def GetRecommendation(user):
        items = {}
        seen_items = set(train[user])
        for u, _ in sorted_user_sim[user][:K]:
            for item in train[u]:
                # 要去掉用户见过的
                if item not in seen_items:
                    if item not in items:
                        items[item] = 0
                    items[item] += sim[user][u]
        recs = list(sorted(items.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs

    return GetRecommendation


# 4. 基于改进的用户余弦相似度的推荐
def UserIIF(train, K, N):
    '''
    :params: train, 训练数据集
    :params: K, 超参数，设置取TopK相似用户数目
    :params: N, 超参数，设置取TopN推荐物品数目
    :return: GetRecommendation, 推荐接口函数
    '''
    # 计算item->user的倒排索引
    item_users = {}
    for user in train:
        for item in train[user]:
            if item not in item_users:
                item_users[item] = []
            item_users[item].append(user)

    # 计算用户相似度矩阵
    sim = {}
    num = {}
    for item in item_users:
        users = item_users[item]
        for i in range(len(users)):
            u = users[i]
            if u not in num:
                num[u] = 0
            num[u] += 1
            if u not in sim:
                sim[u] = {}
            for j in range(len(users)):
                if j == i: continue
                v = users[j]
                if v not in sim[u]:
                    sim[u][v] = 0
                # 相比UserCF，主要是改进了这里
                sim[u][v] += 1 / math.log(1 + len(users))
    for u in sim:
        for v in sim[u]:
            sim[u][v] /= math.sqrt(num[u] * num[v])

    # 按照相似度排序
    sorted_user_sim = {k: list(sorted(v.items(), \
                                      key=lambda x: x[1], reverse=True)) \
                       for k, v in sim.items()}

    # 获取接口函数
    def GetRecommendation(user):
        items = {}
        seen_items = set(train[user])
        for u, _ in sorted_user_sim[user][:K]:
            for item in train[u]:
                # 要去掉用户见过的
                if item not in seen_items:
                    if item not in items:
                        items[item] = 0
                    items[item] += sim[user][u]
        recs = list(sorted(items.items(), key=lambda x: x[1], reverse=True))[:N]
        return recs

    return GetRecommendation


# data = load_all_ratings()
# data = dfToDict(data)
# r = UserCF(data, 5, 5)
# print(r(1))

