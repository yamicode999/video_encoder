import libtorrent as lt
import time
import subprocess
import requests
import os
import zipfile
from pyrogram import filters, Client
from config import *

app = Client(
    name="mybot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)


@app.on_message(filters.document)
def starting(client, message):
    subtitle_path = message.document.file_name
    message.download(file_name=subtitle_path)
    subtitle_path = os.path.join("downloads", subtitle_path)

    def download_torrent(torrent_link):
        # Download the .torrent file
        response = requests.get(torrent_link, allow_redirects=True)
        torrent_file_path = "temp.torrent"
        with open(torrent_file_path, 'wb') as file:
            file.write(response.content)

        # Start downloading video using the .torrent file
        ses = lt.session()
        info = lt.torrent_info(torrent_file_path)
        h = ses.add_torrent({'ti': info, 'save_path': './'})
        print('downloading', h.name())
        while not h.is_seed():
            s = h.status()
            print('%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % (
                s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
                s.num_peers, s.state))
            time.sleep(1)
        print("Download complete!")
        return h.name()

    def encode_video(input_path, output_path, subtitle_path):
        # Set the FONTCONFIG_PATH to the directory containing the fonts
        os.environ['FONTCONFIG_PATH'] = './fonts/font/'
        command = [
            'ffmpeg',
            '-i', input_path,
            '-vf', f'subtitles={subtitle_path}:fontsdir=./fonts/font/,scale=1920:-1',
            '-c:v', 'h264_nvenc',
            '-c:a', 'copy',
            '-preset', 'fast',
            '-crf', '24',
            '-f', 'mp4',
            output_path
        ]
        subprocess.run(command)

    # Prompt user to provide torrent link
    torrent_link = input("Please paste your torrent link here: ")

    # Download the video using the provided torrent link
    downloaded_video = download_torrent(torrent_link)

    # Download font.zip from Dropbox (or any other file-sharing platform)
    print("\nDownloading fonts from Dropbox...")
    font_dropbox_link = 'https://www.dropbox.com/scl/fi/2kgo8sp3lvdkiv05tge3g/font.zip?rlkey=3ld2d98443woar49z2qa4c19u&dl=1'  # Replace with your actual direct download link
    r = requests.get(font_dropbox_link, allow_redirects=True)
    font_zip_path = 'font.zip'
    with open(font_zip_path, 'wb') as f:
        f.write(r.content)

    # Extract the downloaded ZIP file
    with zipfile.ZipFile(font_zip_path, 'r') as zip_ref:
        zip_ref.extractall('fonts/')

    # Define the name for the encoded video, ensuring it's in .mp4 format
    output_video_name = "encoded_" + downloaded_video.split('.')[0] + '.mp4'

    # Perform the encoding using the custom fonts
    encode_video(downloaded_video, output_video_name, subtitle_path)

    # Offer the encoded video for download
    print("\nDownload your encoded video:")
    client.send_video(message.chat.id, output_video_name, supports_streaming=True)


if __name__ == "__main__":
    print("Yami Code Academy.")
    print("Bot Started!")
    app.run()
