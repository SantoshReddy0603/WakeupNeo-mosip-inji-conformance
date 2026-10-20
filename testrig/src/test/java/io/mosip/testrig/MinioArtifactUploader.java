package io.mosip.testrig;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.PutObjectRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;

/**
 * Handles uploading test logs and ExtentReports to MinIO/S3 'automationtests' bucket.
 */
public class MinioArtifactUploader {
    private static final Logger logger = LoggerFactory.getLogger(MinioArtifactUploader.class);

    public static void uploadArtifact(String localFilePath, String s3Key) {
        String s3Endpoint = System.getenv("S3_ENDPOINT");
        String s3Bucket = System.getenv("S3_BUCKET");
        if (s3Bucket == null || s3Bucket.isEmpty()) {
            s3Bucket = "automationtests";
        }

        String accessKey = System.getenv("AWS_ACCESS_KEY_ID");
        String secretKey = System.getenv("AWS_SECRET_ACCESS_KEY");

        if (accessKey == null && secretKey == null) {
            logger.info("S3/MinIO credentials not provided. Skipping artifact upload for: {}", localFilePath);
            return;
        }

        if (accessKey == null || secretKey == null) {
            throw new IllegalStateException("Both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required");
        }

        try {
            AmazonS3ClientBuilder builder = AmazonS3ClientBuilder.standard()
                    .withCredentials(new AWSStaticCredentialsProvider(new BasicAWSCredentials(accessKey, secretKey)))
                    .withPathStyleAccessEnabled(true);

            if (s3Endpoint != null && !s3Endpoint.isEmpty()) {
                builder.withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(s3Endpoint, "us-east-1"));
            } else {
                builder.withRegion(System.getenv("AWS_REGION") == null ? "us-east-1" : System.getenv("AWS_REGION"));
            }

            AmazonS3 s3Client = builder.build();
            File fileToUpload = new File(localFilePath);
            if (!fileToUpload.exists()) {
                logger.warn("File to upload does not exist: {}", localFilePath);
                throw new IllegalStateException("Artifact missing: " + localFilePath);
            }

            if (!s3Client.doesBucketExistV2(s3Bucket)) {
                logger.info("Creating bucket: {}", s3Bucket);
                s3Client.createBucket(s3Bucket);
            }

            logger.info("Uploading artifact {} to s3://{}/{}", localFilePath, s3Bucket, s3Key);
            s3Client.putObject(new PutObjectRequest(s3Bucket, s3Key, fileToUpload));
            logger.info("Upload successful.");
            s3Client.shutdown();
        } catch (Exception ex) {
            throw new IllegalStateException("Configured S3 artifact upload failed", ex);
        }
    }
}
