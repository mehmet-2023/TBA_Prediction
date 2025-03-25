import pandas as pd
import tbapy
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
import time

TBA_AUTH_KEY = "D58izqXU2LkInbiq8oBNgZIhzBrae8crytaz0OrSKegE5fypwATQ31Ibebx4l6yv".strip()
tba = tbapy.TBA(TBA_AUTH_KEY)


training_event_key = "2025tuhc"
teams_train = tba.event_teams(training_event_key)
rankings_train = tba.event_rankings(training_event_key)
oprs_train = tba.event_oprs(training_event_key)

train_team_numbers = []
train_oprs = []
train_dprs = []
train_ccwms = []
train_ranks = []

for team in teams_train:
    team_num = team.team_number
    train_team_numbers.append(team_num)
    
    team_rank = None
    for r in rankings_train["rankings"]:
        if r["team_key"] == "frc" + str(team_num):
            team_rank = r["rank"]
            break
    train_ranks.append(team_rank)

    team_opr = oprs_train["oprs"].get("frc" + str(team_num), 0)
    team_dpr = oprs_train["dprs"].get("frc" + str(team_num), 0)
    team_ccwm = abs(oprs_train["ccwms"].get("frc" + str(team_num), 0))
    
    train_oprs.append(team_opr)
    train_dprs.append(team_dpr)
    train_ccwms.append(team_ccwm)

df_train = pd.DataFrame({
    "Team Number": train_team_numbers,
    "OPR": train_oprs,
    "DPR": train_dprs,
    "CCWM": train_ccwms,
    "Rank": train_ranks
}).dropna(subset=["Rank"])

X_train_data = df_train[["OPR", "DPR", "CCWM"]]
y_train_data = df_train["Rank"]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_data)

model = MLPRegressor(hidden_layer_sizes=(64, 32), activation='relu', solver='adam',
                      max_iter=1000, random_state=42)
model.fit(X_train_scaled, y_train_data)

train_preds = model.predict(X_train_scaled)
train_mse = mean_squared_error(y_train_data, train_preds)
print("Training MSE:", train_mse)

regional_event_key = "2025flwp" 
teams_regional = tba.event_teams(regional_event_key)

def get_team_avg_metrics(team_key, current_event_key, year="2025"):
    try:
        events = tba.team_events(team_key, year=year)
    except Exception:
        return 0, 0, 0
    opr_list, dpr_list, ccwm_list = [], [], []
    for event in events:
        if event.get("key") == current_event_key:
            continue
        try:
            event_oprs = tba.event_oprs(event["key"])
            if team_key in event_oprs["oprs"]:
                opr_list.append(event_oprs["oprs"][team_key])
                dpr_list.append(event_oprs["dprs"][team_key])
                ccwm_list.append(abs(event_oprs["ccwms"][team_key]))
        except Exception:
            continue
        time.sleep(0.2)
    if opr_list:
        return np.mean(opr_list), np.mean(dpr_list), np.mean(ccwm_list)
    else:
        return 0, 0, 0

regional_team_numbers = []
regional_oprs = []
regional_dprs = []
regional_ccwms = []

for team in teams_regional:
    team_key = "frc" + str(team.team_number)
    regional_team_numbers.append(team.team_number)
    avg_opr, avg_dpr, avg_ccwm = get_team_avg_metrics(team_key, regional_event_key, year="2025")
    regional_oprs.append(avg_opr)
    regional_dprs.append(avg_dpr)
    regional_ccwms.append(avg_ccwm)

df_regional = pd.DataFrame({
    "Team Number": regional_team_numbers,
    "OPR": regional_oprs,
    "DPR": regional_dprs,
    "CCWM": regional_ccwms
})


X_regional = df_regional[["OPR", "DPR", "CCWM"]]
X_regional_scaled = scaler.transform(X_regional)
predicted_ranks = model.predict(X_regional_scaled)
df_regional["Predicted Rank"] = predicted_ranks

print(df_regional)


fig = go.Figure(data=go.Scatter(
    x = df_regional["OPR"],
    y = predicted_ranks,
    mode='markers+text',
    marker=dict(
        size=20,
        color=predicted_ranks,
        colorscale='Blues',
        showscale=True
    ),
    text = df_regional["Team Number"],
    textposition="top center",
    hovertemplate="Team %{text}<br>Avg. OPR: %{x}<br>Predicted Rank: %{y}<extra></extra>"
))
fig.update_layout(
    title="Regional Etkinliği Öncesi Takım Performansı Tahminleri",
    xaxis_title="Geçmiş Etkinliklerden Ortalama OPR",
    yaxis_title="Tahmin Edilen Final Sıralaması",
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=False,
        showline=True,
        linewidth=2,
        linecolor='black'
    ),
    xaxis=dict(
        range=[df_regional["OPR"].min() - 10, df_regional["OPR"].max() + 10],
        showgrid=True,
        zeroline=False,
        showline=True,
        linewidth=2,
        linecolor='black'
    ),
    hovermode="closest"
)
fig.show()
