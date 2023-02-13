from googleapiclient.discovery import build
import json
import requests
import time
import pandas as pd
import re
import numpy as np

url_input = "https://www.youtube.com/watch?v=9U684GbFST4"
video_id_split =url_input.split('=')
video_id=video_id_split[1]
print(video_id)

api_key = ''
url = 'https://www.googleapis.com/youtube/v3/videos?id='+video_id+'&key='+api_key+'&part=id,statistics'
response_info=requests.get(url).json()

# Contains all comments (both top-level comments and replies to those comments).
all_comments = []

# Get the total (sum) of comments the video has: 
for comment_count in response_info['items']:
  total = int(comment_count['statistics']['commentCount'])

# Show the total amount of comments for the given video: 
print("Total comments for (" + video_id + "): " + str(total))

def getAllTopLevelCommentReplies(topCommentId, token): 
  """
  Recursive function that retrieves the replies a given comment has.
  """

  replies_response=youtube.comments().list(part='snippet',maxResults=100,parentId=topCommentId,pageToken=token).execute()

  for indx, reply in enumerate(replies_response['items']):
    all_comments.append(reply['snippet']['textDisplay'])
    
  if "nextPageToken" in replies_response: 
    return getAllTopLevelCommentReplies(topCommentId, replies_response['nextPageToken'])
  else:
    return []
      
def get_comments(youtube, video_id, token): 
  """
  Recursive function that retrieves the comments (top-level ones) a given video has.
  """

  global all_comments
  totalReplyCount = 0
  token_reply = None

  if (len(token.strip()) == 0): 
    all_comments = []

  if (token == ''): 
    video_response=youtube.commentThreads().list(part='snippet',maxResults=100,videoId=video_id,order='relevance').execute() 
  else: 
    video_response=youtube.commentThreads().list(part='snippet',maxResults=100,videoId=video_id,order='relevance',pageToken=token).execute() 


  # INICIO 

  # Loop comments from the video: 
  for indx, item in enumerate(video_response['items']): 
    # Append coments:
    all_comments.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])

    # Get total reply count: 
    totalReplyCount = item['snippet']['totalReplyCount']

    # If the comment has replies, get them:
    if (totalReplyCount > 0): 
      # Get replies - first batch: 
      replies_response=youtube.comments().list(part='snippet',maxResults=100,parentId=item['id']).execute()
      for indx, reply in enumerate(replies_response['items']):
        # Append the replies to the main array: 
        all_comments.append((" "*2) + reply['snippet']['textDisplay'])

      # If the reply has a token for get more replies, loop those replies 
      # and add those replies to the main array: 
      while "nextPageToken" in replies_response:
        token_reply = replies_response['nextPageToken']
        replies_response=youtube.comments().list(part='snippet',maxResults=100,parentId=item['id'],pageToken=token_reply).execute()
        for indx, reply in enumerate(replies_response['items']):
          all_comments.append((" "*4) + reply['snippet']['textDisplay'])
    
  # Check if the video_response has more comments:
  if "nextPageToken" in video_response: 
    return get_comments(youtube, video_id, video_response['nextPageToken']) 
  else: 
    # Remove empty elements added to the list "due to the return in both functions":
    all_comments = [x for x in all_comments if len(x) > 0]
    print("Fin")
    return []
      
all_comments=[]
qtyReplies = 0
qtyMainComments = 0

youtube = build('youtube', 'v3',developerKey=api_key)
comments = get_comments(youtube,video_id,'')

df = pd.DataFrame(all_comments,columns=['Comments'])

# DATA CLEANING

df = df.astype(str).apply(lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))


df['Comments'] = df['Comments'].apply(lambda x: re.split('<a href="https:\/\/.*', str(x))[0])


def process_content(content):
    return " ".join(re.findall("[A-Za-z]+",content))

df['Comments'] = df['Comments'].apply(process_content)

df['Comments'] = df['Comments'].str.lower()

df['Comments'].replace('', np.nan, inplace=True)

df.dropna()


print(df['Comments'])

# transform to csv 
df.to_csv('comments.csv', index=False)
