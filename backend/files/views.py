from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.models import AnonymousUser
from .models import File
from .serializers import FileSerializer
from .services import FileSimilarityService
from django.db import models
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    queryset = File.objects.all()
    
    def get_queryset(self):
        logger.debug("Starting get_queryset")
        try:
            if isinstance(self.request.user, AnonymousUser):
                logger.debug("User is anonymous")
                if not self.request.session.exists(self.request.session.session_key):
                    logger.debug("Creating new session")
                    self.request.session.create()
                session_id = self.request.session.session_key
                logger.debug(f"Session ID: {session_id}")
                return File.objects.filter(session_id=session_id)
            logger.debug(f"User is authenticated: {self.request.user.id}")
            return File.objects.filter(user=self.request.user)
        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}", exc_info=True)
            return File.objects.none()

    def create(self, request, *args, **kwargs):
        logger.debug("Starting file upload")
        try:
            with transaction.atomic():
                # Create and validate serializer
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                
                # Save the file - duplicate checking happens in serializer
                file_instance = serializer.save()
                logger.debug(f"File processed successfully: {file_instance.id}")

                # Check if this was a duplicate (not created new)
                if hasattr(file_instance, '_created_new') and not file_instance._created_new:
                    logger.debug(f"Handling duplicate file response for: {file_instance.id}")
                    response_data = {
                        'file': FileSerializer(file_instance).data,
                        'is_duplicate': True,
                        'similarity': 1.0
                    }
                    logger.debug(f"Sending duplicate response: {response_data}")
                    return Response(response_data, status=status.HTTP_200_OK)

                # Return newly created file
                logger.debug("Handling new file response")
                response_data = FileSerializer(file_instance).data
                logger.debug(f"Sending new file response: {response_data}")
                return Response(
                    response_data,
                    status=status.HTTP_201_CREATED
                )

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Upload failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def storage_usage(self, request):
        """Get current storage usage for the user"""
        if isinstance(request.user, AnonymousUser):
            if not request.session.session_key:
                request.session.create()
            total_size = File.objects.filter(
                session_id=request.session.session_key
            ).aggregate(total=models.Sum('size'))['total'] or 0
        else:
            total_size = File.objects.filter(
                user=request.user
            ).aggregate(total=models.Sum('size'))['total'] or 0

        return Response({
            'used': total_size,
            'total': File.MAX_STORAGE_BYTES,
            'percentage': (total_size / File.MAX_STORAGE_BYTES) * 100
        })

    def perform_destroy(self, instance):
        """Override destroy to handle file deletion"""
        if instance.is_original:
            # Check if any other files reference this as original
            references = File.objects.filter(original_file=instance)
            if references.exists():
                # Make the most recent reference the new original
                new_original = references.order_by('-created_at').first()
                new_original.is_original = True
                new_original.original_file = None
                new_original.save()
                
                # Update other references
                references.exclude(pk=new_original.pk).update(
                    original_file=new_original
                )

        instance.file.delete()
        instance.delete()
