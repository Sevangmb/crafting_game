# Generated manually to add performance indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0027_clothing_weapon'),
    ]

    operations = [
        # Player indexes
        migrations.AlterField(
            model_name='player',
            name='user',
            field=models.OneToOneField(
                on_delete=models.deletion.CASCADE,
                to='auth.user',
                db_index=True
            ),
        ),
        migrations.AddIndex(
            model_name='player',
            index=models.Index(fields=['grid_x', 'grid_y'], name='game_player_grid_xy_idx'),
        ),
        migrations.AddIndex(
            model_name='player',
            index=models.Index(fields=['level'], name='game_player_level_idx'),
        ),
        migrations.AddIndex(
            model_name='player',
            index=models.Index(fields=['last_energy_update'], name='game_player_energy_update_idx'),
        ),

        # MapCell indexes
        migrations.AddIndex(
            model_name='mapcell',
            index=models.Index(fields=['grid_x', 'grid_y'], name='game_mapcell_grid_xy_idx'),
        ),
        migrations.AddIndex(
            model_name='mapcell',
            index=models.Index(fields=['biome'], name='game_mapcell_biome_idx'),
        ),

        # Inventory indexes
        migrations.AddIndex(
            model_name='inventory',
            index=models.Index(fields=['player', 'material'], name='game_inventory_player_material_idx'),
        ),
        migrations.AddIndex(
            model_name='inventory',
            index=models.Index(fields=['quantity'], name='game_inventory_quantity_idx'),
        ),

        # GatheringLog indexes
        migrations.AddIndex(
            model_name='gatheringlog',
            index=models.Index(fields=['player', 'timestamp'], name='game_gatherlog_player_time_idx'),
        ),
        migrations.AddIndex(
            model_name='gatheringlog',
            index=models.Index(fields=['timestamp'], name='game_gatherlog_time_idx'),
        ),

        # CraftingLog indexes
        migrations.AddIndex(
            model_name='craftinglog',
            index=models.Index(fields=['player', 'timestamp'], name='game_craftlog_player_time_idx'),
        ),
        migrations.AddIndex(
            model_name='craftinglog',
            index=models.Index(fields=['timestamp'], name='game_craftlog_time_idx'),
        ),

        # CellMaterial indexes
        migrations.AddIndex(
            model_name='cellmaterial',
            index=models.Index(fields=['cell', 'material'], name='game_cellmat_cell_material_idx'),
        ),
        migrations.AddIndex(
            model_name='cellmaterial',
            index=models.Index(fields=['quantity'], name='game_cellmat_quantity_idx'),
        ),

        # Material indexes
        migrations.AddIndex(
            model_name='material',
            index=models.Index(fields=['rarity'], name='game_material_rarity_idx'),
        ),
        migrations.AddIndex(
            model_name='material',
            index=models.Index(fields=['category'], name='game_material_category_idx'),
        ),
        migrations.AddIndex(
            model_name='material',
            index=models.Index(fields=['is_food'], name='game_material_is_food_idx'),
        ),
        migrations.AddIndex(
            model_name='material',
            index=models.Index(fields=['is_equipment'], name='game_material_is_equipment_idx'),
        ),

        # Recipe indexes
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['result_material'], name='game_recipe_result_idx'),
        ),

        # RecipeIngredient indexes
        migrations.AddIndex(
            model_name='recipeingredient',
            index=models.Index(fields=['recipe', 'material'], name='game_recipeingred_recipe_mat_idx'),
        ),

        # PlayerSkill indexes
        migrations.AddIndex(
            model_name='playerskill',
            index=models.Index(fields=['player', 'skill'], name='game_playerskill_player_skill_idx'),
        ),

        # PlayerTalent indexes
        migrations.AddIndex(
            model_name='playertalent',
            index=models.Index(fields=['player', 'talent_node'], name='game_playertalent_player_node_idx'),
        ),

        # DroppedItem indexes (if exists)
        migrations.AddIndex(
            model_name='droppeditem',
            index=models.Index(fields=['cell'], name='game_droppeditem_cell_idx'),
        ),
        migrations.AddIndex(
            model_name='droppeditem',
            index=models.Index(fields=['dropped_by'], name='game_droppeditem_player_idx'),
        ),
    ]
