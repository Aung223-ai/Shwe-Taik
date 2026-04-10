from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_landingcontent'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video_url', models.CharField(blank=True, default='', max_length=255)),
                ('photo_1', models.CharField(blank=True, default='', max_length=255)),
                ('photo_2', models.CharField(blank=True, default='', max_length=255)),
                ('photo_3', models.CharField(blank=True, default='', max_length=255)),
                ('best_title', models.CharField(blank=True, default='', max_length=255)),
                ('recommend_title', models.CharField(blank=True, default='', max_length=255)),
            ],
        ),
    ]
