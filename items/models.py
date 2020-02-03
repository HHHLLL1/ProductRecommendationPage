from django.db import models

# Create your models here.

class Item(models.Model):
    item_id = models.CharField(max_length=30, unique=True, primary_key=True)
    title = models.CharField(max_length=300)
    price = models.FloatField(null=True)
    pic_file = models.CharField(max_length=500)
    pic_url = models.URLField(max_length=500)
    type = models.CharField(max_length=30)
    sales = models.IntegerField()

    def __str__(self):
        return self.title
