import requests
from bs4 import BeautifulSoup
import pandas as pd
from boto3.session import Session

class AmazonScraper:
    def __init__(self, url):
        self.url = url
        self.data = {'title': [], 'price': []}

    def scrape(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }
        r = requests.get(self.url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Selecting the title and price elements with correct selectors
        titles = soup.select('span.a-size-medium.a-color-base.a-text-normal')
        prices = soup.select('span.a-price-whole')

        # Ensure that we only append data if both title and price are available
        for title, price in zip(titles, prices):
            title_text = title.get_text(strip=True)
            price_text = price.get_text(strip=True)

            # Debugging: print title and price
            print("Title:", title_text)
            print("Price:", price_text)

            # Append title and price to the 'data' dictionary
            self.data['title'].append(title_text)
            self.data['price'].append(price_text)

    def save_to_csv(self, filename):
        df = pd.DataFrame(self.data)
        df.to_csv(filename, index=False)  # Write DataFrame to CSV file without index column
        print("Data saved to", filename)

# Initialize an S3 session
ACCESS_KEY_ID = 'AKIAJ2FTIRCMY33C7FIA'
SECRET_KEY = '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'
session = Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')
bucket = 'CsvFileUpload'
my_bucket = s3.Bucket(bucket)

# Usage
url = 'https://www.amazon.in/s?k=iphone+15+pro+max&crid=13WT9U9AXOP4R&sprefix=i%2Caps%2C263&ref=nb_sb_ss_ts-doa-p_1_1'
scraper = AmazonScraper(url)
scraper.scrape()
scraper.save_to_csv('data.csv')

# Upload data.csv file to S3
file_to_be_uploaded = 'data.csv'
object_name = 'data.csv'
my_bucket.upload_file(file_to_be_uploaded, object_name)
print('\nObject After Uploading:')
