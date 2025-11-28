# Generated migration for Achievement system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0014_mob'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField()),
                ('icon', models.CharField(default='🏆', max_length=50)),
                ('category', models.CharField(choices=[
                    ('exploration', 'Exploration'),
                    ('crafting', 'Crafting'),
                    ('gathering', 'Gathering'),
                    ('combat', 'Combat'),
                    ('progression', 'Progression'),
                    ('collection', 'Collection')
                ], default='progression', max_length=20)),
                ('requirement_type', models.CharField(choices=[
                    ('gather_count', 'Gather Count'),
                    ('craft_count', 'Craft Count'),
                    ('move_count', 'Move Count'),
                    ('level_reached', 'Level Reached'),
                    ('material_collected', 'Material Collected'),
                    ('recipe_crafted', 'Recipe Crafted'),
                    ('biome_visited', 'Biome Visited'),
                    ('mob_defeated', 'Mob Defeated')
                ], max_length=30)),
                ('requirement_value', models.IntegerField(help_text='Quantity or ID required')),
                ('requirement_target', models.CharField(blank=True, help_text='Material name, recipe name, etc.', max_length=100, null=True)),
                ('reward_xp', models.IntegerField(default=0)),
                ('hidden', models.BooleanField(default=False, help_text='Hidden until unlocked')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='PlayerAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress', models.IntegerField(default=0)),
                ('completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('achievement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.achievement')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.player')),
            ],
            options={
                'unique_together': {('player', 'achievement')},
            },
        ),
    ]
