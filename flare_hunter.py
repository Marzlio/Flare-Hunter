import requests
import json
import os
import pandas as pd
from dotenv import load_dotenv, set_key
from datetime import datetime, timezone, timedelta
import jwt

# Load environment variables from .env file
load_dotenv()

def get_env_var(key, default=None, cast_func=None):
    value = os.getenv(key, default)
    return cast_func(value) if cast_func and value else value

def set_env_var(key, value):
    os.environ[key] = value
    set_key('.env', key, value)

def log_verbose(verbose, message):
    if verbose:
        print(message)

def generate_token(verbose):
    api_key = get_env_var('API_KEY')
    tenant_id = get_env_var('TENANT_ID', cast_func=int)

    url = 'https://api.flare.io/tokens/generate'
    headers = {'Content-Type': 'application/json'}
    data = {'tenant_id': tenant_id}

    log_verbose(verbose, f"Request URL: {url}")
    log_verbose(verbose, f"Request Headers: {headers}")
    log_verbose(verbose, f"Request Data: {data}")

    response = requests.post(url, headers=headers, auth=("", api_key), json=data)

    log_verbose(verbose, f"Response Status Code: {response.status_code}")
    log_verbose(verbose, f"Response Headers: {response.headers}")
    log_verbose(verbose, f"Response Text: {response.text}")

    if response.status_code == 200:
        response_json = response.json()
        new_token = response_json.get('token')
        if new_token:
            set_env_var('TOKEN', new_token)
            print("Token generated and saved to .env")
        else:
            print("Failed to generate token. No new token received.")
    else:
        print(f"Failed to generate token: {response.status_code} - {response.text}")

def token_is_valid(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256"])
        exp = datetime.fromtimestamp(decoded_token['exp'], timezone.utc)
        return exp > datetime.now(timezone.utc) + timedelta(minutes=5)
    except Exception as e:
        print(f"Error decoding token: {e}")
        return False

def ensure_valid_token(verbose):
    token = get_env_var('TOKEN')
    if not token or not token_is_valid(token):
        generate_token(verbose)

def get_report_path():
    report_path = get_env_var('REPORT_PATH', './reports')
    os.makedirs(report_path, exist_ok=True)
    return report_path

def fetch_data_by_leak(domain, size, order_by_desc, verbose, source_filter):
    ensure_valid_token(verbose)
    token = get_env_var('TOKEN')
    url = f'https://api.flare.io/firework/v2/activities/leak/leaksdb/{domain}?order_by_desc={order_by_desc}&size={size}'
    headers = {
        'Content-Type': 'application/json',
        'authorization': f'Bearer {token}'
    }

    log_verbose(verbose, f"Request URL: {url}")
    log_verbose(verbose, f"Request Headers: {headers}")

    response = requests.get(url, headers=headers)

    log_verbose(verbose, f"Response Status Code: {response.status_code}")
    log_verbose(verbose, f"Response Headers: {response.headers}")
    log_verbose(verbose, f"Response Text: {response.text}")

    if response.status_code == 200:
        data = response.json()
        log_verbose(verbose, f"Response Data: {json.dumps(data, indent=4)}")
        
        activity_data = data.get('activity', {}).get('data', {})
        identities = activity_data.get('identities', [])
        
        formatted_data = [
            {
                "domain": domain,
                "email": identity.get('name'),
                "password": pwd.get('hash'),
                "imported_at": pwd.get('imported_at'),
                "source_id": pwd.get('source_id'),
                "source_params": pwd.get('source_params')
            }
            for identity in identities
            for pwd in identity.get('passwords', [])
            if not source_filter or pwd.get('source_id') == source_filter
        ]

        return formatted_data
    else:
        print(f"Failed to retrieve data for {domain}: {response.status_code} - {response.text}")
        return []

def export_data(data, file_type, prefix, domain, verbose):
    df = pd.DataFrame(data)
    log_verbose(verbose, f"DataFrame head for {domain}: {df.head()}")
    report_path = get_report_path()
    prefix = prefix or datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{prefix}_{domain}_leaked_data.{file_type}'
    full_path = os.path.join(report_path, filename)
    
    log_verbose(verbose, f"Full path for {domain}: {full_path}")
    
    try:
        if file_type == 'csv':
            df.to_csv(full_path, index=False)
        else:
            df.to_excel(full_path, index=False)
        print(f"Data exported successfully to '{full_path}' for domain {domain}.")
    except Exception as e:
        print(f"Error exporting data for {domain}: {e}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Fetch data by leak from Flare API and export to CSV or Excel')
    parser.add_argument('-d', '--domains', type=str, required=True, help='Comma separated list of domain names to query')
    parser.add_argument('-s', '--size', type=int, default=2000, help='Number of results to fetch')
    parser.add_argument('-o', '--order_by_desc', type=bool, default=True, help='Order results by descending')
    parser.add_argument('-t', '--type', type=str, choices=['csv', 'xlsx'], default='csv', help='Output file type (csv or xlsx)')
    parser.add_argument('-p', '--prefix', type=str, default='', help='Prefix for the output file name')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-f', '--filter', type=str, help='Filter results by source_id')

    args = parser.parse_args()

    for domain in args.domains.split(','):
        domain = domain.strip()
        data = fetch_data_by_leak(domain, args.size, args.order_by_desc, args.verbose, args.filter)
        if data:
            export_data(data, args.type, args.prefix, domain, args.verbose)
        else:
            print(f"No data fetched for domain: {domain}")
