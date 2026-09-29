from django.db import models

class Conference(models.Model):
    title       = models.CharField(max_length=200)
    topics      = models.TextField(help_text='Chủ đề, cách nhau bởi dấu phẩy')
    venue       = models.CharField(max_length=200)
    start_date  = models.DateField()
    end_date    = models.DateField()
    description = models.TextField()
    venue_desc  = models.TextField()
    conditions  = models.TextField()

    def __str__(self):
        return self.title


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Venue(models.Model):
    name    = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    desc    = models.TextField(blank=True)

    def __str__(self):
        return self.name