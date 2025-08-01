# Så här kör du programmet i PowerShell:
# 1. Öppna PowerShell
# 2. Navigera till mappen där filen ligger, t.ex.:
#    cd C:\Users\Gräddskålen
# 3. Kör programmet:
#    


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Tjänstepension med löneväxling", layout="wide")

# Avtalsvillkor (procent upp till 7.5 IBB, över 7.5 IBB)
AVTAL = {
    "BTP1 (bank)":               {"under": 0.065, "over": 0.32},
    "ITP1 (privat tjänsteman)":  {"under": 0.045, "over": 0.30},
    "SAF-LO (privat arbetare)":  {"under": 0.05,  "over": 0.00},
    "PA 16 Avd I (statlig)":     {"under": 0.025, "over": 0.20},
    "AKAP-KR (kommun/region)":   {"under": 0.06,  "over": 0.315}
}

# Avtalsinformation för visning högst upp
AVTALSINFO = {
    "BTP1 (bank)": """
**BTP1 (bankanställda)**  
6,5 % upp till 7,5 IBB (≈ 50 375 kr/mån)  
32 % på lönedelar mellan 7,5 IBB och 30 IBB (≈ 201 500 kr/mån)
""",
    "ITP1 (privat tjänsteman)": """
**ITP 1 (privatanställda tjänstemän)**  
4,5 % av lön upp till 7,5 IBB (≈ 50 375 kr/mån)  
30 % på lönedelar mellan 7,5 IBB och 30 IBB (≈ 201 500 kr/mån)
""",
    "SAF-LO (privat arbetare)": """
**SAF‑LO (privatanställda arbetare)**  
Standard är 5 % av lön upp till 7,5 IBB (≈ 50 375 kr/mån)  
Nivån höjs successivt till 6 % under en övergångsperiod
""",
    "PA 16 Avd I (statlig)": """
**PA 16 Avdelning I (statligt anställda födda 1988 eller senare)**  
2,5 % av lön upp till 7,5 IBB (≈ 50 375 kr/mån)  
20 % på lön över 7,5 IBB (upp till 30 IBB ≈ 201 500 kr/mån)
""",
    "AKAP-KR (kommun/region)": """
**AKAP‑KR (kommuner och regioner)**  
6 % av lön upp till 7,5 IBB (≈ 50 375 kr/mån)  
31,5 % på lönedelar över 7,5 IBB (upp till 30 IBB ≈ 201 500 kr/mån)
"""
}

def pension_growth(startkapital, manadslon, avkastning, ar,
                   basbelopp=80600, lonetillvaxt=0.02,
                   lonevaxling=0, ag_tillagg=0.06,
                   avtal=None):
    saldo = startkapital
    data = []

    under_proc = AVTAL[avtal]["under"]
    over_proc = AVTAL[avtal]["over"]

    for ar_nr in range(1, ar + 1):
        ars_lon = manadslon * 12

        under_grans = min(ars_lon, 7.5 * basbelopp) * under_proc
        over_grans = max(0, ars_lon - 7.5 * basbelopp) * over_proc
        bankavtal_insattning = under_grans + over_grans

        lonevaxling_insattning = lonevaxling * 12 * (1 + ag_tillagg)
        ars_insattning = bankavtal_insattning + lonevaxling_insattning

        saldo += ars_insattning
        saldo *= (1 + avkastning / 100)

        data.append([
            ar_nr, round(saldo), round(bankavtal_insattning),
            round(lonevaxling_insattning), round(ars_insattning)
        ])
        manadslon *= (1 + lonetillvaxt)
        lonevaxling *= (1 + lonetillvaxt)

    df = pd.DataFrame(data, columns=[
        "År", "Kapital", "Bankavtal", "Löneväxling", "Totalt"
    ])
    return df

def plot_comparison(df_med, df_utan, startkapital):
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(df_med["År"], df_med["Kapital"], marker='o', label="Med löneväxling")
    ax.plot(df_utan["År"], df_utan["Kapital"], marker='o', linestyle='--', label="Utan löneväxling", color='gray')
    ax.axhline(y=startkapital, color='r', linestyle=':', label="Startkapital")

    ax.set_xlabel("År")
    ax.set_ylabel("Kapital (kr)")
    ax.set_title("Utveckling av tjänstepension – med vs. utan löneväxling")
    ax.grid(True)
    ax.legend()
    return fig

# 🎛️ Sidopanel
st.sidebar.header("Inmatning")

avtal = st.sidebar.selectbox(
    "Avtalsområde",
    list(AVTAL.keys()),
    index=0
)

startkapital = st.sidebar.number_input("Startkapital (kr)", value=2_200_000, step=100000)
manadslon = st.sidebar.number_input("Månadslön (kr)", value=50000, step=1000)
avkastning = st.sidebar.number_input("Avkastning (% per år)", value=8.0, step=0.1)
ar = st.sidebar.number_input("Antal år", value=13, step=1)
lonevaxling = st.sidebar.number_input("Löneväxling (kr/mån)", value=500, step=500)
ag_tillagg = st.sidebar.number_input("AG-tillägg (%)", value=6.0, step=0.1)
lonetillvaxt = st.sidebar.number_input("Lönetillväxt (% per år)", value=2.0, step=0.1)

# 📊 Beräkning
df_med = pension_growth(
    startkapital=startkapital,
    manadslon=manadslon,
    avkastning=avkastning,
    ar=ar,
    lonevaxling=lonevaxling,
    ag_tillagg=ag_tillagg / 100,
    lonetillvaxt=lonetillvaxt / 100,
    avtal=avtal
)

df_utan = pension_growth(
    startkapital=startkapital,
    manadslon=manadslon,
    avkastning=avkastning,
    ar=ar,
    lonevaxling=0,
    ag_tillagg=ag_tillagg / 100,
    lonetillvaxt=lonetillvaxt / 100,
    avtal=avtal
)

# 📝 Visa avtalsinformation högst upp
st.markdown(AVTALSINFO[avtal])

# 🧾 Visa tabell och skillnad
st.header(f"Utveckling av tjänstepension ({avtal})")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Med löneväxling")
    st.dataframe(df_med.style.format(thousands=" ", precision=0), use_container_width=True)

with col2:
    st.subheader("Utan löneväxling")
    st.dataframe(df_utan.style.format(thousands=" ", precision=0), use_container_width=True)

# 💡 Skillnad på slutkapital
diff = df_med["Kapital"].iloc[-1] - df_utan["Kapital"].iloc[-1]
st.markdown(f"### Skillnad på slutkapital: **{diff:,.0f} kr**")

# 📈 Graf
st.pyplot(plot_comparison(df_med, df_utan, startkapital))
