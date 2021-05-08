import pandas as pd
import os
cwd= os.getcwd()
df = pd.read_csv(os.path.join(cwd, "dane", "test_instance.csv"),
                sep=";",
                names=["index","column1","column2","column3"]).fillna(0)
df["label"] = df["index"].apply(lambda x: x if not x.isnumeric() else pd.NA).fillna(method = "ffill")
print(df)
df = df[df["index"] != df["label"]]

demand = df.loc[df.label=="demand"].set_index('index').drop(['label'], axis=1)
workhours = df.loc[df.label=="workhours"].set_index('index').drop(['label'], axis=1)
vacation = df.loc[df.label=="vacation"].set_index('index').drop(['label'], axis=1)
preferred_companions = df.loc[df.label=="preferred_companions"].set_index('index').drop(['label'], axis=1)
unpreferred_companions = df.loc[df.label=="unpreferred_companions"].set_index('index').drop(['label'], axis=1)
preferred_shifts = df.loc[df.label=="preferred_shifts"].set_index('index').drop(['label'], axis=1)
unpreferred_shifts = df.loc[df.label=="unpreferred_shifts"].set_index('index').drop(['label'], axis=1)

if not os.path.exists('tabele'):
    os.makedirs('tabele')

names =['demand','workhours','vacation','preferred_companions','unpreferred_companions','preferred_shifts','unpreferred_shifts']
dfs = [demand,workhours,vacation,preferred_companions,unpreferred_companions,preferred_shifts,unpreferred_shifts]

for i in range(len(dfs)):
    dfs[i].to_csv(os.path.join(cwd, "tabele", names[i]+".csv"),header=False)
