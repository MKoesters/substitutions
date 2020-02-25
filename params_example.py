#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 10:14:41 2018

@author: ernestmordret
"""
output_dir = ("output",)  # output folder
path_to_fasta = ("",)  #
tol = (0.005,)
n_term_prob_cutoff = (0.05,)
c_term_prob_cutoff = (0.05,)
positional_probability_cutoff = (0.95,)
fdr = (0.01,)
regex = ("gene_symbol\:(.*)(\s|$)",)  # regex for extraction gene symbol from fasta
excluded_samples = ([],)
path_to_evidence = ("/path/to/evidence.txt",)
path_to_matched_features = ("path/to/matchedFeatures.txt",)
path_to_peptides = (
    "/path/to/peptides.txt",
)  # path to MaxQuant's table, allPeptides.txt
mz_tol = 10 * 10 ** -6  # m/z tolerance for the fetching unidentified features
rt_tol = 0.3  # # retention time tolerance for the fetching unidentified features
