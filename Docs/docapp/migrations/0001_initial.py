# Generated by Django 3.0.2 on 2020-01-21 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Commits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Docid', models.CharField(max_length=50)),
                ('timestamp', models.IntegerField(max_length=50)),
                ('author', models.CharField(max_length=50)),
                ('Document', models.CharField(max_length=10000)),
                ('sha', models.CharField(max_length=50)),
            ],
        ),
    ]