from django.db import models
from django.contrib.auth.models import User

class Dish(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=200, null= False,blank=False)
    description = models.TextField(blank=False,null=False)
    image = models.ImageField(upload_to='Dishes', null=True)

    def __str__(self) -> str:
        return self.name