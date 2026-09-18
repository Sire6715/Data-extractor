import json
import logging
import tempfile
import time
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, Timeout

logger = logging.getLogger(__name__)


class RestAccess:
    """
    Handles authentication and communication with the Kaggle REST API.
    """

    def __init__(self, credentials, username=None):
        """
        Authenticate with the Kaggle REST API.
        
        Args:
            credentials: Path to credentials file (JSON or raw token file).
            username: Required when using raw token file (ignored for JSON).
        
        Returns:
            None
        
        Raises:
            FileNotFoundError: If credentials file doesn't exist.
            json.JSONDecodeError: If JSON file is malformed.
            KeyError: If required fields missing from JSON file.
            ValueError: If invalid config (missing username, empty token, etc.).
        """
        self.credentials = Path(credentials)

        try:
            if self.credentials.suffix == ".json":
                with self.credentials.open("r", encoding="utf-8") as file:
                    data = json.load(file)

                kaggle_username = data["username"]
                kaggle_key = data["key"]

                logger.info("Loaded Kaggle credentials from JSON file.")

            else:
                if username is None:
                    raise ValueError(
                        "username is required when using a raw access token file."
                    )

                with self.credentials.open("r", encoding="utf-8") as file:
                    kaggle_key = file.read().strip()

                if not kaggle_key:
                    raise ValueError("Access token file is empty.")

                kaggle_username = username

                logger.info("Loaded Kaggle credentials from token file.")

            self.auth = HTTPBasicAuth(kaggle_username, kaggle_key)

        except FileNotFoundError: 
            logger.exception("Credentials file not found: %s.", self.credentials)
            raise

        except json.JSONDecodeError:
            logger.exception("Malformed JSON credentials file: %s", self.credentials)
            raise

        except KeyError as error:
            logger.exception("Missing required field in JSON file: %s", error)
            raise

        except ValueError:
            logger.exception("Invalid credentials configuration.")
            raise


    def get_zip(self, url, max_retries=3):
        """Download a ZIP archive from URL, retrying on HTTP 429 rate limits.
        
        Args:
            url: URL to download the ZIP archive from.
            max_retries: Maximum number of retry attempts (default: 3).
        
        Returns:
            Path: Path to the downloaded temporary ZIP file.
        
        Raises:
            ConnectionError: If network connection fails.
            Timeout: If request times out.
            requests.HTTPError: For HTTP errors (401, 404, etc.) or too many retries.
        """
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(
                    url, auth=self.auth, timeout=30, stream=True
                )

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(
                        "Rate limited (attempt %d/%d). Retrying in %s seconds...",
                        attempt,
                        max_retries,
                        retry_after,3
                    )
                    time.sleep(retry_after)
                    continue  

                if response.status_code == 401:
                    logger.error("Authentication failed (HTTP 401).")
                    response.raise_for_status()

                if response.status_code == 404:
                    logger.error("Dataset not found: %s", url)
                    response.raise_for_status()

                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".zip"
                ) as temp_file:
                    zip_path = Path(temp_file.name)

                with zip_path.open("wb") as out:
                    for chunk in response.iter_content(chunk_size=8192):
                        out.write(chunk)

                logger.info("ZIP archive downloaded to %s", zip_path)
                return zip_path

            except (ConnectionError, Timeout):
                logger.exception("Network failure while downloading ZIP archive.")
                raise

            except requests.HTTPError:
                logger.exception("HTTP error while downloading ZIP archive.")
                raise

        logger.error("Exceeded %d retries for URL: %s", max_retries, url)
        raise requests.HTTPError(f"Too many retries ({max_retries}) for {url}")
        
        
    def dataset_iter(self, url, query):
        """Iterate over paginated dataset results from Kaggle API.
        
        Args:
            url: Kaggle API endpoint URL for dataset search.
            query: Dictionary of query parameters (search terms, filters, etc.).
        
        Yields:
            dict: Individual dataset records from each page of results.
        
        Raises:
            ConnectionError: If network connection fails.
            Timeout: If request times out.
            ValueError: If response JSON parsing fails.
        """
        page = 1
        
        while True:
            params = {**query, "page": page}

            try:
                response = requests.get(
                    url, params=params, auth=self.auth, timeout=30
                )
            except (ConnectionError, Timeout):
                logger.exception(
                    "Network failure fetching page %d of dataset list.", page
                )
                raise
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                
                logger.warning(
                    "Rate limited on page %d. Retrying in %d seconds(s)...",
                    page,
                    retry_after,
                )
                time.sleep(retry_after)
                continue
            
            
            if response.status_code != 200:
                logger.error(
                    "Unexpected HTTP %d on page %d. Body: %s",
                    response.status_code,
                    page,
                    response.text[:500],
                )
                
                break
            
            try:
                rows = response.json()
            except ValueError:
                logger.exception("Failed to parse JSON response on page %d.", page)
                raise
            
            if not rows:
                break 
            
            yield from rows
            
            page += 1