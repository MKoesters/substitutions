#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  1 13:56:13 2017

@author: ernestmordret
"""

import pandas as pd
from scipy.interpolate import interp1d
import re
import numpy as np
import os



def create_modified_seq(modified_seq, destination):
    """
    Input: base sequence with probabilities of substitution for each AA, observed destination AA.
    Output: modified sequence.
    (ACY(0.1)KFL(0.9)S, Y) -> ACYKFYS
    """
    possible_sites = re.findall("\(([^\)]+)\)", modified_seq)
    best_site = np.argmax([float(i) for i in possible_sites])
    modified_pos_prime = [m.start() - 1 for m in re.finditer("\(", modified_seq)][
        best_site
    ]
    modified_pos = len(re.sub("\(([^\)]+)\)", "", modified_seq[:modified_pos_prime]))
    base_seq = re.sub("\(([^\)]+)\)", "", modified_seq)
    return base_seq[:modified_pos] + destination + base_seq[modified_pos + 1 :]


def get_evidence_ids(peptide):
    evidence_ids = pep.loc[peptide, "Evidence IDs"]
    return [int(i) for i in evidence_ids.split(";")]


def get_BP_intensities(peptide, charge):
    x = evidence.loc[get_evidence_ids(peptide)]
    y = x[x["Charge"] == charge].groupby("Sample")["Intensity"].sum()
    return y.reindex(samples)


def main(args):
    path_to_subs = os.path.join(args['output_dir'], "subs")
    columns_evidence = [
        "Raw file",
        "Retention time",
        "Calibrated retention time",
        "Intensity",
        "Charge",
    ]
    
    
    """
    matchedFeatured.txt contains features that weren't identified and appeared in more than one sample.
    Those features have both uncalibrated and calibrated retention time.
    subs, which is derived from allPeptides.txt, has only uncalibrated retention time;
    to extract features from mf.txt, retention times are calibrated using evidence.txt
    """
    evidence = pd.read_csv(path_to_evidence, sep="\t", usecols=columns_evidence)
    
    evidence["Sample"] = evidence["Raw file"].map(lambda x: x.split("_")[-2])
    
    calibrate = {}
    for i, j in evidence.groupby(
        "Raw file"
    ):  # RT for each file (fraction) is being calibrated
        calibrate[i] = interp1d(
            j["Retention time"], j["Calibrated retention time"], fill_value="extrapolate"
        )
    
    subs = pd.read_pickle(path_to_subs)
    
    # exclude samples
    subs = subs[~subs["Raw file"].str.contains("|".join(excluded_samples))]
    
    subs["modified_sequence"] = subs.apply(
        lambda row: create_modified_seq(row["DP Probabilities"], row["destination"]), axis=1
    )
    subs["base RT"] = subs["Retention time"] - subs["DP Time Difference"]
    
    for i, j in subs.groupby("Raw file"):
        subs.loc[j.index, "Calibrated retention time"] = subs.loc[
            j.index, "Retention time"
        ].map(lambda x: calibrate[i](x))
        subs.loc[j.index, "Calibrated base RT"] = subs.loc[j.index, "base RT"].map(
            lambda x: calibrate[i](x)
        )
    
    subs["Calibrated DPTD"] = subs["Calibrated retention time"] - subs["Calibrated base RT"]
    subs["Base m/z"] = subs["m/z"] - (subs["DPMD"] / subs["Charge"])
    
    mf = pd.read_csv(path_to_matched_features, sep="\t")
    mf.replace(0, np.nan, inplace=True)
    
    pep_head = pd.read_csv(path_to_peptides, sep="\t", nrows=10, index_col="Sequence")
    
    intensities = [str(i) for i in pep_head.columns if "Intensity " in i]
    samples = [i.split()[-1] for i in intensities]
    samples = [i for i in samples if not i in excluded_samples]
    intensities = ["Intensity " + i for i in samples]
    
    pep_columns = ["Sequence", "Intensity", "Evidence IDs"] + intensities
    
    pep = pd.read_csv(path_to_peptides, sep="\t", usecols=pep_columns, index_col="Sequence")
    
    pep.replace(0, np.nan, inplace=True)
    
    D = pd.DataFrame(columns=["DP", "Base", "substitution"])
    
    gb = subs.groupby(["Charge", "DP Base Sequence", "modified_sequence"])
    substitution_index = 0
    for i, j in gb:
        charge, base_sequence, modified_sequence = i
        ref_dp = j.loc[j["DP PEP"].argmin()]
        charge, dp_mz, base_sequence, dp_rt = ref_dp[
            ["Charge", "m/z", "DP Base Sequence", "Calibrated retention time",]
        ]
    
        f1 = mf["Calibrated retention time"] < dp_rt + rt_tol
        f2 = mf["Calibrated retention time"] > dp_rt - rt_tol
        f3 = mf["m/z"] < dp_mz * (1 + mz_tol)
        f4 = mf["m/z"] > dp_mz * (1 - mz_tol)
        f5 = mf["Charge"] == charge
    
        m = mf[f1 & f2 & f3 & f4 & f5]
        l = len(m)
    
        if l >= 1:
            substitution_index += 1
            bps = get_BP_intensities(base_sequence, charge)
            bps.index = intensities
            d = pd.concat(
                [m[intensities].sum(), bps], axis=1
            )  # if the response curve isn't linear, why is it OK to sum intensities?
            d.columns = ["DP", "Base"]
            d["substitution_index"] = substitution_index
            d["codon"] = ref_dp["codon"]
            d["destination"] = ref_dp["destination"]
            d["origin"] = ref_dp["origin"]
            d["mispairing"] = ref_dp["mispairing"]
            d["position"] = ref_dp["position"]
            d["protein"] = ref_dp["protein"]
            d["base_sequence"] = base_sequence
            d["modified_sequence"] = modified_sequence
            D = D.append(d)
    
    D["Ratio"] = D["DP"] / D["Base"]
    D["Sample"] = D.index.str.extract("Intensity ([\w-]*)", expand=False).fillna("")
    D["substitution"] = float("NaN")
    D.loc[pd.notnull(D["codon"]), "substitution"] = D[pd.notnull(D["codon"])].apply(
        lambda x: x["codon"] + " to " + x["destination"], axis=1
    )
    D.reset_index(inplace=True)
    D.to_pickle(os.path.join(output_dir, "qSubs"))
    D.to_csv(os.path.join(output_dir, "qSubs"))
