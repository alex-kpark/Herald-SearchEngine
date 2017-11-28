# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from .engine import engine_doc2vec

# Create your models here.

class User(AbstractUser):

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('not-specified', 'Not specified')
    )

    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, default='male')

class Query(models.Model):
    
    words = models.CharField(max_length=100)
    author = models.ForeignKey('User', related_name="log")