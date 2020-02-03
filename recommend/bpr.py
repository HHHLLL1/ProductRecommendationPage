import os
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RecSysInItem.settings")
import django
django.setup()

import pickle
from tqdm import tqdm
from datetime import datetime
from math import exp

import random
import pandas as pd
import numpy as np

from decimal import Decimal
from collections import defaultdict

from analytics.models import Rating

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
logger = logging.getLogger('BPR calculator')

class BayesianPersonalizationRanking(object):

    def __init__(self, save_path):

        self.save_path = save_path
        self.user_factors = None
        self.item_factors = None
        self.user_ids = None
        self.item_ids = None
        self.ratings = None
        self.user_item = None
        self.error = 0

        self.learning_rate = 0.05
        self.bias_regularization = 0.002
        self.user_regularization = 0.005
        self.positive_item_regularization = 0.003
        self.negative_item_regularization = 0.0003


    def initialize_factors(self, train_data, k=25):
        self.ratings = train_data[['user_id', 'item_id', 'rating']].as_matrix()
        self.k = k
        self.user_ids = pd.unique(train_data['user_id'])
        self.item_ids = pd.unique(train_data['item_id'])

        self.u_inx = {r: i for i, r in enumerate(self.user_ids)}
        self.i_inx = {r: i for i, r in enumerate(self.item_ids)}

        self.user_factors = np.random.random_sample((len(self.user_ids), k))
        self.item_factors = np.random.random_sample((len(self.item_ids), k))
        self.user_item = train_data.groupby('user_id')['item_id'].apply(lambda x: x.tolist()).to_dict()
        self.item_bias = defaultdict(lambda: 0)
        self.create_loss_samples()

    def build(self, ratings, params):

        if params:
            k = params['k']
            num_iterations = params['num_iterations']

        self.train(ratings, k, num_iterations)

    def train(self, train_data, k=25, num_iterations=4):

        self.initialize_factors(train_data, k)
        for iteration in tqdm(range(num_iterations)):
            self.error = self.loss()

            logger.debug('iteration {} loss {}'.format(iteration, self.error))

            for usr, pos, neg in self.draw(self.ratings.shape[0]):
                self.step(usr, pos, neg)

            self.save(iteration, iteration == num_iterations - 1)

    def step(self, u, i, j):

        lr = self.learning_rate
        ur = self.user_regularization
        br = self.bias_regularization
        pir = self.positive_item_regularization
        nir = self.negative_item_regularization

        ib = self.item_bias[i]
        jb = self.item_bias[j]

        u_dot_i = np.dot(self.user_factors[u, :],
                         self.item_factors[i, :] - self.item_factors[j, :])
        x = ib - jb + u_dot_i

        z = 1.0/(1.0 + exp(x))

        ib_update = z - br * ib
        self.item_bias[i] += lr * ib_update

        jb_update = - z - br * jb
        self.item_bias[j] += lr * jb_update

        update_u = ((self.item_factors[i,:] - self.item_factors[j,:]) * z
                    - ur * self.user_factors[u,:])
        self.user_factors[u,:] += lr * update_u

        update_i = self.user_factors[u,:] * z - pir * self.item_factors[i,:]
        self.item_factors[i,:] += lr * update_i

        update_j = -self.user_factors[u,:] * z - nir * self.item_factors[j,:]
        self.item_factors[j,:] += lr * update_j

    def loss(self):
        br = self.bias_regularization
        ur = self.user_regularization
        pir = self.positive_item_regularization
        nir = self.negative_item_regularization

        ranking_loss = 0
        for u, i, j in self.loss_samples:
            x = self.predict(u, i) - self.predict(u, j)
            ranking_loss += 1.0 / (1.0 + exp(x))

        c = 0
        for u, i, j in self.loss_samples:

            c += ur * np.dot(self.user_factors[u], self.user_factors[u])
            c += pir * np.dot(self.item_factors[i], self.item_factors[i])
            c += nir * np.dot(self.item_factors[j], self.item_factors[j])
            c += br * self.item_bias[i] ** 2
            c += br * self.item_bias[j] ** 2

        return ranking_loss + 0.5 * c

    def predict(self, user, item):
        i_fac = self.item_factors[item]
        u_fac = self.user_factors[user]
        pq = i_fac.dot(u_fac)

        return pq + self.item_bias[item]

    def create_loss_samples(self):

        num_loss_samples = int(100 * len(self.user_ids) ** 0.5)
        logger.debug("[BEGIN]building {} loss samples".format(num_loss_samples))

        self.loss_samples = [t for t in self.draw(num_loss_samples)]
        logger.debug("[END]building {} loss samples".format(num_loss_samples))

    def draw(self, no):

        for _ in range(no):
            u = random.choice(self.user_ids)
            user_items = self.user_item[u]

            pos = random.choice(user_items)

            neg = pos
            while neg in user_items:
                neg = random.choice(self.item_ids)

            yield self.u_inx[u], self.i_inx[pos], self.i_inx[neg]

    def save(self, factor, finished):

        save_path = self.save_path + '/model/'
        if not finished:
            save_path += str(factor) + '/'

        ensure_dir(save_path)

        logger.info("saving factors in {}".format(save_path))
        item_bias = {iid: self.item_bias[self.i_inx[iid]] for iid in self.i_inx.keys()}

        uf = pd.DataFrame(self.user_factors,
                          index=self.user_ids)
        it_f = pd.DataFrame(self.item_factors,
                            index=self.item_ids)

        with open(save_path + 'user_factors.json', 'w') as outfile:
            outfile.write(uf.to_json())
        with open(save_path + 'item_factors.json', 'w') as outfile:
            outfile.write(it_f.to_json())
        with open(save_path + 'item_bias.data', 'wb') as ub_file:
            pickle.dump(item_bias, ub_file)

def load_all_ratings(min_ratings=1):
    columns = ['user_id', 'item_id', 'rating', 'rating_timestamp', 'type']

    ratings_data = Rating.objects.all().values(*columns)

    ratings = pd.DataFrame.from_records(ratings_data, columns=columns)

    item_count = ratings[['item_id', 'rating']].groupby('item_id').count()

    item_count = item_count.reset_index()
    item_count['rating'] = item_count['rating'].astype(np.dtype(Decimal))
    item_ids = item_count.loc[item_count['rating'] > min_ratings]['item_id']
    ratings = ratings[ratings['item_id'].isin(item_ids)]

    ratings['rating'] = ratings['rating'].astype(np.dtype(Decimal))
    return ratings


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

# if __name__ == '__main__':
#
#     number_of_factors = 10
#     logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
#     logger = logging.getLogger('BPR calculator')
#
#     train_data = load_all_ratings(min_ratings=60)
#     bpr = BayesianPersonalizationRanking(save_path='./models/bpr/{}/'.format(datetime.now()))
#     bpr.train(train_data, 10, 20)






#############################################################################################################################


# import numpy as np
# import tensorflow as tf
# import os
# import random
# from collections import defaultdict
#
#
#         # def load_data():
#     user_ratings = defaultdict(set)
#     max_u_id = -1
#     max_i_id = -1
#     with open('../test/ml-100k/u.data','r') as f:
#         for line in f.readlines():
#             u,i,_,_ = line.split("\t")
#             u = int(u)
#             i = int(i)
#             user_ratings[u].add(i)
#             max_u_id = max(u,max_u_id)
#             max_i_id = max(i,max_i_id)
#
#
#     print("max_u_id:",max_u_id)
#     print("max_i_idL",max_i_id)
#
#     return max_u_id,max_i_id,user_ratings
#
# def generate_test(user_ratings):
#     """
#     对每一个用户u，在user_ratings中随机找到他评分过的一部电影i,保存在user_ratings_test，
#     后面构造训练集和测试集需要用到。
#     """
#     user_test = dict()
#     for u,i_list in user_ratings.items():
#         user_test[u] = random.sample(user_ratings[u],1)[0]
#     return user_test
#
#
# def generate_train_batch(user_ratings,user_ratings_test,item_count,batch_size=512):
#     """
#     构造训练用的三元组
#     对于随机抽出的用户u，i可以从user_ratings随机抽出，而j也是从总的电影集中随机抽出，当然j必须保证(u,j)不在user_ratings中
#     """
#     t = []
#     for b in range(batch_size):
#         u = random.sample(user_ratings.keys(),1)[0]
#         i = random.sample(user_ratings[u],1)[0]
#         while i==user_ratings_test[u]:
#             i = random.sample(user_ratings[u],1)[0]
#
#         j = random.randint(1,item_count)
#         while j in user_ratings[u]:
#             j = random.randint(1,item_count)
#
#         t.append([u,i,j])
#
#     return np.asarray(t)
#
#
# def generate_test_batch(user_ratings,user_ratings_test,item_count):
#     """
#     对于每个用户u，它的评分电影i是我们在user_ratings_test中随机抽取的，它的j是用户u所有没有评分过的电影集合，
#     比如用户u有1000部电影没有评分，那么这里该用户的测试集样本就有1000个
#     """
#     for u in user_ratings.keys():
#         t = []
#         i = user_ratings_test[u]
#         for j in range(1,item_count + 1):
#             if not(j in user_ratings[u]):
#                 t.append([u,i,j])
#         yield np.asarray(t)
#
#
# def bpr_mf(user_count,item_count,hidden_dim):
#     u = tf.placeholder(tf.int32,[None])
#     i = tf.placeholder(tf.int32,[None])
#     j = tf.placeholder(tf.int32,[None])
#
#     user_emb_w = tf.get_variable("user_emb_w", [user_count + 1, hidden_dim],
#                                  initializer=tf.random_normal_initializer(0, 0.1))
#     item_emb_w = tf.get_variable("item_emb_w", [item_count + 1, hidden_dim],
#                                  initializer=tf.random_normal_initializer(0, 0.1))
#
#     u_emb = tf.nn.embedding_lookup(user_emb_w, u)
#     i_emb = tf.nn.embedding_lookup(item_emb_w, i)
#     j_emb = tf.nn.embedding_lookup(item_emb_w, j)
#
#
#     x = tf.reduce_sum(tf.multiply(u_emb,(i_emb-j_emb)),1,keep_dims=True)
#
#     mf_auc = tf.reduce_mean(tf.to_float(x>0))
#
#     l2_norm = tf.add_n([
#         tf.reduce_sum(tf.multiply(u_emb, u_emb)),
#         tf.reduce_sum(tf.multiply(i_emb, i_emb)),
#         tf.reduce_sum(tf.multiply(j_emb, j_emb))
#     ])
#
#     regulation_rate = 0.0001
#     bprloss = regulation_rate * l2_norm - tf.reduce_mean(tf.log(tf.sigmoid(x)))
#
#     train_op = tf.train.GradientDescentOptimizer(0.01).minimize(bprloss)
#     return u, i, j, mf_auc, bprloss, train_op
#
#
# user_count,item_count,user_ratings = load_data()
# user_ratings_test = generate_test(user_ratings)
#
# # with tf.Session() as sess:
# #     u,i,j,mf_auc,bprloss,train_op = bpr_mf(user_count,item_count,20)
# #     sess.run(tf.global_variables_initializer())
# #
# #     for epoch in range(1,4):
# #         _batch_bprloss = 0
# #         for k in range(1,5000):
# #             uij = generate_train_batch(user_ratings,user_ratings_test,item_count)
# #             _bprloss,_train_op = sess.run([bprloss,train_op],
# #                                           feed_dict={u:uij[:,0],i:uij[:,1],j:uij[:,2]})
# #
# #             _batch_bprloss += _bprloss
# #
# #         print("epoch:",epoch)
# #         print("bpr_loss:",_batch_bprloss / k)
# #         print("_train_op")
# #
# #         user_count = 0
# #         _auc_sum = 0.0
# #
# #         for t_uij in generate_test_batch(user_ratings, user_ratings_test, item_count):
# #             _auc, _test_bprloss = sess.run([mf_auc, bprloss],
# #                                               feed_dict={u: t_uij[:, 0], i: t_uij[:, 1], j: t_uij[:, 2]}
# #                                               )
# #             user_count += 1
# #             _auc_sum += _auc
# #         print("test_loss: ", _test_bprloss, "test_auc: ", _auc_sum / user_count)
# #         print("")
# #     variable_names = [v.name for v in tf.trainable_variables()]
# #     values = sess.run(variable_names)
# #     for k, v in zip(variable_names, values):
# #         print("Variable: ", k)
# #         print("Shape: ", v.shape)
# #         print(v)
# #
# # #  0号用户对这个用户对所有电影的预测评分
# # session1 = tf.Session()
# # u1_dim = tf.expand_dims(values[0][0], 0)
# # u1_all = tf.matmul(u1_dim, values[1],transpose_b=True)
# # result_1 = session1.run(u1_all)
# # print (result_1)
# #
# # print("以下是给用户0的推荐：")
# # p = np.squeeze(result_1)
# # p[np.argsort(p)[:-5]] = 0
# # for index in range(len(p)):
# #     if p[index] != 0:
# #         print (index, p[index])