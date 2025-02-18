from django.db import models
import uuid
import os
import hashlib
from django.core.exceptions import ValidationError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def file_upload_path(instance, filename):
    """Generate file path for new file upload"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

def calculate_file_hash(file):
    """Calculate SHA-256 hash of file"""
    sha256_hash = hashlib.sha256()
    for chunk in file.chunks():
        sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

class File(models.Model):
    CONTENT_TYPES = {
        'text': ['text/plain', 'text/csv', 'text/html'],
        'pdf': ['application/pdf'],
        'image': ['image/jpeg', 'image/png', 'image/gif']
    }
    
    MAX_STORAGE_BYTES = 250 * 1024 * 1024  # 250MB

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=file_upload_path)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    size = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User or session identification
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='files',
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Deduplication fields
    content_hash = models.CharField(max_length=64, db_index=True)
    is_original = models.BooleanField(default=True)
    original_file = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='duplicates'
    )
    reference_count = models.IntegerField(default=1)
    similarity_score = models.FloatField(null=True, blank=True)
    sequence_number = models.IntegerField(default=0)  # For duplicate naming
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_hash']),
            models.Index(fields=['user', 'original_filename']),
            models.Index(fields=['session_id', 'original_filename']),
        ]
    
    def __str__(self):
        return self.original_filename

    def clean(self):
        if not self.id:  # New file
            # Check storage quota
            if self.user:
                user_storage = File.get_user_storage(self.user)
            else:
                user_storage = File.get_session_storage(self.session_id)
            if user_storage + self.size > self.MAX_STORAGE_BYTES:
                logger.error(f"Storage quota exceeded. Current: {user_storage}, New: {self.size}")
                raise ValidationError("Storage quota exceeded")

    def save(self, *args, **kwargs):
        if not self.content_hash and self.file:
            self.content_hash = calculate_file_hash(self.file)
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        """Generate display name with sequence number if duplicate"""
        if self.sequence_number > 0:
            name, ext = os.path.splitext(self.original_filename)
            return f"{name}_{self.sequence_number}{ext}"
        return self.original_filename

    @classmethod
    def get_user_storage(cls, user):
        """Calculate total storage used by user"""
        return cls.objects.filter(
            user=user,
            is_original=True  # Only count original files
        ).aggregate(
            total=models.Sum('size')
        )['total'] or 0

    @classmethod
    def get_session_storage(cls, session_id):
        """Calculate total storage used by session"""
        return cls.objects.filter(
            session_id=session_id,
            is_original=True  # Only count original files
        ).aggregate(
            total=models.Sum('size')
        )['total'] or 0

    @property
    def storage_impact(self):
        """Calculate storage impact of this file"""
        if self.is_original:
            return self.size
        return 0  # Duplicates don't impact storage

    def get_content_type_category(self):
        """Get the category of the file (text, pdf, image)"""
        for category, types in self.CONTENT_TYPES.items():
            if self.file_type in types:
                return category
        return 'other'
