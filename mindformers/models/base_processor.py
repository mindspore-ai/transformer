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
BaseProcessor
"""
import os
import shutil

import yaml

from ..mindformer_book import print_path_or_list, MindFormerBook
from .build_processor import build_processor
from .base_tokenizer import BaseTokenizer
from ..tools import logger
from ..tools.register import MindFormerConfig


class BaseImageProcessor:
    """
    BaseImageProcessor for all image preprocess.
    """
    def __init__(self, **kwargs):
        self.config = {}
        self.config.update(kwargs)

    def __call__(self, image_data, **kwargs):
        """forward process"""
        return self.preprocess(image_data, **kwargs)

    def preprocess(self, images, **kwargs):
        """preprocess method"""
        raise NotImplementedError("Each image processor must implement its own preprocess method")


class BaseAudioProcessor:
    """
    BaseAudioProcessor for all audio preprocess.
    """
    def __init__(self, **kwargs):
        self.config = {}
        self.config.update(kwargs)

    def __call__(self, audio_data, **kwargs):
        """forward process"""
        return self.preprocess(audio_data, **kwargs)

    def preprocess(self, audio_data, **kwargs):
        """preprocess method"""
        raise NotImplementedError("Each audio processor must implement its own preprocess method")


class BaseProcessor:
    """Base processor"""
    _support_list = []

    def __init__(self, **kwargs):
        self.config = {}
        self.config.update(kwargs)
        self.image_processor = kwargs.pop("image_processor", None)
        self.audio_processor = kwargs.pop("audio_processor", None)
        self.tokenizer = kwargs.pop("tokenizer", None)
        self.max_length = kwargs.pop("max_length", None)
        self.padding = kwargs.pop("padding", False)
        self.return_tensors = kwargs.pop("return_tensors", None)

    def __call__(self, image_input=None, text_input=None):
        """call function"""
        output = {}

        if image_input is not None and self.image_processor:
            if not isinstance(self.image_processor, BaseImageProcessor):
                raise TypeError(f"feature_extractor should inherit from the BaseImageProcessor,"
                                f" but got {type(self.image_processor)}.")

            image_output = self.image_processor(image_input)
            output['image'] = image_output

        if text_input is not None and self.tokenizer:
            if not isinstance(self.tokenizer, BaseTokenizer):
                raise TypeError(f"tokenizer should inherited from the BaseTokenizer,"
                                f" but got {type(self.tokenizer)}.")
            # Format the input into a batch
            if isinstance(text_input, str):
                text_input = [text_input]
            text_output = self.tokenizer(text_input, return_tensors=self.return_tensors,
                                         max_length=self.max_length,
                                         padding=self.padding)["input_ids"]
            output['text'] = text_output

        return output

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

        parsed_config = self._inverse_parse_config(self.config)
        wraped_config = self._wrap_config(parsed_config)

        config_path = os.path.join(save_directory, save_name + '.yaml')
        meraged_dict = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as file_reader:
                meraged_dict = yaml.load(file_reader.read(), Loader=yaml.Loader)
            file_reader.close()
        meraged_dict.update(wraped_config)

        with open(config_path, 'w') as file_pointer:
            file_pointer.write(yaml.dump(meraged_dict))
        file_pointer.close()
        logger.info("processor saved successfully!")

    def _inverse_parse_config(self, config):
        """
        Inverse parse config method, which builds yaml file content for feature extractor config.

        Args:
            Config (dict): a dict, which contains input parameters of feature extractor.

        Returns:
            A dict, which follows the yaml content.
        """
        parsed_config = {"type": self.__class__.__name__}

        for key, val in config.items():
            if isinstance(val, BaseTokenizer):
                parsed_sub_config = {"type": val.__class__.__name__}
                parsed_sub_config.update(val.init_kwargs)
                parsed_config.update({key: parsed_sub_config})
            elif isinstance(val, (BaseImageProcessor, BaseAudioProcessor)):
                parsed_sub_config = {"type": val.__class__.__name__}
                parsed_sub_config.update(self._inverse_parse_config(val.config))
                parsed_config.update({key: parsed_sub_config})
            else:
                parsed_config.update({key: val})
        return parsed_config

    def _wrap_config(self, config):
        """
        Wrap config function, which wraps a config to rebuild content of yaml file.

        Args:
            config (dict): a dict processed by _inverse_parse_config function.

        Returns:
            A dict for yaml.dump.
        """
        return {"processor": config}

    @classmethod
    def from_pretrained(cls, yaml_name_or_path):
        """
        From pretrain method, which instantiates a processor by yaml name or path.

        Args:
            yaml_name_or_path (str): A supported yaml name or a path to .yaml file,
            the supported model name could be selected from .show_support_list().

        Returns:
            A processor which inherited from BaseProcessor.
        """
        if not isinstance(yaml_name_or_path, str):
            raise TypeError(f"yaml_name_or_path should be a str,"
                            f" but got {type(yaml_name_or_path)}")

        is_exist = os.path.exists(yaml_name_or_path)
        if not is_exist and yaml_name_or_path not in cls._support_list:
            raise ValueError(f'{yaml_name_or_path} does not exist,'
                             f' or it is not supported by {cls.__name__}. '
                             f'please select from {cls._support_list}.')
        if is_exist:
            logger.info("config in %s is used for processor"
                        " building.", yaml_name_or_path)

            config_args = MindFormerConfig(yaml_name_or_path)
        else:
            checkpoint_path = os.path.join(MindFormerBook.get_default_checkpoint_download_folder(),
                                           yaml_name_or_path.split("_")[0])
            if not os.path.exists(checkpoint_path):
                os.makedirs(checkpoint_path)

            yaml_file = os.path.join(checkpoint_path, yaml_name_or_path+".yaml")
            if not os.path.exists(yaml_file):
                default_yaml_file = os.path.join(
                    MindFormerBook.get_project_path(),
                    "configs", yaml_name_or_path.split("_")[0],
                    "model_config", yaml_name_or_path + ".yaml")
                if os.path.realpath(default_yaml_file) and os.path.exists(default_yaml_file):
                    shutil.copy(default_yaml_file, yaml_file)
                    logger.info("default yaml config in %s is used.", yaml_file)
                else:
                    raise FileNotFoundError(f'default yaml file path must be correct, but get {default_yaml_file}')

            config_args = MindFormerConfig(yaml_file)

        processor = build_processor(config_args.processor)
        logger.info("processor built successfully!")
        return processor

    @classmethod
    def show_support_list(cls):
        """show_support_list"""
        logger.info("support list of %s is:", cls.__name__)
        print_path_or_list(cls._support_list)

    @classmethod
    def get_support_list(cls):
        """get_support_list method"""
        return cls._support_list
