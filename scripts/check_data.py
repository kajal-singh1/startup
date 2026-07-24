import pandas as pd

for code in ["GOV_WGI_GE.EST", "GOV_WGI_RQ.EST", "GOV_WGI_RL.EST",
             "GOV_WGI_CC.EST", "GOV_WGI_PV.EST", "GOV_WGI_VA.EST"]:
    df = pd.read_csv(f"data/raw/world_bank/{code}.csv")
    print(code, "min:", df["value"].min(), "max:", df["value"].max())


df = pd.read_csv("data/raw/world_bank/EN.GHG.CO2.PC.CE.AR5.csv")
print(df[df["country_code"] == "USA"].sort_values("year").tail(10))
print(df[df["country_code"] == "IND"].sort_values("year").tail(10))
