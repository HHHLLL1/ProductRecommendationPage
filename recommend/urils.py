import os
import numpy as np
import pandas as pd
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RecSysInItem.settings")
django.setup()

from analytics.models import Rating
from items.models import Item


def load_all_ratings(min_ratings=1, columns=[]):
	if len(columns) == 0:
		columns = ['user_id', 'item_id', 'rating', 'rating_timestamp', 'type']

	ratings_data = Rating.objects.all().values(*columns)

	ratings = pd.DataFrame.from_records(ratings_data, columns=columns)

	item_count = ratings[['item_id', 'rating']].groupby('item_id').count()

	item_count = item_count.reset_index()
	# item_count['rating'] = item_count['rating'].astype(np.dtype(Decimal))
	item_count['rating'] = item_count['rating'].astype(np.float32)
	item_ids = item_count.loc[item_count['rating'] > min_ratings]['item_id']
	ratings = ratings[ratings['item_id'].isin(item_ids)]

	# ratings['rating'] = ratings['rating'].astype(np.dtype(Decimal))
	ratings['rating'] = ratings['rating'].astype(np.float32)
	return ratings




def load_all_items(columns=[]):
	if len(columns) == 0:
		columns = ['item_id', 'title', 'price', 'pic_file', 'pic_url', 'type', 'sales']
	item_data = Item.objects.all().values(*columns)
	items = pd.DataFrame.from_records(item_data, columns=columns)
	return items



def get_user_item_matrix(df):
	df = df[['user_id', 'item_id', 'rating']]
	df_rating = df.groupby(['user_id', 'item_id'])['rating'].mean()
	df_rating = df_rating.unstack()
	df_rating = df_rating.fillna(0)
	return df_rating


def matrixToDF(df_matrix):
	df = df_matrix.stack().reset_index()
	df = df.rename(columns={0:'rating'})
	return df


def dfToDict(df):
	df_ = df.groupby(['user_id'])['item_id'].unique()
	df_ = df_.reset_index()
	dic = df_.to_dict()
	return dic['item_id']




def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

#
# a = load_all_ratings()
# # print(a)
# a = dfToDict(a)
# print(a)
# # print(a.info())
