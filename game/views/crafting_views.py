from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count
from ..models import Recipe, Workstation, PlayerWorkstation, RecipeIngredient, Player
from ..serializers import RecipeSerializer, WorkstationSerializer, PlayerWorkstationSerializer, RecipeIngredientAdminSerializer
from ..services import crafting_service

class WorkstationViewSet(viewsets.ModelViewSet):
    queryset = Workstation.objects.all()
    serializer_class = WorkstationSerializer

    def get_permissions(self):
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [IsAdminUser()]
        return super().get_permissions()

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related('ingredients__material', 'required_workstation')
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        # Use admin serializer for write operations
        if self.request and self.request.method in ('POST', 'PUT', 'PATCH'):
            from ..serializers import RecipeAdminSerializer
            return RecipeAdminSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def duplicates(self, request):
        # Duplicates by name
        by_name = (
            Recipe.objects.values('name')
            .annotate(c=Count('id'))
            .filter(c__gt=1)
            .order_by('-c', 'name')
        )
        name_details = []
        for row in by_name:
            items = list(
                Recipe.objects.filter(name=row['name'])
                .values('id', 'name', 'result_material__id', 'result_material__name')
            )
            name_details.append({'name': row['name'], 'count': row['c'], 'items': items})

        # Duplicates by result material
        by_result = (
            Recipe.objects.values('result_material')
            .annotate(c=Count('id'))
            .filter(c__gt=1)
            .order_by('-c', 'result_material')
        )
        result_details = []
        for row in by_result:
            items = list(
                Recipe.objects.filter(result_material_id=row['result_material'])
                .values('id', 'name', 'result_material__id', 'result_material__name')
            )
            # Safe material name fetch
            mat_name = items[0]['result_material__name'] if items else None
            result_details.append({
                'result_material_id': row['result_material'],
                'result_material_name': mat_name,
                'count': row['c'],
                'items': items,
            })

        return Response({
            'duplicates_by_name': name_details,
            'duplicates_by_result_material': result_details,
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def delete_duplicates(self, request):
        # Optional: restrict to staff users
        user = request.user
        if not user.is_staff:
            return Response({'error': 'Action réservée aux administrateurs'}, status=status.HTTP_403_FORBIDDEN)

        removed = []
        kept = []

        # Delete duplicate recipes by exact same name, keep the most complete (highest ingredient count), tie-breaker lowest id
        name_groups = (
            Recipe.objects.values('name')
            .annotate(c=Count('id'))
            .filter(c__gt=1)
        )
        for g in name_groups:
            same_qs = Recipe.objects.filter(name=g['name']).annotate(num_ing=Count('ingredients')).order_by('-num_ing', 'id')
            same_ids = list(same_qs.values_list('id', flat=True))
            if not same_ids:
                continue
            keep_id = same_ids[0]
            dup_ids = same_ids[1:]
            kept.append(keep_id)
            if dup_ids:
                Recipe.objects.filter(id__in=dup_ids).delete()
                removed.extend(dup_ids)

        # Delete duplicate recipes by same result material, keep the most complete (highest ingredient count), tie-breaker lowest id
        res_groups = (
            Recipe.objects.values('result_material')
            .annotate(c=Count('id'))
            .filter(c__gt=1)
        )
        for g in res_groups:
            same_qs = Recipe.objects.filter(result_material_id=g['result_material']).annotate(num_ing=Count('ingredients')).order_by('-num_ing', 'id')
            same_ids = list(same_qs.values_list('id', flat=True))
            if not same_ids:
                continue
            keep_id = same_ids[0]
            dup_ids = same_ids[1:]
            # Avoid deleting a recipe we already decided to keep by name
            dup_ids = [i for i in dup_ids if i not in kept]
            kept.append(keep_id)
            if dup_ids:
                Recipe.objects.filter(id__in=dup_ids).delete()
                removed.extend(dup_ids)

        # Return summary
        return Response({'removed_ids': sorted(set(removed)), 'kept_ids': sorted(set(kept))})

class PlayerWorkstationViewSet(viewsets.ModelViewSet):
    queryset = PlayerWorkstation.objects.all()
    serializer_class = PlayerWorkstationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        player = Player.objects.get(user=self.request.user)
        return PlayerWorkstation.objects.filter(player=player)

class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all().select_related('recipe', 'material')
    serializer_class = RecipeIngredientAdminSerializer

    def get_permissions(self):
        # Only admins can modify ingredients; allow read for authenticated users
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return [IsAdminUser()]
        return [IsAuthenticated()]

class CraftingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def craft(self, request):
        recipe_id = request.data.get('recipe_id')
        quantity = request.data.get('quantity', 1)
        player = request.user.player

        result, status_code = crafting_service.craft_recipe(player, recipe_id, quantity)
        return Response(result, status=status_code)

    @action(detail=False, methods=['post'])
    def install_workstation(self, request):
        material_id = request.data.get('material_id')
        player = request.user.player

        result, status_code = crafting_service.install_workstation(player, material_id)
        return Response(result, status=status_code)

    @action(detail=False, methods=['post'])
    def repair_tool(self, request):
        material_id = request.data.get('material_id')
        player = request.user.player

        result, status_code = crafting_service.repair_tool(player, material_id)
        return Response(result, status=status_code)

    @action(detail=False, methods=['post'])
    def build_workstation(self, request):
        """Build a workstation from a recipe"""
        # This logic was delegating to craft in the original view.
        # Since craft_recipe handles workstation building logic internally (check end of craft_recipe),
        # we can just call craft here too.
        return self.craft(request)
