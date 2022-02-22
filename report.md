# Using Nextclade as pango lineage classifier

## Abstract

## Introduction

Pango lineages have become the standard micro-clade system for SARS-CoV-2. Currently, there are two ways of assigning lineages: pangoLEARN and UShER. Of the now 8 million SARS-CoV-2 sequences available through GISAID, around 1m are explicitly labeled with on of more than 1,500 lineages. Both methods use these labeled sequences to classify new sequences. pangoLEARN currently employs a decision tree-based approach, where the labeled sequences (or a subset thereof) form the training set. UShEr classifies new sequences by placing them on a phylogenetic tree in the most parsimonious way. The tree used for pango classification is a pruned version (30 sequences per lineage) of the huge USheR tree that contains almost all SARS-CoV-2 sequences available through GISAID. When compared with each other, UShEr has been found to be more stable across releases, which is not surprising given the blackbox nature of pangoLEARN's decision tree.

This report outlines how Nextclade can be used to predict pango lineages, how it's accuracy compares with pangoLEARN and UShER mode and what the limitations are.

## Methods

### Overview

At the core of Nextclade is a reference tree representing the global phylogeny. For each query sequence, the nearest neighbor on the reference tree is identified by direct comparison. The pango lineage assigned to the query sequence is then the nearest neighbor's pango lineage.

### Reference tree

Since only lineages present in the reference tree can be assigned, it is important that as many lineages as possible are present in the reference tree. To keep Nextclade fast, around 3,000 sequences are chosen using an algorithm that gives more weight to widespread and recent lineages. As a result, many small lineages, particularly from the first year of the pandemic are not in the reference tree and hence will never be assigned by Nextclade.

Care is taken to ensure lineages common on continents with less sequencing are also included. For lineages defined in the past year, at least 1 sequence is included. The reference tree is constructed using an Augur pipeline with IQtree2 as the phylogenetic tree builder.

### Assignment of pango lineages to internal nodes

Nextclade also takes internal nodes, that is ancestral, reconstructed sequences, into account for nearest neighbor placement. As a result, all internal nodes in the reference tree need to be assigned a pango lineage. This is done using treetime's ancestral reconstruction algorithm.

Each tip is given a pseudo-sequence that is derived from that tip's pango lineage. Each position in the pseud-sequence corresponds to one level of a pango lineage hierarchy, for example, position 1 means `B`, position 2 `B.1`, position 3 `B.2`, position 4 `B.1.1` etc. The pango lineage `B.1.1` is thus encoded as binary `1011` or translated into nucleotides with `A=0, C=1` as `CACCAAAA...`.

The reference tree together with the pseudo-sequences is then fed to `treetime ancestral` in maximum-likelihood mode to reconstruct pseudo-sequences at all internal (ancestral) nodes. The pseudo-sequences are then converted back to pango lineages using the same encoding as above.

The resulting assignment of pango lineages to internal nodes is found to be robust to occasional misdesignations. Alternative methods, such as using Fitch parsimony, were tried but found to be less robust.

## Validation

We validated Nextclade's pango lineage predictions in two ways: against designations and against a consensus of the three methods (lineage call shared by 2 out of 3).

### Comparison against designations

Nextclade's was used to predict pango lineages for each of the sequences for which a designation is available (~1m). Nextclade's predictions were then compared with the truth (lineage according to pango designations).

For each sequence, prediction and truth are compared and classified as follows: correct, one level too specific (e.g. Nextclade says `B.1.3` but truth is `B.1.`), one level too generic (e.g. Nextclade says `B.1` but truth is `B.1.3`), or other (e.g. multiple levels too generic, or cousin relationsships like Nextclade says `B.2` but truth is `B.1`).

Since the share of sequences per lineage that is contained in the designation dataset varies wildly by a factor of 100 (e.g. of the 13 `AQ.1` in all of GISAID's sequences, 9 are designated, whereas of about 500k `BA.1.1` only ~400 are designated) we normalize the results based on how common a lineage is in all of GISAID's sequences, instead of how often a lineage is in the designation dataset.

The results are shown in the table below.

| Type of error against designations | Share (last 12m) | Share (all times) |
| ---------------------------------- | ---------------- | ----------------- |
| Correct                            | 97.8%            | 95.6%             |
| Nextclade 1 level too general      | 1.7%             | 3.8%              |
| Nextclade 1 level too specific     | 0.3%             | 0.3%              |
| Other type of misclassification    | 0.2%             | 0.2%              |

<!--- TODO: maybe include UShER and pangoLEARN performance and compare -->

The biggest error type is that Nextclade is too general. This occurs for example when a lineage is not present in the reference tree at all due to being too small and/or too old. For more recent lineages, Nextclade is more accurate, because the tree contains a sample for each recent lineage.

### Comparison against consensus

One disadvantage of comparison against designations is that sequences included in the designation dataset are not representative of sequences belonging to that lineage, but tend to be biased towards early, basal sequences. Hence we compared accuracy against a consensus of the three methods: pangoLEARN, UShER and Nextclade. Pango lineages are predicted using each of the three methods (with designation hash switched off for a fair comparison). Consensus is defined as at least two out of three methods agreeing on a lineage.

Results are shown in the table below:

q


## Limitations