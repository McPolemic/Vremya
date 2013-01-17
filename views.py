from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
import json
from vremya.models import Event,Activity
from vremya import utils
import settings

#Redirect to the current day
@login_required
def index(request):
    today = date.today()
    (y,m,d) = [str(i) for i in (today.year, today.month, today.day)]
    return HttpResponseRedirect(reverse('vremya.views.daily', args=(y,m,d)))

@login_required
def daily(request, year, month, day):
    (y, m, d) = (int(year), int(month), int(day))
    date_target = date(y,m,d)
    event_list = Event.objects.filter(date = date_target).filter(user = request.user.username)

    #Temp object to return total time.  Do not save.
    total = Event(total_minutes = sum([e.total_minutes for e in event_list]))
    remaining = 8 - total.frac_hours()
    
    date_url = '/'.join((year, month, day))

    activity_list = Activity.objects.filter(user = request.user.username)

    #Create previous and next day links
    one_day = timedelta(1)

    prev_date = date_target-one_day
    next_date = date_target+one_day

    (py, pm, pd) = (str(prev_date.year), str(prev_date.month), str(prev_date.day))
    day_prev = reverse('vremya.views.daily', args=(py,pm,pd))
    (ny, nm, nd) = (str(next_date.year), str(next_date.month), str(next_date.day))
    day_next = reverse('vremya.views.daily', args=(ny,nm,nd))

    return render_to_response('vremya/daily.html',
                              {'event_list': event_list,
                               'activity_list': activity_list,
			                         'remaining': remaining,
                               'total': total,
                               'user': request.user,
                               'day_prev': day_prev,
                               'day_next': day_next,
                               'day_curr': date_target,
                               'date_url': date_url,
                               'development': settings.DEVELOPMENT},
                              context_instance=RequestContext(request))

"""Create a new event with time associated to a specific activity"""
def add_event(request, year, month, day):
    (y, m, d) = (int(year), int(month), int(day))
    date_target = date(y,m,d)
    act_id = request.POST['activity']
    act = get_object_or_404(Activity, pk=act_id)
    minutes = 0
    hours = 0

    if request.POST['minutes']:
        minutes = int(request.POST['minutes'])
    
    if request.POST['hours']:
        hours = int(request.POST['hours'])

    if 'event_id' in request.POST.keys():
        #We're modifying an existing event
        event_id = int(request.POST['event_id'])
        e = Event.objects.get(id=event_id)
        e.activity = act
        e.total_minutes = minutes + (hours * 60)
        e.save()
    else:
        #We're creating a new event
        e = Event(user = request.user.username,
                  date = date_target, 
                  activity = act, 
                  total_minutes = minutes + (hours * 60))
        e.save()

    return HttpResponseRedirect(reverse('vremya.views.daily', args=(y,m,d)))

"""Delete an event via JSON.
Returns a JSON object {"response": "error"} or {"response": "ok"}"""
def delete_event(request):
    if request.POST['event_id']:
        event_id = int(request.POST['event_id'])

        print 'Deleting event %s' % event_id

        e = Event.objects.get(id=event_id)
        
        #Generate new total time data again
        event_date = e.date
        e.delete()

        event_list = Event.objects.filter(date = event_date).filter(user = request.user.username)

        #Temp object to return total time.  Do not save.
        total = Event(total_minutes = sum([e.total_minutes for e in event_list]))
        remaining = 8 - total.frac_hours()

        response = {'response': 'ok',
                    'total_frac': total.frac_hours(),
                    'total_eng': total.english_time(),
                    'remaining': remaining}

        return HttpResponse(json.dumps(response))
    else:
        return HttpResponse(json.dumps({'response': 'error'}))

"""Try to create a new activity.
Returns a JSON object {"response": "error"} or {"response": (id_of_new_object)}"""
def add_activity(request):
    activity_name = request.POST['name']
    try:
	      act = Activity(name=activity_name, user=request.user.username)
	      act.save()
	      return HttpResponse(json.dumps({'response': act.id}))
    except:
        return HttpResponse(json.dumps({'response': 'error'}))

"""Show weekly status report for this week"""
@login_required
def reports_index(request):
    today = date.today()
    (year, week) = utils.find_week_from_date(today)
    (y,w) = [str(i) for i in (year, week)]
    return HttpResponseRedirect(reverse('vremya.views.reports', args=(y,w)))

"""Show weekly status report"""
@login_required
def reports(request, year, week):
    monday = utils.find_start_date_from_week(year, week)

    day_of_week = [monday,]

    #Fill out the rest of the days of the week
    for i in range(1,7):
        day_offset = timedelta(days=i)
        day_of_week.append(monday + day_offset)

    activity_list = Activity.objects.filter(user = request.user.username)
    event_list = Event.objects.select_related().filter(date__range=(monday, day_of_week[-1])).filter(user = request.user.username)

    report_week = []
    act_name_list = [act.name for act in activity_list]
    act_name_list.sort()

    for act_name in act_name_list:
        #Construct week-long object if activity happened this week
        week_activity = {}
        week_activity['name'] = act_name
        
        #Initialize fractional hour display to all 0s
        week_activity['values'] = [0.0 for i in range(7)]

        events_for_act = [e for e in event_list if e.activity.name == act_name]

        if events_for_act == None:
            continue
        
        for e in events_for_act:
            #the array index is the weekday (0 for Monday, 1 for Tuesday, etc.)
            index = e.date.weekday()
            week_activity['values'][index] += e.frac_hours()
        
        report_week.append(week_activity)
    
    #Fill out the totals for the week
    total = [0.0 for i in range(7)]

    for i in range(7):
        for week_activity in report_week:
            total[i] += week_activity['values'][i]
    
    report_week.append({'name': 'Total',
                        'values': total})
    
    #Create links for next/prev weeks
    week_prev_date = utils.find_week_from_date_with_offset(monday, -7)
    week_next_date = utils.find_week_from_date_with_offset(monday, 7)
    week_next = reverse('vremya.views.reports', args=(str(week_next_date[0]), str(week_next_date[1])))
    week_prev = reverse('vremya.views.reports', args=(str(week_prev_date[0]), str(week_prev_date[1])))

    return render_to_response('vremya/report.html',
                              {'day_of_week': day_of_week,
                               'report_week': report_week,
                               'week_next': week_next,
                               'week_prev': week_prev,
                               'user': request.user,
                               'development': settings.DEVELOPMENT
                               },
                              context_instance=RequestContext(request))
