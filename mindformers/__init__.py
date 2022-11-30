# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

'''mindformers init'''
from .dataset import MIMDataset, ImageCLSDataset
from .models import ClipModel, ClipConfig, ClipVisionConfig,\
    ClipTextConfig, MaeConfig, MaeModel
from .modules import *
from .wrapper import ClassificationMoeWrapper
from .processor import *
from .pipeline import *
from .tools import logger, MindFormerRegister,\
    MindFormerModuleType, MindFormerConfig, CFTS
from .common import *

from .mindformer_book import MindFormerBook
from .auto_class import (
    AutoConfig, AutoModel,
    AutoFeatureExtractor, AutoProcessor
)
