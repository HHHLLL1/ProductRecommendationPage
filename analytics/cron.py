import os

def reptile_go():
	os.system('python ../reptile/getItemInfo.py')


def rec_run_go():
	os.system('python ../run/rec_run.py')

def auto_go():
	reptile_go()
	rec_run_go()




import time
while True:
    time_now = time.strftime("%H", time.localtime())  # 刷新
    if time_now == "12": #此处设置每天定时的时间
        auto_go()
        time.sleep(2) # 因为以秒定时，所以暂停2秒，使之不会在1秒内执行多次

