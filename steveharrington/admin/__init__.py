from django.contrib import admin
from django.apps import apps

from ..apps import SteveharringtonConfig


for model in apps.get_app_config(SteveharringtonConfig.label).models.values():
    admin.site.register(model)
