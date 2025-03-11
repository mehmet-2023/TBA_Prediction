import pandas as pd
import tbapy
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

TBA_AUTH_KEY = "D58izqXU2LkInbiq8oBNgZIhzBrae8crytaz0OrSKegE5fypwATQ31Ibebx4l6yv".strip()
tba = tbapy.TBA(TBA_AUTH_KEY)

event_key = "2025tuis2"

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
    for r in rankings["rankings"]:
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


X = df[['OPR', 'DPR', 'CCWM']]
y = df['Rank']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)


X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

#AI BASED ALGORITHYM
model = MLPRegressor(hidden_layer_sizes=(64, 32), activation='relu', solver='adam',
                      max_iter=1000, random_state=42)
model.fit(X_train, y_train)


y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)


future_predictions = model.predict(X_scaled)


fig_current = go.Figure(data=go.Scatter(
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
fig_current.update_layout(
    title="Current Team Performance",
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

# Geleceğe yönelik tahmin grafiği
fig_future = go.Figure(data=go.Scatter(
    x=df['OPR'],
    y=future_predictions,
    mode='markers+text',
    marker=dict(
        size=20,
        color=future_predictions,
        colorscale='Blues',
        showscale=True
    ),
    text=df['Team Number'],
    textposition="top center",
    hovertemplate="Team %{text}<br>OPR: %{x}<br>Predicted Rank: %{y}<extra></extra>"
))
fig_future.update_layout(
    title="Future Team Performance Prediction (AI Model)",
    xaxis_title="OPR (Individual Performance)",
    yaxis_title="Predicted Regional Rank",
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


fig_current.show()
fig_future.show()
