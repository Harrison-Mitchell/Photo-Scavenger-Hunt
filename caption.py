import os
import subprocess
from glob import glob
from challenges import CHALLENGES

# This is a helper utility to add a caption to the bottom of each image

os.makedirs("captioned", exist_ok=True)

# For each sorted photo upload
for i in sorted(glob("uploads/*_*")):
	# Strip uploads/ off the path
	i = i.replace("uploads/", "")

	# Print what image we're currently captioning
	caption = "Team " + i.split("_")[0].title() + ": " + CHALLENGES[int(i.split("_")[1].split(".")[0]) - 1].replace('"', '\\"')
	print(f"{i}|{caption}")

	# ImageMagick command to add the caption
	cmd = f'convert uploads/{i} -gravity South -background white -splice 0x150 -gravity South -fill black -font Arial -pointsize 80 -annotate +0+5 \"{caption}\" captioned/{i}'

	# Run the ImageMagick command
	_ = subprocess.run(cmd, shell=True, capture_output=True, text=True)