# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.gis.db import models
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.signals import post_save
from django.utils.translation import pgettext_lazy, get_language, activate, \
    ugettext as _
from django_pgjson.fields import JsonBField

from .conf import settings


VALUEUSER_RELATIONS = (
    (settings.CONFIGURATION_VALUEUSER_UNCCD, _('UNCCD Focal Point')),
)


class Configuration(models.Model):
    """
    The model representing a configuration of the
    :class:`questionnaire.models.Questionnaire`.
    """
    CODE_CHOICES = [
        ('approaches', 'approaches'),
        ('cca', 'cca'),
        ('technologies', 'technologies'),
        ('unccd', 'unccd'),
        ('watershed', 'watershed'),
        ('wocat', 'wocat'),
    ]
    data = JsonBField(help_text="""
            The JSON configuration. See section "Questionnaire
            Configuration" of the manual for more information.<br/>
            <strong style="color:red;">Warning!</strong> You should not
            edit existing JSON configurations directly. Instead, create
            a new version and edit there.<br/><strong>Hint</strong>: Use
            <a href="https://jqplay.org/">jq play</a> to format your
            JSON.""")
    edition = models.CharField(max_length=10)
    code = models.CharField(choices=CODE_CHOICES, max_length=20)
    created = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('code', 'edition')

    @classmethod
    def latest_by_code(cls, code):
        return cls.objects.filter(code=code).latest('created')

    def __str__(self):
        return f'{self.code} {self.edition}'

    def get_previous_edition(self):
        return self.get_previous_by_created(type=self.code)

    def get_next_edition(self):
        return self.get_next_by_created(type=self.code)


class Translation(models.Model):
    """
    The model representing all translations of the database entries.

    .. important::
        Every translated model (with a foreign key to this model) needs
        to have a static attribute ``translation_type`` defined.
    """
    translation_type = models.CharField(max_length=63)
    data = JsonBField()

    def clean(self):
        """
        This function is called to validate the model, e.g. before it is
        saved to the database. Custom validation is handled in this
        function, namely:

        * ``translation_type`` needs to be a valid type.

          .. seealso::
              :func:`Translation.get_translation_types`.

        Raises:
            ``ValidationError``.
        """
        if self.translation_type not in self.get_translation_types():
            raise ValidationError(
                'Translation.translation_type needs to be one of: {}'.format(
                    ', '.join(self.get_translation_types())))

    @staticmethod
    def get_translation_types():
        """
        Return all ``translation_type`` attributes of the translated
        models. In order to do this, all related objects are looped
        dynamically.

        Returns:
            ``list``. A list with the ``validation_types`` of the
            translated models, e.g. ``['key', 'value', 'category']``.
        """
        translation_types = []
        for related in Translation._meta.get_all_related_objects():
            translation_types.append(related.related_model.translation_type)
        return translation_types

    def get_translation(self, keyword, configuration='wocat', locale=None):
        """
        Return the translation of the instance by looking it up in the
        TranslationContent text and getting the translated content.
        If no ``locale`` is provided, the currently active locale is used.
        If no configuration is provided, the wocat configuration is used.
        If no translation is found for a given locale, the default locale (the
        first language of the settings) is used.

        The translations are searched in the following order:
            * configuration > locale
            * configuration > default_locale
            * wocat > locale
            * wocat > default_locale

        Args:
            ``keyword`` (str): The keyword of the translation.

        Kwargs:
            ``configuration`` (str): The keyword of the configuration to
            find the translation for.

            ``locale`` (str): The locale to find the translation for.

        Returns:
            ``str`` or ``None``. The translation or ``None`` if no entry
            for the given locale was not found.
        """

        # translation = self.translationcontent_set.filter(
        #     configuration__in=[configuration, 'wocat'],
        #     keyword=keyword,
        # )
        # if not translation.exists():
        #     return ''
        # Use the configuration as dict-key.
        # values = dict(translation.values_list('configuration', 'text'))
        # text = values.get(configuration, values.get('wocat'))

        # Performance improvement: omit query by trusting that 'makemessages'
        # was executed and translation exists.
        text = self.data.get(
            configuration, self.data.get('wocat', {})
        ).get(
            keyword, {}
        ).get('en')

        if not text:
            return None

        # When creating the values, the configuration and keyword was used as
        # context. Recreate this.
        context = '{} {}'.format(configuration, keyword)
        fallback_context = 'wocat {}'.format(keyword)

        current_language = get_language()
        if locale != current_language:
            # Get translation in requested language and restore current lang.
            # '%' signs are escaped in gettext using double '%%', in order for
            # the translation to be found, it is necessary to do this as well
            # (and reverse it again).
            activate(locale)
            translated = pgettext_lazy(context, text.replace('%', '%%'))
            if translated == text and configuration != 'wocat':
                # TODO: Find a better way to handle "wocat" translations
                # For "global" keys and values (eg. countries), the translation
                # is stored in context "wocat". Therefore, if no translation is
                # found for the current context, try to find a translation in
                # the "wocat" context.
                translated = pgettext_lazy(
                    fallback_context, text.replace('%', '%%'))
            activate(current_language)
            return translated.replace('%%', '%')

        return pgettext_lazy(context, text)

    def __str__(self):
        return self.data.get(settings.LANGUAGES[0][0], '-')


class TranslationContent(models.Model):
    """
    Store the translated strings for the 'Translation' model.

    These are the 'original' texts from the fixtures for the configurations. All
    this content is expected to be English.
    """
    translation_type = 'content'

    translation = models.ForeignKey(Translation, on_delete=models.PROTECT)
    keyword = models.CharField(max_length=50)
    configuration = models.CharField(max_length=50, default='wocat')
    text = models.TextField()


class Key(models.Model):
    """
    The model representing the keys of the
    :class:`questionnaire.models.Questionnaire`.
    """
    translation_type = 'key'

    keyword = models.CharField(max_length=63, unique=True)
    translation = models.ForeignKey(
        'Translation', limit_choices_to={'translation_type': translation_type})
    configuration = JsonBField(help_text="""
            The JSON configuration. See section "Questionnaire
            Configuration" of the manual for more information.<br/>
            <strong>Hint</strong>: Use <a href="https://jqplay.org/">jq
            play</a> to format your JSON.""")
    values = models.ManyToManyField('Value')

    def get_translation(self, *args, **kwargs):
        """
        Return the translation of the key. Passes all arguments to the
        relative :class:`Translation` model's function.

        .. seealso::
            :func:`Translation.get_translation`
        """
        return self.translation.get_translation(*args, **kwargs)

    @property
    def type_(self):
        """
        Helper function to access the ``type`` of the configuration
        JSON.

        Returns:
            ``str`` or ``None``. The value found at key ``type`` of the
            JSON or None if the key was not found.
        """
        return self.configuration.get('type')

    def __str__(self):
        return self.keyword


class Value(models.Model):
    """
    The model representing the predefined values of the
    :class:`questionnaire.models.Questionnaire`.
    """
    translation_type = 'value'

    keyword = models.CharField(max_length=63, unique=True)
    order_value = models.IntegerField(blank=True, null=True)
    translation = models.ForeignKey(
        'Translation', limit_choices_to={'translation_type': translation_type})
    configuration = JsonBField(blank=True, help_text="""
            The JSON configuration. See section "Questionnaire
            Configuration" of the manual for more information.<br/>
            <strong>Hint</strong>: Use <a href="https://jqplay.org/">jq
            play</a> to format your JSON.""")

    class Meta:
        ordering = ('order_value',)

    def get_translation(self, *args, **kwargs):
        """
        Return the translation of the value. Passes all arguments to the
        relative :class:`Translation` model's function.

        .. seealso::
            :func:`Translation.get_translation`
        """
        return self.translation.get_translation(*args, **kwargs)

    def __str__(self):
        return str(self.get_translation(keyword='label') or '[Value]')


class Questiongroup(models.Model):
    """
    The model representing the questiongroups of the
    :class:`questionnaire.models.Questionnaire`
    """
    translation_type = 'value'

    keyword = models.CharField(max_length=63, unique=True)
    translation = models.ForeignKey(
        'Translation', limit_choices_to={'translation_type': translation_type},
        null=True, blank=True)
    configuration = JsonBField(blank=True, help_text="""
            The JSON configuration. See section "Questionnaire
            Configuration" of the manual for more information.<br/>
            <strong>Hint</strong>: Use <a href="https://jqplay.org/">jq
            play</a> to format your JSON.""")

    def get_translation(self, *args, **kwargs):
        """
        Return the translation of the questiongroup. Passes all
        arguments to the relative :class:`Translation` model's function.

        .. seealso::
            :func:`Translation.get_translation`
        """
        return self.translation.get_translation(*args, **kwargs)

    def __str__(self):
        return self.keyword


class Category(models.Model):
    """
    The model representing the categories of the
    :class:`questionnaire.models.Questionnaire`.
    """
    translation_type = 'category'

    keyword = models.CharField(max_length=63, unique=True)
    translation = models.ForeignKey(
        'Translation', limit_choices_to={'translation_type': translation_type})

    def get_translation(self, *args, **kwargs):
        """
        Return the translation of the category. Passes all arguments to
        the relative :class:`Translation` model's function.

        .. seealso::
            :func:`Translation.get_translation`
        """
        return self.translation.get_translation(*args, **kwargs)

    def __str__(self):
        return self.keyword

    class Meta:
        verbose_name_plural = 'categories'


class Project(models.Model):
    """
    The model representing the Projects as they are managed by the WOCAT
    website. IDs must be identical!

    Only "active" Projects can be selected in the form.
    """
    id = models.AutoField(
        primary_key=True,
        help_text="The ID must be exactly the same as on the WOCAT website!")
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=63, null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if not self.abbreviation:
            return self.name
        return '{} ({})'.format(self.name, self.abbreviation)


class Institution(models.Model):
    """
    The model representing the Institutions as they are managed by the WOCAT
    website. IDs must be identical!

    Only "active" Institutions can be selected in the form.
    """
    id = models.IntegerField(
        primary_key=True,
        help_text="The ID must be exactly the same as on the WOCAT website!")
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=255, null=True, blank=True)
    country = models.ForeignKey(
        'Value', null=True, blank=True,
        limit_choices_to=Q(key__keyword='country'))
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if not self.abbreviation:
            name = self.name
        else:
            name = '{} ({})'.format(self.name, self.abbreviation)
        if self.country:
            name = '{} - {}'.format(name, self.country)
        return name

    @classmethod
    def as_select(cls):
        # Method get_or_set is not available for file-based caches
        # (as in local development)
        cache_key = '{key}-{language}'.format(
            key=settings.CONFIGURATION_CACHE_KEY_INSTITUTION_SELECT,
            language=get_language()
        )
        select = cache.get(cache_key)
        if select is None:
            select = [(i.id, str(i)) for i in Institution.objects.all()]
            cache.set(cache_key, select)
        return select


class ValueUser(models.Model):
    """
    Represents a many-to-many relationship between Values and Users with
    additional fields. Additional fields define the type of relationship.
    """
    value = models.ForeignKey('Value')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    relation = models.CharField(max_length=64, choices=VALUEUSER_RELATIONS)


class Country(object):
    """
    Basically a filtered view on the Country values of the questionnaire.
    """

    key_keyword = 'country'
    value_prefix = 'country_'

    @classmethod
    def all(cls):
        """
        Return a list of all country values.

        Returns:
            List of country values (configuration.models.Value)
        """
        key = Key.objects.get(keyword=cls.key_keyword)
        return key.values.all()

    @classmethod
    def get(cls, iso_code):
        """
        Return a single country value or None if not found.

        Args:
            iso_code: The country ISO code.

        Returns:
            A country value (configuration.models.Value) or None.
        """
        value_keyword = '{}{}'.format(cls.value_prefix, iso_code)
        return cls.all().filter(keyword=value_keyword).first()
