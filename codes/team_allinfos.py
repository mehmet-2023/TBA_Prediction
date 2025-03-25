import pandas as pd
import tbapy

TBA_AUTH_KEY = "D58izqXU2LkInbiq8oBNgZIhzBrae8crytaz0OrSKegE5fypwATQ31Ibebx4l6yv".strip()
tba = tbapy.TBA(TBA_AUTH_KEY)

def get_team_performance(team_number):
    events = tba.team_events(f'frc{team_number}', year=2025)
    
    team_data = []
    
    for event in events:
        try:
            event_key = event['key']
            event_name = event['name']
            rankings = tba.event_rankings(event_key)
            oprs = tba.event_oprs(event_key)

            team_rank = None
            opr, dpr, ccwm = 0, 0, 0

            for r in rankings.get("rankings", []):
                if r["team_key"] == f"frc{team_number}":
                    team_rank = r["rank"]
                    break
                
            opr = oprs["oprs"].get(f"frc{team_number}", 0)
            dpr = oprs["dprs"].get(f"frc{team_number}", 0)
            ccwm = oprs["ccwms"].get(f"frc{team_number}", 0)

            team_data.append({
                "Event": event_name,
                "Rank": team_rank,
                "OPR": opr,
                "DPR": dpr,
                "CCWM": ccwm
            })
        except:
            print("")
    
    return pd.DataFrame(team_data)

team_number = int(input("Enter Team Number: "))
df = get_team_performance(team_number)
print(df)
