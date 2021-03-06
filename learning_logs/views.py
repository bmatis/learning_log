from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

def check_topic_owner(request, topic):
    """
    Check if the current user is the owner of the topic and raise 404
    error if not.
    """
    if topic.owner != request.user:
        raise Http404

def index(request):
    """The home page for Learning Log."""

    context = {}

    try:
        # Get all topics for displaying in main nav
        topics = Topic.objects.filter(owner=request.user).order_by('text')
        topic_count = len(topics)

        entries = Entry.objects.filter(topic__owner=request.user).order_by('-date_added')
        entry_count = len(entries)

        context = {'topics': topics,
                   'entries': entries,
                   'topic_count': topic_count,
                   'entry_count': entry_count,
                   }
    except TypeError:
        print("TypeError occured when rendering index.")

    return render(request, 'learning_logs/index.html', context)

@login_required
def topics(request):
    """Show all topics."""
    topics = Topic.objects.filter(owner=request.user).order_by('text')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Show a single topic and all its entries."""
    topic = get_object_or_404(Topic, id=topic_id)

    # Make sure the topic belongs to the current user.
    check_topic_owner(request, topic)

    entries = topic.entry_set.order_by('-date_added')

    # Get all topics for displaying in main nav
    topics = Topic.objects.filter(owner=request.user).order_by('text')

    context = {'topic': topic, 'entries': entries, 'topics': topics}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """Add a new topic."""
    # Get all topics for displaying in main nav
    topics = Topic.objects.filter(owner=request.user).order_by('text')

    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TopicForm()
    else:
        # POST data submitted; process data.
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            # return HttpResponseRedirect(reverse('learning_logs:topics'))
            return HttpResponseRedirect(reverse('learning_logs:topic', kwargs={'topic_id':new_topic.id}))

    context = {'form': form, 'topics': topics}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    # Get all topics for displaying in main nav
    topics = Topic.objects.filter(owner=request.user).order_by('text')

    topic = Topic.objects.get(id=topic_id)
    check_topic_owner(request, topic)

    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = EntryForm()
    else:
        # POST data submitted; process data.
        form = EntryForm(request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return HttpResponseRedirect(reverse('learning_logs:topic',
                args=[topic_id]))

    context = {'topic': topic, 'form': form, 'topics': topics}
    return render(request, 'learning_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    # Get all topics for displaying in main nav
    topics = Topic.objects.filter(owner=request.user).order_by('text')

    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic)

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = EntryForm(instance=entry)
    else:
        # POST data submitted; process data.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learning_logs:topic',
                args=[topic.id]))

    context = {'entry': entry, 'topic': topic, 'form': form, 'topics': topics}
    return render(request, 'learning_logs/edit_entry.html', context)
