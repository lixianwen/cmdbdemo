# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Upload(models.Model):
    filename = models.FileField(upload_to='upload')
