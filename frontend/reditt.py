import time

import pandas as pd
import requests
import requests.auth
import praw
import asyncio
from pytrends.request import TrendReq
from bs4 import BeautifulSoup

from metagpt.llm import LLM
from PIL import Image
import numpy as np
from wordcloud import WordCloud
# client_auth = requests.auth.HTTPBasicAuth('z9ggGSMPU_KPe_fuXX1RhQ', '971DQsUHSw4iuV98YVoCTfl_oY9MXw')
# post_data = {"grant_type": "password", "username": "arunneoz", "password": "sUmmertime123$"}
# headers = {'User-Agent': 'MyBot/0.0.1'}
# response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
# response.json()
#
# TOKEN = response.json()['access_token']
#
# # add authorization to our headers dictionary
# headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}
llm = LLM()
reddit = praw.Reddit(client_id='z9ggGSMPU_KPe_fuXX1RhQ',
                     client_secret='971DQsUHSw4iuV98YVoCTfl_oY9MXw',
                     password='sUmmertime123$',
                     user_agent='cpg_product_bot',
                     username='arunneoz')

productworthy_headlines = []
memeworthy_urls = []
df = pd.DataFrame()
top_week_posts = reddit.subreddit('SkincareAddiction').top(time_filter='week', limit=1)
# for submission in top_week_posts.hot(limit=50):  # Define the limit here and filter method
#     sub_ids.append(submission.id)
for sub_id in top_week_posts:
    submission = reddit.submission(id=sub_id).id
    productworthy_headlines.append(submission.title)

print(productworthy_headlines)

def get_keywords_from_article(article):
    response = llm.aaskes(f"We are identifying keywords from the below news article. Extract five keywords from the below article in the format of Word1,word2,word3,word4,word5 \n\narticle:{article}",

    )
   # Sample text from response.choices[0].text
    text = response
    text_cleaned = text.replace("\n", "").strip()
    keywords=text_cleaned.split(',')
    return keywords


#fetch trends for the keywords
def check_google_trends(keyword):
    pytrends = TrendReq(hl='en-US', tz=360)
    keyword = keyword.strip()
    kw_list = [keyword]
    try:
        pytrends.build_payload(kw_list)
        data_region = pytrends.interest_by_region()
        mean_region_scores = data_region.mean()
        return mean_region_scores[keyword]
    except Exception as e:
        return 0

def fetch_article_content(url, headline):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        article_text = ' '.join([p.get_text() for p in soup.find_all('p')])
        return article_text
    except requests.RequestException:
        print(f"Error fetching article for URL: {url}. Using headline as the content.")
        return headline  # return the headline if there's an error fetching the article

def get_sentiment(headline):

    response = llm.aaskes(f"What is the sentiment of this headline? Positive, neutral, or negative? I am trying to do product research, anything to fit the objective. If you are unsure put it under neutral and if you feel it is not a good fit make it negative \"{headline}\"")


    sentiment = response

    return sentiment

def get_article_summary(article_content):

    response = llm.aaskes(f"Summarize the following content \"{article_content}\"")


    sentiment = response

    return sentiment


# for headline, url in zip(memeworthy_headlines, memeworthy_urls):
#     # Fetch Article Content
#     article_content = fetch_article_content(url, headline)
#
#     # Get Article Summary
#     article_summary = get_article_summary(article_content)
#
#     # Extract Keywords
#     keywords = get_keywords_from_article(article_content)
#
#     # Get keyword scores
#     keyword_scores = [f"{kw}: {check_google_trends(kw)}" for kw in keywords]
#     keyword_data_str = ', '.join(keyword_scores)
#
#     # Append to DataFrame
#     df.loc[len(df)] = [headline, url, article_summary, ', '.join(keywords), keyword_data_str]
#
#     time.sleep(2)  # Avoid hitting rate limits

# Save to CSV (or Excel if preferred)
df.to_csv('memeworthy_articles.csv', index=False)


# subreddit = reddit.subreddit('SkincareAddiction')  # Change the subreddit's name here
# sub_ids = []
# for submission in subreddit.hot(limit=50):  # Define the limit here and filter method
#     sub_ids.append(submission.id)
#
# top_level_comments = []
# second_level_comments = []
# title = []
# selftext = []
#
#
# def generate_wordcloud(text, stopwords=None, mask=None):
#     """Generate Word Cloud"""
#
#
#
#     mask_object = None
#     if mask != None:
#         mask_object = np.array(Image.open(mask))
#
#     wordcloud = WordCloud(width=1200, height=600, stopwords=stopwords, max_font_size=200, mask=mask_object,
#                           background_color='white', colormap='viridis')
#     wordcloud = wordcloud.generate(' '.join(text))
#     # Display the generated image:
#     # the matplotlib way:
#     import matplotlib.pyplot as plt
#     plt.figure()
#     plt.imshow(wordcloud, interpolation="bilinear")
#     plt.axis("off")
#     plt.show()
#
# for sub_id in sub_ids:
#     submission = reddit.submission(id=sub_id)
#     title.append(submission.title)  # Get submission title
#     selftext.append(submission.selftext)  # Get submission content
#     submission.comments.replace_more(limit=None)
#     for top_level_comment in submission.comments:
#         top_level_comments.append(top_level_comment.body)  # Get top-level comments
#         for second_level_comment in top_level_comment.replies:
#             second_level_comments.append(second_level_comment.body)
#
# print(generate_wordcloud(top_level_comments))