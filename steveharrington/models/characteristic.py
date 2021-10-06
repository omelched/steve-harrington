from django.db import models
from django.utils.translation import ugettext_lazy as _


class Characteristic(models.Model):
    class Meta:
        verbose_name = _('characteristic')
        verbose_name_plural = _('characteristics')

    class CharacteristicTypeEnum(models.TextChoices):
        COMMON = 'c', _('common characteristic')
        POTENTIAL = 'p', _('project potential')

    name = models.CharField(
        max_length=63,
        null=False,
        editable=True,
        verbose_name=_('name'),
        unique=True
    )
    type = models.CharField(
        null=False,
        blank=False,
        max_length=1,
        choices=CharacteristicTypeEnum.choices,
        editable=True,
        verbose_name=_('characteristic type')
    )

    objects = models.Manager()

    def __str__(self):
        return f'{self.name}'
