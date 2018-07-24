from configuration.editions.sample_2018 import Sample
from configuration.models import Configuration, Translation, Value, Key


def run():
    Sample(
        key=Key, value=Value, configuration=Configuration,
        translation=Translation
    ).run_operations()
