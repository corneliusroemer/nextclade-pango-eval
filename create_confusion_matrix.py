#%%
import pandas as pd
import numpy as np

#%%
# scp -rC roemer0001@login-transfer.scicore.unibas.ch:/scicore/home/neher/roemer0001/nextclade-full-run/pango-test/usher_clades_meta.tsv .
# Load data
# Create new dataframe with multi-index (designation, prediction) and (prediction, designation)
# Add columns: total of des, total of pred
# Output as csv
df = pd.read_csv('usher_clades_meta.tsv', sep='\t', index_col=0)
#%%
df = df[['date','Nextstrain_clade','pango_designated','inferred_lineage','lineage','lineage.1']]
df.rename(columns={'Nextstrain_clade':'clade','pango_designated':'designation','inferred_lineage':'nextclade','lineage':'usher','lineage.1':'pangolearn'}, inplace=True)
df
# %%
df.columns
# %%
df[df.nextclade != df.designation].groupby(['clade']).size()
# %%
df.groupby(['clade']).size()
# %%
df[df.usher != df.designation].groupby(['clade']).size()

# %%
df[df.pangolearn != df.designation].groupby(['clade']).size()

# %%
df[df.usher != df.designation]
# %%
df.groupby(['designation','nextclade']).size()
# %%
designation_counts = df.designation.value_counts()
nextclade_counts = df.nextclade.value_counts()

# %%
cm = df.groupby(['designation','nextclade']).size().to_frame().reset_index().join(designation_counts, on='designation', rsuffix='_total').join(nextclade_counts, on='nextclade',rsuffix='_total').sort_values(by=['designation_total','designation',0], ascending=False)
cm.rename(columns={0:'counts'}, inplace=True)
cm['d_share'] = cm.counts / cm.designation_total
cm['p_share'] = cm.counts / cm.nextclade_total
cm.to_csv('confusion_matrix_full.tsv', sep='\t', index=False, float_format='%.4f')
# %%
cm[cm.designation != cm.nextclade].to_csv('confusion_matrix_off_diagonal.tsv', sep='\t', index=False, float_format='%.4f')
cm[cm.designation == cm.nextclade].to_csv('confusion_matrix_diagonal.tsv', sep='\t', index=False, float_format='%.4f')
