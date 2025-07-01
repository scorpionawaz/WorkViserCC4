import uuid
from fastapi import UploadFile, HTTPException
import boto3
from app.config.amazon_s3_config import settings

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf", "docx"}

s3 = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

def upload_to_s3(file: UploadFile) -> str:
    file_extension = file.filename.split('.')[-1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    contents = file.file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File size exceeds limit")

    file.file.seek(0)  

    filename = f"{uuid.uuid4()}.{file_extension}"

    try:
        s3.upload_fileobj(
            file.file,
            settings.AWS_BUCKET_NAME,
            filename,
            ExtraArgs={"ACL": "public-read"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="S3 upload failed: " + str(e))

    file_url = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{filename}"
    return file_url



#example usage:- @router.post("/upload")
# async def upload(file: UploadFile = File(...)):
#     file_url = upload_to_s3(file)
#     return {"file_url": file_url}