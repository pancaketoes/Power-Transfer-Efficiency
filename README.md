# Power-Transfer-Efficiency
(PTE) Dashboard

What It Is:

A Streamlit-powered dashboard that analyzes how efficiently MLB hitters convert bat speed into exit velocity. It introduces a custom metric, PTE, calculated as:

PTE = Exit Velocity / Bat Speed


This project combines Baseball Savant bat speed data with Statcast exit velocity to create player-specific, situation-specific insights.


Why It Matters:

Exit velocity alone doesn't tell the whole story. PTE highlights:

Efficient hitters vs. over-swingers, 

Who's producing power vs. who’s just swinging hard,

How efficiency changes vs. pitch types, counts, pitcher handedness, and location

It’s valuable for scouts, coaches, and analysts focused on player development and biomechanical performance.


What It Does:

Displays overall PTE for any player (2024 season)


Breaks PTE down by:

Pitch type, 

Pitch velocity, 

Count, 

Horizontal pitch location, 

Pitcher handedness, 

Visualizes all of it with clean bar charts using Seaborn


Run It Locally:

Clone the repo, 

Install dependencies: pip install -r requirements.txt, 

Run: streamlit run app.py, 

View dashboard in your browser at http://localhost:8501


Future Plans:

Simulated per-swing bat speed to improve PTE accuracy, 

PTE leaderboard across all players, 

Live hosted version on Streamlit Cloud, 

Long-term tracking: PTE over season, per game
