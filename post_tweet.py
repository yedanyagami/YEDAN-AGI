"""
YEDAN - Twitter Revenue Poster
Direct Twitter API posting for traffic generation
"""
import sys
import io
import os
import tweepy
from dotenv import load_dotenv

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv(dotenv_path=".env.reactor")


def post_tweet(text: str) -> dict:
    """Post a tweet using Twitter API v2"""
    client = tweepy.Client(
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    )
    
    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data['id']
        return {
            'success': True,
            'tweet_id': tweet_id,
            'url': f"https://twitter.com/yedanyagamiio/status/{tweet_id}"
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    tweet = """AI tip for entrepreneurs:

Use ChatGPT to draft your client follow-up emails.

Prompt: 'Write 3 varied follow-up emails for past clients focusing on market updates'

Saves 2 hours/week.

More tips in my profile.
#AI #Entrepreneur #Productivity"""

    print("Posting tweet...")
    result = post_tweet(tweet)
    
    if result['success']:
        print(f"SUCCESS! Tweet posted")
        print(f"URL: {result['url']}")
    else:
        print(f"Error: {result['error']}")
    
    return result


if __name__ == "__main__":
    main()
