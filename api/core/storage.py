"""Storage utilities for file uploads."""
import os
import uuid
from io import BytesIO
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException
from api.config import settings

# Initialize MinIO client
minio_endpoint = settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
minio_client = Minio(
    endpoint=minio_endpoint,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_ENDPOINT.startswith("https://")
)

# Ensure bucket exists
AVATARS_BUCKET = "avatars"
try:
    if not minio_client.bucket_exists(bucket_name=AVATARS_BUCKET):
        minio_client.make_bucket(bucket_name=AVATARS_BUCKET)
    
    # Always ensure public read policy
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{AVATARS_BUCKET}/*"]
            }
        ]
    }
    import json
    minio_client.set_bucket_policy(bucket_name=AVATARS_BUCKET, policy=json.dumps(policy))
        
except S3Error as e:
    print(f"Error configuring bucket: {e}")


async def upload_avatar(file: UploadFile, user_id: str) -> str:
    """
    Upload user avatar to MinIO storage.
    
    Args:
        file: The uploaded file
        user_id: User ID for organizing files
        
    Returns:
        str: The URL to access the uploaded file
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Validate file size (5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{user_id}/{uuid.uuid4()}.{file_extension}"
    
    try:
        # Upload to MinIO
        minio_client.put_object(
            bucket_name=AVATARS_BUCKET,
            object_name=filename,
            data=BytesIO(contents),
            length=len(contents),
            content_type=file.content_type
        )
        
        # Return public URL
        protocol = "https" if settings.MINIO_SECURE else "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{AVATARS_BUCKET}/{filename}"
    
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


def delete_avatar(avatar_url: str):
    """Delete avatar from MinIO storage."""
    if not avatar_url or AVATARS_BUCKET not in avatar_url:
        return
    
    try:
        # Extract filename from URL
        filename = avatar_url.split(f"/{AVATARS_BUCKET}/")[1]
        minio_client.remove_object(bucket_name=AVATARS_BUCKET, object_name=filename)
    except Exception as e:
        print(f"Error deleting avatar: {e}")


# Ensure banners bucket exists
BANNERS_BUCKET = "banners"
try:
    if not minio_client.bucket_exists(bucket_name=BANNERS_BUCKET):
        minio_client.make_bucket(bucket_name=BANNERS_BUCKET)
    
    # Always ensure public read policy
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{BANNERS_BUCKET}/*"]
            }
        ]
    }
    import json
    minio_client.set_bucket_policy(bucket_name=BANNERS_BUCKET, policy=json.dumps(policy))
        
except S3Error as e:
    print(f"Error configuring banners bucket: {e}")


async def upload_banner(file: UploadFile, user_id: str) -> str:
    """
    Upload user banner to MinIO storage.
    
    Args:
        file: The uploaded file
        user_id: User ID for organizing files
        
    Returns:
        str: The URL to access the uploaded file
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Validate file size (10MB for banners)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{user_id}/{uuid.uuid4()}.{file_extension}"
    
    try:
        # Upload to MinIO
        minio_client.put_object(
            bucket_name=BANNERS_BUCKET,
            object_name=filename,
            data=BytesIO(contents),
            length=len(contents),
            content_type=file.content_type
        )
        
        # Return public URL
        protocol = "https" if settings.MINIO_SECURE else "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{BANNERS_BUCKET}/{filename}"
    
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


def delete_banner(banner_url: str):
    """Delete banner from MinIO storage."""
    if not banner_url or BANNERS_BUCKET not in banner_url:
        return
    
    try:
        # Extract filename from URL
        filename = banner_url.split(f"/{BANNERS_BUCKET}/")[1]
        minio_client.remove_object(bucket_name=BANNERS_BUCKET, object_name=filename)
    except Exception as e:
        print(f"Error deleting banner: {e}")
