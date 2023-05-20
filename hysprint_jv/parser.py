#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
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
#

from nomad.datamodel import EntryArchive
from nomad.parsing import MatchingParser

from hysprint_s import HySprint_108_HyVap_JVmeasurement

from baseclasses.helper.jv_archive import get_jv_archive
from baseclasses.helper.jv_parser import get_jv_data

from baseclasses.helper.utilities import set_sample_reference, create_archive


import json
import os
import datetime

'''
This is a hello world style example for an example parser/converter.
'''


class JVParser(MatchingParser):
    def __init__(self):
        super().__init__(
            name='parsers/hysprintjv', code_name='HYSPRINTJV', code_homepage='https://www.example.eu/',
            supported_compressions=['gz', 'bz2', 'xz']
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.

        from baseclasses.helper.utilities import get_encoding
        with open(mainfile, "br") as f:
            encoding = get_encoding(f)

        mainfile_split = os.path.basename(mainfile).split('.')
        notes = ''
        if len(mainfile_split) > 2:
            notes = mainfile_split[1]

        jv_dict = get_jv_data(mainfile, encoding)
        jvm = HySprint_108_HyVap_JVmeasurement()
        get_jv_archive(jv_dict, mainfile, jvm)

        archive.metadata.entry_name = os.path.basename(mainfile)
        search_id = mainfile_split[0]
        set_sample_reference(archive, jvm, search_id)

        jvm.name = f"{search_id} {notes}"
        jvm.description = f"Notes from file name: {notes}"
        jvm.data_file = os.path.basename(mainfile)
        jvm.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        file_name = f'{os.path.basename(mainfile)}.archive.json'
        create_archive(jvm, archive, file_name)
