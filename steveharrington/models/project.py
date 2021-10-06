from django.db import models
from django.utils.translation import ugettext_lazy as _

from .user import HarringtonUser


class Project(models.Model):
    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    name = models.CharField(
        max_length=63,
        null=False,
        editable=True,
        verbose_name=_('name'),
        unique=True
    )
    owners = models.ManyToManyField(
        HarringtonUser,
        related_name='projects',
        verbose_name=_('owners'),
    )

    objects = models.Manager()

    def __str__(self):
        return f'{self.name}'
