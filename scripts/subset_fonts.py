#!/usr/bin/env python3
# coding=UTF-8
#
# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modified from: https://cs.android.com/android/platform/superproject/main/+/main:external/noto-fonts/scripts/subset_noto_cjk.py;drc=d8536c6637d9506ccd8ffb09810ceb7e864e20d8

"""Create a curated subset of Noto CJK for Android."""

import argparse
import logging
import os
from pathlib import Path

from fontTools import ttLib
from nototools import font_data
from nototools import tool_utils
from nototools import ttc_utils

EMOJI_IN_CJK = {
    0x1F18E, # 🆎 NEGATIVE SQUARED AB
    0x1F191, # 🆑 SQUARED CL
    0x1F192, # 🆒 SQUARED COOL
    0x1F193, # 🆓 SQUARED FREE
    0x1F194, # 🆔 SQUARED ID
    0x1F195, # 🆕 SQUARED NEW
    0x1F196, # 🆖 SQUARED NG
    0x1F197, # 🆗 SQUARED OK
    0x1F198, # 🆘 SQUARED SOS
    0x1F199, # 🆙 SQUARED UP WITH EXCLAMATION MARK
    0x1F19A, # 🆚 SQUARED VS
    0x1F201, # 🈁 SQUARED KATAKANA KOKO
    0x1F232, # 🈲 SQUARED CJK UNIFIED IDEOGRAPH-7981
    0x1F233, # 🈳 SQUARED CJK UNIFIED IDEOGRAPH-7A7A
    0x1F234, # 🈴 SQUARED CJK UNIFIED IDEOGRAPH-5408
    0x1F235, # 🈵 SQUARED CJK UNIFIED IDEOGRAPH-6E80
    0x1F236, # 🈶 SQUARED CJK UNIFIED IDEOGRAPH-6709
    0x1F238, # 🈸 SQUARED CJK UNIFIED IDEOGRAPH-7533
    0x1F239, # 🈹 SQUARED CJK UNIFIED IDEOGRAPH-5272
    0x1F23A, # 🈺 SQUARED CJK UNIFIED IDEOGRAPH-55B6
    0x1F250, # 🉐 CIRCLED IDEOGRAPH ADVANTAGE
    0x1F251, # 🉑 CIRCLED IDEOGRAPH ACCEPT
}

ANDROID_EMOJI = {
    0x263A, # ☺ WHITE SMILING FACE
    0x270C, # ✌ VICTORY HAND
    0x2744, # ❄ SNOWFLAKE
    0x2764, # ❤ HEAVY BLACK HEART
}

# We don't want support for ASCII control chars.
CONTROL_CHARS = tool_utils.parse_int_ranges('0000-001F')

EXCLUDED_CODEPOINTS = sorted(EMOJI_IN_CJK | ANDROID_EMOJI | CONTROL_CHARS)

def remove_from_cmap(infile, outfile, exclude=frozenset()):
    """Removes a set of characters from a font file's cmap table."""
    font = ttLib.TTFont(infile)
    font_data.delete_from_cmap(font, exclude)
    font.save(outfile)


def remove_codepoints_from_ttc_using_ttc_utils(ttc_name, out_dir):
    otf_names = ttc_utils.ttcfile_extract(ttc_name, out_dir)

    with tool_utils.temp_chdir(out_dir):
        for index, otf_name in enumerate(otf_names):
            logging.info('Subsetting %s...', otf_name)
            remove_from_cmap(otf_name, otf_name, exclude=EXCLUDED_CODEPOINTS)
        ttc_utils.ttcfile_build(ttc_name, otf_names)
        for f in otf_names:
            os.remove(f)


def remove_codepoints_from_ttc(ttc_path, out_dir):
    """Removes a set of characters from a TTC font file's cmap table."""
    logging.info('Loading %s', ttc_path)
    ttc = ttLib.ttCollection.TTCollection(ttc_path)

    logging.info('Subsetting %d fonts in the collection', len(ttc))
    for font in ttc:
        font_data.delete_from_cmap(font, EXCLUDED_CODEPOINTS)

    out_path = out_dir / ttc_path.name
    logging.info('Saving to %s', out_path)
    ttc.save(out_path)
    logging.info('Size: %d --> %d, delta=%d',
                 ttc_path.stat().st_size,
                 out_path.stat().st_size,
                 out_path.stat().st_size - ttc_path.stat().st_size)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ttc_names', nargs='+')
    parser.add_argument('-o', '--output', default='subsetted')
    parser.add_argument('--use-ttc-utils', action='store_true')
    parser.add_argument('-v', '--verbose', action='count')
    args = parser.parse_args()
    if args.verbose:
        if args.verbose > 1:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    for ttc_name in args.ttc_names:
        if args.use_ttc_utils:
            logging.info(ttc_name)
            remove_codepoints_from_ttc_using_ttc_utils(ttc_name, out_dir)
        else:
            logging.info(Path(ttc_name))
            remove_codepoints_from_ttc(Path(ttc_name), out_dir)


if __name__ == "__main__":
    main()
