from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:title>", views.entry, name="entry"),
    path("newpage/", views.addpage, name="addpage"),
    path("editpage/<str:title>/", views.editpage, name="editpage"),
    path("random/", views.random, name="random"),
]
