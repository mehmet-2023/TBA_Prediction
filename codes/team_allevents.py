import pandas as pd
import tbapy
import plotly.graph_objects as go

TBA_AUTH_KEY = "D58izqXU2LkInbiq8oBNgZIhzBrae8crytaz0OrSKegE5fypwATQ31Ibebx4l6yv".strip()
tba = tbapy.TBA(TBA_AUTH_KEY)

events = tba.team_events('frc180', year=2025)
event_keys = [event['key'] for event in events]

for event_key in event_keys:
    try:
        teams = tba.event_teams(event_key)
        rankings = tba.event_rankings(event_key)
        oprs = tba.event_oprs(event_key)

        team_numbers = []
        opr_values = []
        dpr_values = []
        ccwm_values = []
        rank_values = []

        for team in teams:
            team_num = team.team_number
            team_numbers.append(team_num)
            team_rank = None

            for r in rankings.get("rankings", []):
                if r["team_key"] == "frc" + str(team_num):
                    team_rank = r["rank"]
                    break
            rank_values.append(team_rank)

            team_opr = oprs["oprs"].get("frc" + str(team_num), 0)
            team_dpr = oprs["dprs"].get("frc" + str(team_num), 0)
            team_ccwm = abs(oprs["ccwms"].get("frc" + str(team_num), 0))

            opr_values.append(team_opr)
            dpr_values.append(team_dpr)
            ccwm_values.append(team_ccwm)

        df = pd.DataFrame({
            'Team Number': team_numbers,
            'OPR': opr_values,
            'DPR': dpr_values,
            'CCWM': ccwm_values,
            'Rank': rank_values
        })
        df = df.dropna(subset=['Rank'])

        fig = go.Figure(data=go.Scatter(
            x=df['OPR'],
            y=df['Rank'],
            mode='markers+text',
            marker=dict(
                size=20,
                color=df['Rank'],
                colorscale='Viridis',
                showscale=True
            ),
            text=df['Team Number'],
            textposition="top center",
            hovertemplate="Team %{text}<br>OPR: %{x}<br>Rank: %{y}<extra></extra>"
        ))
        fig.update_layout(
            title=f"{event_key.upper()} - Current Team Performance",
            xaxis_title="OPR (Individual Performance)",
            yaxis_title="Regional Rank",
            yaxis=dict(
                autorange=True,
                showgrid=True,
                zeroline=False,
                showline=True,
                linewidth=2,
                linecolor='black'
            ),
            xaxis=dict(
                range=[df['OPR'].min() - 10, df['OPR'].max() + 10],
                showgrid=True,
                zeroline=False,
                showline=True,
                linewidth=2,
                linecolor='black'
            ),
            hovermode="closest"
        )
        fig.show()
    except:
        print("exception")
