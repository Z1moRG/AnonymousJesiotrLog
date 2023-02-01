from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404

from django.db.models import Count, Q, OuterRef, Subquery

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

def check_topic_owner(tpo, usr):
    if tpo != usr:
        raise Http404

def check_entry_owner(ent, usr):
    if ent != usr:
        raise Http404
# ---------------------------------------------

def index(request):
    """Strona główna aplikacji Learning Log."""
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    """Wyświetlanie wszystkich tematów."""

    # TODO: dodać ilość wpisów dla każdego z tematów
    #topics = Topic.objects.filter(owner=request.user).order_by('date_added') 
    topics = Topic.objects\
        .values('id', 'text', 'owner__username')\
        .annotate(
           cnt=Subquery(
               Entry.objects.filter(topic=OuterRef('pk'))
                   .values('topic_id')
                   .annotate(cnt=Count('topic_id'))
                   .values('cnt')
#.filter(owner=request.user)\
            )
    ) 
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Wyświetla pojedyńczy temat i wszystkie powiązane z nim wpisy"""
    topic = Topic.objects.get(id=topic_id)
    # Upewniamy się, że temat należy do bieżącego użytkownika.
    # check_topic_owner(topic.owner, request.user)
    
    entries = topic.entry_set.order_by('-date_added')           
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """dodaj nowy temat"""
    if request.method != 'POST':
        # Nie przekazano żadnych danych, należy utworzyć pusty formularz
        form = TopicForm()
    else:
        # Przekazano dane za pomocą żądania POST, należy je przetworzyć
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    # Wyświetlenie pustego formularza
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Dodanie nowego wpisu dla określonego tematu"""
    topic = Topic.objects.get(id=topic_id)
    # check_topic_owner(topic.owner, request.user)

    if request.method != 'POST':
        # Nie przekazano żadnych danych, należy utworzyć pusty formularz
        form = EntryForm()
    else:
        # Przekazano dane za pomocą żądania POST, należy je przetworzyć
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.owner = request.user
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    
    # Wyświetlenie pustego formularza
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edycja istniejącego wpisu"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_entry_owner(entry.owner, request.user)

    if request.method != 'POST':
        # Żądanie początkowe, wypełnienie formularza aktualną treścią wpisu
        form = EntryForm(instance=entry)
    else:
        # Przekazano dane za pomocą żądania POST, należy je przetworzyć
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
    
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)

@login_required
def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, id = topic_id)
    check_topic_owner(topic.owner, request.user)

    if request.method == 'POST':
        # delete the band from the database
        topic.delete()
        # redirect to the bands list
        return redirect('learning_logs:topics')
       
    context = {'obj': topic, 'topicname': topic.text}
    return render(request, 'learning_logs/delete_topic.html', context)

@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(Entry, id = entry_id)
    topic = entry.topic
    check_entry_owner(entry.owner, request.user)

    if request.method == 'POST':
        # delete the band from the database
        entry.delete()
        # redirect to the bands list
        return redirect('learning_logs:topic', topic_id=topic.id)
       
    context = {'obj': topic, 'entry': entry, 'entrydate': entry.date_added}
    return render(request, 'learning_logs/delete_entry.html', context)