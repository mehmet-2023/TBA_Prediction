import os
import tbapy
import subprocess

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

def download_youtube_video(url, save_path, filename):
    os.makedirs(save_path, exist_ok=True)
    output_path = os.path.join(save_path, filename)
    
    if os.path.exists(output_path):
        print(f"Zaten mevcut: {filename}")
        return
    
    print(f"İndiriliyor: {filename}")
    
    try:
        subprocess.run(["yt-dlp", "-f", "best", "-o", output_path, url], check=True)
        print(f"İndirildi: {filename}")
    except subprocess.CalledProcessError as e:
        print(f"Hata: {url} - {e}")

team_number = int(input("Takım numarası: "))
videos = get_team_match_videos(team_number)

for video in videos:
    folder_name = f"frc{team_number}"
    file_name = f"{video['event']}_match_{video['match']}.mp4"
    download_youtube_video(video["video_url"], folder_name, file_name)
