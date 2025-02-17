from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup
import pandas as pd


def grab_channel_id(user):
    """Parses channel ID from user-provided YouTube channel name"""
    # create User-Agent (optional)
    headers = {"User-Agent": "Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/31.0.1650.0 Safari/537.36"}
    # get() Request
    url = 'https://www.youtube.com/@' + user
    response = requests.get(url, headers=headers)
    # Store the webpage contents
    webpage = response.content
    # Check Status Code (Optional)
    # print(response.status_code)
    # Create a BeautifulSoup object out of the webpage content
    soup = BeautifulSoup(webpage, "html.parser")
    # to find channel id, go to source and find <link rel="canonical" href="https://www.youtube.com/channel/[ID]>
    tag = soup.find("link", rel="canonical")
    # convert to string and extract channel_id from tag
    tag_str = str(tag)
    found_id = tag_str.split("/channel/")[1].split(" ")[0][:-1]
    return found_id


# Program user will need their own API key
DEVELOPER_KEY = 'INSERT KEY HERE'
done = 0

# Dictionary to store channel statistics
channel_info = {
    'name': [],
    'id': [],
    'subscribers': [],
    'videos': [],
    'views': [],
}

while done == 0:
    # prompt user for username, grab channel ID
    channel_name = input("Enter username: ")

    # make sure Youtube channel exists
    url_test = 'https://www.youtube.com/@' + channel_name
    response_test = requests.get(url_test)

    while response_test.status_code == 404:
        print("Channel does not exist. Try again:\n")
        channel_name = input("Enter username: ")
        # make sure Youtube channel exists
        url_test = 'https://www.youtube.com/@' + channel_name
        response_test = requests.get(url_test)

    channel_id = grab_channel_id(channel_name)
    print(channel_id)

    # Create YouTube Object
    youtube = build('youtube', 'v3',
                    developerKey=DEVELOPER_KEY)

    ch_request = youtube.channels().list(
        part='statistics',
        id=channel_id)

    # Channel Information
    ch_response = ch_request.execute()

    subscriber_count = ch_response['items'][0]['statistics']['subscriberCount']
    video_count = ch_response['items'][0]['statistics']['videoCount']
    view_count = ch_response['items'][0]['statistics']['viewCount']

    channel_info['name'].append(channel_name)
    channel_info['id'].append(channel_id)
    channel_info['subscribers'].append(subscriber_count)
    channel_info['videos'].append(video_count)
    channel_info['views'].append(view_count)

    print("Total Subscribers: ", subscriber_count)
    print("Total Number of Videos: ", video_count)
    print("Total Views: ", view_count)

    # Append each new channel info to csv
    pd.DataFrame(data=channel_info).to_csv("yt_channel_data.csv", index=False)

    done_check = input("Do you want to enter another user? y/n   ")
    if done_check.lower() in ['y', 'yes']:
        print("Continuing...")
    else:
        print("Exiting...")
        done = 1
