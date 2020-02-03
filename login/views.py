from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.shortcuts import render,redirect
from login.models import User
from items.models import Item
from analytics.models import Rec_Items
from login.forms import UserForm, RegisterForm
import pandas as pd
# Create your views here.


def index(request):
    item_column = ['item_id', 'title', 'price', 'pic_file', 'sales']
    # uid = request.session['user_name']
    try:
        uid = request.session['user_name']
        a = User.objects.filter(name__exact=uid).values(*['id'])
        a = pd.DataFrame.from_records(a, columns=['id']).values[0][0]
        res = Rec_Items.objects.filter(user_id__exact=str(a)).values(*['rec_item'])
        res = pd.DataFrame.from_records(res, columns=['rec_item']).values[0][0]
        res = eval(res)
        res_list = [i for i, j in res]
        res_df = Item.objects.filter(item_id__in=res_list).values(*item_column)
        res_df = pd.DataFrame.from_records(res_df, columns=item_column)
        res_df = res_df.to_json(orient='records')
        res_df = eval(res_df)
        for j in res_df:
            j['pic_file'] = str(j['pic_file']).replace('\\', '')
            # print(res_df)
    except:
        # uid = None
        res_df = Item.objects.all().values(*item_column)
        res_df = pd.DataFrame.from_records(res_df, columns=item_column)
        res_df = res_df.sort_values(by='sales')[-40:]
        res_df = res_df.to_json(orient='records')
        res_df = eval(res_df)
        for j in res_df:
            j['pic_file'] = str(j['pic_file']).replace('\\', '')

    # print(uid)
    # if uid != None:
    #     a = User.objects.filter(name__exact=uid).values(*['id'])
    #     a = pd.DataFrame.from_records(a, columns=['id']).values[0][0]
    #     res = Rec_Items.objects.filter(user_id__exact=str(a)).values(*['rec_item'])
    #     res = pd.DataFrame.from_records(res, columns=['rec_item']).values[0][0]
    #     res = eval(res)
    #     res_list = [i for i, j in res]
    #     res_df = Item.objects.filter(item_id__in=res_list).values(*item_column)
    #     res_df = pd.DataFrame.from_records(res_df, columns=item_column)
    #     res_df = res_df.to_json(orient='records')
    #     res_df = eval(res_df)
    #     for j in res_df:
    #         j['pic_file'] = str(j['pic_file']).replace('\\', '')
    #     # print(res_df)
    # else:
    #     # res_df = Item.objects.all().values(*item_column)
    #     # res_df = pd.DataFrame.from_records(res_df, columns=item_column)
    #     # res_df = res_df.sort_values(by='sales')[-40:]
    #     # res_df = res_df.to_json(orient='records')
    #     # res_df = eval(res_df)
    #     # for j in res_df:
    #     #     j['pic_file'] = str(j['pic_file']).replace('\\', '')
    #     res_df = [{'item_id': '1_158', 'title': '悦雅古筝初学者入门演奏职业考级筝成人儿童自学乐器教学初级古筝', 'price': 898.0, 'pic_file': 'data/乐器/乐器_158.jpg', 'sales': 900},
    #               {'item_id': '1_166', 'title': '【润扬民乐】 新楠木九龙实木演奏古筝 专业10级 扬州乐器', 'price': 1748.0, 'pic_file': 'data/乐器/乐器_166.jpg', 'sales': 4882},
    #               {'item_id': '1_28', 'title': '星海 杨靖监制款琵琶乐器奥氏黄檀材质酸枝红木演奏琵琶琴8974JZ', 'price': 6825.0, 'pic_file': 'data/乐器/乐器_28.jpg', 'sales': 3934},
    #               {'item_id': '1_43', 'title': 'Stentor全欧料高档演奏级小提琴手工小提琴 专业级成人儿童乐器', 'price': 3280.0, 'pic_file': 'data/乐器/乐器_43.jpg', 'sales': 4541},
    #               {'item_id': '1_5', 'title': '宝声手工实木小提琴初学者入门考级乐器专业级儿童练习弹奏小提琴', 'price': 580.0, 'pic_file': 'data/乐器/乐器_5.jpg', 'sales': 4932},
    #               {'item_id': '10_141', 'title': '12期免息 顺丰速发Huawei\\/华为nova 5 Pro全网通手机官方旗舰店官网正品 直降', 'price': 2499.0, 'pic_file': 'data/手机/手机_141.jpg', 'sales': 7213},
    #               {'item_id': '10_63', 'title': '【8+256G赠耳机】红米k30 索尼6400万大电量120Hz智能游戏学生手机K20升级redmi小米官方旗舰店网正品xiaomi', 'price': 1699.0, 'pic_file': 'data/手机/手机_63.jpg', 'sales': 1139}]
    print(res_df)


    item_type = Item.objects.values_list('type')
    item_type = list(set(item_type))
    item_type_dict = {}
    for i in range(1, len(item_type)+1):
        item_type_dict['#tab'+str(i)] = item_type[i-1][0]


    it_dict = {}
    for i in range(1, len(item_type)+1):
        a = Item.objects.filter(type__contains=item_type[i-1][0]).values(*item_column)
        a = pd.DataFrame.from_records(a, columns=item_column)
        a = a.iloc[:10, :]
        a = a.to_json(orient='records')
        a = eval(a)
        for j in a:
            j['pic_file'] = str(j['pic_file']).replace('\\', '')
        it_dict['tab'+str(i)] = a
        # context[i] = a
        # print(it_dict['tab'+str(i)])

    # r = request.POST.get('submit1')
    # print(r)

    return render(request,'login/index.html', {'item_type_dict':item_type_dict, 'it_dict':it_dict, 'res_df':res_df})
    # return render(request, 'login/index.html', context)


def login(request):
    if request.session.get('is_login',None):
        return redirect('/index')
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(name=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())



def register(request):
    if request.session.get('is_login', None): # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"

        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            age = register_form.cleaned_data['age']

            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals()) # 当一切都OK的情况下，创建新用户
                new_user = User.objects.create(name=username,
                                               password=password1,
                                               email=email,
                                               sex = sex,
                                               age = age)
                # new_user.name = username
                # new_user.password = password1
                # new_user.email = email
                # new_user.sex = sex
                # new_user.age = int(age)
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())




def logout(request):
    if not request.session.get('is_login', None): # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index/")


def detail(request, item_id):
    item_column = ['item_id', 'title', 'price', 'pic_file', 'sales']
    print(item_id)
    item_detail = Item.objects.filter(item_id__exact=item_id).values(*item_column)
    item_detail = pd.DataFrame.from_records(item_detail, columns=item_column)
    item_detail = item_detail.to_json(orient='records')
    item_detail = eval(item_detail)[0]
    item_detail['pic_file'] = str(item_detail['pic_file']).replace('\\', '')
    print(item_detail)
    return render(request, 'login/detail.html', {'item_detail':item_detail})


###########################################################################################################################


# def hash_code(s, salt='mysite'):
#     h = hashlib.sha256()
#     s += salt
#     h.update(s.encode())
#     return h.hexdigest()

# def pay(request):
#     return render(request, 'pay.html')
#
# def item_detail(request):
#     return render(request, 'item_detail.html')
#
# def success(request):
#     return render(request, 'success.html')
#
# def car(request):
#     return render(request, 'car.html')
#
# def index(request):
#     if request.method == 'POST':
#         keyStr = request.POST.get('mykey')
#         limit = 16 # 每页显示的记录数
#         datas = Item.objects.filter(title__contains=keyStr)
#         tuijian=Item.objects.filter(title__contains=keyStr)[:6]
#         paginator = Paginator(datas, limit)  # 实例化一个分页对象
#         page = request.GET.get('page')  # 获取页码
#         try:
#             datas = paginator.page(page)  # 获取某页对应的记录
#         except PageNotAnInteger:  # 如果页码不是个整数
#             datas = paginator.page(1)  # 取第一页的记录
#         except EmptyPage:  # 如果页码太大，没有相应的记录
#             datas = paginator.page(paginator.num_pages)  # 取最后一页的记录
#
#         return render(request, 'search.html',{'datas':datas,'keyStr':keyStr,'tuijian':tuijian})
#     else:
#         return render(request, 'index.html')
#
# def search(request):
#     if request.method == 'POST':
#         keyStr = request.POST.get('mykey')
#         limit = 16 # 每页显示的记录数
#         datas = Item.objects.filter(title__contains=keyStr)
#         tuijian=Item.objects.filter(title__contains=keyStr)[:6]
#         paginator = Paginator(datas, limit)  # 实例化一个分页对象
#         page = request.GET.get('page')  # 获取页码
#         try:
#             datas = paginator.page(page)  # 获取某页对应的记录
#         except PageNotAnInteger:  # 如果页码不是个整数
#             datas = paginator.page(1)  # 取第一页的记录
#         except EmptyPage:  # 如果页码太大，没有相应的记录
#             datas = paginator.page(paginator.num_pages)  # 取最后一页的记录
#
#         return render(request, 'search.html',{'datas':datas,'keyStr':keyStr,'tuijian':tuijian})
#     else:
#         return render(request, 'search.html')
#
# def login(request):
#     if request.session.get('is_login', None):  # 不允许重复登录
#         return redirect('/index/')
#     if request.method == 'POST':
#         login_form = UserForm(request.POST)
#         message = '请检查填写的内容！'
#         if login_form.is_valid():
#             username = login_form.cleaned_data.get('username')
#             password = login_form.cleaned_data.get('password')
#
#             try:
#                 user = User.objects.get(name=username)
#             except :
#                 message = '用户不存在！'
#                 return render(request, 'login.html', locals())
#
#             if user.password == hash_code(password):
#                 request.session['is_login'] = True
#                 request.session['user_id'] = user.id
#                 request.session['user_name'] = user.name
#                 return redirect('/index/')
#             else:
#                 message = '密码不正确！'
#                 return render(request, 'login.html', locals())
#         else:
#             return render(request, 'login.html', locals())
#
#     login_form = UserForm()
#     return render(request, 'login.html', locals())
#
#
# def register(request):
#     if request.session.get('is_login', None):
#         return redirect('/index/')
#
#     if request.method == 'POST':
#         register_form = RegisterForm(request.POST)
#         message = "请检查填写的内容！"
#         if register_form.is_valid():
#             username = register_form.cleaned_data.get('username')
#             password1 = register_form.cleaned_data.get('password1')
#             password2 = register_form.cleaned_data.get('password2')
#             email = register_form.cleaned_data.get('email')
#             sex = register_form.cleaned_data.get('sex')
#             age = register_form.cleaned_data.get('age')
#
#             if password1 != password2:
#                 message = '两次输入的密码不同！'
#                 return render(request, 'register.html', locals())
#             else:
#                 same_name_user = User.objects.filter(name=username)
#                 if same_name_user:
#                     message = '用户名已经存在'
#                     return render(request, 'register.html', locals())
#                 same_email_user = User.objects.filter(email=email)
#                 if same_email_user:
#                     message = '该邮箱已经被注册了！'
#                     return render(request, 'register.html', locals())
#
#                 # new_user = User()
#                 new_user = User.objects.create(name=username,
#                                                password=password1,
#                                                email=email,
#                                                sex = sex,
#                                                age = age)
#                 # new_user.name = username
#                 # new_user.password = hash_code(password1)
#                 # new_user.email = emai
#                 # new_user.sex = sex
#                 new_user.save()
#
#                 return redirect('/login/')
#         else:
#             return render(request, 'register.html', locals())
#     register_form = RegisterForm()
#     return render(request, 'register.html', locals())
#
#
# def logout(request):
#     if not request.session.get('is_login', None):
#         return redirect('/login/')
#
#     request.session.flush()
#     # del request.session['is_login']
#     return redirect("/login/")


