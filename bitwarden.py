import subprocess
import json
import re
import os
import shutil
from pathlib import Path

# Global API credentials
BW_CLIENT_ID = ""
BW_CLIENT_SECRET = ""
MASTER_PASSWORD = ""

# Environment variable name for session token
BW_SESSION_ENV_VAR = "BW_SESSION_TOKEN"


def find_bw_executable():
    """Find Bitwarden CLI executable across different systems."""

    # List of possible locations to check
    possible_paths = [
        'bw',  # If it's in PATH
        'bw.cmd',  # Windows command
        'bw.exe',  # Windows executable
    ]

    # Add common installation paths
    if os.name == 'nt':  # Windows
        # Get current user's npm directory
        user_profile = os.environ.get('USERPROFILE', '')
        if user_profile:
            npm_path = os.path.join(user_profile, 'AppData', 'Roaming', 'npm', 'bw.cmd')
            possible_paths.append(npm_path)

        # Common Windows paths
        possible_paths.extend([
            r'C:\Program Files\Bitwarden CLI\bw.exe',
            r'C:\Program Files (x86)\Bitwarden CLI\bw.exe',
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\WindowsApps\\bw.exe'),
            os.path.expanduser('~\\AppData\\Roaming\\npm\\bw.cmd'),
        ])
    else:  # Linux/macOS
        possible_paths.extend([
            '/usr/local/bin/bw',
            '/usr/bin/bw',
            os.path.expanduser('~/.local/bin/bw'),
            '/snap/bin/bw',  # Snap package on Linux
        ])

    # First, try using shutil.which() to find bw in PATH
    bw_in_path = shutil.which('bw')
    if bw_in_path:
        try:
            result = subprocess.run([bw_in_path, '--version'],
                                    capture_output=True, text=True, check=True, timeout=10)
            print(f"✅ Found Bitwarden CLI in PATH: {bw_in_path}")
            print(f"   Version: {result.stdout.strip()}")
            return bw_in_path
        except Exception as e:
            print(f"⚠️ Found bw in PATH but couldn't verify: {e}")

    # If not found in PATH, try each possible location
    for path in possible_paths:
        if not path or path in ['bw', 'bw.cmd', 'bw.exe']:  # Skip generic names we already tried
            continue

        try:
            # Check if file exists first
            if os.path.exists(path):
                result = subprocess.run([path, '--version'],
                                        capture_output=True, text=True, check=True, timeout=10)
                print(f"✅ Found Bitwarden CLI at: {path}")
                print(f"   Version: {result.stdout.strip()}")
                return path
        except Exception as e:
            continue  # Try next path

    # If still not found, provide helpful error message
    print("❌ Bitwarden CLI not found!")
    print("Please install Bitwarden CLI:")
    if os.name == 'nt':  # Windows
        print("  - npm install -g @bitwarden/cli")
        print("  - Or download from: https://bitwarden.com/download/")
        print("  - Or use: winget install Bitwarden.CLI")
    else:  # Linux/macOS
        print("  - npm install -g @bitwarden/cli")
        print("  - Or download from: https://bitwarden.com/download/")
        print("  - Or use package manager (brew install bitwarden-cli, apt install bitwarden-cli, etc.)")

    return None


def get_cached_session_token():
    """Get session token from environment variable if it exists."""
    # First check in process environment
    token = os.environ.get(BW_SESSION_ENV_VAR)
    
    # If not found in process environment, try to get from system environment
    if not token and os.name == 'nt':  # Windows
        try:
            # Use PowerShell to get system environment variable
            result = subprocess.run(
                ['powershell', '-Command', f'[Environment]::GetEnvironmentVariable("{BW_SESSION_ENV_VAR}", "User")'],
                capture_output=True, 
                text=True,
                check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                token = result.stdout.strip()
                # Set in current process too
                os.environ[BW_SESSION_ENV_VAR] = token
        except Exception as e:
            print(f"⚠️ Error checking system environment: {e}")
    
    if token:
        print(f"🔄 Found cached session token in environment variable")
        return token
    
    print("ℹ️ No cached session token found, will need to create a new one")
    return None


def set_session_token_cache(session_token):
    """Set session token as environment variable for current process and future use."""
    if not session_token:
        print("⚠️ Attempted to cache empty token - ignoring")
        return
        
    # Store in process environment
    os.environ[BW_SESSION_ENV_VAR] = session_token
    
    # Also try to persist the token for future runs
    try:
        # For Windows
        if os.name == 'nt':
            # Use setx for normal persistence
            subprocess.run(['setx', BW_SESSION_ENV_VAR, session_token], 
                          capture_output=True, check=False)
            
            # Additionally use PowerShell for better persistence (system-wide)
            try:
                ps_cmd = f'[Environment]::SetEnvironmentVariable("{BW_SESSION_ENV_VAR}", "{session_token}", "User")'
                subprocess.run(['powershell', '-Command', ps_cmd], 
                              capture_output=True, check=False)
            except Exception as e:
                print(f"⚠️ PowerShell environment setting failed: {e}")
                
            print(f"💾 Session token cached in environment variable and persisted for future sessions: {BW_SESSION_ENV_VAR}")
        # For Linux/macOS
        else:
            home = os.path.expanduser("~")
            shell_profiles = [
                os.path.join(home, '.bashrc'),
                os.path.join(home, '.bash_profile'),
                os.path.join(home, '.zshrc')
            ]
            
            for profile in shell_profiles:
                if os.path.exists(profile):
                    with open(profile, 'r') as f:
                        content = f.read()
                    
                    # Remove existing export if present
                    if f'export {BW_SESSION_ENV_VAR}=' in content:
                        lines = content.split('\n')
                        filtered_lines = [line for line in lines if not line.startswith(f'export {BW_SESSION_ENV_VAR}=')]
                        content = '\n'.join(filtered_lines)
                    
                    # Add new export at the end
                    with open(profile, 'w') as f:
                        f.write(content)
                        if not content.endswith('\n'):
                            f.write('\n')
                        f.write(f'export {BW_SESSION_ENV_VAR}="{session_token}"\n')
                    
                    print(f"💾 Session token cached and persisted in {profile}")
                    break
    except Exception as e:
        print(f"⚠️ Could not persist token for future sessions: {e}")
        print(f"💾 Session token cached in memory for current process only: {BW_SESSION_ENV_VAR}")


def clear_session_token_cache():
    """Clear cached session token from environment."""
    if BW_SESSION_ENV_VAR in os.environ:
        del os.environ[BW_SESSION_ENV_VAR]
        print(f"🗑️ Cleared cached session token from current process")
        
    # Also try to remove from persistent storage
    try:
        # For Windows
        if os.name == 'nt':
            # Use setx to clear variable
            subprocess.run(['setx', BW_SESSION_ENV_VAR, ''], 
                          capture_output=True, check=False)
            
            # Additionally use PowerShell for thorough cleanup
            try:
                ps_cmd = f'[Environment]::SetEnvironmentVariable("{BW_SESSION_ENV_VAR}", $null, "User")'
                subprocess.run(['powershell', '-Command', ps_cmd], 
                              capture_output=True, check=False)
            except Exception as e:
                print(f"⚠️ PowerShell environment clearing failed: {e}")
                
            print(f"🗑️ Removed persistent session token from system environment")
        # For Linux/macOS
        else:
            home = os.path.expanduser("~")
            shell_profiles = [
                os.path.join(home, '.bashrc'),
                os.path.join(home, '.bash_profile'),
                os.path.join(home, '.zshrc')
            ]
            
            for profile in shell_profiles:
                if os.path.exists(profile):
                    with open(profile, 'r') as f:
                        content = f.read()
                    
                    # Remove existing export if present
                    if f'export {BW_SESSION_ENV_VAR}=' in content:
                        lines = content.split('\n')
                        filtered_lines = [line for line in lines if not line.startswith(f'export {BW_SESSION_ENV_VAR}=')]
                        with open(profile, 'w') as f:
                            f.write('\n'.join(filtered_lines))
                            if filtered_lines and not filtered_lines[-1].endswith('\n'):
                                f.write('\n')
                        print(f"🗑️ Removed persistent session token from {profile}")
                    break
    except Exception as e:
        print(f"⚠️ Could not remove persistent token: {e}")


def is_session_valid(session_token, bw_path='bw'):
    """Check if the current session token is still valid."""
    if not session_token:
        print("❌ No session token provided to validate")
        return False

    try:
        print(f"🔍 Validating session token...")
        
        # Try a simple operation that requires authentication
        result = subprocess.run(
            [bw_path, 'status', '--session', session_token],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            status_data = json.loads(result.stdout)
            if status_data.get('status') == 'unlocked':
                print("✅ Session token is valid and vault is unlocked")
                return True
            else:
                print(f"⚠️ Vault is not unlocked. Current status: {status_data.get('status', 'unknown')}")
                
                # Try a more definitive test - list items
                try:
                    list_result = subprocess.run(
                        [bw_path, 'list', 'items', '--search', 'test', '--session', session_token],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if list_result.returncode == 0:
                        print("✅ Session token is valid (successfully listed items)")
                        return True
                    else:
                        print(f"❌ Session token validation failed on item list test")
                        return False
                except Exception as e:
                    print(f"❌ Error during secondary validation: {e}")
                    return False
        
        print(f"⚠️ Session token appears invalid or expired. Return code: {result.returncode}")
        if result.stderr:
            print(f"   Error: {result.stderr}")
        return False

    except json.JSONDecodeError:
        print(f"⚠️ Invalid JSON response when validating token")
        return False
    except Exception as e:
        print(f"⚠️ Error validating session token: {e}")
        return False


def logout(bw_path: str = 'bw'):
    """Logs out of the Bitwarden session."""
    try:
        subprocess.run([bw_path, 'logout'], capture_output=True, text=True, timeout=10)
        print("✅ Successfully logged out.")
        clear_session_token_cache()
    except Exception as e:
        print(f"⚠️ Logout note: {e}")


def get_bw_session(bw_path: str = 'bw', force_new=False) -> str:
    """Get Bitwarden session using API key authentication and master password."""
    
    print("🔍 Looking for existing session token...")

    # Check for cached session token first (unless forcing new session)
    if not force_new:
        cached_token = get_cached_session_token()
        if cached_token:
            print("🔍 Validating cached session token...")
            if is_session_valid(cached_token, bw_path):
                print("🔐 Using valid cached session token")
                return cached_token
            else:
                print("🔄 Cached session token expired or invalid, obtaining new one...")
                clear_session_token_cache()
        else:
            print("🔑 No valid session token found, creating new one...")
    else:
        print("🔄 Forcing creation of new session token as requested...")
        clear_session_token_cache()

    try:
        print(f"🚀 Starting authentication process...")

        # First, logout if already logged in (to clean state)
        try:
            subprocess.run([bw_path, 'logout'], capture_output=True, text=True, timeout=10)
            print("🔄 Logged out of any existing sessions")
        except:
            pass

        # Set environment variables temporarily for this subprocess only
        env = os.environ.copy()
        env['BW_CLIENTID'] = BW_CLIENT_ID
        env['BW_CLIENTSECRET'] = BW_CLIENT_SECRET

        # Login with API key using environment variables
        print("🔑 Logging in with API key...")
        result = subprocess.run(
            [bw_path, 'login', '--apikey'],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )

        if result.returncode != 0:
            print(f"❌ API key login failed: {result.stderr}")
            # Try alternative login method
            print("🔄 Trying alternative login method...")

            try:
                result = subprocess.run(
                    [bw_path, 'login', '--apikey', '--raw'],
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=30
                )

                if result.returncode != 0:
                    print(f"❌ Alternative login also failed: {result.stderr}")
                    return None
            except:
                print("❌ Alternative login method failed")
                return None

        print("✅ API key login successful!")

        # Check if we're already unlocked
        try:
            status_result = subprocess.run(
                [bw_path, 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )
            status_data = json.loads(status_result.stdout)
            if status_data.get('status') == 'unlocked':
                session_key = status_data.get('sessionKey', '')
                if session_key:
                    print("✅ Vault is already unlocked!")
                    set_session_token_cache(session_key)
                    return session_key
        except:
            pass

        # Now unlock with master password to get session token
        print("🔓 Unlocking vault with master password...")

        # Try unlock with password via environment variable
        env['BW_PASSWORD'] = MASTER_PASSWORD
        unlock_result = subprocess.run(
            [bw_path, 'unlock', '--passwordenv', 'BW_PASSWORD', '--raw'],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )

        if unlock_result.returncode == 0:
            session_token = unlock_result.stdout.strip()
            print("✅ Session token obtained!")
            set_session_token_cache(session_token)
            return session_token
        else:
            # Try alternative unlock method
            print("🔄 Trying alternative unlock method...")
            unlock_result = subprocess.run(
                [bw_path, 'unlock', '--raw'],
                capture_output=True,
                text=True,
                input=f"{MASTER_PASSWORD}\n",
                timeout=30
            )

            if unlock_result.returncode == 0:
                session_token = unlock_result.stdout.strip()
                print("✅ Session token obtained!")
                set_session_token_cache(session_token)
                return session_token
            else:
                print(f"❌ Failed to unlock vault: {unlock_result.stderr}")
                return None

    except subprocess.TimeoutExpired:
        print("❌ Operation timed out")
        return None
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return None


def sync_vault(session_token: str, bw_path: str = 'bw'):
    """Syncs the Bitwarden vault to get the latest data."""
    try:
        subprocess.run(
            [bw_path, 'sync', '--session', session_token],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        print("✅ Vault synced successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during vault sync: {e.stderr}")
        # Don't raise exception here as sync failure shouldn't stop credential retrieval


def extract_ids_from_error(error_message: str) -> list:
    """Extract IDs from the 'More than one result' error message."""
    id_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    ids = re.findall(id_pattern, error_message)
    return ids


def get_credentials_with_retry(item_name: str, session_token: str, bw_path: str = 'bw', max_retries: int = 2) -> dict:
    """Retrieves an item from the Bitwarden vault with retry logic for expired sessions."""

    for attempt in range(max_retries):
        try:
            print(f"🔍 Attempting to get credentials for '{item_name}' (attempt {attempt + 1}/{max_retries})")
            return get_credentials(item_name, session_token, bw_path)
        except subprocess.CalledProcessError as e:
            error_message = str(e.stderr).lower()

            # Check if it's an authentication/session error
            if any(keyword in error_message for keyword in
                   ['unauthorized', 'invalid', 'expired', 'unauthenticated', 'session']):
                if attempt < max_retries - 1:  # Not the last attempt
                    print(
                        f"🔄 Session token expired (attempt {attempt + 1}/{max_retries}), getting new session token...")
                    clear_session_token_cache()
                    new_session_token = get_bw_session(bw_path, force_new=True)
                    if new_session_token:
                        session_token = new_session_token
                        print(f"✅ Successfully obtained new session token, retrying operation...")
                        continue  # Retry with new token
                    else:
                        print("❌ Failed to get new session token")
                        break
                else:
                    print(f"❌ All retry attempts exhausted")
                    break
            else:
                # It's not a session error, handle normally
                print(f"⚠️ Error not related to session expiration: {error_message}")
                return get_credentials(item_name, session_token, bw_path)
        except Exception as e:
            print(f"❌ Unexpected error in get_credentials_with_retry: {e}")
            break

    return None


def get_credentials(item_name: str, session_token: str, bw_path: str = 'bw') -> dict:
    """Retrieves an item from the Bitwarden vault by name, ID, or URL."""
    try:
        # First, try with the original item name/email
        result = subprocess.run(
            [bw_path, 'get', 'item', item_name, '--session', session_token],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        item_data = json.loads(result.stdout)
        return item_data
    except subprocess.CalledProcessError as e:
        error_message = str(e.stderr)

        # Check if it's a "More than one result" error
        if "More than one result was found" in error_message:
            print(f"⚠️  Multiple entries found for '{item_name}'")

            # Extract IDs from the error message
            ids = extract_ids_from_error(error_message)

            if ids:
                first_id = ids[0]
                print(f"🔄 Using first ID: {first_id}")

                try:
                    # Try again with the first ID
                    result = subprocess.run(
                        [bw_path, 'get', 'item', first_id, '--session', session_token],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=30
                    )
                    item_data = json.loads(result.stdout)
                    print(f"✅ Successfully retrieved item using ID: {first_id}")
                    return item_data
                except subprocess.CalledProcessError as e2:
                    print(f"❌ Error retrieving item by ID: {e2.stderr}")
                    raise  # Re-raise to trigger retry logic if needed
                except json.JSONDecodeError as e2:
                    print(f"❌ Error decoding JSON: {e2}")
                    return None
            else:
                print("❌ Could not extract IDs from error message")
                return None
        else:
            print(f"❌ Error retrieving item: {error_message}")
            raise  # Re-raise to trigger retry logic if needed
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {e}")
        return None


def extract_credentials(item_data: dict) -> dict:
    """Extracts username and password from the retrieved Bitwarden item data."""
    try:
        login_data = item_data.get('login', {})
        username = login_data.get('username')
        password = login_data.get('password')
        return {'username': username, 'password': password}
    except KeyError as e:
        print(f"❌ Error extracting credentials: {e}")
        return {'username': None, 'password': None}


def get_totp_with_retry(item_name: str, session_token: str, bw_path: str = 'bw', max_retries: int = 2) -> str:
    """Fetches the TOTP for the specified Bitwarden item with retry logic."""

    for attempt in range(max_retries):
        try:
            print(f"🔐 Attempting to get TOTP for '{item_name}' (attempt {attempt + 1}/{max_retries})")
            return get_totp(item_name, session_token, bw_path)
        except subprocess.CalledProcessError as e:
            error_message = str(e.stderr).lower()

            # Check if it's an authentication/session error
            if any(keyword in error_message for keyword in
                   ['unauthorized', 'invalid', 'expired', 'unauthenticated', 'session']):
                if attempt < max_retries - 1:  # Not the last attempt
                    print(
                        f"🔄 Session token expired for TOTP (attempt {attempt + 1}/{max_retries}), getting new session token...")
                    
                    # First try to get the updated session token from environment
                    cached_token = get_cached_session_token()
                    if cached_token and cached_token != session_token and is_session_valid(cached_token, bw_path):
                        print("✅ Using recently refreshed session token from cache")
                        session_token = cached_token
                        continue
                    
                    # If that doesn't work, force a new session
                    print("🔄 Cached token invalid or not found, creating new session token...")
                    clear_session_token_cache()
                    new_session_token = get_bw_session(bw_path, force_new=True)
                    if new_session_token:
                        session_token = new_session_token
                        print(f"✅ Successfully obtained new session token for TOTP, retrying operation...")
                        continue  # Retry with new token
                    else:
                        print("❌ Failed to get new session token for TOTP")
                        break
                else:
                    print(f"❌ All TOTP retry attempts exhausted")
                    break
            else:
                # It's not a session error, handle normally
                print(f"⚠️ Error not related to session expiration: {error_message}")
                return get_totp(item_name, session_token, bw_path)
        except Exception as e:
            print(f"❌ Unexpected error in get_totp_with_retry: {e}")
            break

    return None


def get_totp(item_name: str, session_token: str, bw_path: str = 'bw') -> str:
    """Fetches the TOTP for the specified Bitwarden item."""
    try:
        # First, try with the original item name/email
        result = subprocess.run(
            [bw_path, 'get', 'totp', item_name, '--session', session_token],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        totp = result.stdout.strip()
        return totp
    except subprocess.CalledProcessError as e:
        error_message = str(e.stderr)

        # Check if it's a "More than one result" error
        if "More than one result was found" in error_message:
            print(f"⚠️  Multiple TOTP entries found for '{item_name}'")

            # Extract IDs from the error message
            ids = extract_ids_from_error(error_message)

            if ids:
                first_id = ids[0]
                print(f"🔄 Using first ID for TOTP: {first_id}")

                try:
                    # Try again with the first ID
                    result = subprocess.run(
                        [bw_path, 'get', 'totp', first_id, '--session', session_token],
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=30
                    )
                    totp = result.stdout.strip()
                    print(f"✅ Successfully retrieved TOTP using ID: {first_id}")
                    return totp
                except subprocess.CalledProcessError as e2:
                    print(f"❌ Error retrieving TOTP by ID: {e2.stderr}")
                    raise  # Re-raise to trigger retry logic if needed
            else:
                print("❌ Could not extract IDs from TOTP error message")
                return None
        else:
            print(f"❌ Error retrieving TOTP: {error_message}")
            raise  # Re-raise to trigger retry logic if needed


def get_bitwarden_credentials(email):
    """
    Retrieve credentials for a given email from Bitwarden.

    Args:
        email (str): The email or name of the item to fetch from Bitwarden

    Returns:
        dict: A dictionary containing 'username', 'password', and 'totp' keys,
              or None if retrieval failed
    """
    print(f"\n=== Getting Bitwarden Credentials for: {email} ===")

    # Find Bitwarden CLI first
    bw_path = find_bw_executable()
    if not bw_path:
        print("❌ Cannot proceed without Bitwarden CLI")
        return None

    print(f"✅ Using API credentials:")
    print(f"   Client ID: {BW_CLIENT_ID}")
    print(
        f"   Client Secret: {'*' * (len(BW_CLIENT_SECRET) - 4) + BW_CLIENT_SECRET[-4:] if len(BW_CLIENT_SECRET) > 4 else '*' * len(BW_CLIENT_SECRET)}")

    # Get session token (will use cached if available and valid)
    print("\n=== Session Token Management ===")
    session_token = get_bw_session(bw_path)

    if not session_token:
        print("❌ Failed to get session token, cannot proceed")
        return None

    try:
        # Sync vault to ensure latest data (non-blocking)
        print("\n=== Syncing Vault ===")
        sync_vault(session_token, bw_path)

        # Get credentials with retry logic
        print("\n=== Retrieving Credentials ===")
        item_data = get_credentials_with_retry(email, session_token, bw_path)

        if not item_data:
            print(f"❌ Failed to retrieve credentials for '{email}'")
            return None

        # Get updated session token in case it was refreshed during retry
        current_session_token = get_cached_session_token() or session_token

        # Get TOTP with retry logic
        print("\n=== Retrieving TOTP ===")
        totp = get_totp_with_retry(email, current_session_token, bw_path)

        credentials = extract_credentials(item_data)
        username = credentials['username']
        password = credentials['password']

        # Perform a final check on token status
        token_status = "Not Cached"
        final_token = get_cached_session_token()
        if final_token:
            if is_session_valid(final_token, bw_path):
                token_status = "Cached and Valid"
            else:
                token_status = "Cached but Invalid"

        print(f"\n=== Credentials Summary ===")
        print(f"✅ Successfully retrieved credentials for {email}")
        print(f"   Username: {username}")
        print(f"   Password: {'*' * len(password) if password else 'None'}")
        print(f"   TOTP: {totp if totp else 'None'}")
        print(f"   Session Token: {token_status}")

        # Show a reminder about token persistence
        print("\n=== Token Persistence Info ===")
        print(f"✅ Session token has been stored in the {BW_SESSION_ENV_VAR} environment variable")
        print(f"   This token will be reused for future runs to avoid unnecessary logins")
        print(f"   Token will expire after several hours of inactivity")

        return {
            'username': username,
            'password': password,
            'totp': totp
        }

    except Exception as e:
        print(f"❌ Error retrieving Bitwarden credentials: {e}")
        return None

    # Note: We don't logout here anymore to preserve the session for future use


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        email = sys.argv[1]
        print(f"Retrieving credentials for: {email}")
        credentials = get_bitwarden_credentials(email)

        if credentials:
            print("\n=== CREDENTIALS RETRIEVED SUCCESSFULLY ===")
            print(f"Username: {credentials['username']}")
            print(f"Password: {credentials['password']}")
            print(f"TOTP: {credentials['totp'] if credentials['totp'] else 'None'}")
        else:
            print(f"\n❌ Failed to retrieve credentials for {email}")
    else:
        print("Usage: python bitwardenAuth.py <email_address>")
        print("Example: python bitwardenAuth.py admin@rtqa1securly.com")
        print(f"\nNote: Session tokens are cached in environment variable: {BW_SESSION_ENV_VAR}")