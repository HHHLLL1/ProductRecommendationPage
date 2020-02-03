from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.views.decorators.csrf import ensure_csrf_cookie
from analytics.models import Rating
from login.models import User
import pandas as pd
# Create your views here.




@ensure_csrf_cookie
def log(request):

    if request.method == 'POST':
        date = request.GET.get('date', datetime.datetime.now())
        date = str(date).split(':')[0]

        user_id = request.POST['user_id']
        user_id = User.objects.filter(name__exact=user_id).values(*['id'])
        user_id = pd.DataFrame.from_records(user_id, columns=['id']).values[0][0]
        item_id = request.POST['item_id']
        rating = request.POST['rating']
        type = request.POST['type']
        type = str(type).split('_')[0]

        print(user_id, item_id, rating, date, type)
        l = Rating(
            user_id=user_id,
	        item_id=str(item_id),
	        rating=rating,
	        rating_timestamp=date,
	        type=type)
        l.save()
    else:
        HttpResponse('log only works with POST')

    return HttpResponse('ok')



