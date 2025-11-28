from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from PIL import Image
from io import BytesIO

@api_view(['POST'])
@permission_classes([IsAdminUser])
def upload_icon(request):
    """Upload an icon image and return the URL"""
    if 'image' not in request.FILES:
        return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    image_file = request.FILES['image']
    
    # Validate image
    try:
        img = Image.open(image_file)
        img.verify()
    except Exception:
        return Response({'error': 'Invalid image file'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Reopen image (verify() closes it)
    img = Image.open(image_file)
    
    # Resize to icon size (64x64) to save space
    img.thumbnail((64, 64), Image.Resampling.LANCZOS)
    
    # Convert to RGB if necessary (for PNG with transparency)
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    
    # Save to BytesIO
    output = BytesIO()
    img.save(output, format='PNG', optimize=True)
    output.seek(0)
    
    # Generate unique filename
    filename = f'icons/{uuid.uuid4()}.png'
    
    # Save to media folder
    path = default_storage.save(filename, ContentFile(output.read()))
    
    # Return URL
    url = request.build_absolute_uri(default_storage.url(path))
    
    return Response({'url': url, 'path': path}, status=status.HTTP_201_CREATED)
