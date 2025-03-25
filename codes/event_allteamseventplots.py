import os
import pandas as pd
import tbapy
import matplotlib.pyplot as plt

# TBA API Anahtarı ve Bağlantı
TBA_AUTH_KEY = "D58izqXU2LkInbiq8oBNgZIhzBrae8crytaz0OrSKegE5fypwATQ31Ibebx4l6yv".strip()
tba = tbapy.TBA(TBA_AUTH_KEY)

# 2025tuhc etkinliğine katılan takımları al
teams_tuhc = tba.event_teams("2025flwp")

for team in teams_tuhc:
    team_no = team.team_number
    events = tba.team_events(team_no, 2025)

    for event in events:
        event_key = event.key
        rankings = tba.event_rankings(event_key)
        oprs = tba.event_oprs(event_key)

        # Verilerin toplanacağı listeler
        team_numbers = []
        opr_values = []
        dpr_values = []
        ccwm_values = []
        rank_values = []

        # OPR, DPR ve CCWM verilerini her takım için al
        for t in tba.event_teams(event_key):
            t_num = t.team_number
            team_numbers.append(t_num)

            # Takım sıralamasını al
            team_rank = None
            if "rankings" in rankings:
                for r in rankings["rankings"]:
                    if r["team_key"] == "frc" + str(t_num):
                        team_rank = r["rank"]
                        break
            rank_values.append(team_rank)

            # OPR, DPR ve CCWM verilerini güvenli bir şekilde al
            oprs_values = oprs.get("oprs", {})
            dprs_values = oprs.get("dprs", {})
            ccwms_values = oprs.get("ccwms", {})

            team_opr = oprs_values.get("frc" + str(t_num), 0)
            team_dpr = dprs_values.get("frc" + str(t_num), 0)
            team_ccwm = abs(ccwms_values.get("frc" + str(t_num), 0))

            opr_values.append(team_opr)
            dpr_values.append(team_dpr)
            ccwm_values.append(team_ccwm)

        # Verileri DataFrame'e çevir
        df = pd.DataFrame({
            "Team Number": team_numbers,
            "OPR": opr_values,
            "DPR": dpr_values,
            "CCWM": ccwm_values,
            "Rank": rank_values
        })

        # Rank değeri eksik olanları çıkar
        df = df.dropna(subset=["Rank"])

        # Grafik oluştur
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(df["OPR"], df["Rank"], c=df["Rank"], cmap="viridis", s=50, edgecolors="black", alpha=0.7)

        # Vurgulanan takım numarasını ayır
        highlight_team = team_no  # Bu takımı vurgulamak için

        # Takım numaralarını noktaların yanına yazdır
        for i, txt in enumerate(df["Team Number"]):
            # Eğer takım, vurgulanan takım ise farklı renk ve büyüklükte göster
            if df["Team Number"].iloc[i] == highlight_team:
                plt.annotate(txt, (df["OPR"].iloc[i], df["Rank"].iloc[i]), fontsize=12, ha='right', color='red', weight='bold')
            else:
                plt.annotate(txt, (df["OPR"].iloc[i], df["Rank"].iloc[i]), fontsize=8, ha='right', color='black')

        # Başlık ve etiketler
        plt.title(f"Performance in {event_key}", fontsize=14)
        plt.xlabel("OPR (Individual Performance)", fontsize=12)
        plt.ylabel("Regional Rank", fontsize=12)
        plt.colorbar(scatter, label="Rank")
        plt.grid(True)

        # Takım klasörünü oluştur ve görseli kaydet
        os.makedirs(f"frc{team_no}", exist_ok=True)
        plt.savefig(f"frc{team_no}/{event_key}.png", dpi=300, bbox_inches="tight")
        plt.close()
