# Photo Scavenger Hunt

A web app to allow youth groups to send leaders off with groups of kids to solve riddles to unlock photo scavenger hunt opportunities. I.e. a modern "chalk chase". Saves leaders from transferring photos from a number of devices with various picture formats + makes it more interactive and fun.

<p align="center">
  <img width="300" src="https://github.com/Harrison-Mitchell/Photo-Scavenger-Hunt/assets/17722100/ecbf3737-23d1-4a0f-9921-a4c109c107d7">
</p>

## Gameplay

- Teams must solve (get within 10 metres of) an initial riddle (which leads to a location) to unlock a bank of 10 photo scavenger hunt challenges
- When 3 or less challenges remain, the next riddle is unlocked to let teams unlock another 10 challenges
- At any time teams can review their photos and / or delete them to retake them
- Photos must be taken inline to save taking the photos separately and uploading them
	- Saves leaders flurrying to upload them all at the end, only to face troubles later
	- Ensures photos of kids aren't hanging around on leader phones

## Requirements

- High tech knowledge - requires running python on a VPS with a reverse proxy
- `python3` + flask (`pip3 install flask`)
- VPS + reverse proxy e.g. `nginx`

## Standing Up

1. Customise `challenges.py`
2. Customise `riddles.py` (replacing latitudes / longitudes with precise locations)
3. Change instances of `/randompath` to a... random path for "security" (there's otherwise no auth and it's open to the internet)
4. Stand up a reverse proxy e.g. for nginx you'll need to add:
	```
	location /randompath/ {
		rewrite ^/randompath(/.*)$ $1 break;
		proxy_pass http://localhost:5000;
	}
	```
5. Run `python3 app.py`

## Limitations

- Does not allow pre-taken photos to be uploaded (this is by design)
- There's no "proper" security, just a random path (if the server is only up for an hour - meh)
- It reloads the UI each submission / deletion etc. - no AJAX (meh, that messies the codebase, it's pure HTML/JS and text, it's cheap to reload / rerender)

## Notes

- There's a customisable status message to update teams as the challenge progresses (see: `templates/ui.html` just under `<body>`)
- `/last` can be used for debugging / seeing what the most recently uploaded photo is
- All uploads go to: `/uploads`
- Optional: add captions to images at the end with `python3 caption.py` (then check `captioned/`)
- Ensure there are (number of challenges / 10) riddles e.g. 6 riddles for 60 challenges
- You can edit the DB files directly to force apply a riddle if the GPS gets stuck
- GPSs can get unstuck by reloading, or switching to Google Maps app to force a GPS refresh
- IOS seems to default to blocking all Safari location requests, you may need to go to IOS settings and change that
- It's not robust / prod ready / fool proof - but if you know what you're doing to debug on the fly, go crazy
- Teams roughly take photos at a rate of one every 90 seconds. So for 60 minutes, plan for 40 challenges
- The web app assumes you're online at all times - be careful of underground / low reception challenges

## Monitoring

If you're going to have someone monitor the game for bugs etc. a few ideas:

- Run the app with the following to tail / save the flask log

	`python3 -u app.py 2>&1 | egrep -v '/testleader|/last' | tee -a app.log`
- Have a browser with a page auto reloader to watch `/last` to make sure images continue to come in
- If you don't trust that the server won't shatter and all images will be deleted mid-game, maintain a local copy

	`while true; do rsync -av --update --ignore-existing --progress -e "ssh -i key" user@IP:/home/user/chalkchase localchalkchasesync/ && sleep 60; done`
- Display a stats screen with: number of photos taken, the progress of each leader/database, and a curl to ensure the server is returning `200`s

	`while true; do clear && echo -n "Num total uploads: " && ls -lah uploads/ | wc -l && echo && tail -v -n +1 databases/* && echo && echo && curl https://127.0.0.1/randompath/testleader -k -I -X GET && sleep 3; done`
