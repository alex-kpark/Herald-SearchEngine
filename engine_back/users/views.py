# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Importing Libraries to make a Http response-request with Client-side through View
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from . import models
from images import models as image_models



# Create your views here.
