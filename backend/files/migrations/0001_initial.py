from django.db import migrations, models
import django.db.models.deletion
import uuid
from files.models import file_upload_path

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('file', models.FileField(upload_to=file_upload_path)),
                ('original_filename', models.CharField(max_length=255)),
                ('file_type', models.CharField(max_length=100)),
                ('size', models.BigIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session_id', models.CharField(blank=True, max_length=100, null=True)),
                ('content_hash', models.CharField(db_index=True, max_length=64)),
                ('is_original', models.BooleanField(default=True)),
                ('reference_count', models.IntegerField(default=1)),
                ('similarity_score', models.FloatField(blank=True, null=True)),
                ('sequence_number', models.IntegerField(default=0)),
                ('original_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='duplicates', to='files.file')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['content_hash'], name='files_file_content_idx'),
                    models.Index(fields=['user', 'original_filename'], name='files_file_user_idx'),
                    models.Index(fields=['session_id', 'original_filename'], name='files_file_session_idx'),
                ],
            },
        ),
    ] 