import csv
import logging
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

CSV_MODELS = [
    ('ingredients.csv', Ingredient, ('name', 'measurement_unit',)),
]

formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


class Command(BaseCommand):
    help = 'Loads ingredients data from csv-files into Ingredient model'

    def add_arguments(self, parser):
        parser.add_argument(
            '-p',
            '--csv_path',
            dest='csv_path',
            type=str,
            default=os.path.join(settings.BASE_DIR, 'data'),
            help='Путь к папке с csv файлами'
        ),
        parser.add_argument(
            '--no_delete',
            action='store_false',
            help='Не удалять текущие данные перед заливкой новых',
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        try:
            list_dir = os.listdir(csv_path)
        except FileNotFoundError:
            logger.error(f'Директория {csv_path} не найдена!')
            raise FileNotFoundError
        logger.info(f'директория с csv-файлами - {csv_path}')
        files = [f for f in list_dir
                 if os.path.isfile(os.path.join(csv_path, f))
                 and f in [CSV_MODELS[i][0] for i in range(len(CSV_MODELS))]]
        logger.info(f'Файлы - {files}')
        for file, model, headers in CSV_MODELS:
            model_observe_number = model.objects.count()
            if file not in files:
                logger.warning(f'отсутствует заявленный файл - {file}')
                continue
            if options['no_delete']:
                model.objects.all().delete()
            logger.info(f'обработка файла - {file}')
            with open(
                os.path.join(csv_path, file),
                newline='',
                encoding='utf-8'
            ) as csvfile:
                data = csv.DictReader(csvfile, delimiter=',',
                                      fieldnames=headers,)
                model.objects.bulk_create(
                    [model(**observe) for observe in data],
                    ignore_conflicts=True
                )
            if model.objects.count() > model_observe_number:
                logger.info(f'Данные файла {file} загружены')
            else:
                logger.warning(f'Данные файла {file} НЕ загружены')
