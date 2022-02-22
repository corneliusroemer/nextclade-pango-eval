#%%
import pandas as pd
import numpy as np

#%%
# scp -rC roemer0001@login-transfer.scicore.unibas.ch:/scicore/home/neher/roemer0001/nextclade-full-run/pango-test/usher_clades_meta.tsv .
# aws s3 cp s3://nextstrain-ncov-private/metadata.tsv.gz - | pigz -cd | tsv-select -H -f date,region,country,Nextstrain_clade,pango_lineage > meta_condensed.tsv
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

#%%
#%%
class Aliasor:
    def __init__(self, alias_file='../pango-designation/pango_designation/alias_key.json'):
        import pandas as pd

        aliases = pd.read_json(alias_file)

        self.alias_dict = {}
        for column in aliases.columns:
            if column.startswith('X'):
                self.alias_dict[column] = column
            else:
                self.alias_dict[column] = aliases[column][0]

        self.alias_dict['A'] = 'A'
        self.alias_dict['B'] = 'B'

        self.realias_dict = {v: k for k, v in self.alias_dict.items()}

    def compress(self,name):
        name_split = name.split('.')
        if len(name_split) < 5:
            return name
        letter = self.realias_dict[".".join(name_split[0:4])]
        if len(name_split) == 5:
            return letter + '.' + name_split[4]
        else:
            return letter + '.' + ".".join(name_split[4:])

    def uncompress(self,name):
        name_split = name.split('.')
        letter = name_split[0]
        unaliased = self.alias_dict[letter]
        if len(name_split) == 1:
            return name
        if len(name_split) == 2:
            return unaliased + '.' + name_split[1]
        else:
            return unaliased + '.' + ".".join(name_split[1:])

aliasor = Aliasor()

def get_pango_relation(true:str, pred:str):
    # First dealias both
    # Maybe make this a method of aliasor? Or pass it in
    # (B.1, B.1) -> (0,0)
    # (B.1, B.1.7) -> (0,1)
    # (B.1.7, B.1) -> (1,0)
    # (B.1.7, B.1.5) -> (1,1)

    # Or dealias the lineages already as a series

    ts = aliasor.uncompress(true).split(".")
    ps = aliasor.uncompress(pred).split(".")
    for ix, (t,p) in enumerate(zip(ts,ps),1):
        if t != p:
            ix -= 1
            break
    
    return (len(ts)-ix,len(ps)-ix)

assert(get_pango_relation("B.1","B.1") == (0,0))
assert(get_pango_relation("B.1.7","B.1") == (1,0))
assert(get_pango_relation("B.1","B.1.7") == (0,1))
assert(get_pango_relation("B.1.1","B.1.2") == (1,1))
assert(get_pango_relation("B","A") == (1,1))
assert(get_pango_relation("B.1.1.7.7","Q.7") == (0,0))
#%%
cm['mismatch'] = cm.apply(lambda row: get_pango_relation(row.designation, row.nextclade), axis=1)
cm['mis_general'] = cm.mismatch.apply(lambda x: x[0])
cm['mis_specific'] = cm.mismatch.apply(lambda x: x[1])
#%%
#%%
cm[cm['mis_specific']!=0].sort_values('counts')
#%%
cm[(cm['mis_specific']!=0) & (~cm.designation.str.startswith('X'))].groupby('mismatch').counts.sum()
#%%
cm[(cm['mis_specific']!=0) & (~cm.designation.str.startswith('X'))].sort_values('counts').to_csv('overly_specific.tsv',sep='\t')
#%%
#%%
cm.to_csv('confusion_matrix_full.tsv', sep='\t', index=False, float_format='%.4f')
# %%
cm[cm.designation != cm.nextclade].to_csv('confusion_matrix_off_diagonal.tsv', sep='\t', index=False, float_format='%.6f')
cm[cm.designation == cm.nextclade].to_csv('confusion_matrix_diagonal.tsv', sep='\t', index=False, float_format='%.6f')

# %%
#%%
# Can normalize in two ways: either normalize the confusion matrix itself by overall numbers
# Or for simpler dicing/slicing etc, join new columns to the metadata, every sample gets average values of its lineage
# E.g. give it following extra columns: (0,0) (0,1) (1,0) (1,1) (0,2+) (2+,0) other, populate average values per lineage

meta = pd.read_csv('meta_condensed.tsv', sep='\t', parse_dates=['date'], infer_datetime_format=True)
#%%
meta.date = pd.to_datetime(meta.date,errors='coerce')
meta.dropna(subset=['date'], inplace=True)
meta


#%%
lineage_counts = meta.pango_lineage.value_counts()
# %%
cm = cm.join(lineage_counts, on='designation')
#%%
cm['counts_norm'] = cm.d_share * cm.pango_lineage
cm['counts_norm'] = cm['counts_norm'] / cm.counts_norm.sum()
cm
# %%
cm.groupby('mismatch').counts_norm.sum()

# %%
cm.counts_norm.sum()
# %%
lineage_counts = meta[meta.date > '20210201'].pango_lineage.value_counts()
lineage_counts
# %%
cm.drop(columns=['pango_lineage'], inplace=True)
cm = cm.join(lineage_counts, on='designation')
#%%
cm['counts_norm'] = cm.d_share * cm.pango_lineage
cm['counts_norm'] = cm['counts_norm'] / cm.counts_norm.sum()
cm
# %%
cm.groupby('mismatch').counts_norm.sum()

# %%
cm.counts_norm.sum()
# %%
