from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class HarringtonUser(models.Model):
    class Meta:
        verbose_name = _('Harrington user')
        verbose_name_plural = _('Harrington users')

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='harrington_user',
        null=False,
        blank=False,
        editable=False,
        verbose_name=_('harrington user')
    )
    jwt_issuance_time = models.DateTimeField(
        null=False,
        blank=False,
        default=timezone.now,
        editable=True,
        verbose_name=_('JWT issuance time')
    )

    objects = models.Manager()

    def __str__(self):
        return f'{self.user}'

    @staticmethod
    @receiver(post_save, sender=get_user_model())
    def create_Harrington_user(sender, instance, created, **kwargs):
        if created:
            HarringtonUser.objects.create(user=instance)
