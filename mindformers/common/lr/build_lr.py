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
"""Build LR Schedule API."""
import inspect

from mindspore import nn

from mindformers.tools.register import MindFormerRegister, MindFormerModuleType


def build_lr(
        config: dict = None, default_args: dict = None,
        module_type: str = 'lr', class_name: str = None, **kwargs):
    """Build LR API."""
    if config is None and class_name is None:
        return None
    if config is not None:
        return MindFormerRegister.get_instance_from_cfg(
            config, MindFormerModuleType.LR, default_args=default_args)
    return MindFormerRegister.get_instance(module_type, class_name, **kwargs)


def register_ms_lr():
    """ register MindSpore builtin LR class. """
    for module_name in dir(nn.learning_rate_schedule):
        if module_name.startswith('__'):
            continue
        lr_schedule = getattr(nn.learning_rate_schedule, module_name)
        if inspect.isclass(lr_schedule):
            MindFormerRegister.register_cls(
                lr_schedule, MindFormerModuleType.LR)


register_ms_lr()
