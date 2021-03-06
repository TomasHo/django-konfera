from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext_lazy as _

from konfera.models import Event
from konfera.models.talk import CFP
from konfera.forms import SpeakerForm, TalkForm


def event_sponsors_list_view(request, event_slug):
    event = get_object_or_404(Event.objects.published(), slug=event_slug)
    sponsors = event.sponsors.all().order_by('type', 'title')

    context = {'event': event,
               'sponsors': sponsors,
               }

    return render(request=request,
                  template_name='konfera/event_sponsors.html',
                  context=context, )


def event_speakers_list_view(request, event_slug):
    event = get_object_or_404(Event.objects.published(), slug=event_slug)
    talks = event.talk_set.all().order_by('primary_speaker__last_name')

    context = {'event': event,
               'talks': talks,
               }

    return render(request=request,
                  template_name='konfera/event_speakers.html',
                  context=context, )


def event_list(request):
    events = Event.objects.published().order_by('date_from')

    if events.count() == 1:
        return redirect('event_details', event_slug=events[0].slug)

    paginator = Paginator(events, 10)
    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)
    context = {'events': events}
    return render(request=request,
                  template_name='konfera/events.html',
                  context=context)


def event_details_view(request, event_slug):
    event = get_object_or_404(Event.objects.published(), slug=event_slug)
    sponsors = event.sponsors.all()
    context = {'event': event,
               'sponsors': sponsors,
               }

    return render(request=request,
                  template_name='konfera/event_details.html',
                  context=context, )


def cfp_form_view(request, event_slug):
    speaker_form = SpeakerForm(request.POST or None, prefix='speaker')
    talk_form = TalkForm(request.POST or None, prefix='talk')
    if speaker_form.is_valid() and talk_form.is_valid():
        speaker_instance = speaker_form.save()
        talk_instance = talk_form.save(commit=False)
        talk_instance.primary_speaker = speaker_instance
        talk_instance.status = CFP
        talk_instance.event = Event.objects.get(slug=event_slug)
        talk_instance.save()
        message_text = _("Your talk proposal successfully created")
        messages.success(request, message_text)
        return HttpResponseRedirect(redirect_to='/event/')
    context = {'speaker_form': speaker_form,
               'talk_form': talk_form,
               }

    return render(request=request,
                  template_name='konfera/cfp_form.html',
                  context=context, )
