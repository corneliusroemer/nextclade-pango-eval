# Evaluating Nextclade's pango assignments

## Prior Art

### NY/CA UShER vs pangoLEARN

Paper: [SARS-CoV-2 lineage assignment is more stable with UShER](https://virological.org/t/sars-cov-2-lineage-assignment-is-more-stable-with-usher/781)

#### Issues

Compares only against two regional datasets, 7k NY, and 20k CA.

Focus on non-permitted reassignments and stability as opposed to correctness or match with designations

Based on early Delta lineages, dataset contains almost only Deltas and only a few Delta lineages


## Considerations

### Modes

#### Against designations

Designations are ground truth

Switch off pangolin hash for fair comparison

Implementation: simply use filtered designation sequences from Nextclade data workflow

#### Head to head

All against all: 3 comparisons (useful in itself)

#### Against consensus

Consensus is, whenever 2 out of 3 agree. Otherwise it's ambiguous and don't count.

### Metrics

Simplify confusion matrix by grouping types of misclassification

Is prediction:

- Correct
- Too general by 1,2,...
- Too specific by 1,2,...
- Both (uncle, cousin, ...)

Can summarize as:

- Is actual descendant? -> Too general (0,2)
- Is actual ancestor? -> Too specific (2,0)
- How far up is most recent common ancestor? If 1, and then actual is 2 down: (1,2)

Codify distance in tuple of non-negative integers.

Can use for summary evaluations, e.g. mapping to tuple to "penalty". Or identifying lineages that have particularly high scores.

### Breakdown

#### Raw confusion matrix

Start off with big confusion matrix: actual vs truth

Can sum rows and columns

For each lineage, sorted by number in sample:

##### What are B.1.1.7 predicted as?

```tsv
pred	share
B.1.1.7	95%
Q.1	3%
B.1.1	2%
...
```

##### What are predicted B.1.1.7 actually?

```tsv
pred	share
B.1.1.7	95%
Q.1	3%
B.1.1	2%
```

#### By sampling month

#### By number of samples in designations

#### By number of samples by Usher

#### By number of samples in Nextclade reference tree

#### By coverage

## Implementation

Start with designations as ground truth, simpler.

1m samples. Should take about 1h to run with 500 cores.
200 splits and 4 cores -> 10m per split.

Select down to `date,4xlineages`

Produce big file confusion matrix as multi-indexed dataframe

Two views: (truth,pred) and (pred,truth) per method

Can calculate overall score

Then augment with summary tuple, again calculate score

Turn tuple into penalty, calculate score

Output results always as tsv, one results file per method

## Progress

### Confusion matrix

Create confusion matrix, split into diagonal and off-diagonal. Uploaded to Google Sheets for inspection.

Most errors seem to be in the direction of too general, e.g. AY.7.2 (Designation) -> AY.7 (Nextclade)

Some errors could be down to misdesignations (or missed updates rather), like when B.1.617.2 should be AY.122

About 3% of Deltas are misclassified (most too general)

## Further work

Manually check for a subset of disagreements who is right

Need defining mutations to check why we're being too specific. For example P.1.10.1, not clear at all what's supposedly defining. Turns out: a non-designated sequence got in the way and wrong inference took place, the internal node got P.1.10.1 rather than P.1.10

Hard mask things like S:142? Creating noise in Delta placements.

How did `Denmark/DCGC-8062/2020,C.30.1` end up in reference tree, when it wasn't supposed to be sampled in, according to `nr.tsv`.

## Ideas for improving Nextclade pango

- Add at least 2 lineages for each recent lineage (sample date within last year)
- Add calculated basal lineage
- Remove outliers, lineages that are designated differently by Usher than the designation
