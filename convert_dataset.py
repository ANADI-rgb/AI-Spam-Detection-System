import pandas as pd

df = pd.read_csv("SMSSpamCollection", sep="\t", header=None)

df.columns = ["v1","v2"]

df.to_csv("dataset/spam.csv", index=False)

print("Dataset converted successfully!")