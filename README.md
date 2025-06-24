# SecureAI ThreatScope

SecureAI ThreatScope is a Streamlit application designed for threat intelligence analysis. It allows users to input logs or Indicators of Compromise (IOCs) and analyze them using either custom rule-based logic or Google's Gemini AI model via Vertex AI. The application features Firebase authentication and stores analysis history in Google Cloud Storage.

## Features

-   **User Authentication:** Secure login using Firebase Authentication.
-   **Dual Analysis Modes:**
    -   **Custom Rules:** Analyzes input based on predefined Python logic.
    -   **Gemini AI:** Leverages Google's Vertex AI Gemini Pro model for advanced threat analysis.
-   **Analysis History:** Stores all analysis results in a Google Cloud Storage bucket for persistence and review.
-   **Containerized Deployment:** Dockerfile provided for easy deployment on services like Google Cloud Run.

## Prerequisites

Before deploying and running this application, ensure you have the following:

1.  **Google Cloud Platform (GCP) Project:**
    -   A GCP project with billing enabled.
    -   APIs Enabled:
        -   Cloud Build API
        -   Cloud Run API
        -   Vertex AI API
        -   Secret Manager API (Recommended for future enhancements, though not strictly used for service account keys if using ADC or Cloud Run service identity)
        -   IAM API
    -   `gcloud` CLI installed and configured.

2.  **Firebase Project:**
    -   Create a Firebase project (can be linked to your GCP project).
    -   Enable Firebase Authentication (e.g., Email/Password).
    -   **Service Account Key:**
        -   The application uses the Firebase Admin SDK. This requires service account credentials.
        -   **Recommended:** Rely on Application Default Credentials (ADC) by running `gcloud auth application-default login` in your local environment, or by assigning appropriate IAM roles to the service account used by Cloud Run.
        -   Alternatively, you can provide a path to your service account JSON key file via the `FIREBASE_SERVICE_ACCOUNT_KEY_PATH` environment variable (less secure for Cloud Run).

3.  **Google Cloud Storage (GCS):**
    -   Create a GCS bucket in your GCP project to store analysis history.

4.  **Python Environment (for local development/understanding):**
    -   Python 3.9 or higher.
    -   `pip` for installing dependencies.

5.  **Docker (for containerization):**
    -   Docker installed if you plan to build and run the image locally or push to a registry.

## Configuration (Environment Variables)

The application is configured using environment variables. Create a `.env` file (copy from `.env.example`) for local development or set these directly in your Cloud Run service configuration.

-   `GCP_PROJECT_ID`: Your Google Cloud Project ID.
-   `GCP_REGION`: The GCP region for services like Vertex AI (e.g., `us-central1`).
-   `GCS_BUCKET_NAME`: The name of your GCS bucket for storing history.
-   `GOOGLE_APPLICATION_CREDENTIALS` (Optional, for local): Path to your GCP service account key JSON file if not using `gcloud auth application-default login`. For Cloud Run, prefer service identity.
-   `FIREBASE_SERVICE_ACCOUNT_KEY_PATH` (Optional, for local): Specific path to Firebase service account key if not using ADC or `GOOGLE_APPLICATION_CREDENTIALS`.

**Important Note on Firebase Authentication in `auth.py`:**
The current email/password login mechanism in `auth.py` using the Firebase Admin SDK is a **placeholder and NOT secure for production end-user authentication.** The Admin SDK is not designed for direct end-user password handling. For a production application, you should:
1.  Implement Firebase client-side authentication (e.g., using the Firebase JavaScript SDK in the frontend).
2.  Have the client send the ID token to the Streamlit backend.
3.  Verify the ID token on the backend using the Firebase Admin SDK.
This project provides the backend structure but would require frontend JavaScript integration for secure Firebase Web Auth.

## Local Development (Conceptual - Full functionality requires GCP setup)

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Set up Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    -   Create a `.env` file from `.env.example` and populate it with your GCP project details, GCS bucket name, etc.
    -   Ensure your GCP authentication is set up (e.g., `gcloud auth application-default login`).

5.  **Run the Streamlit application:**
    ```bash
    streamlit run secureai_streamlit.py
    ```
    The application will be accessible at `http://localhost:8501`.

## Deployment to Google Cloud Run

1.  **Ensure Prerequisites are met** (GCP Project, APIs, GCS Bucket, Firebase Project).

2.  **(Optional but Recommended) Create an Artifact Registry Docker repository:**
    ```bash
    gcloud artifacts repositories create secureai-repo \
        --repository-format=docker \
        --location=<your-gcp-region> \
        --description="Docker repository for SecureAI ThreatScope"
    ```
    Replace `<your-gcp-region>` with your desired region (e.g., `us-central1`).

3.  **Build the Docker image using Cloud Build and push to Artifact Registry:**
    ```bash
    gcloud builds submit --tag <your-gcp-region>-docker.pkg.dev/${GCP_PROJECT_ID}/secureai-repo/secureai-threatscope:latest .
    ```
    Replace `<your-gcp-region>` and ensure `GCP_PROJECT_ID` is set in your environment or replaced directly.

4.  **Deploy to Cloud Run:**
    ```bash
    gcloud run deploy secureai-threatscope-service \
        --image <your-gcp-region>-docker.pkg.dev/${GCP_PROJECT_ID}/secureai-repo/secureai-threatscope:latest \
        --platform managed \
        --region <your-gcp-region> \
        --allow-unauthenticated \ # For public access, or use --no-allow-unauthenticated and configure IAM
        --set-env-vars GCP_PROJECT_ID="<your-gcp-project-id>" \
        --set-env-vars GCP_REGION="<your-gcp-region>" \
        --set-env-vars GCS_BUCKET_NAME="<your-gcs-bucket-name-for-history>" \
        # --service-account <your-cloud-run-service-account-email> # Recommended
    ```
    -   Replace placeholders (`<...>`).
    -   **Service Account for Cloud Run:** It's highly recommended to run the Cloud Run service with a dedicated service account that has the necessary permissions:
        -   **Vertex AI User:** To access Gemini models.
        -   **Storage Object Admin (or finer-grained):** On the GCS bucket used for history.
        -   **Firebase-related permissions:** If using Firebase Admin SDK, the service account needs appropriate permissions (e.g., roles/firebase.admin or custom roles). Often, `roles/firebaseauth.userAdmin` might be relevant for user management tasks, but token verification itself typically doesn't require extensive Firebase roles if the SDK is just verifying.
        -   If you don't specify `--service-account`, Cloud Run uses the default Compute Engine service account, which might have overly broad permissions.

5.  **Access the application:** Once deployed, `gcloud` will provide the URL to access your application.

## Code Structure

-   `secureai_streamlit.py`: Main Streamlit application file.
-   `auth.py`: Handles Firebase authentication logic.
-   `history.py`: Manages loading and saving analysis history to GCS.
-   `gemini.py`: Interface for Vertex AI Gemini model analysis.
-   `rules.py`: Contains custom rule-based analysis logic.
-   `requirements.txt`: Python dependencies.
-   `Dockerfile`: For building the application container.
-   `.dockerignore`: Specifies files to exclude from the Docker image.
-   `.env.example`: Example environment variable configuration.

## Future Enhancements / Security Notes

-   **Secure Firebase Web Authentication:** Implement client-side Firebase JS for login and pass ID tokens to the backend for verification, instead of the current placeholder in `auth.py`.
-   **Secret Manager for Sensitive Configs:** While environment variables are good, for very sensitive parts of configuration (e.g., if you had API keys for other services), consider integrating Google Secret Manager.
-   **More Granular IAM:** Review and apply the principle of least privilege for all GCP service accounts and user roles.
-   **Input Validation & Sanitization:** Robustly validate and sanitize all user inputs.
-   **Comprehensive Testing:** Add unit and integration tests.
-   **CI/CD Pipeline:** Set up a CI/CD pipeline (e.g., using Cloud Build triggers) for automated builds and deployments.
-   **Custom Domain & SSL:** Configure a custom domain and managed SSL for the Cloud Run service.
-   **Cost Management:** Monitor GCP costs associated with Cloud Run, GCS, Vertex AI, and Firebase.
-   **Advanced Error Monitoring:** Integrate more advanced error reporting (e.g., Sentry, or GCP Error Reporting).
