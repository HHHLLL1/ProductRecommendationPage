import numpy as np
import requests
import re
import pandas as pd
import time
import os
import tqdm
import urllib

from PIL import Image
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RecSysInItem.settings")
django.setup()

from items.models import Item



# file_dict = {'乐器':1, '保健品':2, '办公':3, '化妆品':4, '图书':5, '学习':6,
#              '家具':7, '家电':8, '帽子':9, '手机':10, '杯子':11, '汽车':12,
#              '玩具':13, '珠宝':14, '生鲜':15, '电脑':16, '眼镜':17, '衣服':18, '零食':19}
#
#
# #UA列表
# user_agent_list = [
#             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
#             "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
#             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
#             "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
#             "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
#             "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
#             "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
#             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
#             "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
#             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
#             "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
#             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
#             "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
#             "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
#             "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
#             "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
#             "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
# 			"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
# 			"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
# 			'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
#         ]
# len_userA = len(user_agent_list)
#
# #构建代理IP池
# with open("./verified_proxies.json", "r+") as fb:
# 	proxy_list = fb.read()
# proxy_list = proxy_list.split('\n')
# proxy_list = [eval(i) for i in proxy_list if len(i) != 0]
# proxy_list = [{i['type'] : i['type'] + '://' + i['host'] + ':' + str(i['port'])} for i in proxy_list]
# https_proxy_list = [i for i in proxy_list if 'https' in i.keys()]
# len_https_proxy_list = len(https_proxy_list)
# http_proxy_list = [i for i in proxy_list if 'http' in i.keys()]
# len_http_proxy_list = len(https_proxy_list)
# # print(https_proxy_list[:5])
#
#
# #淘宝
# index_global = 500

def getHTMLText(url):
	a = None
	for i in range(5):
		n= np.random.choice(len_userA, 1)[0]
		headers = {
			"user-agent": user_agent_list[n],
			"cookie": "t=c1e8231792f007e72593175d60586f3a; cna=HthOFWZZfEoCAZkiYyMw5eUw; hng=CN%7Czh-CN%7CCNY%7C156; thw=cn; tracknick=tb313659628; lgc=tb313659628; tg=0; enc=C%2B2%2F0QsEwiUFmf00owySlc7hJiEsY4t4EIGdIzzH6ih9ajzhcMJCs7wzlX4%2B4gJrv2IlLviuxk0B1VAXlVwD8Q%3D%3D; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; miid=1314040285196636905; uc3=vt3=F8dBy3vI3wKCeS4bgiY%3D&id2=VyyWskFTTiu0DA%3D%3D&nk2=F5RGNwsJzCC9CC4%3D&lg2=Vq8l%2BKCLz3%2F65A%3D%3D; _cc_=VFC%2FuZ9ajQ%3D%3D; _m_h5_tk=ec90707af142ccf8ce83ead2feda4969_1560657185501; _m_h5_tk_enc=2bc06ae5460366b0574ed70da887384e; mt=ci=-1_0; cookie2=14c413b3748cc81714471780a70976ec; v=0; _tb_token_=e33ef3765ebe5; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; swfstore=97544; JSESSIONID=80EAAE22FC218875CFF8AC3162273ABF; uc1=cookie14=UoTaGdxLydcugw%3D%3D; l=bBjUTZ8cvDlwwyKtBOCNCuI8Li7OsIRAguPRwC4Xi_5Z86L6Zg7OkX_2fFp6Vj5RsX8B41jxjk99-etki; isg=BP__g37OnjviDJvk_MB_0lRbjtNJTFLqmxNfMJHMlK71oB8imbTI1uey5jD7-Cv-",
			'Connection': 'close'
			}
		# headers = {
		# 	"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
		# 	"cookie": "t=c1e8231792f007e72593175d60586f3a; cna=HthOFWZZfEoCAZkiYyMw5eUw; hng=CN%7Czh-CN%7CCNY%7C156; thw=cn; tracknick=tb313659628; lgc=tb313659628; tg=0; enc=C%2B2%2F0QsEwiUFmf00owySlc7hJiEsY4t4EIGdIzzH6ih9ajzhcMJCs7wzlX4%2B4gJrv2IlLviuxk0B1VAXlVwD8Q%3D%3D; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; miid=1314040285196636905; uc3=vt3=F8dBy3vI3wKCeS4bgiY%3D&id2=VyyWskFTTiu0DA%3D%3D&nk2=F5RGNwsJzCC9CC4%3D&lg2=Vq8l%2BKCLz3%2F65A%3D%3D; _cc_=VFC%2FuZ9ajQ%3D%3D; _m_h5_tk=ec90707af142ccf8ce83ead2feda4969_1560657185501; _m_h5_tk_enc=2bc06ae5460366b0574ed70da887384e; mt=ci=-1_0; cookie2=14c413b3748cc81714471780a70976ec; v=0; _tb_token_=e33ef3765ebe5; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; swfstore=97544; JSESSIONID=80EAAE22FC218875CFF8AC3162273ABF; uc1=cookie14=UoTaGdxLydcugw%3D%3D; l=bBjUTZ8cvDlwwyKtBOCNCuI8Li7OsIRAguPRwC4Xi_5Z86L6Zg7OkX_2fFp6Vj5RsX8B41jxjk99-etki; isg=BP__g37OnjviDJvk_MB_0lRbjtNJTFLqmxNfMJHMlK71oB8imbTI1uey5jD7-Cv-",
		# 	'Connection': 'close'
		# 	}
		m = np.random.choice(len_https_proxy_list, 1)[0]
		r=requests.get(url,timeout=30,headers=headers, proxies=http_proxy_list[m])
		# r = requests.get(url, timeout=30, headers=headers)
		# print(r.raise_for_status())
		time.sleep(np.random.choice(5 , 1))
		r.encoding=r.apparent_encoding
		if r != None:
			a = r.text
			break
		print(f"第{i}次失败")

	if a != None:
		return a
	else:
		return ""

def parsePage(ilt,html, itemtype):
    global index_global
    try:

        plt=re.findall(r'\"view_price\"\:\"[\d\.]*\"', html)
        tlt=re.findall(r'\"raw_title\"\:\".*?\"', html)
        purl=re.findall(r'\"pic_url\"\:\".*?\"', html)
        detail_url = re.findall(r'\"detail_url\"\:\".*?\"', html)
        sales = re.findall(r'\"view_sales\"\:\".*?\"', html)

        # item = Item(item_id=iid,
        #             title=tlt,
        #             price=float(plt),
        #             pic_url=purl,
        #             pic_file=f'data/{itemtype}/{itemtype}_{index_global}.jpg',
        #             sales=sales,
        #             type=itemtype)


        try:
            os.makedirs(f'../data/{itemtype}')
        except:
            pass

        for i in range(len(plt)):
            price=eval(plt[i].split(':')[1])
            title=eval(tlt[i].split(':')[1])
            pic_url = 'http:' + eval(purl[i].split(':')[1])
            sale = eval(sales[i].split(':')[1])
            sale = re.findall(r'\d+', sale)
            sale = int(''.join(sale))
            # ilt.append([price, title, pic_url, itemtype])
            try:
                iid = str(file_dict[itemtype]) + '_' + str(index_global)
                file = f'data/{itemtype}/{itemtype}_{index_global}.jpg'
                # sale = np.random.choice(10000, 1)[0]


                item = Item(item_id=iid,
	                        title=title,
	                        price=float(price),
	                        pic_url=pic_url,
	                        pic_file=file,
	                        sales=sale,
	                        type=itemtype)
                item.save()
                print([iid, price, title, pic_url, itemtype, sale, file])

                urllib.request.urlretrieve(pic_url,f'../data/{itemtype}/{itemtype}_{index_global}.jpg')
                img = Image.open(f'../data/{itemtype}/{itemtype}_{index_global}.jpg')
                out = img.resize((200, 200))
                out.save(f'../static/data/{itemtype}/{itemtype}_{index_global}.jpg', 'jpeg')
                ilt.append([index_global, price, title, pic_url, itemtype, sales])
                # print([index_global, price, title, pic_url, itemtype, sales])
                index_global += 1
                time.sleep(np.random.choice(5, 1))
            except:
                print(f'{title}数据保存失败')
    except:
        return ""

def printGoodsList(ilt):
	tply="{:4}\t{:8}\t{:16}"
	print(tply.format("序号","价格","商品价格", "图片URL"))
	count=0
	for g in ilt:
		count=count+1
		print(tply.format(count,g[0],g[1],g[2]))

def toCsv(ilt, name):
	data = pd.DataFrame(ilt, columns=["序号", "价格", "名称", "图片URL", "类型", "销量"])
	data.to_csv(f'../data/{name}.csv', index=False)
	print(data.head())
	return data

def main():
	global index_global
	# goods=["玩具", "生鲜", "家具", "乐器", "化妆品", "衣服", "帽子", "杯子", "电脑", "手机", "零食", "图书", "帽子"]
	goods = ["学习"]
	# goods = ['家电', "眼镜", "珠宝", "鞋子", "鲜花", "餐厨", "保健品", "办公"]
	depth=5
	for j in range(len(goods)):
		print(goods[j])
		infoList = []
		index_global = 500
		strat_url='https://s.taobao.com/search?q='+goods[j]

		# for i in range(8, depth):
		for i in range(8, 9):
			url=strat_url+"&s="+str(44*i)
			html=getHTMLText(url)
			parsePage(infoList, html, goods[j])
			time.sleep(np.random.choice(5, 1))

		# toCsv(infoList, goods[j])
	# printGoodsList(infoList)


###############################################################################


class CrawlDog:
    def __init__(self, keyword):
        """
        初始化
        :param keyword: 搜索的关键词
        """
        self.keyword = keyword
        self.mongo_client = pymongo.MongoClient(host='localhost')
        self.mongo_collection = self.mongo_client['spiders']['jd']
        self.mongo_collection.create_index([('item_id', pymongo.ASCENDING)])

    def get_index(self, page):
        """
        从搜索页获取相应信息并存入数据库
        :param page: 搜索页的页码
        :return: 商品的id
        """
        url = 'https://search.jd.com/Search?keyword=%s&enc=utf-8&page=%d' % (self.keyword, page)

        n = np.random.choice(len_userA, 1)[0]
        m = np.random.choice(len_https_proxy_list, 1)[0]
        index_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'Accept-Charset': 'utf-8',
            'accept-language': 'zh,en-US;q=0.9,en;q=0.8,zh-TW;q=0.7,zh-CN;q=0.6',
            'user-agent': user_agent_list[n],
        }

        rsp = requests.get(url=url, headers=index_headers, proxies=https_proxy_list[m]).content.decode()
        rsp = etree.HTML(rsp)
        items = rsp.xpath('//li[contains(@class, "gl-item")]')
        for item in items:
            try:
                info = dict()
                info['名称'] = ''.join(item.xpath('.//div[@class="p-name p-name-type-2"]//em//text()'))
                info['url'] = 'https:' + item.xpath('.//div[@class="p-name p-name-type-2"]/a/@href')[0]
                info['store'] = item.xpath('.//div[@class="p-shop"]/span/a/text()')[0]
                info['store_url'] = 'https' + item.xpath('.//div[@class="p-shop"]/span/a/@href')[0]
                info['序号'] = info.get('url').split('/')[-1][:-5]
                info['价格'] = item.xpath('.//div[@class="p-price"]//i/text()')[0]
                info['图片URL'] = item.xpath('.//[@class="p-img"]//i/@source-data-lazy-img')[0]
                info['类型'] = self.keyword
                info['comments'] = []
                # self.mongo_collection.insert_one(info)
                yield info['序号']
            # 实际爬取过程中有一些广告, 其中的一些上述字段为空
            except IndexError:
                print('item信息不全, drop!')
                continue

    def get_comment(self, params):
        """
        获取对应商品id的评论
        :param params: 字典形式, 其中item_id为商品id, page为评论页码
        :return:
        """
        url = 'https://sclub.jd.com/comment/productPageComments.action?productId=%s&score=0&sortType=5&page=%d&' \
              'pageSize=10' % (params['item_id'], params['page'])
        comment_headers = {
            'Referer': 'https://item.jd.com/%s.html' % params['item_id'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/74.0.3729.169 Safari/537.36'
        }
        rsp = requests.get(url=url, headers=comment_headers).json()
        comments_count = rsp.get('productCommentSummary').get('commentCountStr')
        comments = rsp.get('comments')
        comments = [comment.get('content') for comment in comments]
        # self.mongo_collection.update_one(
        #     # 定位至相应数据
        #     {'item_id': params['item_id']},
        #     {
        #         '$set': {'comments_count': comments_count},  # 添加comments_count字段
        #         '$addToSet': {'comments': {'$each': comments}}  # 将comments中的每一项添加至comments字段中
        #     }, True)

    def main(self, index_pn, comment_pn):
        """
        实现爬取的函数
        :param index_pn: 爬取搜索页的页码总数
        :param comment_pn: 爬取评论页的页码总数
        :return:
        """
        # 爬取搜索页函数的参数列表
        il = [i * 2 + 1 for i in range(index_pn)]
        # 创建一定数量的线程执行爬取
        with futures.ThreadPoolExecutor(15) as executor:
            res = executor.map(self.get_index, il)
        for item_ids in res:
            # 爬取评论页函数的参数列表
            cl = [{'item_id': item_id, 'page': page} for item_id in item_ids for page in range(comment_pn)]
            with futures.ThreadPoolExecutor(15) as executor:
                executor.map(self.get_comment, cl)


######################################################################

if __name__ == '__main__':
    # 测试, 只爬取两页搜索页与两页评论
    # test = CrawlDog('耳机')
    # test.main(2, 2)

    file_dict = {'乐器': 1, '保健品': 2, '办公': 3, '化妆品': 4, '图书': 5, '学习': 6,
                 '家具': 7, '家电': 8, '帽子': 9, '手机': 10, '杯子': 11, '汽车': 12,
                 '玩具': 13, '珠宝': 14, '生鲜': 15, '电脑': 16, '眼镜': 17, '衣服': 18, '零食': 19}

    # UA列表
    user_agent_list = [
	    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
	    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
	    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
	    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
	    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
	    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
	    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
	    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
	    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
	    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
	    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
	    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
	    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
	    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
	    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
	    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
	    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    ]
    len_userA = len(user_agent_list)

    # 构建代理IP池
    with open("verified_proxies.json", "r+") as fb:
	    proxy_list = fb.read()
    proxy_list = proxy_list.split('\n')
    proxy_list = [eval(i) for i in proxy_list if len(i) != 0]
    proxy_list = [{i['type']: i['type'] + '://' + i['host'] + ':' + str(i['port'])} for i in proxy_list]
    https_proxy_list = [i for i in proxy_list if 'https' in i.keys()]
    len_https_proxy_list = len(https_proxy_list)
    http_proxy_list = [i for i in proxy_list if 'http' in i.keys()]
    len_http_proxy_list = len(https_proxy_list)
    # print(https_proxy_list[:5])


    # 淘宝
    index_global = 500

    main()

