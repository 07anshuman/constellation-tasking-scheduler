import pandas as pd
df = pd.read_csv("/home/anshuman-shukla/constellation_schedular/outputs/log_Kinshasa_DefaultGS_ISS.csv")
print(df[(df['action'] == 'image') & (df['over_target'] == False)])
