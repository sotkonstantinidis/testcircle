from configuration.editions.technologies_2018 import Technologies
from configuration.models import Configuration, Translation, Value, Key


def run():
    Technologies(
        key=Key, value=Value, configuration=Configuration,
        translation=Translation
    ).run_operations()
