from django.contrib import admin

from .models import Auctionlisting, Bids, Comments, User, Watchlist
# Register your models here.

admin.site.register(Auctionlisting)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Watchlist)
admin.site.register(User)
