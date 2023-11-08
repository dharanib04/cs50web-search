from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Auctionlisting, Bids, Comments, Watchlist
from django.contrib.auth.decorators import login_required
from django.db.models import Max

class NewForm(forms.ModelForm):
    category = forms.CharField(max_length=64, label="Category", required=False)
    image = forms.URLField(label="Image URL", required=False)

    class Meta:
        model = Auctionlisting
        fields = "__all__"
        exclude = ["user_id", "active", "winner"]

class BidsForm(forms.ModelForm):
    class Meta:
        model = Bids
        fields = "__all__"
        exclude = ["list_id"]

def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auctionlisting.objects.filter(active=True),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Auctionlisting.objects.all().values("category").distinct()
    })

def category(request, category):
    return render(request, "auctions/category.html", {
        "category": category,
        "auctions": Auctionlisting.objects.filter(category=category)
    })

@login_required
def create(request):
    if request.method == "POST":
        formdata = Auctionlisting(title=request.POST["title"], price=request.POST["price"], category=request.POST["category"], description=request.POST["description"], image=request.POST["image"], user_id=request.user)
        formdata.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create.html", {
        "form": NewForm()
    })

@login_required
def watchlist(request):
    items = Watchlist.objects.filter(user_id=request.user)
    return render(request, "auctions/watchlist.html", {
        "list_items": Auctionlisting.objects.filter(id__in=[item.list_id.id for item in items]),
    })

def listing(request, id):
    listing = Auctionlisting.objects.get(id=int(id))
    owner = listing.user_id 
    comments = Comments.objects.filter(list_id=listing)
    if not request.user.is_authenticated:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "bids": Bids.objects.all().count(),
            "owner": owner,
            "comments": comments
        })
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": Bids.objects.all().count(),
        "in_watchlist": Watchlist.objects.filter(user_id=request.user, list_id=Auctionlisting.objects.get(id=int(id))).exists(),
        "owner": owner,
        "comments": comments
    })

@login_required
def addwatchlist(request, id):
    if request.method == "POST":
        auction_list = Auctionlisting.objects.get(id=int(id))
        if not Watchlist.objects.filter(user_id=request.user, list_id=auction_list).exists():
            data = Watchlist(user_id = request.user, list_id=auction_list)
            data.save()
    return render(request, "auctions/listing.html", {
        "listing": Auctionlisting.objects.get(id=id),
        "bids": Bids.objects.all().count(),
        "in_watchlist": True,
        "owner": auction_list.user_id,
        "comments": Comments.objects.filter(list_id=auction_list)
    })

@login_required
def removewatchlist(request, id):
    if request.method == "POST":
        list_id = Auctionlisting.objects.get(id=id)
        Watchlist.objects.get(user_id=request.user, list_id=list_id).delete()
    return render(request, "auctions/listing.html", {
        "listing": list_id,
        "bids": Bids.objects.all().count(),
        "in_watchlist": False,
        "owner": Auctionlisting.objects.get(id=int(id)).user_id,
        "comments": Comments.objects.filter(list_id=list_id)
    })

@login_required
def bids(request, id):
    owner = Auctionlisting.objects.get(id=int(id)).user_id
    listing = Auctionlisting.objects.get(id=int(id))
    bids = Bids.objects.all().count()
    in_watchlist = Watchlist.objects.filter(user_id=request.user, list_id=listing).exists()
    comments = Comments.objects.filter(list_id=listing)
    if request.method == "POST":
        amount = request.POST["amount"]
        max_bid = Bids.objects.all().aggregate(Max('amount'))['amount__max']
        if max_bid is None:
            max_bid = 0
        if amount == "":
            return render(request, "auctions/listing.html", {
                "message": "Your bid cannot be empty.",
                "listing": listing,
                "bids": bids,
                "in_watchlist": in_watchlist,
                "owner": owner,
                "comments": comments
            })
        if int(amount) <= max_bid:
            return render(request, "auctions/listing.html", {
                "message": "Your bid must be greater than the highest bid.",
                "listing": listing,
                "bids": bids,
                "in_watchlist": in_watchlist,
                "owner": owner,
                "comments": comments
            })
        if int(amount) < Auctionlisting.objects.get(id=int(request.POST["listing_id"])).price:
            return render(request, "auctions/listing.html", {
                "message": "Your bid must be equal to or greater than the listed price.",
                "listing": listing,
                "bids": bids,
                "in_watchlist": in_watchlist,
                "owner": owner,
                "comments": comments
            })
        new_bid = Bids(list_id=listing, amount=amount, user_id=request.user)
        new_bid.save()
        return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/listing.html", {
         "listing": listing,
         "bids": bids,
         "in_watchlist": in_watchlist,
         "owner": owner,
         "comments": comments
    })

@login_required
def comment(request, id):
    if request.method == "POST":
        comment = request.POST["comment"]
        if comment == "":
            return HttpResponseRedirect(reverse("index"))
        new_comment = Comments(list_id=Auctionlisting.objects.get(id=id), comment=comment)
        new_comment.save()
    return HttpResponseRedirect(reverse("index"))

@login_required
def close(request, id):
    listing = Auctionlisting.objects.get(id=id)
    try: 
        winner = Bids.objects.filter(list_id=id).order_by('-amount').first().user_id
    except:
        AttributeError 
        listing.active = False
        listing.save()
        return HttpResponseRedirect(reverse("index"))
    listing.winner = winner
    listing.active = False
    listing.save()
    return HttpResponseRedirect(reverse("index"))