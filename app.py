import os
import random
from glob import glob
from riddles import RIDDLES
from challenges import CHALLENGES
from flask import Flask, render_template, request, redirect, send_from_directory

# Create the flask app and root it in a random path for "security"
app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/randompath'

def readDB (leader):
    """Reads and returns the progress i.e. database text file for the given leader"""

    # Return a blank dataframe if the DB doesn't exist i.e first submission
    if not os.path.exists(f"databases/{leader}.txt"):
        return [[], []]
    
    # Otherwise, open the existing database then read and return the submissions and riddles
    with open(f"databases/{leader}.txt", "r") as db:
        submissions, solvedRiddles, *_ = [i.strip() for i in db.readlines()]
        if submissions:
            submissions = [int(i) for i in submissions.strip().split("|")] or []
        if solvedRiddles:
            solvedRiddles = [int(i) for i in solvedRiddles.strip().split("|")] or []
        return [submissions, solvedRiddles]

def writeDB (leader, submissions, solvedRiddles):
    """Updates the database i.e. progress text file with a newly solved riddle or submission"""

    with open(f"databases/{leader}.txt", "w") as db:
        db.write("|".join([str(i) for i in submissions]) + "\n" + 
                 "|".join([str(i) for i in solvedRiddles]))

@app.route('/')
def index():
    """If we hit the root, show the index template which captures the leader's name
    and redirects them to /leader_name as a lazy way of storing who is the current leader"""

    return render_template('index.html')

@app.route('/last')
def last():
    """Special endpoint for monitoring the newest picture submitted"""

    return send_from_directory("uploads", max(glob("uploads/*"), key=os.path.getctime).replace("uploads/", ""))

@app.route('/<leader>')
def ui(leader):
    """Prepare the main UI for the leader including current / complete riddles / challenges"""
    
    submissions, solvedRiddles = readDB(leader)
    submissionIDs = [*submissions]
    # Dictionary the ID and text for the JINJA UI to reference
    submissions = [{"id": i + 1, "text": text} for i, text in enumerate(submissions)]
    
    # Randomly shuffle challenges seeded to the leader
    challengeShuf = [*CHALLENGES]
    random.seed(leader)
    random.shuffle(challengeShuf)

    # Randomly shuffle riddles (other than the first shared one) seeded to the leader
    riddleKeys = list(RIDDLES.keys())[1:]
    random.shuffle(riddleKeys)
    riddlesKeys = [1, *riddleKeys]

    # Sanity check to not surpass the number of riddles
    if len(solvedRiddles) < len(riddlesKeys):
        # Turn the riddle into a dict for JINJA
        curRiddle = {
            "id": riddlesKeys[len(solvedRiddles)],
            "latlng": RIDDLES[riddlesKeys[len(solvedRiddles)]][0],
            "text": RIDDLES[riddlesKeys[len(solvedRiddles)]][1]
        }
    else:
        # Ensure there are enough riddles relative to challenges
        curRiddle = {"id": 0, "latlng": [-30, 151], "text": "YOU SHOULDN'T SEE THIS"}

    # Logic to show unlocked challenges, ignoring complete, relative to number of solved riddles
    curChallenges = []
    for challenge in challengeShuf[:10 * len(solvedRiddles)]:
        if CHALLENGES.index(challenge) + 1 not in submissionIDs:
            curChallenges.append({"id": CHALLENGES.index(challenge) + 1, "text": challenge})

    return render_template('ui.html', curChallenges=curChallenges, submissions=submissions, leader=leader, curRiddle=curRiddle)

@app.route('/riddle/<leader>/<int:riddleKey>', methods=['POST'])
def riddle(leader, riddleKey):
    """Commits solved riddles to the database"""

    submissions, solvedRiddles = readDB(leader)
    
    # Sanity check that the riddle is not already solved 
    if riddleKey not in solvedRiddles:
        writeDB(leader, submissions, [*solvedRiddles, riddleKey])

    # Redirect to main page to reload UI and mark riddle as solved
    return redirect(app.config['APPLICATION_ROOT'] + "/" + leader)

@app.route('/submit/<leader>/<int:challengeKey>', methods=['POST'])
def submit(leader, challengeKey):
    """Accept a submitted challenge image and commit it to the database and disk"""

    file = request.files['image']

    # Format the filename e.g. john_12.jpg and save to disk
    filename = f"{leader}_{challengeKey}.{file.filename.split('.')[-1]}"
    file.save(os.path.join("uploads", filename))

    # Get a fresh copy of the DB then commit an updated DB
    submissions, solvedRiddles = readDB(leader)
    writeDB(leader, [*submissions, challengeKey], solvedRiddles)

    # Once the image is posted, refresh the page to reload UI and show challenge complete
    return redirect(app.config['APPLICATION_ROOT'] + "/" + leader)

@app.route('/delete/<leader>/<int:submissionKey>', methods=['POST'])
def delete(leader, submissionKey):
    """Remove a deleted image from the database and disk"""

    submissions, solvedRiddles = readDB(leader)
    # Sanity check that the image does exist
    if submissionKey in submissions:
        os.remove(glob(f"uploads/{leader}_{submissionKey}.*")[0])
        submissions.remove(submissionKey)
        writeDB(leader, submissions, solvedRiddles)

    # Reload main page to refresh UI and show image deleted
    return redirect(app.config['APPLICATION_ROOT'] + "/" + leader)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Returns the rendered image (for previewing in the UI)"""
    
    return send_from_directory("uploads", glob(f"uploads/{filename}.*")[0][len("uploads/"):])

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("databases", exist_ok=True)
    app.run(debug=True, host="127.0.0.1", port=5000)
