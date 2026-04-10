from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_homecontent'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.CharField(choices=[('video', 'Video'), ('photo', 'Photo')], max_length=10)),
                ('file', models.FileField(upload_to='home/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='HomeSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('subtitle', models.CharField(blank=True, default='', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
