class ConfigurationErrorNoConfigurationFound(Exception):

    def __init__(self, keyword):
        self.keyword = keyword

    def __str__(self):
        return 'No active configuration found for keyword "{}"'.format(
            self.keyword)


class ConfigurationErrorNotInDatabase(Exception):

    def __init__(self, Model, keyword):
        self.Model = Model
        self.keyword = keyword

    def __str__(self):
        return 'No database entry found for keyword "{}" in model {}'.format(
            self.keyword, self.Model)


class ConfigurationErrorInvalidOption(Exception):

    def __init__(self, option, configuration, object_):
        self.option = option
        self.configuration = configuration
        self.object_ = object_

    def __str__(self):
        return 'Option "{}" is not valid for configuration "{}" of object {}.'\
            .format(self.option, self.configuration, self.object_)


class ConfigurationErrorInvalidConfiguration(Exception):

    def __init__(self, configuration, format, parent):
        self.configuration = configuration
        self.format = format
        self.parent = parent

    def __str__(self):
        return 'Configuration "{}" (part of "{}") is missing or is not of '\
            'format "{}"'.format(self.configuration, self.parent, self.format)
