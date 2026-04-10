from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_profile_last_message_read_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='LandingContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hero_title', models.CharField(blank=True, default='', max_length=255)),
                ('hero_subtitle', models.CharField(blank=True, default='', max_length=255)),
                ('trust_line', models.CharField(blank=True, default='', max_length=255)),
                ('about_text', models.TextField(blank=True, default='')),
                ('mission_text', models.TextField(blank=True, default='')),
                ('vision_text', models.TextField(blank=True, default='')),
                ('services_text', models.TextField(blank=True, default='')),
                ('projects_1', models.CharField(blank=True, default='', max_length=255)),
                ('projects_2', models.CharField(blank=True, default='', max_length=255)),
                ('projects_3', models.CharField(blank=True, default='', max_length=255)),
                ('activities_1', models.CharField(blank=True, default='', max_length=255)),
                ('activities_2', models.CharField(blank=True, default='', max_length=255)),
                ('activities_3', models.CharField(blank=True, default='', max_length=255)),
                ('testimonial_1', models.CharField(blank=True, default='', max_length=255)),
                ('testimonial_2', models.CharField(blank=True, default='', max_length=255)),
                ('testimonial_3', models.CharField(blank=True, default='', max_length=255)),
                ('partner_1', models.CharField(blank=True, default='', max_length=255)),
                ('partner_2', models.CharField(blank=True, default='', max_length=255)),
                ('partner_3', models.CharField(blank=True, default='', max_length=255)),
                ('partner_4', models.CharField(blank=True, default='', max_length=255)),
                ('faq1_q', models.CharField(blank=True, default='', max_length=255)),
                ('faq1_a', models.CharField(blank=True, default='', max_length=255)),
                ('faq2_q', models.CharField(blank=True, default='', max_length=255)),
                ('faq2_a', models.CharField(blank=True, default='', max_length=255)),
                ('newsletter_text', models.CharField(blank=True, default='', max_length=255)),
                ('contact_phone', models.CharField(blank=True, default='', max_length=100)),
                ('contact_email', models.CharField(blank=True, default='', max_length=100)),
                ('contact_address', models.CharField(blank=True, default='', max_length=255)),
                ('careers_text', models.CharField(blank=True, default='', max_length=255)),
                ('cta_title', models.CharField(blank=True, default='', max_length=255)),
                ('cta_button_text', models.CharField(blank=True, default='', max_length=100)),
            ],
        ),
    ]
