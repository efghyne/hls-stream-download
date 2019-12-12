# For parsing m3u8
import m3u8
# For HTTP communication
import requests
# Fancy output
import sys

# We need to spoof user agent, the site doesn't allow us to download as request
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"}
# Base server url (without the trailing slash, ex. https://example.com)
BASE_URL = ""
# Initial playlist URL (ex. /hls/playlist.m3u8)
INITIAL_PLAYLIST_URL = ""
# Output file name (will be in MPG format)
OUTPUT_FILE = "output.mpg"

# Get initial playlist
r = requests.get(BASE_URL + INITIAL_PLAYLIST_URL, headers=HEADERS)
# Parse initial playlist
m3u8_obj = m3u8.loads(r.text)

# Ensure that it's variant (points to other lists)
assert m3u8_obj.is_variant

# Show all available playlists to the user
for i in range(len(m3u8_obj.playlists)):
    print("Playlist {}".format(i))
    print("    Resolution: {}x{}".format(m3u8_obj.playlists[i].stream_info.resolution[0], m3u8_obj.playlists[i].stream_info.resolution[1]))
    print("    URI: {}".format(m3u8_obj.playlists[i].uri))
print("")
# Get user's selection (NOTE: program will crash if the input is invalid. (that means that the program isn't ready to be used by illiterate users)
selection = int(input("Your selection: "))

# Create output file object
output_file_object = open(OUTPUT_FILE, "wb")

# Get the non-variant playlist
r = requests.get(BASE_URL + m3u8_obj.playlists[selection].uri, headers=HEADERS)
# Parse it
m3u8_obj = m3u8.loads(r.text)
# Get the number of segments we have to download
num_segments = len(m3u8_obj.segments)

# Loop through the segments
for i in range(num_segments):
    # Download a segment
    r = requests.get(m3u8_obj.segments[i].uri, headers=HEADERS)

    # Write it to the file without the PNG prefix
    # 0x13B in hex equals to 315 in decimal
    output_file_object.write(r.content[0x13B:])

    # Update the stats on display
    sys.stdout.buffer.write("Downloaded segment {}/{}\r".format(i+1, num_segments).encode())
    sys.stdout.buffer.flush()

# Flush and close the file
output_file_object.flush()
output_file_object.close()

print("\n")
print("Download finished!")

