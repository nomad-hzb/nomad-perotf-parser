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

from perotf_s import (peroTF_CR_SolSimBox_JVmeasurement,
                      peroTF_CR_SolSimBox_MPPTracking,
                      peroTF_TFL_GammaBox_JVmeasurement,
                      peroTF_TFL_GammaBox_EQEmeasurement,
                      peroTF_Measurement)

from nomad.datamodel.metainfo.eln import SolarCellEQE


from baseclasses.helper.utilities import set_sample_reference, create_archive

import os
import datetime

'''
This is a hello world style example for an example parser/converter.
'''


class PeroTFParser(MatchingParser):
    def __init__(self):
        super().__init__(
            name='parsers/hysprintjv', code_name='HYSPRINTJV', code_homepage='https://www.example.eu/',
            supported_compressions=['gz', 'bz2', 'xz']
        )

    def parse(self, mainfile: str, archive: EntryArchive, logger):
        # Log a hello world, just to get us started. TODO remove from an actual parser.

        mainfile_split = os.path.basename(mainfile).split('.')
        print(mainfile_split)
        notes = ''
        if len(mainfile_split) > 2:
            notes = mainfile_split[1]
        entry = peroTF_Measurement()
        if mainfile_split[-1] == "csv" and mainfile_split[-2] == "jv":
            entry = peroTF_CR_SolSimBox_JVmeasurement()
        if mainfile_split[-1] == "dat" and mainfile_split[-2] == "eqe":
            header_lines = 63
            sc_eqe = SolarCellEQE()
            sc_eqe.eqe_data_file = os.path.basename(mainfile)
            sc_eqe.header_lines = header_lines
            entry = peroTF_TFL_GammaBox_EQEmeasurement()
            entry.eqe_data = [sc_eqe]
        if mainfile_split[-1] == "csv" and mainfile_split[-2] == "jvg":
            entry = peroTF_TFL_GammaBox_JVmeasurement()
        if mainfile_split[-1] == "csv" and mainfile_split[-2] == "mpp":
            entry = peroTF_CR_SolSimBox_MPPTracking()
        
        if  mainfile_split[-2] in ["jv", "eqe", "jvg"] and len(mainfile_split) > 2:
            if "top" in mainfile_split[1]:
                entry.multijunction_position = "top"
            if "mid" in mainfile_split[1]:
                entry.multijunction_position = "mid"
            if "bot" in mainfile_split[1]:
                entry.multijunction_position = "bottom"
        
        archive.metadata.entry_name = os.path.basename(mainfile)
        search_id = mainfile_split[0]
        set_sample_reference(archive, entry, search_id)

        entry.name = f"{search_id} {notes}"
        entry.description = f"Notes from file name: {notes}"
        if not mainfile_split[-2] == "eqe":
            entry.data_file = os.path.basename(mainfile)
        entry.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        file_name = f'{os.path.basename(mainfile)}.archive.json'
        create_archive(entry, archive, file_name)
