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

from hysprint_s import HySprint_108_HyVap_EQEmeasurement

from nomad.datamodel.metainfo.eln import SolarCellEQE
from baseclasses.helper.eqe_archive import get_eqe_archive
from baseclasses.helper.eqe_parser import EQEAnalyzer

from baseclasses.helper.utilities import set_sample_reference, create_archive


import json
import os
import datetime

'''
This is a hello world style example for an example parser/converter.
'''


class EQEParser(MatchingParser):
    def __init__(self):
        super().__init__(
            name='parsers/hysprinteqe', code_name='HYSPRINTEQE', code_homepage='https://www.example.eu/',
            supported_compressions=['gz', 'bz2', 'xz']
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.

        mainfile_split = os.path.basename(mainfile).split('.')
        notes = ''
        if len(mainfile_split) > 2:
            notes = mainfile_split[1]

        header_lines = 9
        eqe_dict = EQEAnalyzer(mainfile, header_lines=header_lines).eqe_dict()
        eqem = HySprint_108_HyVap_EQEmeasurement()
        sc_eqe = SolarCellEQE()
        sc_eqe.header_lines = header_lines
        get_eqe_archive(eqe_dict, mainfile, sc_eqe, logger)

        archive.metadata.entry_name = os.path.basename(mainfile)
        search_id = mainfile_split[0]
        set_sample_reference(archive, eqem, search_id)

        eqem.name = f"{search_id} {notes}"
        eqem.description = f"Notes from file name: {notes}"
        eqem.data_file = os.path.basename(mainfile)
        eqem.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        sc_eqe.eqe_data_file = os.path.basename(mainfile)
        eqem.eqe_data = [sc_eqe]

        file_name = f'{os.path.basename(mainfile)}.archive.json'
        create_archive(eqem, archive, file_name)
