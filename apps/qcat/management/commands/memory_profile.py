from pathlib import Path

from django.core.management.base import BaseCommand
from django.db.models import Avg, Sum
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from tabulate import tabulate

from qcat.models import MemoryLog


class Command(BaseCommand):
    help = 'Read log files and show some metrics.'

    # Delimiter in the log files
    delimiter = ';'
    # Glob pattern for log file names
    cache_file_name = 'caches*.log'
    # Number of results to display
    slice_size = 10

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-truncate',
            dest='no-truncate',
            action='store_true',
            default=False,
            help='Do not truncate db if a path for log files is given!'
        )
        parser.add_argument(
            '--path',
            dest='path',
            default='',
            help='Path to folder containing log files'
        )

    def handle(self, *args, **options):
        if options['path']:
            if not options['no-truncate']:
                self.truncate_logs_in_db()
            self.save_logs_to_db(path=options['path'])

        self.display_stats()

    def save_logs_to_db(self, path):
        """
        Read log files and save them to the DB for easy AVG, SUM and stuff.
        """
        log_files = Path(path).glob(self.cache_file_name)
        for log in log_files:
            with log.open() as f:
                self.parse_line(*f.readlines())

    @property
    def titles(self):
        """
        Model field names without the ID field.
        """
        return [field.name for field in MemoryLog._meta.get_fields()[1:]]

    def parse_line(self, *lines):
        """
        Split given lines according to delimiter, and prepare model row generation.
        """
        for line in lines:
            attrs = {}
            for index, param in enumerate(line.split(self.delimiter)):
                # Read datetime from string. Not the nicest approach, but the log is always 'info',
                # so it starts at position 5.
                if index is 0:
                    param = make_aware(parse_datetime(param[5:21]))
                attrs[self.titles[index]] = param
            MemoryLog(**attrs).save()

    @staticmethod
    def truncate_logs_in_db():
        MemoryLog.objects.all().delete()

    def display_stats(self):
        """
        Show:
        - largest absolute increments
        - largest avg increments
        - largest sum of increments

        """
        largest = MemoryLog.objects.values(
            'params', 'increment'
        ).order_by(
            '-increment'
        )
        self.print_rows(
            title='Largest absolute (single) increments',
            queryset=largest
        )

        increment_avg = MemoryLog.objects.values('params').annotate(
            Avg('increment')
        ).order_by('-increment__avg')
        self.print_rows(
            title='Highest average increments',
            queryset=increment_avg
        )

        increment_sum = MemoryLog.objects.values('params').annotate(
            Sum('increment')
        ).order_by('-increment__sum')[0:self.slice_size]
        self.print_rows(
            title='Highest sum of increments',
            queryset=increment_sum
        )

    def print_rows(self, title, queryset):
        print('\n')
        print(title.upper())
        rows = []
        for item in queryset[0:self.slice_size]:
            values = list(item.values())
            values[1] = int(values[1]) >> 20
            rows.append(values)
        print(tabulate(
            tabular_data=rows,
            headers=['Params', 'Increment (MB)'],
            tablefmt='grid')
        )
        print('\n')
