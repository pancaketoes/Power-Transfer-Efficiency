import streamlit as st
import pandas as pd
from pybaseball import statcast_batter, playerid_lookup
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# -------------------- CONFIG --------------------
sns.set(style="whitegrid")
st.set_page_config(page_title="PTE Dashboard", layout="wide")

# -------------------- LOAD BAT SPEED CSV --------------------
bat_df = pd.read_csv("bat-tracking.csv")
bat_df.columns = bat_df.columns.str.strip()

# -------------------- PTE GRADING --------------------
def grade_pte(pte):
    if pte >= 1.20:
        return 'Elite'
    elif pte >= 1.15:
        return 'Above Average'
    elif pte >= 1.10:
        return 'Average'
    else:
        return 'Needs Improvement'

pitch_map = {
    'FF': 'Four-Seam Fastball',
    'SI': 'Sinker',
    'SL': 'Slider',
    'CU': 'Curveball',
    'CH': 'Changeup',
    'FC': 'Cutter',
    'FS': 'Splitter',
    'KC': 'Knuckle Curve',
    'KN': 'Knuckleball',
    'EP': 'Eephus',
    'FT': 'Two-Seam Fastball'
}

hand_map = {'L': 'Left-Handed', 'R': 'Right-Handed'}

def pitch_speed_group(speed):
    if speed >= 95:
        return "High Velo (95+)"
    elif speed >= 90:
        return "Medium Velo (90-94)"
    else:
        return "Low Velo (<90)"

def zone_group(x):
    if x < -0.5:
        return "Left Zone"
    elif x > 0.5:
        return "Right Zone"
    else:
        return "Middle Zone"

# -------------------- STREAMLIT SIDEBAR --------------------
st.sidebar.title("Select Player")
first = st.sidebar.text_input("First Name", "Aaron")
last = st.sidebar.text_input("Last Name", "Judge")

# -------------------- MAIN PROCESSING --------------------
try:
    player_row = playerid_lookup(last, first)
    player_id = int(player_row.iloc[0]["key_mlbam"])
    player_name = f"{first} {last}"
except:
    st.error("Could not find player ID. Check name spelling.")
    st.stop()

# Get average bat speed
csv_name_format = f"{last}, {first}"
player_bat = bat_df[bat_df['name'] == csv_name_format]

if player_bat.empty:
    st.error("Player not found in bat-tracking.csv.")
    st.stop()

avg_bat_speed = float(player_bat['avg_bat_speed'].values[0])

# Get statcast data
st.write(f"## PTE Dashboard for {player_name}")
with st.spinner("Fetching Statcast data..."):
    data = statcast_batter("2024-03-28", "2024-10-01", player_id)

if "launch_speed" not in data.columns:
    st.warning("No batted ball data available.")
    st.stop()

# Filter to valid swings
data = data.dropna(subset=["launch_speed"])
avg_ev = data["launch_speed"].mean()
overall_pte = avg_ev / avg_bat_speed

st.metric(label="Average Bat Speed", value=f"{avg_bat_speed:.2f} mph")
st.metric(label="Average Exit Velocity", value=f"{avg_ev:.2f} mph")
st.metric(label="Power Transfer Efficiency", value=f"{overall_pte:.3f}", delta=grade_pte(overall_pte))

# -------------------- VISUAL DASHBOARD --------------------
st.markdown("### PTE Breakdown by Scenario")

def make_barplot(df, x, y, title, xlabel, ylabel, palette="Blues_d", order=None):
    fig, ax = plt.subplots()
    sns.barplot(data=df, x=x, y=y, ax=ax, palette=palette, order=order)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    st.pyplot(fig)

# PTE by pitch type
pt = data.dropna(subset=["pitch_type"]).groupby("pitch_type")["launch_speed"].mean().reset_index()
pt["pitch_name"] = pt["pitch_type"].map(pitch_map)
pt["PTE"] = pt["launch_speed"] / avg_bat_speed
make_barplot(pt.sort_values("PTE", ascending=False), "PTE", "pitch_name",
             "PTE by Pitch Type", "Power Transfer Efficiency", "Pitch Type")

# PTE by velocity range
vdf = data.dropna(subset=["release_speed"]).copy()
vdf["velo_group"] = vdf["release_speed"].apply(pitch_speed_group)
vg = vdf.groupby("velo_group")["launch_speed"].mean().reset_index()
vg["PTE"] = vg["launch_speed"] / avg_bat_speed
make_barplot(vg, "velo_group", "PTE", "PTE by Pitch Velocity Range", "Pitch Velocity Group", "PTE", "Reds_d")

# PTE by count
cdf = data.dropna(subset=["balls", "strikes"]).copy()
cdf["count"] = cdf["balls"].astype(str) + "-" + cdf["strikes"].astype(str)
cg = cdf.groupby("count")["launch_speed"].mean().reset_index()
cg["PTE"] = cg["launch_speed"] / avg_bat_speed
make_barplot(cg.sort_values("count"), "count", "PTE", "PTE by Count", "Count", "PTE", "Purples_d")

# PTE by pitch location
zdf = data.dropna(subset=["plate_x"]).copy()
zdf["zone"] = zdf["plate_x"].apply(zone_group)
zg = zdf.groupby("zone")["launch_speed"].mean().reset_index()
zg["PTE"] = zg["launch_speed"] / avg_bat_speed
make_barplot(zg, "zone", "PTE", "PTE by Horizontal Zone", "Zone", "PTE", "Greens_d")

# PTE by handedness
hdf = data.dropna(subset=["p_throws"]).copy()
hdf["handedness"] = hdf["p_throws"].map(hand_map)
hg = hdf.groupby("handedness")["launch_speed"].mean().reset_index()
hg["PTE"] = hg["launch_speed"] / avg_bat_speed
make_barplot(hg, "handedness", "PTE", "PTE by Pitcher Handedness", "Pitcher Handedness", "PTE", "Oranges_d")
