import os
from difflib import SequenceMatcher
import PyPDF2
from PIL import Image
import imagehash
from django.core.files.storage import default_storage
from django.contrib.auth.models import AnonymousUser
from .models import File
import logging

logger = logging.getLogger(__name__)

class FileSimilarityService:
    SIMILARITY_THRESHOLD = 0.8  # 80% similarity threshold

    @staticmethod
    def get_text_similarity(file1_path, file2_path):
        """Compare two text files for similarity"""
        logger.debug(f"Comparing text files: {file1_path} and {file2_path}")
        try:
            with open(file1_path, 'r', encoding='utf-8') as f1, \
                 open(file2_path, 'r', encoding='utf-8') as f2:
                text1 = f1.read()
                text2 = f2.read()
                similarity = SequenceMatcher(None, text1, text2).ratio()
                logger.debug(f"Text similarity: {similarity}")
                return similarity
        except UnicodeDecodeError:
            logger.error("UnicodeDecodeError in text comparison")
            return 0.0
        except Exception as e:
            logger.error(f"Error comparing text files: {str(e)}", exc_info=True)
            return 0.0

    @staticmethod
    def get_pdf_similarity(file1_path, file2_path):
        """Compare two PDF files using metadata and basic content"""
        logger.debug(f"Comparing PDF files: {file1_path} and {file2_path}")
        try:
            pdf1 = PyPDF2.PdfReader(file1_path)
            pdf2 = PyPDF2.PdfReader(file2_path)

            # Compare number of pages
            if len(pdf1.pages) != len(pdf2.pages):
                logger.debug("PDFs have different number of pages")
                return 0.5

            # Compare metadata
            meta1 = pdf1.metadata or {}
            meta2 = pdf2.metadata or {}
            meta_similarity = SequenceMatcher(None, 
                str(meta1), str(meta2)).ratio()
            logger.debug(f"PDF metadata similarity: {meta_similarity}")
            return meta_similarity
        except Exception as e:
            logger.error(f"Error comparing PDF files: {str(e)}", exc_info=True)
            return 0.0

    @staticmethod
    def get_image_similarity(file1_path, file2_path):
        """Compare two images using perceptual hashing"""
        logger.debug(f"Comparing image files: {file1_path} and {file2_path}")
        try:
            img1 = Image.open(file1_path)
            img2 = Image.open(file2_path)

            hash1 = imagehash.average_hash(img1)
            hash2 = imagehash.average_hash(img2)

            # Convert hash difference to similarity ratio
            max_diff = 64  # Max possible difference for 8x8 hash
            diff = hash1 - hash2
            similarity = 1 - (diff / max_diff)
            logger.debug(f"Image similarity: {similarity}")
            return max(0, similarity)
        except Exception as e:
            logger.error(f"Error comparing image files: {str(e)}", exc_info=True)
            return 0.0

    @classmethod
    def check_similarity(cls, new_file, existing_file):
        """Check similarity between two files"""
        logger.debug(f"Checking similarity between {new_file.original_filename} and {existing_file.original_filename}")
        new_path = default_storage.path(new_file.file.name)
        existing_path = default_storage.path(existing_file.file.name)

        # If exact hash match, return 1.0
        if new_file.content_hash == existing_file.content_hash:
            logger.debug("Exact hash match found")
            return 1.0

        # Get file category
        category = new_file.get_content_type_category()
        logger.debug(f"File category: {category}")

        # Calculate similarity based on file type
        if category == 'text':
            similarity = cls.get_text_similarity(new_path, existing_path)
        elif category == 'pdf':
            similarity = cls.get_pdf_similarity(new_path, existing_path)
        elif category == 'image':
            similarity = cls.get_image_similarity(new_path, existing_path)
        else:
            logger.debug("Unsupported file type for similarity check")
            similarity = 0.0

        logger.debug(f"Final similarity score: {similarity}")
        return similarity

    @classmethod
    def find_similar_files(cls, new_file):
        """Find similar files for the given file"""
        logger.debug(f"Finding similar files for {new_file.original_filename}")
        logger.debug(f"File type: {new_file.file_type}")
        logger.debug(f"Content hash: {new_file.content_hash}")
        
        # Build query based on user or session
        if new_file.user:
            query = {'user': new_file.user}
            logger.debug(f"Searching for user: {new_file.user.id}")
        else:
            query = {'session_id': new_file.session_id}
            logger.debug(f"Searching for session: {new_file.session_id}")

        # First, check for exact hash matches
        logger.debug(f"Exact match query params: content_hash={new_file.content_hash}, is_original=True, query={query}")
        exact_matches = File.objects.filter(
            content_hash=new_file.content_hash,
            is_original=True,
            **query
        )
        
        # Log all found matches for debugging
        logger.debug(f"Number of exact matches found: {exact_matches.count()}")
        for match in exact_matches:
            logger.debug(f"Match found - ID: {match.id}, Filename: {match.original_filename}, Session: {match.session_id}, Hash: {match.content_hash}")
        
        if exact_matches.exists():
            match = exact_matches.first()
            logger.debug(f"Found exact match: {match.original_filename}")
            logger.debug(f"Match details - Session: {match.session_id}, Hash: {match.content_hash}")
            return {
                'file': match,
                'similarity': 1.0,
                'is_exact': True
            }

        # Check for similar files
        similar_files = []
        try:
            category = new_file.get_content_type_category()
            logger.debug(f"Checking files of category: {category}")
            potential_matches = File.objects.filter(
                is_original=True,
                file_type__in=File.CONTENT_TYPES[category],
                **query
            )
        except KeyError:
            logger.error(f"Invalid category: {category}")
            return None
        except Exception as e:
            logger.error(f"Error finding similar files: {str(e)}", exc_info=True)
            return None

        for existing_file in potential_matches:
            similarity = cls.check_similarity(new_file, existing_file)
            if similarity >= cls.SIMILARITY_THRESHOLD:
                logger.debug(f"Found similar file: {existing_file.original_filename} with score {similarity}")
                similar_files.append({
                    'file': existing_file,
                    'similarity': similarity,
                    'is_exact': False
                })

        # Return the most similar file if any
        if similar_files:
            most_similar = max(similar_files, key=lambda x: x['similarity'])
            logger.debug(f"Most similar file: {most_similar['file'].original_filename}")
            return most_similar

        logger.debug("No similar files found")
        return None

    @classmethod
    def handle_duplicate_name(cls, filename, user=None, session_id=None):
        """Generate appropriate sequence number for duplicate filename"""
        name, ext = os.path.splitext(filename)
        
        # Build query based on user or session
        if user:
            query = {'user': user}
        else:
            query = {'session_id': session_id}

        existing_files = File.objects.filter(
            original_filename__startswith=name,
            **query
        ).order_by('-sequence_number')

        if not existing_files.exists():
            return 0

        return existing_files.first().sequence_number + 1 