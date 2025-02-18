from rest_framework import serializers
from .models import File
import os

class FileSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    storage_path = serializers.SerializerMethodField()
    similarity_info = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            'id', 'file', 'original_filename', 'file_type', 'size',
            'created_at', 'updated_at', 'content_hash', 'is_original',
            'original_file', 'sequence_number', 'similarity_score',
            'display_name', 'storage_path', 'similarity_info'
        ]
        read_only_fields = [
            'content_hash', 'is_original', 'original_file',
            'sequence_number', 'similarity_score', 'display_name',
            'storage_path', 'similarity_info', 'original_filename',
            'file_type', 'size'
        ]

    def to_internal_value(self, data):
        """Handle file upload data before validation"""
        file_obj = data.get('file')
        if not file_obj:
            raise serializers.ValidationError({'file': 'No file was submitted'})

        # Add required fields from the file object
        data = data.copy()  # Make data mutable
        data['original_filename'] = file_obj.name
        data['file_type'] = file_obj.content_type
        data['size'] = file_obj.size

        return super().to_internal_value(data)

    def create(self, validated_data):
        """Handle file upload with pre-save duplicate checking"""
        from .models import calculate_file_hash
        from django.contrib.auth.models import AnonymousUser
        import logging

        logger = logging.getLogger(__name__)
        
        file_obj = validated_data.get('file')
        request = self.context.get('request')
        
        if not file_obj or not request:
            raise serializers.ValidationError("Invalid request data")

        # Ensure file metadata is set
        file_metadata = {
            'original_filename': file_obj.name,
            'file_type': file_obj.content_type,
            'size': file_obj.size
        }
        validated_data.update(file_metadata)

        # Calculate hash before saving
        content_hash = calculate_file_hash(file_obj)

        # Build query based on user or session
        if isinstance(request.user, AnonymousUser):
            if not request.session.session_key:
                request.session.create()
            query = {'session_id': request.session.session_key}
            validated_data['session_id'] = request.session.session_key
        else:
            query = {'user': request.user}
            validated_data['user'] = request.user

        # Check for existing duplicate
        existing_file = File.objects.filter(
            content_hash=content_hash,
            is_original=True,
            **query
        ).first()

        if existing_file:
            logger.info(f"Found duplicate file: {existing_file.id}")
            existing_file._created_new = False
            return existing_file

        # No duplicate found, proceed with save
        validated_data['content_hash'] = content_hash
        validated_data['is_original'] = True
        
        file_instance = super().create(validated_data)
        file_instance._created_new = True
        return file_instance

    def get_display_name(self, obj):
        """Get the display name for the file, including sequence number if needed"""
        if obj.sequence_number > 0:
            name, ext = os.path.splitext(obj.original_filename)
            return f"{name} ({obj.sequence_number}){ext}"
        return obj.original_filename

    def get_storage_path(self, obj):
        """Get the storage path for the file"""
        return obj.file.name if obj.file else None

    def get_similarity_info(self, obj):
        """Get similarity information if available"""
        if obj.similarity_score is not None and obj.original_file:
            return {
                'score': obj.similarity_score,
                'original_file': {
                    'id': obj.original_file.id,
                    'filename': obj.original_file.original_filename,
                    'created_at': obj.original_file.created_at
                }
            }
        return None 