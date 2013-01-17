from django.db import models

"""Activity one takes part in (i.e. "Clean room", "Hamster room")"""
class Activity(models.Model):
    user = models.CharField(max_length=30)
    name = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
    	return self.name
 
    class Meta:
        ordering = ["name"]
        verbose_name_plural = 'Activities'

"""Event that happened in a workday"""
class Event(models.Model):
    user = models.CharField(max_length=30)
    date = models.DateField('date of activity')
    activity = models.ForeignKey(Activity)
    total_minutes = models.IntegerField()

    def _get_hours(self):
        return self.total_minutes/60

    hours = property(_get_hours)
	
    def _get_minutes(self):
        return self.total_minutes - (self.hours*60)

    minutes = property(_get_minutes)

    def frac_hours(self):
        return round((float(self.total_minutes)/60), 1)
    
    def english_time(self):
        return '%d:%02d' % (self.hours, self.minutes)

    english_time.short_description = "Time"
    frac_hours.short_description = "Hours (Fraction)"

    @models.permalink
    def get_absolute_url(self):
        return ('vremya.views.daily', (), {
            'year':  self.date.year,
            'month': self.date.month,
            'day':   self.date.day
        })

    def __unicode__(self):
    	return '%s - %s' % (self.date, self.activity)
