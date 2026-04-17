from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0002_auto_20260401_1836'),
        ('app', '0007_homemedia_homesection'),
    ]

    operations = [
        migrations.AddField(
            model_name='homecontent',
            name='hero_photo_1',
            field=models.ImageField(blank=True, null=True, upload_to='home/'),
        ),
        migrations.AddField(
            model_name='homecontent',
            name='hero_photo_2',
            field=models.ImageField(blank=True, null=True, upload_to='home/'),
        ),
        migrations.AddField(
            model_name='homecontent',
            name='hero_photo_3',
            field=models.ImageField(blank=True, null=True, upload_to='home/'),
        ),
        migrations.AddField(
            model_name='homesection',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='category.SubCategory'),
        ),
    ]
