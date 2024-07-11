
# Flare Hunter

## Overview

This repository contains a Python script to interact with the Flare API. It allows you to query data by domain and export the results to CSV or Excel files. The script handles token management, ensuring that a valid token is used for API requests.

## Setup

### Prerequisites

- Python 3.6+
- pip (Python package installer)
- A valid [Flare.io](https://flare.io) license and API key

### Clone the Repository

```sh
git clone https://github.com/Marzlio/flare-hunter.git
cd flare-hunter
```

### Install Dependencies

```sh
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory with the following content:

```
API_KEY=your_api_key
TENANT_ID=your_tenant_id
REFRESH_TOKEN=your_refresh_token
TOKEN=your_token
REPORT_PATH=./reports
```

Replace the placeholders with your actual values.

### Directory Structure

```
flare-hunter/
├── flare_hunter.py
├── .env
├── README.md
├── requirements.txt
└── reports/
```

## Usage

### Command-line Arguments

- `-d, --domains`: Comma-separated list of domain names to query.
- `-s, --size`: Number of results to fetch. Default is 2000.
- `-o, --order_by_desc`: Order results by descending. Default is True.
- `-t, --type`: Output file type (`csv` or `xlsx`). Default is `csv`.
- `-p, --prefix`: Prefix for the output file name.
- `-v, --verbose`: Enable verbose output.
- `-f, --filter`: Filter results by `source_id`.

### Examples

#### Query Data by Domain

```sh
python flare_hunter.py -d example.com -t xlsx -p your_prefix -v
```

#### Filter Results by Source ID

```sh
python flare_hunter.py -d example.com -f source_id_value -t csv -p your_prefix -v
```

## Notes

- Ensure your `.env` file contains the correct `API_KEY`, `TENANT_ID`, `REFRESH_TOKEN`, `TOKEN`, and `REPORT_PATH`.
- The script will generate a new token if the current token is invalid or expired.
- Reports will be saved in the directory specified by `REPORT_PATH`.

## Contributing

Feel free to open issues or submit pull requests if you have suggestions or improvements.

## License

This project is licensed under the MIT License.
