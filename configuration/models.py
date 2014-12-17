from django.contrib.gis.db import models
from django_pgjson.fields import JsonBField


class Configuration(models.Model):
    """
    The model representing a configuration of the
    :class:`questionnaire.models.Questionnaire`.
    """
    data = JsonBField()
    code = models.CharField(max_length=63)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    created = models.DateTimeField(auto_now=True)
    activated = models.DateTimeField(null=True)


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
