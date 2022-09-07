# Generated by Django 4.0.5 on 2022-07-06 11:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0006_alter_recipe_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='favorited',
            field=models.ManyToManyField(related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='В избранном'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='in_shopping_cart',
            field=models.ManyToManyField(related_name='shoping_cart', to=settings.AUTH_USER_MODEL, verbose_name='В корзине'),
        ),
    ]
