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

"""
BaseConfig class,
which is all model configs' base class
"""
import os
import yaml

from ..mindformer_book import MindFormerBook
from ..mindformer_book import print_path_or_list
from ..tools import logger
from ..tools.register.config import MindFormerConfig
from ..tools.download_tools import downlond_with_progress_bar
from ..models.build_config import build_model_config


class BaseConfig(dict):
    """
    Base Config for all models' config
    """
    _support_list = []

    def __init__(self, **kwargs):
        super(BaseConfig, self).__init__()
        self.update(kwargs)

    def __getattr__(self, key):
        if key not in self:
            return None
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        del self[key]

    def to_dict(self):
        """
        for yaml dump,
        transform from Config to a strict dict class
        """
        return_dict = {}
        for key, val in self.items():
            if isinstance(val, BaseConfig):
                val = val.to_dict()
            return_dict[key] = val
        return return_dict

    @classmethod
    def from_pretrained(cls, yaml_name_or_path):
        """
        From pretrain method, which instantiates a config by yaml name or path.

        Args:
            yaml_name_or_path (str): A supported model name or a path to model
            config (.yaml), the supported model name could be selected from
            AutoConfig.show_support_list().

        Returns:
            A model config, which inherited from BaseConfig.
        """
        if not isinstance(yaml_name_or_path, str):
            raise TypeError(f"yaml_name_or_path should be a str,"
                            f" but got {type(yaml_name_or_path)}.")

        if os.path.exists(yaml_name_or_path):
            if not yaml_name_or_path.endswith(".yaml"):
                raise ValueError(f"{yaml_name_or_path} should be a .yaml file for model"
                                 " config.")

            config_args = MindFormerConfig(yaml_name_or_path)
            logger.info("the content in %s is used for"
                        " config building.", yaml_name_or_path)
        elif yaml_name_or_path not in cls._support_list:
            raise ValueError(f"{yaml_name_or_path} is not a supported"
                             f" model type or a valid path to model config."
                             f" supported model could be selected from {cls._support_list}.")
        else:
            checkpoint_path = os.path.join(MindFormerBook.get_default_checkpoint_download_folder(),
                                           yaml_name_or_path.split('_')[0])
            if not os.path.exists(checkpoint_path):
                os.makedirs(checkpoint_path)

            yaml_file = os.path.join(checkpoint_path, yaml_name_or_path + ".yaml")
            if not os.path.exists(yaml_file):
                url = MindFormerBook.get_model_config_url_list()[yaml_name_or_path][0]
                succeed = downlond_with_progress_bar(url, yaml_file)

                if not succeed:
                    yaml_file = os.path.join(
                        MindFormerBook.get_project_path(),
                        "configs", yaml_name_or_path.split('_')[0],
                        "model_config", yaml_name_or_path + ".yaml"
                    )
                    logger.info("yaml download failed, default config in %s is used.", yaml_file)
                else:
                    logger.info("the content in %s is used for"
                                " config building.", yaml_file)
            config_args = MindFormerConfig(yaml_file)

        config = build_model_config(config_args.model.model_config)
        return config

    def save_pretrained(self, save_directory=None, save_name="mindspore_model"):
        """
        Save_pretrained.

        Args:
            save_directory (str): a directory to save config yaml

            save_name (str): the name of save files.
        """
        if save_directory is None:
            save_directory = MindFormerBook.get_default_checkpoint_save_folder()

        if not isinstance(save_directory, str) or not isinstance(save_name, str):
            raise TypeError(f"save_directory and save_name should be a str,"
                            f" but got {type(save_directory)} and {type(save_name)}.")

        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        save_path = os.path.join(save_directory, save_name + ".yaml")

        parsed_config = self._inverse_parse_config()
        wraped_config = self._wrap_config(parsed_config)

        meraged_dict = {}
        if os.path.exists(save_path):
            with open(save_path, 'r') as file_reader:
                meraged_dict = yaml.load(file_reader.read(), Loader=yaml.Loader)
            file_reader.close()
        meraged_dict.update(wraped_config)

        with open(save_path, 'w') as file_pointer:
            file_pointer.write(yaml.dump(meraged_dict))
        file_pointer.close()
        logger.info("model saved successfully!")

    def inverse_parse_config(self):
        """inverse_parse_config"""
        return self._inverse_parse_config()

    def _inverse_parse_config(self):
        """
        Inverse parse config method, which builds yaml file content for model config.

        Returns:
            A model config, which follows the yaml content.
        """
        self.update({"type": self.__class__.__name__})

        for key, val in self.items():
            if isinstance(val, BaseConfig):
                val = val.inverse_parse_config()
            self.update({key: val})

        return self

    def _wrap_config(self, config):
        """
        Wrap config function, which wraps a config to rebuild content of yaml file.

        Args:
            config (BaseConfig): a config processed by _inverse_parse_config function.

        Returns:
            A (config) dict for yaml.dump.
        """
        config_name = self.__class__.__name__
        model_name = MindFormerBook.get_model_config_to_name().get(config_name, None)
        if not model_name:
            raise ValueError("cannot get model_name from model_config, please use"
                             " MindFormerBook.set_model_config_to_name(model_config, model_name).")
        return {"model": {"model_config": config.to_dict(), "arch": {"type": model_name}}}

    @classmethod
    def show_support_list(cls):
        """show support list method"""
        logger.info("support list of %s is:", cls.__name__)
        print_path_or_list(cls._support_list)

    @classmethod
    def get_support_list(cls):
        """get support list method"""
        return cls._support_list
