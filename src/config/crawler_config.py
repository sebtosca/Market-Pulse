"""Configuration settings for the crawler agent."""

# Search settings
SEARCH_SETTINGS = {
    "num_results": 10,  # Increased to get more press releases
    "delay": {
        "min": 2,  # Increased delay to avoid rate limiting
        "max": 4
    }
}

# URL scoring weights
URL_SCORING = {
    "news_domain": 5,  # Higher score for news domains
    "press_release": 4,  # High score for press releases
    "company_domain": 3,  # Lower score for company domains
    "pipeline_page": 2,  # Lower score for pipeline pages
    "biotech_domain": 1  # Lower score for biotech domains
}

# Website patterns to look for
WEBSITE_PATTERNS = [
    "press-release",
    "news",
    "media",
    "announcement",
    "update",
    "pipeline",
    "clinical",
    "trial",
    "results",
    "partnership",
    "collaboration",
    "license",
    "acquisition"
]

# Search queries to use with company name
SEARCH_QUERIES = [
    "{company} press release",
    "{company} news update",
    "{company} announces",
    "{company} clinical trial results",
    "{company} partnership announcement",
    "{company} collaboration news",
    "{company} license agreement",
    "{company} acquisition news",
    "{company} recent developments",
    "{company} investor update"
]

# Common news and press release domains
NEWS_DOMAINS = [
    "reuters.com",
    "bloomberg.com",
    "biospace.com",
    "fiercebiotech.com",
    "biopharmadive.com",
    "endpts.com",
    "statnews.com",
    "genengnews.com",
    "pharmatimes.com",
    "pharmalive.com",
    "bioworld.com",
    "seekingalpha.com",
    "businesswire.com",
    "globenewswire.com",
    "prnewswire.com"
]

# Common biotech/pharma domains
BIOTECH_DOMAINS = [
    ".com",
    ".io",
    ".bio",
    ".pharma",
    ".healthcare"
]

# Request settings
REQUEST_SETTINGS = {
    "timeout": 30,
    "max_retries": 3,
    "headers": {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"'
    }
} 