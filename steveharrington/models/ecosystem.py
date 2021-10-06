from typing import Union

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .user import HarringtonUser
from .project import Project
from .characteristic import Characteristic
from .term import Term


class Ecosystem(models.Model):
    class Meta:
        verbose_name = _('ecosystem')
        verbose_name_plural = _('ecosystems')

    name = models.CharField(
        max_length=63,
        null=False,
        editable=True,
        verbose_name=_('name'),
        unique=True
    )
    owners = models.ManyToManyField(
        HarringtonUser,
        related_name='ecosystems',
        verbose_name=_('owners'),
    )

    objects = models.Manager()

    def __str__(self):
        return f'{self.name}'


class EcosystemProjects(models.Model):
    class Meta:
        verbose_name = _('ecosystem project info')
        verbose_name_plural = _('ecosystem projects info')
        constraints = [
            models.UniqueConstraint(
                fields=['ecosystem', 'project', 'characteristic', 'rank'],
                name='unique_project_info',
            )
        ]

    ecosystem = models.ForeignKey(
        Ecosystem,
        models.CASCADE,
        null=False,
        editable=True,
        verbose_name=_('ecosystem'),
        related_name='projects',
    )
    project = models.ForeignKey(
        Project,
        models.CASCADE,
        null=False,
        editable=True,
        verbose_name=_('project'),
        related_name='ecosystems',
    )
    characteristic = models.ForeignKey(
        Characteristic,
        models.CASCADE,
        null=False,
        editable=True,
        verbose_name=_('characteristic'),
        related_name='projects',
    )
    rank = models.IntegerField(
        null=False,
        blank=False,
        editable=True,
        default=0,
        verbose_name=_('rank'),
    )

    def fuzzy_value(self):
        queryset = EcosystemCharacteristicsTerms.objects.filter(
            ecosystem=self.ecosystem,
            characteristic=self.characteristic,
        )
        if not queryset.exists():
            raise  # TODO: raise what?

        return tuple((term, term.mu(self.rank)) for term in queryset)

    def value(self):
        values = self.fuzzy_value()
        return sorted(values, key=lambda x: x[1], reverse=True)[0][0]

    def potentials_fuzzy_value(self):
        potentials_qs = EcosystemPotentials.objects.filter(ecosystem=self.ecosystem)
        terms_qs = EcosystemCharacteristicsTerms.objects.filter(ecosystem=self.ecosystem)
        characteristics_qs = EcosystemProjects.objects.filter(ecosystem=self.ecosystem, project=self.project)

        values = {}

        for potential in potentials_qs.distinct('potential'):
            characteristics = characteristics_qs.filter(characteristic__potentials__potential=potential.potential)\
                .annotate(weight=models.F('characteristic__potentials__weight'))

            values[potential.potential] = {
                term: sum(characteristic.weight * term.mu(characteristic.value().index) for characteristic in characteristics)
                for term in terms_qs.filter(characteristic=potential.potential)
            }

        return values

    def potentials_value(self):
        result = self.potentials_fuzzy_value()
        for potential in result:
            # TODO: if term.a1 < 0?
            result[potential] = sum(value * (term.a4 - max(term.a1, 0)) for term, value in result[potential].items())

        return result

    objects = models.Manager()

    def __str__(self):
        return f'{self.project}: {self.characteristic} ({self.ecosystem})'


class EcosystemPotentials(models.Model):
    class Meta:
        verbose_name = _('ecosystem potential info')
        verbose_name_plural = _('ecosystem potentials info')
        constraints = [
            models.UniqueConstraint(
                fields=['ecosystem', 'potential', 'characteristic'],
                name='unique_potential_info',
                include=['characteristic'],
            )
        ]

    ecosystem = models.ForeignKey(
        Ecosystem,
        models.CASCADE,
        null=False,
        editable=True,
        verbose_name=_('ecosystem'),
        related_name='potentials',
    )
    potential = models.ForeignKey(
        Characteristic,
        models.CASCADE,
        null=False,
        editable=True,
        verbose_name=_('potential'),
        related_name='characteristics',
    )
    characteristic = models.ForeignKey(
        Characteristic,
        models.CASCADE,
        null=False,
        editable=True,
        verbose_name=_('characteristic'),
        related_name='potentials',
    )
    weight = models.FloatField(
        null=False,
        blank=False,
        editable=True,
        verbose_name=_('weight'),
    )

    objects = models.Manager()

    def __str__(self):
        return f'{self.potential}: {self.characteristic} ({self.ecosystem})'


class EcosystemCharacteristicsTerms(models.Model):
    class Meta:
        verbose_name = _('ecosystem term info')
        verbose_name_plural = _('ecosystem terms info')
        constraints = [
            models.UniqueConstraint(
                fields=['ecosystem', 'characteristic', 'index'],
                name='unique_term_info',
                include=['term'],
            )
        ]

    ecosystem = models.ForeignKey(
        Ecosystem,
        models.CASCADE,
        null=False,
        editable=True,
        verbose_name=_('ecosystem'),
        related_name='characteristics',
    )
    characteristic = models.ForeignKey(
        Characteristic,
        models.CASCADE,
        null=False,
        editable=True,
        verbose_name=_('characteristic'),
        related_name='terms',
    )
    index = models.IntegerField(
        null=False,
        blank=False,
        editable=True,
        default=0,
        verbose_name=_('index')
    )
    term = models.ForeignKey(
        Term,
        models.CASCADE,
        null=False,
        editable=True,
        verbose_name=_('term'),
        related_name='characteristics',
    )
    a1 = models.FloatField(
        null=False,
        blank=False,
        editable=True,
        verbose_name=_('a1'),
    )
    a2 = models.FloatField(
        null=False,
        blank=False,
        editable=True,
        verbose_name=_('a2'),
    )
    a3 = models.FloatField(
        null=False,
        blank=False,
        editable=True,
        verbose_name=_('a3'),
    )
    a4 = models.FloatField(
        null=False,
        blank=False,
        editable=True,
        verbose_name=_('a4'),
    )

    def mu(self, x: Union[float, int]) -> float:

        if self.a1 < x < self.a2:
            return (x - self.a1) / (self.a2 - self.a1)
        if self.a2 <= x <= self.a3:
            return 1.
        if self.a3 < x < self.a4:
            return (self.a4 - x) / (self.a4 - self.a3)
        else:
            return 0.

    objects = models.Manager()

    def __str__(self):
        return f'{self.characteristic}: {self.term} ({self.ecosystem})'
