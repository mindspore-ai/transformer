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

"""Parse arguments"""

import os
import ast
import argparse
from pprint import pprint, pformat
import yaml

from mindspore import log as logger
from mindspore.context import ParallelMode

class Config:
    """
    Configuration namespace. Convert dictionary to members.
    """
    def __init__(self, cfg_dict):
        for k, v in cfg_dict.items():
            if isinstance(v, (list, tuple)):
                setattr(self, k, [Config(x) if isinstance(x, dict) else x for x in v])
            else:
                setattr(self, k, Config(v) if isinstance(v, dict) else v)

    def __str__(self):
        return pformat(self.__dict__)

    def __repr__(self):
        return self.__str__()


def parse_cli_to_yaml(parser, cfg, helper=None, choices=None, cfg_path="default_config.yaml"):
    """
    Parse command line arguments to the configuration according to the default yaml.

    Args:
        parser: Parent parser.
        cfg: Base configuration.
        helper: Helper description.
        cfg_path: Path to the default yaml config.
    """
    parser = argparse.ArgumentParser(description="[REPLACE THIS at config.py]",
                                     parents=[parser])
    helper = {} if helper is None else helper
    choices = {} if choices is None else choices
    for item in cfg:
        help_description = helper[item] if item in helper else "Please reference to {}".format(cfg_path)
        choice = choices[item] if item in choices else None
        if not isinstance(cfg[item], list) and not isinstance(cfg[item], dict):
            if isinstance(cfg[item], bool):
                parser.add_argument("--" + item, type=ast.literal_eval, default=cfg[item], choices=choice,
                                    help=help_description)
            else:
                parser.add_argument("--" + item, type=type(cfg[item]), default=cfg[item], choices=choice,
                                    help=help_description)
        else:
            parser.add_argument("--" + item, type=type(cfg[item][0]), default=cfg[item], nargs='+',
                                help=help_description)
    args = parser.parse_args()
    return args


def parse_yaml(yaml_path):
    """
    Parse the yaml config file.

    Args:
        yaml_path: Path to the yaml config.
    """
    with open(yaml_path, 'r') as fin:
        try:
            cfgs = yaml.load_all(fin.read(), Loader=yaml.FullLoader)
            cfgs = [x for x in cfgs]
            if len(cfgs) == 1:
                cfg_helper = {}
                cfg = cfgs[0]
                cfg_choices = {}
            elif len(cfgs) == 2:
                cfg, cfg_helper = cfgs
                cfg_choices = {}
            elif len(cfgs) == 3:
                cfg, cfg_helper, cfg_choices = cfgs
            else:
                raise ValueError("At most 3 docs (config, description for help, choices) are supported in config yaml")
            print(cfg_helper)
        except:
            raise ValueError("Failed to parse yaml")
    return cfg, cfg_helper, cfg_choices


def merge(args, cfg):
    """
    Merge the base config from yaml file and command line arguments.

    Args:
        args: Command line arguments.
        cfg: Base configuration.
    """
    args_var = vars(args)
    for item in args_var:
        cfg[item] = args_var[item]
    return cfg


def modify_batch_size(config):
    """
    When auto parallel enabled, the batch size will be overwritten by the global batch size
    Mark the global batch size as a logic batch.
    """
    global_batch_size = config['global_batch_size']
    batch_size = config['batch_size']
    device_num = config['device_num']
    if config['parallel_mode'] in (ParallelMode.AUTO_PARALLEL, ParallelMode.SEMI_AUTO_PARALLEL):
        if global_batch_size % device_num != 0:
            logger.error(f"The global batch size {global_batch_size} \
            should be a multiplied by the {batch_size}.")
        if global_batch_size // device_num == 0:
            logger.warning(f"The global batch size {global_batch_size} // {device_num} \
            should not be equal to 0.")
        if global_batch_size % device_num == 0:
            logger.warning("The batch size is overwritten by the global batch size // device_num.")
            config['batch_size'] = global_batch_size // device_num
    else:
        if batch_size != global_batch_size:
            logger.warning("The batch size is overwritten by the global batch size.")
            config['batch_size'] = global_batch_size


def get_config():
    """
    Get Config according to the yaml file and cli arguments.
    """
    parser = argparse.ArgumentParser(description="default name", add_help=False)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '../default_config.yaml')
    default, helper, choices = parse_yaml(config_path)
    args = parse_cli_to_yaml(parser=parser, cfg=default, helper=helper, choices=choices, cfg_path=config_path)
    final_config = merge(args, default)
    modify_batch_size(final_config)
    pprint(final_config)
    pprint(final_config['bucket_boundaries'])
    pprint("Please check the above information for the configurations")
    return Config(final_config)