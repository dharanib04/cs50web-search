from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("addwatchlist/<int:id>", views.addwatchlist, name="addwatchlist"),
    path("removewatchlist/<int:id>", views.removewatchlist, name="removewatchlist"),
    path("category/<str:category>", views.category, name="category"),
    path("bids/<int:id>", views.bids, name="bids"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("close/<int:id>", views.close, name="close"),
]
