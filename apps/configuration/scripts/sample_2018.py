from configuration.editions.sample_2018 import Sample
from configuration.models import Configuration, Translation, Value, Key, \
    Questiongroup


def run():
    Sample(
        key=Key, value=Value, questiongroup=Questiongroup,
        configuration=Configuration, translation=Translation
    ).run_operations()
