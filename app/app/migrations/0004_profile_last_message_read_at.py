from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_message_channel_message_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_message_read_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
