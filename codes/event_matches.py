import os
import subprocess
import tbapy

TBA_AUTH_KEY = "D58izqXU2LkInbiq8oBNgZIhzBrae8crytaz0OrSKegE5fypwATQ31Ibebx4l6yv".strip()
tba = tbapy.TBA(TBA_AUTH_KEY)

def get_team_match_videos(team_number):
    events = tba.team_events(f'frc{team_number}', year=2025)
    match_videos = []
    
    for event in events:
        event_key = event['key']
        matches = tba.team_matches(f'frc{team_number}', event_key)
        
        for match in matches:
            if 'videos' in match and match['videos']:
                for video in match['videos']:
                    if video['type'] == 'youtube':
                        match_videos.append({
                            "match": match["match_number"],
                            "event": event["key"],
                            "video_url": f"https://www.youtube.com/watch?v={video['key']}"
                        })
    
    return match_videos

def download_youtube_video(url, folder, filename):
    os.makedirs(folder, exist_ok=True)
    output_path = os.path.join(folder, filename)
    try:
        subprocess.run(["yt-dlp", "-f", "best", "-o", output_path, url], check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Video indirilemedi ({url})")

def get_event_teams(event_key):
    teams = tba.event_teams(event_key)
    return [team["team_number"] for team in teams]

event_key = "2025flwp"
teams = get_event_teams(event_key)

for team in teams:
    videos = get_team_match_videos(team)
    for video in videos:
        folder_name = f"frc{team}"
        file_name = f"{video['event']}_match_{video['match']}.mp4"
        print(f"İndiriliyor: {file_name}")
        download_youtube_video(video["video_url"], folder_name, file_name)
