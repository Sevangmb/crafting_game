from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
import random
from ..models import MapCell, Material, Player, CellMaterial
from ..serializers import MapCellSerializer, MaterialSerializer
from ..services import map_service
from ..resource_generator import get_biome_from_coordinates
from ..osm_utils import reverse_geocode

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def get_permissions(self):
        # Allow reads to any authenticated user, restrict writes to admins
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [IsAdminUser()]
        return super().get_permissions()

class MapCellViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MapCell.objects.all().prefetch_related(
        'materials__material',
        'dropped_items__material',
        'buildings__building_type'
    )
    serializer_class = MapCellSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def current(self, request):
        try:
            player = Player.objects.select_related('user').get(user=request.user)
            
            # Ensure starting cell (0,0) is always plains in Valence
            if player.grid_x == 0 and player.grid_y == 0:
                biome = 'plains'
                default_lat = 44.933
                default_lon = 4.893
            else:
                default_lat = player.current_y
                default_lon = player.current_x
                # Use smart biome detection
                try:
                    biome = get_biome_from_coordinates(default_lat, default_lon, player.grid_x, player.grid_y)
                except Exception as e:
                    print(f"Error getting biome: {str(e)}")
                    biome = 'plains'  # Default to plains if there's an error

            cell, created = MapCell.objects.get_or_create(
                grid_x=player.grid_x,
                grid_y=player.grid_y,
                defaults={
                    'center_lat': default_lat,
                    'center_lon': default_lon,
                    'biome': biome
                }
            )

            # Always refresh environment (biome/description) based on OSM hints without regenerating materials
            try:
                map_service.refresh_cell_environment(cell)
            except Exception as e:
                print(f"Error refreshing cell environment: {str(e)}")

            if created or not cell.materials.exists():
                # Use the smart resource generation
                try:
                    map_service.populate_cell_materials(cell)
                except Exception as e:
                    print(f"Error populating cell materials: {str(e)}")
                    # If population fails, add some default materials
                    default_material = Material.objects.filter(name='Pierre').first()
                    if default_material:
                        CellMaterial.objects.get_or_create(
                            cell=cell,
                            material=default_material,
                            defaults={'quantity': 20, 'max_quantity': 100}
                        )

            serializer = self.get_serializer(cell)
            return Response(serializer.data)
            
        except Player.DoesNotExist:
            return Response(
                {'error': 'Player not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error in current cell view: {str(e)}")
            return Response(
                {'error': 'An error occurred while loading the current cell'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def world_state(self, request):
        """Return current world state: time of day, season, weather, temperature.

        This is computed from server time, player position and current biome,
        in a deterministic way for a given day so the weather does not change
        every request.
        """
        try:
            player = Player.objects.get(user=request.user)

            now = timezone.now()
            hour = now.hour
            month = now.month

            # Time of day buckets
            if 5 <= hour < 8:
                time_of_day = 'dawn'
            elif 8 <= hour < 18:
                time_of_day = 'day'
            elif 18 <= hour < 21:
                time_of_day = 'evening'
            else:
                time_of_day = 'night'

            # Season by month (northern hemisphere)
            if month in (12, 1, 2):
                season = 'winter'
            elif month in (3, 4, 5):
                season = 'spring'
            elif month in (6, 7, 8):
                season = 'summer'
            else:
                season = 'autumn'

            # Determine biome for weather bias
            try:
                biome = get_biome_from_coordinates(player.current_y, player.current_x, player.grid_x, player.grid_y)
            except Exception:
                biome = 'plains'

            # Deterministic RNG per day/biome so weather is stable
            seed_str = f"{now.date()}:{biome}:{player.grid_x}:{player.grid_y}"
            rng = random.Random(seed_str)

            # Base temperature by season (Celsius), with biome adjustments
            base_temp_by_season = {
                'winter': 0,
                'spring': 10,
                'summer': 22,
                'autumn': 12,
            }
            temp = base_temp_by_season.get(season, 10)

            if biome in ('mountain', 'glacier'):
                temp -= 8
            elif biome in ('desert', 'volcano'):
                temp += 8

            temp += rng.randint(-3, 3)

            # Weather distribution depending on biome & season
            if biome in ('forest', 'swamp'):
                weather_options = ['clear', 'cloudy', 'rain', 'rain', 'storm']
            elif biome in ('mountain', 'glacier'):
                weather_options = ['clear', 'cloudy', 'snow', 'snow', 'storm']
            elif biome in ('desert', 'volcano'):
                weather_options = ['clear', 'clear', 'clear', 'storm']
            else:
                weather_options = ['clear', 'cloudy', 'rain']

            # In winter, bias towards snow in cold biomes
            if season == 'winter' and biome in ('plains', 'forest', 'mountain', 'glacier'):
                weather_options.append('snow')

            weather = rng.choice(weather_options)
            
            # Get location information (city and country)
            location = reverse_geocode(player.current_y, player.current_x)
            
            # Get nearby events
            from ..services.event_spawner_service import EventSpawnerService
            from ..serializers import DynamicEventSerializer
            nearby_events = EventSpawnerService.get_events_near_player(player, radius=10)
            events_data = DynamicEventSerializer(nearby_events, many=True).data

            data = {
                'time_of_day': time_of_day,
                'season': season,
                'weather': weather,
                'temperature': temp,
                'biome': biome,
                'city': location.get('city'),
                'country': location.get('country'),
                'nearby_events': events_data,
            }

            return Response(data)

        except Player.DoesNotExist:
            return Response({'error': 'Player not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error in world_state view: {str(e)}")
            return Response({'error': 'Failed to compute world state'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def gather(self, request, pk=None):
        cell = self.get_object()
        player = Player.objects.get(user=request.user)
        material_id = request.data.get('material_id')

        result, status_code = map_service.gather_material(player, cell, material_id)
        return Response(result, status=status_code)

    @action(detail=False, methods=['post'])
    def scavenge(self, request):
        player = Player.objects.get(user=request.user)
        result, status_code = map_service.scavenge_location(player)
        return Response(result, status=status_code)
