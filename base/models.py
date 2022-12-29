from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


#=====================SCHEDULE: POST====================#
class PostSchedule(models.Model):
    class Meta:
        verbose_name="Post"
        verbose_name_plural="posts"

    name=models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Name'),
        help_text=_('Name of job to be performed.')
    )
    
    date_scheduled=models.DateTimeField(
        blank=False,
        default=timezone.now,
        verbose_name=_('Date scheduled'),
        help_text=_("Date when the task was scheduled.")
    )
    
    msg=models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Message'),
        help_text=_("Content of the post.")
    )
    
    receiver=models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Receiver'),
        help_text=_('Individual receiver of the post.')
    )

    visibility=models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Visibility'),
        help_text=_('Visibility of the post.')
    )
    
    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return str(self.pk)
