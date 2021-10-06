from django.db import models
from django.utils.translation import ugettext_lazy as _


class Term(models.Model):
    class Meta:
        verbose_name = _('term')
        verbose_name_plural = _('terms')

    name = models.CharField(
        max_length=63,
        null=False,
        editable=True,
        verbose_name=_('name'),
        unique=True
    )

    objects = models.Manager()

    def __str__(self):
        return f'{self.name}'
