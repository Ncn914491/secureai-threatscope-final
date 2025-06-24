# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to reduce image size
# Using --default-timeout to prevent pip hanging indefinitely
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Make port 8501 available to the world outside this container
# This is the default port for Streamlit applications
EXPOSE 8501

# Define environment variables that might be needed by the application
# These should be set during the `docker run` command or in the Cloud Run service configuration
# ENV GCP_PROJECT_ID="your-gcp-project-id"
# ENV GCP_REGION="your-gcp-region"
# ENV GCS_BUCKET_NAME="your-gcs-bucket-name"
# ENV GOOGLE_APPLICATION_CREDENTIALS="/app/path/to/your/serviceAccountKey.json"
# Note: For GOOGLE_APPLICATION_CREDENTIALS, the service account key file
# would need to be securely copied into the image or mounted,
# or preferably, use workload identity on Cloud Run.

# Healthcheck for Streamlit (optional but good practice for Cloud Run)
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#   CMD curl --fail http://localhost:8501/_stcore/health || exit 1
# Note: Streamlit's healthcheck endpoint might change or require specific configuration.
# As of now, /_stcore/health is common.

# Run secureai_streamlit.py when the container launches
# Use `streamlit run` and specify host and port for accessibility
# `--server.headless true` is recommended for deployments
CMD ["streamlit", "run", "secureai_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
