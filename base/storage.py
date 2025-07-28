from storages.backends.s3boto3 import S3Boto3Storage

class CloudflareStaticStorage(S3Boto3Storage):
    bucket_name = 'mzansiplug-bucket'
    location = 'static'
    endpoint_url = 'https://static.mzansiplug.com'

    def url(self, name, parameters=None, expire=None):
        # build URL without bucket name in path
        url = f"{self.endpoint_url}/{self.location}/{name}"
        # optionally add parameters if needed
        return url
