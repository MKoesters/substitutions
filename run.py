#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 11:32:57 2018

@author: ernestmordret
"""


import argparse
import logging

# from params import *
from detect import main as detect_main
import os


def parse_params(param_file):
    """Parse params file into dict.

    Args:
        param_file (str): Path to param file

    Returns:
        dict: Dict mapping param name to value
    """
    params = {}
    with open(param_file) as fin:
        for line in fin:
            if line.strip().startswith("#"):
                continue
            key, val = line.strip().split("=")
            key, val = key.strip(), val.strip()
            params[key] = val
            if key == "excluded_samples":
                params[key] = params[key].split(",")
                params["excluded_samples"].remove("")
    return params


def create_logger():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    # Create handlers
    # c_handler = logging.StreamHandler()
    # # f_handler = logging.FileHandler('file.log')
    # c_handler.setLevel(logging.DEBUG)
    # # f_handler.setLevel(logging.ERROR)

    # # Create formatters and add it to handlers
    # c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    # # f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # c_handler.setFormatter(c_format)
    # # f_handler.setFormatter(f_format)

    # # Add handlers to the logger
    # logger.addHandler(c_handler)
    # logger.addHandler(f_handler)

    return logger


parser = argparse.ArgumentParser()
logger = create_logger()

parser.add_argument(
    "-d", "--detect", action="store_true", help="run the detect script only."
)

parser.add_argument(
    "-q",
    "--quantify",
    action="store_true",
    help="run the quantify script only. Will not work\
                        unless the detect option was ran first",
)

parser.add_argument(
    "-p",
    "--plot",
    action="store_true",
    help="plot the substitution heatmap, and\
                    output the unique substitutions count matrix.",
)

parser.add_argument("-c", "--config", help="Path to config file")

args = parser.parse_args()

param_dict = parse_params(args.config)
# from pprint import pprint
# pprint(param_dict)

if os.path.isdir(param_dict["output_dir"]):
    pass
else:
    logger.info("creating output directory")
    os.mkdir(param_dict["output_dir"])

if args.detect:
    if os.path.isfile(os.path.join(param_dict["output_dir"], "subs")):
        overwrite = input("output directory already exists. Press y to overwrite: ")
        if overwrite.lower() == "y":
            logger.info("overwriting subs")
            os.remove(os.path.join(param_dict["output_dir"], "subs"))
            os.remove(os.path.join(param_dict["output_dir"], "subs.csv"))
            # os.mkdir(param_dict['output_dir'])
        else:
            logger.info("exit")
            exit()

    logger.info("detecting substitutions. That step might take some time...")
    detect_main(param_dict)
    # try:
    #     import detect
    # except:
    #     "this didn't go smoothly. Please check the parameters in the params.py file"

if args.quantify:
    if os.path.isfile(os.path.join(param_dict["output_dir"], "subs")):
        if os.path.isfile(os.path.join(param_dict["output_dir"], "qSubs")):
            overwrite = input("output directory already exists. Press y to overwrite")
            if overwrite == "y":
                logger.info("overwriting qSsubs")
                try:
                    os.remove(param_dict["output_dir"] + "/qSubs")
                except OSError:
                    exit()
        try:
            import quantify
        except:
            "this didn't go smoothly. Please check the parameters in the params.py file"
    else:
        print("subs not found. Please run detect first")

if args.plot:
    if os.path.isfile(os.path.join(param_dict["output_dir"], "subs")):
        try:
            import plot
        except:
            logger.error("problems happened during the plotting...")
    else:
        logger.warning("subs not found. Please run detect first")
