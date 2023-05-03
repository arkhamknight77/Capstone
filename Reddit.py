import os
import praw

# Replace CLIENT_ID, CLIENT_SECRET, USERNAME, and PASSWORD with your actual values
reddit = praw.Reddit(
    client_id='AafGycDGu3wQSscM8k8vSQ',
    client_secret='5z9OHaIOJy4-U0U4Oc8U-Ux5lZlXrQ',
    username='LuckyAir7055',
    password='mountaindew7',
    user_agent='MyApp/0.1 by LuckyAir7055'
)

# Set the subreddit where you want to post
subreddit = reddit.subreddit('r/recessionanalysis')

# Set the path to the folder containing the images
folder_path = 'C:/Users/Jeetesh/CAPSTONEEEE/CAPSTONE ALLOCATION/graphs'

# Loop through each file in the folder and submit it to Reddit
for file_name in os.listdir(folder_path):
    # Get the full path to the file
    file_path = os.path.join(folder_path, file_name)

    # Check if the file is an image file
    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        try:
            # Submit the image to Reddit
            subreddit.submit_image(
                title=file_name,
                image_path=file_path,
                send_replies=False
            )
            print('Posted {} to Reddit'.format(file_name))
        except Exception as e:
            print('Failed to post {} to Reddit: {}'.format(file_name, e))