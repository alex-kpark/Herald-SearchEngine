# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Query)
class UserAdmin(admin.ModelAdmin):
    pass