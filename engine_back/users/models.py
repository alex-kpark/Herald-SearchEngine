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

    author = models.CharField(max_length=100)
    profile_photo = models.ImageField(null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, default='male')
