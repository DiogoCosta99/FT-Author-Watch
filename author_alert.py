import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os

# Set headers to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0'
}

file_path = 'authors_articles.json'

# Function to read existing articles from file (if it exists)
def load_articles():
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

# Function to save the articles back to the file
def save_articles(articles):
    with open(file_path, 'w') as f:
        json.dump(articles, f, indent=4)

# Gmail credentials (Use an App Password instead of your Google account password)
gmail_user = os.getenv('GMAIL_USER')
gmail_password = os.getenv('GMAIL_PASSWORD')  # Use an App Password for added security

# Function to send an email
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = os.getenv('GMAIL_USER')  # Replace with your recipient email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Set up the server and send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, os.getenv('GMAIL_USER'), text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

authors = load_articles()

for author in authors.keys():
    url =  'https://www.ft.com/{}'.format(author)
    response = requests.get(url, headers=headers)
    print(f"Fetching {url} returned status code {response.status_code}")
    print(response.text[:1000])  # print the first 1000 chars of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    article_list = []

    # You may need to inspect the structure of the page to get the right class or tag
    # This is an example placeholder — inspect the HTML to update this
    latest_article = soup.find('a', class_='js-teaser-heading-link')  # Placeholder class

    if latest_article:
        title = latest_article.get_text(strip=True)
        link = latest_article['href']

        # Here you'd compare with your saved article
        print("Latest article:", title)
        print("Link:", link)

        # Compare with previously stored title/link
        # If new, store it and notify
        if title in authors[author]:
            print("No new article.")
        else:
            #article_list.clear()
            #article_list.append(title)
            print(f"New article added to the list: {title} instead of {authors[author]}")
            authors.update({author:title})
            
            subject = f"New article by {author.replace('-',' ').title()}"
            body = f"{author.replace('-',' ').title()} has published a new article: {title}\nCheck it out here: ft.com{link}"
            send_email(subject, body)
    else:
        print(f"No articles found for author: {author}")


    
save_articles(authors)
print(authors)
