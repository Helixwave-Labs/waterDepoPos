import logging
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.region_name = settings.S3_REGION
        self.access_key = settings.S3_ACCESS_KEY_ID or settings.R2_ACCESS_KEY_ID
        self.secret_key = settings.S3_SECRET_ACCESS_KEY or settings.R2_SECRET_ACCESS_KEY
        self.bucket_name = settings.S3_BUCKET_NAME
        self.public_domain = settings.S3_PUBLIC_DOMAIN or settings.R2_PUBLIC_DOMAIN

        if not self.endpoint_url or not self.access_key or not self.secret_key:
            logger.warning("S3/R2 storage configuration is missing. Image uploads will fail.")

        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name,
        )

    def upload_image(self, file: UploadFile, file_name: str) -> str:
        """
        Uploads an image to S3/R2 Storage and returns the public URL.
        """
        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                file_name,
                ExtraArgs={"ContentType": file.content_type},
            )

            # Construct the public URL.
            # For R2, this is typically https://<public_domain>/<file_name>
            if self.public_domain:
                domain = self.public_domain.rstrip("/")
                public_url = f"{domain}/{file_name}"
            else:
                # Fallback if no public domain is configured (likely won't work for private R2 buckets)
                public_url = f"{self.endpoint_url}/{self.bucket_name}/{file_name}"

            return public_url

        except ClientError as e:
            logger.error(f"Failed to upload image to S3/R2: {e}")
            raise e

    def delete_image(self, file_url: str) -> None:
        """
        Deletes an image from S3/R2 Storage given its public URL.
        """
        if not file_url:
            return

        try:
            # Extract file name from URL (assumes filename is the last part of the URL)
            file_name = file_url.split("/")[-1]

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_name
            )
        except ClientError as e:
            logger.error(f"Failed to delete image from S3/R2: {e}")
            # We log the error but do not raise it, so the product deletion can proceed