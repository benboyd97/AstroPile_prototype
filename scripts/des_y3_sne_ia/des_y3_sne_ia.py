# Copyright 2020 The HuggingFace Datasets Authors and the current dataset script contributor.
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
import datasets
from datasets import Features, Value, Sequence
from datasets.data_files import DataFilesPatternsDict
import itertools
import h5py
import numpy as np
import os

# TODO: Add BibTeX citation
# Find for instance the citation on arxiv or on the dataset repo/website
_CITATION = """
@ARTICLE{2019ApJ...874..106B,
       author = {{Brout}, D. and {Sako}, M. and {Scolnic}, D. and {Kessler}, R. and {D'Andrea}, C.~B. and {Davis}, T.~M. and {Hinton}, S.~R. and {Kim}, A.~G. and {Lasker}, J. and {Macaulay}, E. and {M{\"o}ller}, A. and {Nichol}, R.~C. and {Smith}, M. and {Sullivan}, M. and {Wolf}, R.~C. and {Allam}, S. and {Bassett}, B.~A. and {Brown}, P. and {Castander}, F.~J. and {Childress}, M. and {Foley}, R.~J. and {Galbany}, L. and {Herner}, K. and {Kasai}, E. and {March}, M. and {Morganson}, E. and {Nugent}, P. and {Pan}, Y. -C. and {Thomas}, R.~C. and {Tucker}, B.~E. and {Wester}, W. and {Abbott}, T.~M.~C. and {Annis}, J. and {Avila}, S. and {Bertin}, E. and {Brooks}, D. and {Burke}, D.~L. and {Carnero Rosell}, A. and {Carrasco Kind}, M. and {Carretero}, J. and {Crocce}, M. and {Cunha}, C.~E. and {da Costa}, L.~N. and {Davis}, C. and {De Vicente}, J. and {Desai}, S. and {Diehl}, H.~T. and {Doel}, P. and {Eifler}, T.~F. and {Flaugher}, B. and {Fosalba}, P. and {Frieman}, J. and {Garc{\'\i}a-Bellido}, J. and {Gaztanaga}, E. and {Gerdes}, D.~W. and {Goldstein}, D.~A. and {Gruen}, D. and {Gruendl}, R.~A. and {Gschwend}, J. and {Gutierrez}, G. and {Hartley}, W.~G. and {Hollowood}, D.~L. and {Honscheid}, K. and {James}, D.~J. and {Kuehn}, K. and {Kuropatkin}, N. and {Lahav}, O. and {Li}, T.~S. and {Lima}, M. and {Marshall}, J.~L. and {Martini}, P. and {Miquel}, R. and {Nord}, B. and {Plazas}, A.~A. and {Roodman}, A. and {Rykoff}, E.~S. and {Sanchez}, E. and {Scarpine}, V. and {Schindler}, R. and {Schubnell}, M. and {Serrano}, S. and {Sevilla-Noarbe}, I. and {Soares-Santos}, M. and {Sobreira}, F. and {Suchyta}, E. and {Swanson}, M.~E.~C. and {Tarle}, G. and {Thomas}, D. and {Tucker}, D.~L. and {Walker}, A.~R. and {Yanny}, B. and {Zhang}, Y. and {DES COLLABORATION}},
        title = "{First Cosmology Results Using Type Ia Supernovae from the Dark Energy Survey: Photometric Pipeline and Light-curve Data Release}",
      journal = {\apj},
     keywords = {cosmology: observations, supernovae: general, techniques: photometric, Astrophysics - Instrumentation and Methods for Astrophysics},
         year = 2019,
        month = mar,
       volume = {874},
       number = {1},
          eid = {106},
        pages = {106},
          doi = {10.3847/1538-4357/ab06c1},
archivePrefix = {arXiv},
       eprint = {1811.02378},
 primaryClass = {astro-ph.IM},
       adsurl = {https://ui.adsabs.harvard.edu/abs/2019ApJ...874..106B},
      adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

"""

# TODO: Add description of the dataset here
# You can copy an official description
_DESCRIPTION = """\
Time-series dataset from Dark Energy Survey Year 3 SN Ia (DES Y3 SNe Ia).

Citation:
Brout et al. (2019)
https://ui.adsabs.harvard.edu/abs/2019ApJ...874..106B/abstract
"""

# TODO: Add a link to an official homepage for the dataset here
_HOMEPAGE = "https://des.ncsa.illinois.edu/releases/sn"

# TODO: Add the licence for the dataset here if you can find it
_LICENSE = ""

_VERSION = "0.0.1"

_STR_FEATURES = [
    "object_id",
    "spec_class",
    "bands",
]

_FLOAT_FEATURES = [
    "ra", 
    "dec", 
    "redshift",
    "host_log_mass"
]


class DESY3SNIa(datasets.GeneratorBasedBuilder):
    """"""

    VERSION = _VERSION

    BUILDER_CONFIGS = [
        datasets.BuilderConfig(
            name="des_y3_sne_ia",
            version=VERSION,
            data_files=DataFilesPatternsDict.from_patterns({"train": ["*/*.hdf5"]}), # This seems fairly inflexible. Probably a massive failure point.
            description="Light curves from  DES Y3",
        ),
    ]

    DEFAULT_CONFIG_NAME = "des_y3_sne_ia"

    @classmethod
    def _info(self):
        """Defines the features available in this dataset."""
        # Starting with all features common to light curve datasets
        features = {
            "band_idx": Sequence(Value("int32")),
            "time": Sequence(Value("float32")),
            "flux": Sequence(Value("float32")),
            "flux_err": Sequence(Value("float32")),
        }

        # Adding all values from the catalog
        for f in _FLOAT_FEATURES:
            features[f] = Value("float32")
        for f in _STR_FEATURES:
            features[f] = Value("string")

        return datasets.DatasetInfo(
            # This is the description that will appear on the datasets page.
            description=_DESCRIPTION,
            # This defines the different columns of the dataset and their types
            features=Features(features),
            # Homepage of the dataset for documentation
            homepage=_HOMEPAGE,
            # License for the dataset if available
            license=_LICENSE,
            # Citation for the dataset
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        """We handle string, list and dicts in datafiles"""
        if not self.config.data_files:
            raise ValueError(
                f"At least one data file must be specified, but got data_files={self.config.data_files}"
            )
        data_files = dl_manager.download_and_extract(self.config.data_files)
        if isinstance(data_files, (str, list, tuple)):
            files = data_files
            if isinstance(files, str):
                files = [files]
            # Use `dl_manager.iter_files` to skip hidden files in an extracted archive
            files = [dl_manager.iter_files(file) for file in files]
            return [
                datasets.SplitGenerator(
                    name=datasets.Split.TRAIN, gen_kwargs={"files": files}
                )
            ]
        splits = []
        for split_name, files in data_files.items():
            if isinstance(files, str):
                files = [files]
            # Use `dl_manager.iter_files` to skip hidden files in an extracted archive
            files = [dl_manager.iter_files(file) for file in files]
            splits.append(
                datasets.SplitGenerator(name=split_name, gen_kwargs={"files": files})
            )
        return splits

    def _generate_examples(self, files, object_ids=None):
        """Yields examples as (key, example) tuples."""
        for file_number, file in enumerate(itertools.chain.from_iterable(files)):
            with h5py.File(file, "r") as data:
                if object_ids is not None:
                    keys = object_ids[file_number]
                else:
                    keys = [data["object_id"][()]]

                # Preparing an index for fast searching through the catalog
                sort_index = np.argsort(data["object_id"][()])  # Accessing the scalar index
                sorted_ids = [data["object_id"][()]]  # Ensure this is a list of one element

                for k in keys:
                    # Extract the indices of requested ids in the catalog
                    i = sort_index[np.searchsorted(sorted_ids, k)]
                    # Parse data
                    idxs = np.arange(0, data["flux"].shape[0])
                    band_numbers = idxs.repeat(data["flux"].shape[-1]).reshape(
                        data["bands"].shape[0], -1
                    )
                    example = {
                        "band_idx": band_numbers.flatten().astype("int32"),
                        "time": np.asarray(data["time"]).flatten().astype("float32"),
                        "flux": np.asarray(data["flux"]).flatten().astype("float32"),
                        "flux_err": np.asarray(data["flux_err"]).flatten().astype("float32"),
                    }
                    # Add remaining features
                    for f in _FLOAT_FEATURES:
                        example[f] = np.asarray(data[f]).astype("float32")
                    for f in _STR_FEATURES:
                        # Add band names shared across dataset to each sample.
                        # I can't see a better way to do this.
                        if f == "bands":
                            example[f] = np.asarray(data[f]).astype("str")
                        else:
                            example[f] = data[f][()].astype("str")

                    yield str(data["object_id"][()]), example