from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    pass

class Auctionlisting(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    title = models.CharField(max_length=64)
    price = models.IntegerField()
    category = models.CharField(max_length=64)
    description = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now=True, editable=False, blank=True)
    image = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner", null=True, blank=True)

    def __str__(self):
        return f"{self.title} {self.price} {self.category} {self.description} {self.date} {self.image}"

class Bids(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    list_id = models.ForeignKey(Auctionlisting, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return str(self.amount)

class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    list_id = models.ForeignKey(Auctionlisting, on_delete=models.CASCADE)
    comment = models.CharField(max_length=64)

    def __str__(self):
        return self.comment
    
class Watchlist(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    list_id = models.ForeignKey(Auctionlisting, on_delete=models.CASCADE)

    def __str__(self):
        return f"list_id: {self.list_id}  user_id: {self.user_id}"