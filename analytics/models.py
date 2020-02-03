from django.db import models

# Create your models here.

class Rating(models.Model):
    user_id = models.CharField(max_length=20)
    item_id = models.CharField(max_length=20)
    rating = models.DecimalField(decimal_places=2, max_digits=4)
    rating_timestamp = models.CharField(max_length=100)
    type = models.CharField(max_length=50, default='explicit')

    def __str__(self):
        return "user_id: {}, item_id: {}, rating: {}, type: {}"\
            .format(self.user_id, self.item_id, self.rating, self.type)



class Rec_Items(models.Model):
    user_id = models.CharField(max_length=20, primary_key=True)
    rec_item = models.CharField(max_length=2000)

    def __str__(self):
        return "user_id: {}, rec_item: {}"\
            .format(self.user_id, self.rec_item)


