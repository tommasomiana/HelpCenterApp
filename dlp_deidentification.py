import google.cloud.dlp
import mimetypes
import os

# you need a json file with your gcp credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= os.path.dirname(__file__) + "/tommisac.json"

# put the id of your project here
PROJECT_NAME = "sac-pw2-138078"
DLP = google.cloud.dlp_v2.DlpServiceClient()
# Convert the project id into a full resource id.
PARENT = DLP.project_path(PROJECT_NAME)

def deidentify_string_with_mask(string, info_types):
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    string by masking it with its infoType.
    Args:
        string: The string to deidentify (will be treated as text).
        info_types: infoTypes which has to be searched and masked in the string.
    Returns:
        The deidentified string.
    """

    # Construct inspect configuration dictionary
    inspect_config = {
        "info_types": [{"name": info_type} for info_type in info_types]
    }

    # Construct deidentify configuration dictionary
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [
                {
                    "primitive_transformation": {
                        "replace_with_info_type_config": {}
                    }
                }
            ]
        }
    }

    # Construct item
    item = {"value": string}

    # Call the API
    response = DLP.deidentify_content(
        PARENT,
        inspect_config=inspect_config,
        deidentify_config=deidentify_config,
        item=item,
    )

    # Print out the results
    return response.item.value
    

def deidentify_image_with_mask(filename, info_types):
    """Uses the Data Loss Prevention API to redact protected data in an image.
    Args:
        filename: The absolte filename of the image to deidentify.
        info_types: infoTypes which has to be searched and redacted in the image.
    Returns:
        findings: as a list of string descripting all the infoTypes found in the image.
        redacted_image: as the absolut filename of the redacted file.
    """

    # A match will be considered valid if has at least a likelihood of POSSIBLE
    min_likelihood='POSSIBLE'

    # Prepare info_types by converting the list of strings into a list of dictionaries
    info_types = [{"name": info_type} for info_type in info_types]

    # Prepare image_redaction_configs, a list of dictionaries. Each dictionary
    # contains an info_type and optionally the color used for the replacement.
    # The color is omitted in this sample, so the default (black) will be used.
    image_redaction_configs = []

    for info_type in info_types:
            image_redaction_configs.append({"info_type": info_type})

    # Construct the configuration dictionary
    inspect_config = {
        "min_likelihood": min_likelihood,
        "info_types": info_types,
        "include_quote": True
    }

    # Guess mime type from the filename.
    mime_guess = mimetypes.MimeTypes().guess_type(filename)
    mime_type = mime_guess[0] or "application/octet-stream"

    # Select the content type index from the list of supported types.
    supported_content_types = {
        None: 0,  # "Unspecified"
        "image/jpeg": 1,
        "image/bmp": 2,
        "image/png": 3,
        "image/svg": 4,
        "text/plain": 5,
    }
    content_type_index = supported_content_types.get(mime_type, 0)

    # Construct the byte_item, containing the file's byte data.
    with open(filename, mode="rb") as f:
        byte_item = {"type": content_type_index, "data": f.read()}

    # Call the API.
    response = DLP.redact_image(
        PARENT,
        inspect_config=inspect_config,
        image_redaction_configs=image_redaction_configs,
        byte_item=byte_item,
        include_findings=True,
    )

    # Write out the results
    output_filename = f"redacted_{filename.split('/')[-1]}"
    output_filename = os.path.join(os.path.dirname(__file__), 'uploads', output_filename)
    findings = []
    for finding in response.inspect_result.findings:
        findings.append(f"infoType: {finding.info_type.name}, quote: {finding.quote}, likelihood: {finding.likelihood}\n")
    with open(output_filename, mode="wb") as f:
        f.write(response.redacted_image)
    return findings, output_filename
