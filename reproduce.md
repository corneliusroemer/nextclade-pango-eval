# Note on how to reproduce

Run [Snakemake workflow](https://github.com/corneliusroemer/nextclade-full-run/blob/main/pango-test/Snakefile) to create file `usher_clades_meta.tsv` from either all sequences or only sequences in designations depending on comparison methodl

Output contains at least the following columns, one row for each sequence:

```csv
date,pango_designated,Nextclade_lineage,Usher_lineage,Pangolearn_lineage
```

Then can run the scripts in this repo (adapted to the column names).
