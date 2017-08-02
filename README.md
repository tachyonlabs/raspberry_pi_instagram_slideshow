# Raspberry Pi Instagram Slideshow

I'm a volunteer at the [Idea Fab Labs](https://santacruz.ideafablabs.com/) maker/hacker/artspace here in Santa Cruz, and I was asked to set up a Raspberry Pi with a large TV by the front entrance so that all you had to do was plug it in and it would start running a slideshow of [Idea Fab Labs' Instagram feed](https://www.instagram.com/ideafablabs/). I wrote the slideshow program in Python (Python 2, but Python 3 should be much the same) using the Tkinter GUI interface, on a Raspberry Pi 2 Model B running Raspbian Wheezy.

If you'd like to do something similar with your own Instagram feed, the instructions below will walk you through getting the slideshow set up on your Raspberry Pi.

Because (at least as of August 2017) the Instagram API in [Sandbox Mode](https://www.instagram.com/developer/sandbox/) only gets the 20 most recent photos from an Instagram account, and in the interest of both reducing bandwidth and being able to run the slideshow even when your internet connection is down, once an hour the program checks Instagram to see if any new photos have been posted to the account, and if so, downloads them to its `instagram_photos` directory. If you like you can also copy other jpg files to the directory and they will also be included in the slideshow -- for that matter I used the [InstaG Downloader Chrome Extension](https://chrome.google.com/webstore/detail/instag-downloader/jnkdcmgmnegofdddphijckfagibepdlb?hl=en) to download all the photos from the Idea Fab Labs Instagram feed that were older than the 20 most recent, so they would be in the `instagram_photos` directory too.

You can configure whether the slideshow displays photos in either random order or the order they are in the `instagram_photos` directory (the default is random), and/or configure how long the slideshow displays each photo before moving on to the next (the default is 15 seconds), by pressing `Esc` to exit fullscreen mode, and then selecting `Preferences ...` from the `Edit` pull-down menu. After making configuration changes, click `OK`, and then return to fullscreen display by either pressing `Esc` again or selecting `Enter Fullscreen` from the `View` pulldown menu.

More features later ...

## Getting the slideshow set up on your Raspberry Pi
Follow these instructions to get the slideshow set up and working on your Raspberry Pi:

1. **Set your Raspberry Pi to autologin into the GUI if it doesn't already**

    The slideshow runs in the Raspberry Pi GUI, so follow these instructions to set your Raspberry Pi to autologin to the GUI if it isn't already doing it: https://raspberrypi.stackexchange.com/questions/7261/how-to-set-my-raspberry-pi-to-boot-into-the-gui

2. **Configure your Raspberry Pi to connect to your Wifi if you haven't done so already**

    To download Instagram photos (or for that matter to follow the instructions link in the previous step) your Raspberry Pi needs to be connected to the Internet. If you haven't already done so, in the Raspberry Pi GUI Menu select `Preferences` and then `WIFI Configuration`, and then you can select your Wifi network and enter the password.

3. **Do a general update of your Raspberry Pi software if you haven't done so recently**

    To install updates to your Raspberry Pi, in a terminal window, run
    ```
    sudo apt-get update
    ```

4. **Install python-dev and python-setuptools if you haven't done so already**

    The slideshow is written in Python, and before you can install Python libraries for talking with the Instagram API and displaying photos you will need to install python-dev and python-setuptools if you haven't already done so. Enter the following into a terminal window:
    ```
    sudo apt-get install python-dev python-setuptools
    ```
5. **Install pip (the Python package manager) if you haven't done so already**

    Type the following into a terminal window:
    ```
    sudo apt-get install python-pip
    ```

6. **Install the Python requests library**

    The slideshow uses the Python requests library to talk to the Instagram API -- install it by entering the following into a terminal window:
    ```
    sudo pip install requests
    ```

7. **Install a library for handling JPEG images**

    Instagram photos are downloaded as JPEG images, so type the following into a terminal window:
    ```
    sudo apt-get install libjpeg8-dev
    ```

8. **Install the Pillow Python Imaging Library**

    The slideshow uses the Pillow library to display the Instagram photos, so install Pillow by entering the following into a terminal window:
    ```
    sudo pip install Pillow
    ```
    You may get error messages about missing libraries for other image formats, but right now we're only concerned that the JPEG library in step 7 was installed.

9. **Create a directory for the slideshow, and copy the files from this repo into it**

    Create a directory `raspberry_pi_instagram_slideshow` in the `/home/pi/` directory, and copy the files `instagram_slideshow.py`, `tkSimpleDialog.py`, and `instagram_slideshow.bat` from this repo into it. (Or if you prefer you can use a different slideshow directory name and/or location, adjusting its name/location in subsequent steps accordingly.)

10. **Make `instagram_slideshow.bat` executable.**

    Make the file `instagram_slideshow.bat` executable by entering the following into a terminal window:
    ```
    chmod 755 /home/pi/raspberry_pi_instagram_slideshow/instagram_slideshow.bat
    ```

11. **Get the Instagram access token for the account you want to use with the slideshow, and enter it into the slideshow code**

    There are other ways to download Instagram photos than their API, but I used their API. When I was using the Instagram API for another project last year, all you needed to do to download photos from an account was to register as a developer and get a client id, but now you have to go through a lot more steps to generate an access token for the account you want to access. To get the access token I followed the instructions on this [How to get Instagram API access token and fix your broken feed](https://github.com/adrianengine/jquery-spectragram/wiki/How-to-get-Instagram-API-access-token-and-fix-your-broken-feed) page, and as I do some Django development I used the Django development server (as `python manage.py runserver 0.0.0.0:8000` on my Windows system) in their "your favorite MAMP, LAMP, Node whatever you use to create a local server" step.

    When you get the access token you need, use a text editor to substitute it for "put your access token here" in the line `self.INSTAGRAM_ACCESS_TOKEN = "put your access token here"` in `instagram_slideshow.py`.

12. **Set the Raspberry Pi to run the slideshow automatically after the GUI loads**

    The issue here is that you want the program to run not only after the Raspberry Pi boots, but after the GUI loads. What worked for me was following the instructions in one of the posts in the [How to launch programs on LXDE startup](https://www.raspberrypi.org/forums/viewtopic.php?f=27&t=11256) topic in the raspberypi.org forums, doing
    ```
    sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
    ```
    to edit the autostart file, adding the line
    ```
    @/home/pi/raspberry_pi_instagram_slideshow/instagram_slideshow.bat
    ```
    to the end of the file, and saving it.

    Again, this is with a Raspberry Pi 2 Model B running Raspbian Wheezy. I haven't tested it with Raspbian Jessie yet, so it's possible that with Jessie you will need to use a different technique.

13. **Disable the Raspberry Pi screensaver**

    It's great to be have the Raspberry Pi set up so that all you have to do is plug it in and the slideshow will start, without needing to have a keyboard and/or mouse connected, but pretty sad if the slideshow only lasts for ten or fifteen minutes until the screensaver blanks the screen. :-( What worked for me was following the "2 – Disabling the blank screen forever" instuctions in this [How to Disable the Blank Screen on Raspberry Pi (Raspbian)](http://www.geeks3d.com/hacklab/20160108/how-to-disable-the-blank-screen-on-raspberry-pi-raspbian/) HackLab post.

    Again, this is with a Raspberry Pi 2 Model B running Raspbian Wheezy. I haven't tested it with Raspbian Jessie yet, so it's possible that with Jessie you will need to use a different technique.

## Running the slideshow on your Raspberry Pi

Once you've followed all the above steps, reboot your Raspberry Pi, and after the GUI starts the slideshow should start running automatically.

The first time you run the slideshow, it will create an `instagram_photos` subdirectory, and you will see messages about photos being downloaded in a terminal window before it starts displaying the photos.

If instead of showing messages about downloading photos, it immediately blanks the screen, this means that it was not able to download any photos to display due to not having a connection to the Internet (if there's no Internet connection the slideshow will just display stored photos, but to get stored photos in the first place you need to be connected to the Internet) or there being a problem with your Instagram access token. To see what's going on, use Alt-Tab to switch to the terminal window and see the status messages.

If at any point you want to close the slideshow, here are two ways to do it:

* Do an `Alt-Tab` to switch to the terminal window, and then do a `Ctrl-C` to close the slideshow but leave the terminal window open, or just close the terminal window to close both of them.

* Press `Esc` to get out of fullscreen mode, and then you can either (1) select `Exit` from the `File` pull-down menu, (2) click the `X` close button at the top-right of the slidehow window, or (3) do a `Ctrl-C` from the terminal window or close the terminal window.
