# Generated by Django 4.0.5 on 2022-07-06 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscription',
            name='check_self_subscription',
        ),
    ]