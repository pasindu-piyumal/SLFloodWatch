from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='RiverReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_name', models.CharField(max_length=200)),
                ('river_name', models.CharField(max_length=200)),
                ('water_level', models.FloatField()),
                ('previous_level', models.FloatField(blank=True, null=True)),
                ('unit', models.CharField(default='ft', max_length=10)),
                ('trend', models.CharField(blank=True, default='', max_length=50)),
                ('status', models.CharField(blank=True, default='', max_length=50)),
                ('minor_level', models.FloatField(blank=True, null=True)),
                ('alert_level', models.FloatField(blank=True, null=True)),
                ('major_level', models.FloatField(blank=True, null=True)),
                ('station_id', models.CharField(max_length=100, unique=True)),
                ('river_id', models.CharField(blank=True, default='', max_length=100)),
                ('last_updated', models.DateTimeField(blank=True, null=True)),
                ('scraped_at', models.DateTimeField(auto_now=True)),
                ('station_url', models.URLField(blank=True, null=True)),
            ],
        ),
    ]
