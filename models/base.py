from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from base.methods import (
    demojize,
    has_emoji,
)


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

    post_id = models.JSONField(
        blank=True,
        null=True,
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

    def clean(self):
        # run parent clean method
        super().clean()
        # iterate through all fields of the model
        for field in self._meta.get_fields():
            # if field is a CharField or TextField and has a value
            if isinstance(field, (models.CharField, models.TextField)) and field.value_from_object(self):
                # get field value
                field_value = getattr(self, field.name)
                # if field value is a string and has any emoji
                if isinstance(field_value, str) and has_emoji(field_value):
                    # set field value to its demojized value
                    setattr(self, field.name, demojize(field_value))

    def save(self, *args, **kwargs):
        # run clean method beforehand
        self.clean()
        # run parent save method
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return str(self.pk)


#====================BASE: OBJECT ACCOUNT====================#
class ObjectAccount(models.Model):
    class Meta:
        abstract=True
        unique_together = (("api_base_url", "uid"))

    uid = models.CharField(
        blank=False,
        null=False,
        max_length=255,
        verbose_name=_("UID"),
        help_text=_("Unique Identifier of the account.")
    )

    access_token = models.CharField(
        blank=False,
        null=False,
        unique=True,
        max_length=255,
        verbose_name=_("Access token"),
        help_text=_("Secure token required to authenticate with the Mastodon instance's API.")
    )

    api_base_url = models.CharField(
        blank=False,
        null=False,
        max_length=255,
        verbose_name=_("API endpoint"),
        help_text=_("API endpoint or URL for the Mastodon instance.")
    )

    is_bot = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        verbose_name=_("Is bot"),
        help_text=_("Specifies whether the account should be marked as a bot.")
    )

    is_discoverable = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        verbose_name=_("Is discoverable"),
        help_text=_("Specifies whether the account should appear in the user directory.")
    )

    is_enabled = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        verbose_name=_("Is enabled"),
        help_text=_("Specifies whether the account is enabled for operations.")
    )

    display_name = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("Display name"),
        help_text=_("The account's display name.")
    )

    fields = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Fields"),
        help_text=_("Name-value pairs of information to be displayed in the profile.")
    )

    is_locked = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        verbose_name=_("Is locked"),
        help_text=_("Specifies whether the account needs to manually approve follow requests.")
    )

    note = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Item title"),
        help_text=_("The bio or description of the account.")
    )

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return str(self.pk)


#=====================BASE: OBJECT FEED====================#
class ObjectFeed(models.Model):
    class Meta:
        abstract=True

    uid = models.CharField(
        blank=False,
        null=False,
        unique=True,
        max_length=255,
        verbose_name=_("UID"),
        help_text=_("Unique Identifier of the feed object.")
    )

    endpoint = models.CharField(
        blank=False,
        null=False,
        max_length=255,
        verbose_name=_("Endpoint"),
        help_text=_("The endpoint or URL of the feed.")
    )

    is_enabled = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        verbose_name=_("Is enabled"),
        help_text=_("Specifies whether the feed is enabled for processing.")
    )

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return str(self.pk)
