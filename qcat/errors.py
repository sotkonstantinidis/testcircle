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
