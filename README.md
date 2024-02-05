## LinkedIn Scraper

### Overview
This Python script automates the process of logging in to LinkedIn, searching for a specified subject, and extracting contact information (name, bio, email, LinkedIn URL) from the profiles of the first 9 search results. The script utilizes the Selenium library for web scraping.

### Prerequisites
- Python (3.x recommended)
- Selenium library (`pip install selenium`)
- Chrome browser
- ChromeDriver (Ensure it's in your system PATH or specify the path in the script)
- YAML library (`pip install pyyaml`)

### Configuration
1. **XPath Configuration**
    - Create an `xpath_config.yml` file with the XPaths for various elements.
    ```yaml
    email_input: "//your/email/input/xpath"
    password_input: "//your/password/input/xpath"
    sign_in_button: "//your/sign/in/button/xpath"
    search_bar: "//your/search/bar/xpath"
    all_people: "//your/all/people/xpath"
    linkedin_url: "//your/linkedin/url/xpath"  # Optional: Include this if you want to extract LinkedIn URLs
    ```

2. **Configurations**
    - Create a `config.yml` file with your LinkedIn username, password, and the subject you want to search.
    ```yaml
    username: your_linkedin_username
    password: your_linkedin_password
    subject: your_search_subject
    ```

### Usage
1. **Execution**
    - Run the script using `python Linkedin.py`.
    - The script will log in to LinkedIn, search for the specified subject, and extract contact information from the profiles of the first 9 search results.
    - Extracted data is saved in a CSV file named `{subject}.csv`.

2. **Output**
    - The script will create a CSV file with columns: Name, Bio, Email, and LinkedIn URL (if extracted).
    - The CSV file is automatically opened in Excel for easy viewing.

### Notes
- The script uses explicit waits for elements to ensure proper page loading.
- LinkedIn may have restrictions on automated access, so use the script responsibly and in compliance with LinkedIn's terms of service.
- Handle exceptions gracefully to avoid disruptions during execution.

### Warning
- Automated scraping of LinkedIn may violate their terms of service. Use this script responsibly and at your own risk. The authors are not responsible for any misuse or violation of terms.
