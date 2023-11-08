from django.shortcuts import render, redirect
from django import forms
from . import util
from random import choice
from markdown2 import Markdown

markdowner = Markdown()


class NewTaskForm(forms.Form):
    title = forms.CharField(label="Title")
    entry = forms.CharField(widget=forms.Textarea(
        attrs={"rows": "4", 'cols': 15}), label="Entry")


def index(request):
    if request.method == "POST":
        q = request.POST.get('title')
        entries = util.list_entries()
        lower = [entry.lower() for entry in entries]
        if q.lower() in lower:
            return render(request, "encyclopedia/entry.html", {
                "title": q,
                "entry": markdowner.convert(util.get_entry(q))
            })
        else:
            search_entries = []
            for entry in lower:
                if q.lower() in entry:
                    search_entries.append(entries[lower.index(entry)])
            return render(request, "encyclopedia/index.html", {
                "entries": search_entries,
                "search": True
            })
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    entry = util.get_entry(title)
    if request.method == "POST":
        return redirect('editpage', title=title)
    if entry == None:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "newpage": False
        })
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": markdowner.convert(entry)
    })


def addpage(request):
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry = form.cleaned_data["entry"]
            if title in util.list_entries():
                return render(request, "encyclopedia/error.html", {
                    "title": title,
                    "newpage": True
                })
            util.save_entry(title, entry)
            return index(request)
    return render(request, "encyclopedia/addpage.html", {
        "form": NewTaskForm()
    })


def editpage(request, title):
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry = form.cleaned_data["entry"]
            util.save_entry(title, entry)
            return index(request)
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "wrongform": True
        })
    entry = util.get_entry(title)
    form = NewTaskForm(
        initial={'title': title, 'entry': util.get_entry(title)})
    return render(request, "encyclopedia/editpage.html", {
        "form": form,
        "title": title
    })


def random(request):
    title = choice(util.list_entries())
    return entry(request, title)
