from datetime import datetime
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import to_locale, get_language
from django_pgjson.fields import JsonBField


class Configuration(models.Model):
    """
    The model representing a configuration of the
    :class:`questionnaire.models.Questionnaire`.
    """
    data = JsonBField(help_text="""
            The JSON configuration. See section "Questionnaire
            Configuration" of the manual for more information.<br/>
            <strong style="color:red;">Warning!</strong> You should not
            edit existing JSON configurations directly. Instead, create
            a new version and edit there.<br/><strong>Hint</strong>: Use
            <a href="https://jqplay.org/">jq play</a> to format your
            JSON.""")
    code = models.CharField(
        max_length=63, help_text="""
            The internal code of the configuration, e.g. "core", "wocat"
            or "unccd". The same code can be used multiple times but
            only one configuration per code can be "active".""")
    base_code = models.CharField(
        max_length=63, blank=True, help_text="""
            The code of the base configuration from which the
            configuration inherits. An active configuration with the
            given code needs to exist.""")
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    active = models.BooleanField(
        default=False, help_text="""
            <strong style="color:red;">Warning!</strong> Only one
            configuration per code can be active. If you set this
            configuration "active", an existing configuration with the
            same code will be set inactive.""")
    activated = models.DateTimeField(null=True, blank=True)

    def clean(self):
        """
        This function is called to validate the model, e.g. before it is
        saved to the database. Custom validation is handled in this
        function, namely:

        * If a ``base_code`` is set, an active configuration with this
          code needs to exist.
        * If there is already an active configuration with the given
          code, the ``active`` flag is set to ``False`` for this
          configuration.

        Raises:
            ``ValidationError``.
        """
        if self.base_code:
            # Check if base_code exists and has an active version.
            if Configuration.get_active_by_code(self.base_code) is None:
                raise ValidationError(
                    'The base code does not exist or does not have an active '
                    'version!')

        # Check if there is already an active configuration. In this case,
        # remove the flag from the previously active configuration.
        previously_active = Configuration.get_active_by_code(self.code)
        if self.active and previously_active is not None:
            previously_active.active = False
            previously_active.save()

        if self.active:
            # Check the configuration
            from configuration.configuration import QuestionnaireConfiguration
            configuration = QuestionnaireConfiguration(self.code, self)
            if configuration.configuration_error is not None:
                raise ValidationError(
                    'Error while parsing the configuration JSON: {}'.format(
                        configuration.configuration_error))

    def save(self, force_insert=False, force_update=False):
        """
        This function is called to save the model. Customized saving
        behavious is handled in this function, namely:

        * If a configuration is saved with ``active=True``, it receives
          a timestamp (``activated``).
        """
        if self.active:
            self.activated = datetime.now()
        super(Configuration, self).save(force_insert, force_update)

    @staticmethod
    def get_active_by_code(code):
        """
        Return the **active** Configuration with a given code if
        available.

        Args:
            ``code`` (str): The code of the Configuration.

        Returns:
            :class:`configuration.models.Configuration` or ``None``. The
            active Configuration object or None if no active
            configuration with the given code.
        """
        try:
            return Configuration.objects.get(code=code, active=True)
        except Configuration.DoesNotExist:
            return None

    def __str__(self):
        return self.name


class Translation(models.Model):
    """
    The model representing all translations of the database entries.
    """
    translation_type = models.CharField(max_length=63)
    data = JsonBField()


class Key(models.Model):
    """
    The model representing the keys of the
    :class:`questionnaire.models.Questionnaire`.
    """
    keyword = models.CharField(max_length=63, unique=True)
    translation = models.ForeignKey('Translation')
    data = JsonBField(null=True)

    def get_translation(self):
        return self.translation.data.get(to_locale(get_language()))


class Value(models.Model):
    """
    The model representing the predefined values of the
    :class:`questionnaire.models.Questionnaire`.
    """
    keyword = models.CharField(max_length=63, unique=True)
    translation = models.ForeignKey('Translation')
    key = models.ForeignKey('Key')


class Category(models.Model):
    """
    The model representing the categories of the
    :class:`questionnaire.models.Questionnaire`.
    """
    keyword = models.CharField(max_length=63, unique=True)
    translation = models.ForeignKey('Translation')

    def get_translation(self):
        return self.translation.data.get(to_locale(get_language()))
