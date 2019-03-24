import requests
import json
import os
import sys
import random
from datetime import datetime
from PIL import ImageTk, Image

# For compatibility with both Python 2 and 3
if sys.version_info[0] < 3:
    import Tkinter as tk
    import ttk
    import ConfigParser
else:
    import tkinter as tk
    import tkinter.ttk as ttk
    import configparser as ConfigParser

from tkSimpleDialog import Dialog
# tkSimpleDialog.py is from http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
# Thanks to the author, Fredrik Lundh!

class SlideshowPreferencesDialog(Dialog):
    def body(self, parent):
        # set up the Edit Preferences dialog box labels and input widgets
        display_order_label = tk.Label(parent, text="Photo display order:").grid(row=0, sticky="W")
        self.display_order = tk.StringVar()
        self.display_order_random = tk.Radiobutton(parent, text="Random order", variable=self.display_order, value="random").grid(row=0, column=1, sticky="W")
        self.display_order_directory = tk.Radiobutton(parent, text="Directory order", variable=self.display_order, value="directory").grid(row=1, column=1, sticky="W")
        self.display_order_sorted = tk.Radiobutton(parent, text="Sorted lexicographically", variable=self.display_order, value="sorted").grid(row=2, column=1, sticky="W")
        self.display_order.set(self.parent.PHOTO_DISPLAY_ORDER)

        duration_label = tk.Label(parent, text="Photo duration in seconds: ").grid(row=3, sticky="W", pady=7)
        self.duration = tk.StringVar()
        self.duration_spinbox = tk.Spinbox(parent, from_=5, to=120, increment=5, textvariable=self.duration).grid(row=3, column=1)
        self.duration.set(self.parent.SECONDS_BEFORE_CHANGING_PHOTO)

    def apply(self):
        # if the user clicked OK on the Edit Preferences dialog, see if they made any changes
        selected_photo_display_order = self.display_order.get()
        selected_duration = int(self.duration.get())
        if selected_photo_display_order != self.parent.PHOTO_DISPLAY_ORDER or selected_duration != self.parent.SECONDS_BEFORE_CHANGING_PHOTO:
            self.parent.PHOTO_DISPLAY_ORDER = selected_photo_display_order
            self.parent.SECONDS_BEFORE_CHANGING_PHOTO = selected_duration
            self.parent.preferences_changed = True


class InstagramSlideshow:
    def __init__(self):
        self.window = tk.Tk()

        # set constants
        self.INSTAGRAM_ACCESS_TOKEN = "put your access token here"
        self.MOST_RECENT_PHOTOS_URL = "https://api.instagram.com/v1/users/self/media/recent/?access_token={}".format(self.INSTAGRAM_ACCESS_TOKEN)
        self.LOCAL_PHOTO_DIRECTORY_PATH = "./instagram_photos/"
        self.INI_FILE = "./instagram_slideshow.ini"
        self.PROGRAM_NAME = "Instagram Slideshow"
        self.HOUR_IN_MICROSECONDS = 60 * 60 * 1000
        self.window.SECONDS_BEFORE_CHANGING_PHOTO = 15
        self.window.PHOTO_DISPLAY_ORDER_DIRECTORY = "directory"
        self.window.PHOTO_DISPLAY_ORDER_RANDOM = "random"
        self.window.PHOTO_DISPLAY_ORDER_SORTED = "sorted"
        self.window.PHOTO_DISPLAY_ORDER = self.window.PHOTO_DISPLAY_ORDER_RANDOM

        # set up Tkinter for fullscreen display of photos
        self.fullscreen = True
        self.window.attributes("-fullscreen", self.fullscreen)
        self.window.config(cursor="none")
        self.WIDTH, self.HEIGHT = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        self.ASPECT_RATIO = self.WIDTH * 1.0 / self.HEIGHT
        self.window.title(self.PROGRAM_NAME)
        self.photo_label = tk.Label(self.window, bg="black")
        self.photo_label.pack(fill=tk.BOTH, expand=True)
        self.current_image = None
        self.current_image_index = -1
        self.window.bind('<Escape>', self.fullscreen_swap)
        self.window.preferences_changed = False

        # get configuration settings
        self.get_preferences_from_ini_file()

        # download any new photos, start slideshow
        self.download_any_new_instagram_photos()
        self.photos = self.get_photo_filenames()
        print("Starting slideshow.")
        self.show_photo()

    def create_menus(self):
        # create the pull-down menus you see if you press Esc to leave fullscreen mode
        menu = tk.Menu(self.window)
        file_menu = tk.Menu(menu)
        file_menu.add_command(label="Exit", command=self.window.quit)
        menu.add_cascade(label="File", menu=file_menu)
        edit_menu = tk.Menu(menu)
        edit_menu.add_command(label="Preferences...", command=self.open_preferences_dialog)
        menu.add_cascade(label="Edit", menu=edit_menu)
        view_menu = tk.Menu(menu)
        view_menu.add_command(label="Enter Fullscreen", command=self.fullscreen_swap)
        menu.add_cascade(label="View", menu=view_menu)

        return menu

    def fullscreen_swap(self, event=None):
        # toggles in and out of fullscreen mode so you can get to the Edit Preferences menu
        self.fullscreen = not self.fullscreen
        self.window.attributes("-fullscreen", self.fullscreen)

        # destroying or recreating the menu, because I haven't yet found a way
        # to just hide it in fullscreen mode on the Raspberry Pi :-(
        if self.fullscreen:
            self.menu.destroy()
            self.window.config(cursor="none")
        else:
            self.menu = self.create_menus()
            self.window.config(menu=self.menu)
            self.window.config(cursor="")

    def open_preferences_dialog(self):
        # open the Edit Preferences dialog box
        SlideshowPreferencesDialog(self.window, "Edit Preferences")
        # and if the user clicked OK and had changed any preferences
        if self.window.preferences_changed:
            self.photos = self.get_photo_filenames()
            self.update_ini_file()

    def get_preferences_from_ini_file(self):
        if os.path.isfile(self.INI_FILE):
            # if the .ini file exists, read in the configuration settings
            config = ConfigParser.RawConfigParser()
            config.read(self.INI_FILE)
            self.window.PHOTO_DISPLAY_ORDER = config.get("PhotoDisplaySettings", "photo_display_order")
            self.window.SECONDS_BEFORE_CHANGING_PHOTO = int(
                config.get("PhotoDisplaySettings", "seconds_before_changing_photo"))
        else:
            # or if it doesn't exist, create it with the default settings
            self.update_ini_file()

    def update_ini_file(self):
        # update the ini file either with the default settings the first time you run the program,
        # or any changes made via the Edit Preferences dialog box
        config = ConfigParser.RawConfigParser()
        ini_file = open(self.INI_FILE, 'w')
        config.add_section("PhotoDisplaySettings")
        config.set("PhotoDisplaySettings", "photo_display_order", self.window.PHOTO_DISPLAY_ORDER)
        config.set("PhotoDisplaySettings", "seconds_before_changing_photo", self.window.SECONDS_BEFORE_CHANGING_PHOTO)
        config.write(ini_file)
        ini_file.close()

    def download_any_new_instagram_photos(self):
        # create the instagram_photos subdirectory if it doesn't already exist
        if not os.path.isdir(self.LOCAL_PHOTO_DIRECTORY_PATH):
            os.mkdir(self.LOCAL_PHOTO_DIRECTORY_PATH)

        # get URLs, captions, etc. on the 20 most recent Instagram photos
        print("Checking for any new Instagram photos at {} ...".format(datetime.now()))
        internet_connection = True

        try:
            json_data = json.loads(requests.get(self.MOST_RECENT_PHOTOS_URL).text)
        except:
            internet_connection = False
            print("Unable to reach Instagram ... check your Internet connection. Showing stored photos.")

        if internet_connection:
            new_photos_downloaded = False

            # and check to see whether or not they have already been downloaded
            try:
                for photo in json_data["data"]:
                    image_url = photo["images"]["standard_resolution"]["url"]
                    image_link = photo["link"]
                    photo_filename = image_link.split('/')[4] + '.jpg'
                    if not os.path.isfile(self.LOCAL_PHOTO_DIRECTORY_PATH + photo_filename):
                        # save to disk any new photos that were not saved previously
                        new_photos_downloaded = True
                        if photo["caption"]:
                            print('Downloading and saving photo "{}"'.format(photo["caption"]["text"].encode("utf8")))
                        else:
                            print('Downloading and saving photo "{}"'.format(photo_filename))
                        photo_file = requests.get(image_url).content
                        with open(self.LOCAL_PHOTO_DIRECTORY_PATH + photo_filename, 'wb') as handler:
                            handler.write(photo_file)
            except:
                print("Instagram error:", json_data)

            if new_photos_downloaded:
                # update the list of jpg filenames in the Instagram Photos subdirectory
                self.get_photo_filenames()
            else:
                print("No new photos found.")

        # check for new photos once an hour
        self.window.after(self.HOUR_IN_MICROSECONDS, self.download_any_new_instagram_photos)

    def get_photo_filenames(self):
        # get all the jpg filenames in the instagram_photos subdirectory
        photo_filenames = [file for file in os.listdir(self.LOCAL_PHOTO_DIRECTORY_PATH) if file.endswith(".jpg")]

        if self.window.PHOTO_DISPLAY_ORDER == self.window.PHOTO_DISPLAY_ORDER_SORTED:
            photo_filenames.sort()

        if not photo_filenames:
            print("No stored photos found.")

        return photo_filenames

    def show_photo(self):
        if self.photos:
            # if there are any photos in the instagream_photos subdirectory,
            # open the next image and resize it to fit the screen
            if self.window.PHOTO_DISPLAY_ORDER in [self.window.PHOTO_DISPLAY_ORDER_DIRECTORY, self.window.PHOTO_DISPLAY_ORDER_SORTED]:
                self.current_image_index = (self.current_image_index + 1) % len(self.photos)
            elif self.window.PHOTO_DISPLAY_ORDER == self.window.PHOTO_DISPLAY_ORDER_RANDOM:
                self.current_image_index = random.randint(0, len(self.photos) - 1)

            with Image.open(self.LOCAL_PHOTO_DIRECTORY_PATH + self.photos[self.current_image_index]) as image:
                image_width, image_height = image.size
                image_aspect_ratio = image_width * 1.0 / image_height
                new_width, new_height = self.WIDTH, self.HEIGHT
                if image_aspect_ratio > self.ASPECT_RATIO:
                    new_height = image_height * self.WIDTH / image_width
                else:
                    new_width = image_width * self.HEIGHT // image_height
                image = image.resize((new_width, new_height), Image.ANTIALIAS)
                next_photo = ImageTk.PhotoImage(image)

            # and display it
            self.photo_label.configure(image=next_photo, text="", compound=tk.NONE)
            self.photo_label.image = next_photo

            # and on to the following photo after a delay
            self.window.after(self.window.SECONDS_BEFORE_CHANGING_PHOTO * 1000, self.show_photo)


# create an Instagram Slideshow instance, and start it up
slideshow = InstagramSlideshow()
slideshow.window.mainloop()
