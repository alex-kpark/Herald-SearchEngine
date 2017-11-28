# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('not-specified', 'Not specified')
    )

    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, default='male')

    def __unicode__(self):
        return self.gender


class Query(models.Model):
    
    log = models.ForeignKey(User, on_delete=models.CASCADE)