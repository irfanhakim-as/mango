from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


#====================BASE: OBJECT SCHEDULE META====================#
class ObjectScheduleMeta(models.base.ModelBase):
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        if bases != (models.Model,):
            reference_model = dct.get("SubjectReference", None)
            if reference_model:
                subject_field = models.ForeignKey(
                    reference_model,
                    blank=False,
                    null=False,
                    on_delete=models.CASCADE,
                    verbose_name=_("Subject"),
                    help_text=_("Scheduled subject.")
                )
                new_class.add_to_class("subject", subject_field)
        return new_class


#====================BASE: OBJECT SCHEDULE====================#
class ObjectSchedule(models.Model, metaclass=ObjectScheduleMeta):
    class Meta:
        abstract=True

    name = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Name of job to be performed.")
    )

    date_scheduled = models.DateTimeField(
        blank=False,
        null=False,
        default=timezone.now,
        verbose_name=_("Date scheduled"),
        help_text=_("Date when the task was scheduled.")
    )

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return str(self.pk)


#====================BASE: OBJECT ITEM====================#
class ObjectItem(models.Model):
    class Meta:
        abstract=True

    post_id = models.CharField(
        blank=True,
        null=True,
        unique=True,
        max_length=255,
        verbose_name=_("Post ID"),
        help_text=_("ID of the published Mastodon post.")
    )

    item_id = models.CharField(
        blank=False,
        null=False,
        unique=True,
        max_length=255,
        verbose_name=_("Item ID"),
        help_text=_("ID of the object item.")
    )

    title = models.TextField(
        blank=False,
        null=False,
        verbose_name=_("Item title"),
        help_text=_("Title or content of the object item.")
    )

    link = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("Item link"),
        help_text=_("Link of the object item.")
    )

    tags = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Item tags"),
        help_text=_("Tags of the object item.")
    )

    # published = models.DateTimeField(
    #     blank=False,
    #     null=False,
    #     default=timezone.now,
    #     verbose_name=_("Item published date"),
    #     help_text=_("Date of publication of the object item.")
    # )

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return str(self.pk)
