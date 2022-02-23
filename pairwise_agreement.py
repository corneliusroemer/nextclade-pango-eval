#%%
import pandas as pd
import numpy as np

#%%
# scp -rC roemer0001@login-transfer.scicore.unibas.ch:/scicore/home/neher/roemer0001/nextclade-full-run/pango-test/usher_clades_meta.tsv .
# aws s3 cp s3://nextstrain-ncov-private/metadata.tsv.gz - | pigz -cd | tsv-select -H -f date,region,country,Nextstrain_clade,pango_lineage > meta_condensed.tsv

df = pd.read_csv('usher_clades_meta.tsv', sep='\t', usecols=['date','Nextstrain_clade','inferred_lineage','lineage','lineage.1'])
#%%
df.rename(columns={'Nextstrain_clade':'clade','inferred_lineage':'nextclade','lineage':'usher','lineage.1':'pangolearn'}, inplace=True)
df
#%%
# Create consensus if present and remove non-consensus rows
# def get_consensus(row):
#     if row.nextclade == row.pangolearn or row.nextclade == row.usher:
#         return row.nextclade
#     elif row.pangolearn == row.usher:
#         return row.pangolearn
#     return 'None'

# def full_consensus(row):
#     if row.nextclade == row.pangolearn and row.nextclade == row.usher:
#         return 'Yes'
#     return 'No'

# df['full_consensus'] = df.apply(full_consensus, axis=1)
#%%
# Overwrite designation with consensus to make code similar, this is a hack
# df['designation']=df.apply(get_consensus,axis=1)
# #%%
# df = df[df.designation != 'None']
# %%
# method = 'nextclade'
# method = 'usher'
date_start = '20210201'
# date_start = '20190201'
df

#%%
df.date = pd.to_datetime(df.date,errors='coerce')
df.dropna(subset=['date'], inplace=True)
df = df[df.date >= date_start]
df
#%%
# %%
df['nu'] = df.apply(lambda row: row.nextclade == row.usher, axis=1)
df['np'] = df.apply(lambda row: row.nextclade == row.pangolearn, axis=1)
df['up'] = df.apply(lambda row: row.usher == row.pangolearn, axis=1)
# %%
df

# %%
df.nu.value_counts()/df.shape[0]

# %%
df.np.value_counts()/df.shape[0]

# %%
df.up.value_counts()/df.shape[0]


# %%
