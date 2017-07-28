import requests
import json
import os
import Tkinter as tk
from PIL import ImageTk, Image
from datetime import datetime

class InstagramSlideshow:
    def __init__(self):
        # set constants
        self.INSTAGRAM_ACCESS_TOKEN = "put your access token here"
        self.MOST_RECENT_PHOTOS_URL = "https://api.instagram.com/v1/users/self/media/recent/?access_token={}".format(self.INSTAGRAM_ACCESS_TOKEN)
        self.LOCAL_PHOTO_DIRECTORY_PATH = "./instagram_photos/"
        self.HOUR_IN_MICROSECONDS = 60 * 60 * 1000
        self.HOW_LONG_BEFORE_CHANGING_PHOTO_IN_MICROSECONDS = 15 * 1000

        # set up Tkinter for fullscreen display of photos
        self.window = tk.Tk()
        self.window.attributes("-fullscreen", True)
        self.WIDTH, self.HEIGHT = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        self.ASPECT_RATIO = self.WIDTH * 1.0 / self.HEIGHT
        self.fullscreen = True
        self.window.title('Instagram Slideshow')
        self.photo_label = tk.Label(self.window, bg="black")
        self.photo_label.pack(fill=tk.BOTH, expand=True)
        self.current_image = None
        self.current_image_index = 0

        # create the instagram_photos subdirectory if it doesn't already exist
        if not os.path.isdir(self.LOCAL_PHOTO_DIRECTORY_PATH):
            os.mkdir(self.LOCAL_PHOTO_DIRECTORY_PATH)

        # download any new photos, start slideshow
        self.download_any_new_instagram_photos()
        self.photos = self.get_photo_filenames()
        print "Starting slideshow."
        self.show_photo()

    def download_any_new_instagram_photos(self):
        # get URLs, captions, etc. on the 20 most recent Instagram photos
        print ("Checking for any new Instagram photos at {} ...".format(datetime.now()))
        internet_connection = True
        try:
            json_data = json.loads(requests.get(self.MOST_RECENT_PHOTOS_URL).text)
        except:
            internet_connection = False
            print "Unable to reach Instagram ... check your Internet connection. Showing stored photos."

        if internet_connection:
            new_photos_downloaded = False

            # and check to see whether or not they have already been downloaded
            try:
                for photo in json_data["data"]:
                    image_url = photo["images"]["standard_resolution"]["url"]
                    photo_filename = image_url[image_url.rindex("/") + 1:]
                    if not os.path.isfile(self.LOCAL_PHOTO_DIRECTORY_PATH + photo_filename):
                        # save to disk any new photos that were not saved previously
                        new_photos_downloaded = True
                        print ('Downloading and saving photo "{}"'.format(photo["caption"]["text"].encode("utf8")))
                        photo_file = requests.get(image_url).content
                        with open(self.LOCAL_PHOTO_DIRECTORY_PATH + photo_filename, 'wb') as handler:
                            handler.write(photo_file)
            except:
                print "Instagram error:", json_data

            if new_photos_downloaded:
                # update the list of jpg filenames in the Instagram Photos subdirectory
                self.get_photo_filenames()
            else:
                print "No new photos found."

        # check for new photos once an hour
        self.window.after(self.HOUR_IN_MICROSECONDS, self.download_any_new_instagram_photos)

    def get_photo_filenames(self):
        # get all the jpg filenames in the Instagram Photos subdirectory
        photo_filenames = [file for file in os.listdir(self.LOCAL_PHOTO_DIRECTORY_PATH) if file.endswith(".jpg")]
        if not photo_filenames:
            print "No stored photos found."

        return photo_filenames

    def show_photo(self):
        if self.photos:
            # if there are any photos in the instagream_photos subdirectory,
            # open the next image and resize it to fit the screen
            with Image.open(self.LOCAL_PHOTO_DIRECTORY_PATH + self.photos[self.current_image_index]) as image:
                image_width, image_height = image.size
                image_aspect_ratio = image_width * 1.0 / image_height
                new_width, new_height = self.WIDTH, self.HEIGHT
                if image_aspect_ratio > self.ASPECT_RATIO:
                    new_height = image_height * self.WIDTH / image_width
                else:
                    new_width = image_width * self.HEIGHT / image_height
                image = image.resize((new_width, new_height), Image.ANTIALIAS)
                next_photo = ImageTk.PhotoImage(image)

            # and display it
            self.photo_label.configure(image=next_photo)
            self.photo_label.image = next_photo

            # and on to the following photo after a delay
            self.current_image_index = (self.current_image_index + 1) % len(self.photos)
            self.window.after(self.HOW_LONG_BEFORE_CHANGING_PHOTO_IN_MICROSECONDS, self.show_photo)


# create an Instagram Slideshow instance, and start it up
slideshow = InstagramSlideshow()
slideshow.window.mainloop()
