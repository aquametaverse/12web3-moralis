#!/usr/bin/env python
import argparse
import logging
import sys
import os
import shutil
import time
import json
import configparser
from datetime import datetime
from sr_client import *
from moralis_client import *


LOCAL_MODE = False
IS_VERBOSE = False
DEBUG_LEVEL = 0
DEFAULT_CONFIG = "/etc/wgen.ini"
IPFS_ROOT = "aquametaverse/poc/env_data/spot_id"
STATUS_LOG = "/var/log/wgen/wgen.log"
TIME_FORMATS = {
    "human": "%m/%d/%Y %H:%M",
    "meteo": "%Y%m%dT%H%M",
    "meteo_sec": "%Y%m%dT%H%M%S",
}

rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

fileLogFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
fileHandler = logging.FileHandler(STATUS_LOG)
fileHandler.setFormatter(fileLogFormatter)
rootLogger.addHandler(fileHandler)

consoleFormatter = logging.Formatter("[%(levelname)-5.5s]  %(message)s")
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(consoleFormatter)
rootLogger.addHandler(consoleHandler)

TIME_FORMATS = {
    "human": "%m/%d/%Y %H:%M",
    "meteo": "%Y%m%dT%H%M",
    "meteo_sec": "%Y%m%dT%H%M%S",
}

# functions first
def get_dts_object(dts_str, time_format="human"):
    global TIME_FORMATS
    try:
        dto = datetime.strptime(dts_str, TIME_FORMATS[time_format])
        return dto
    except ValueError:
        return None


def get_datetime_object(dts_str):
    global TIME_FORMATS
    dto = None
    for time_format in TIME_FORMATS:
        dto = get_dts_object(dts_str, time_format=time_format)
        if dto:
            break
    return dto


def main(argv=sys.argv):
    global LOCAL_MODE, SRC_DIR_ROOT, DEFAULT_CONFIG, IPFS_ROOT, logging

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-d", "--debug", action="store_true", required=False, help="debug mode"
    )
    ap.add_argument(
        "-l",
        "--local",
        action="store_true",
        required=False,
        help="local action, do not send to IPFS",
    )
    ap.add_argument(
        "-c",
        "--config",
        action="store",
        required=False,
        help="config file path and name",
    )
    ap.add_argument(
        "-i",
        "--info",
        action="store_true",
        required=False,
        help="spot info - spotinfo.dat",
    )
    ap.add_argument(
        "-w",
        "--waves",
        action="store_true",
        required=False,
        help="waves - waveinfo.dat",
    )

    args = ap.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    config = configparser.ConfigParser()
    if args.config:
        config.read(args.config)
    else:
        config.read(DEFAULT_CONFIG)

    if config["general"]["ipfs_root"]:
        ipfs_root = config["general"]["ipfs_root"]
    else:
        ipfs_root = IPFS_ROOT
    radar_api = AqmSrClient(
        api_host=config["surfradar.info"]["api_host"],
        api_key=config["surfradar.info"]["api_key"],
    )
    ipfs_api = MoralisClient(
        api_host=config["moralis.io"]["api_host"],
        api_key=config["moralis.io"]["api_key"],
    )

    spot_ids = radar_api.get_spot_ids()

    for spot_id in spot_ids:
        if args.info:
            info = radar_api.get_spot_info(spot_id)
            content_json = json.dumps(info)
            logging.debug(f"sr_info_json={content_json}")
            target = "/".join([ipfs_root, spot_id, "spotinfo.dat"])
            logging.info(f"target_folder={target}")
            if not args.local:
                ipfs_result = ipfs_api.ipfs_upload_folder(target, content_json)
                logging.info(f"ipfs_result={repr(ipfs_result)}")

        if args.waves:
            waves = radar_api.get_waves(spot_id)
            logging.debug(f"sr_waves_raw={waves}")
            forecast_dto = get_datetime_object(waves["valid_time_utc"])
            forecast_dts = forecast_dto.strftime(TIME_FORMATS["meteo_sec"])
            content = {"wave_height_ft": waves["wave_height_ft"]}
            content_json = json.dumps({"wave_height_ft": waves["wave_height_ft"]})
            logging.debug(f"waves_json={content_json}")
            target = "/".join([ipfs_root, spot_id, forecast_dts, "waveinfo.dat"])
            logging.info(f"target_folder={target}")
            if not args.local:
                ipfs_result = ipfs_api.ipfs_upload_folder(target, content_json)
                logging.info(f"ipfs_result={repr(ipfs_result)}")


if __name__ == "__main__":
    sys.exit(main())
