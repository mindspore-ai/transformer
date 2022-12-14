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
"""Image Classification Dataset."""
import mindspore.dataset.transforms.c_transforms as C
import mindspore.common.dtype as mstype

from mindformers.tools.register import MindFormerRegister, MindFormerModuleType
from mindformers.tools.logger import logger
from .dataloader import build_dataset_loader
from .transforms import build_transforms
from .sampler import build_sampler
from .base_dataset import BaseDataset


@MindFormerRegister.register(MindFormerModuleType.DATASET)
class ImageCLSDataset(BaseDataset):
    """Image Classification Dataset API."""
    def __new__(cls, dataset_config: dict = None):
        logger.info("Now Create Image Classification Dataset.")
        cls.init_dataset_config(dataset_config)
        dataset = build_dataset_loader(dataset_config.data_loader)
        transforms = build_transforms(dataset_config.transforms)
        sampler = build_sampler(dataset_config.sampler)
        type_cast_op = C.TypeCast(mstype.int32)

        if sampler is not None:
            dataset = dataset.use_sampler(sampler)

        if transforms is not None:
            dataset = dataset.map(
                input_columns=dataset_config.input_columns[0],
                operations=transforms,
                num_parallel_workers=dataset_config.num_parallel_workers,
                python_multiprocessing=dataset_config.python_multiprocessing)

        dataset = dataset.map(
            input_columns=dataset_config.input_columns[1],
            num_parallel_workers=dataset_config.num_parallel_workers,
            operations=type_cast_op)

        dataset = dataset.batch(dataset_config.batch_size, drop_remainder=dataset_config.drop_remainder,
                                num_parallel_workers=dataset_config.num_parallel_workers)
        if not dataset_config.do_eval and dataset_config.mixup_op is not None:
            mixup_op = build_transforms(class_name="Mixup", **dataset_config.mixup_op)
            dataset = dataset.map(
                operations=mixup_op, input_columns=dataset_config.input_columns,
                column_order=dataset_config.column_order,
                output_columns=dataset_config.output_columns,
                num_parallel_workers=dataset_config.num_parallel_workers)
        dataset = dataset.repeat(dataset_config.repeat)
        return dataset
