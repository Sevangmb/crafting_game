from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('game', '0019_player_last_energy_update_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grid_x', models.IntegerField()),
                ('grid_y', models.IntegerField()),
                ('level', models.IntegerField(default=1)),
                ('material_requirements', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='houses', to='game.Player')),
            ],
            options={
                'unique_together': {('player', 'grid_x', 'grid_y')},
            },
        ),
    ]
