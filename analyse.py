import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

import warnings
warnings.filterwarnings("ignore")



pd.set_option('display.max_columns',None)

US_comments = pd.read_csv('comments.csv', error_bad_lines=False)


US_comments.head()
US_comments.shape
US_comments.isnull().sum()
US_comments.dropna(inplace=True)
US_comments.isnull().sum()
US_comments.shape
US_comments.nunique()
US_comments.info()
US_comments = US_comments.reset_index().drop('index',axis=1)
US_comments.head()


# Remove punctuation
US_comments['Comments'] = US_comments['Comments'].str.replace("[^a-zA-Z#]", " ")

# Remove short words (length < 3)
US_comments['Comments'] = US_comments['Comments'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))

# Convert to lowercase
US_comments['Comments'] = US_comments['Comments'].apply(lambda x:x.lower())

# Tokenization
tokenized_tweet = US_comments['Comments'].apply(lambda x: x.split())
tokenized_tweet.head()

#  remove not from stopwords
stopwords = set(stopwords.words('english'))

# remove other word that are negative
stopwords.remove('no')
stopwords.remove('nor')
stopwords.remove('not')
stopwords.remove('don')
stopwords.remove('don\'t')
stopwords.remove('shouldn')
stopwords.remove('shouldn\'t')
stopwords.remove('couldn')
stopwords.remove('couldn\'t')
stopwords.remove('wasn')
stopwords.remove('wasn\'t')
stopwords.remove('weren')
stopwords.remove('weren\'t')
stopwords.remove('won')
stopwords.remove('won\'t')
stopwords.remove('wouldn')
stopwords.remove('wouldn\'t')
stopwords.remove('aren')
stopwords.remove('aren\'t')
stopwords.remove('hadn')
stopwords.remove('hadn\'t')
stopwords.remove('hasn')
stopwords.remove('hasn\'t')

# Stemming & Stopwords
wnl = WordNetLemmatizer()
tokenized_tweet.apply(lambda x: [wnl.lemmatize(i) for i in x if i not in set(stopwords)]) 
tokenized_tweet.head()

# Joining the tokenized tweets back together
for i in range(len(tokenized_tweet)):
    tokenized_tweet[i] = ' '.join(tokenized_tweet[i])

US_comments['Comments'] = tokenized_tweet


# Sentiment Analysis

from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
US_comments['Sentiment Scores'] = US_comments['Comments'].apply(lambda x:sia.polarity_scores(x)['compound'])
US_comments.head()


# Classification of comments
US_comments['Sentiment'] = US_comments['Sentiment Scores'].apply(lambda s : 'Positive' if s > 0 else ('Neutral' if s == 0 else 'Negative'))

US_comments.Sentiment.value_counts()

#  print top 10 negative comments
print(US_comments[US_comments.Sentiment == 'Negative'].Comments.head(10))

# to csv
US_comments.to_csv('result.csv', index=False)



