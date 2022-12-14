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
Test Module for testing clip_pretrain dataset for clip trainer.

How to run this:
windows:
pytest .\\tests\\st\\test_trainer\\
test_contrastive_language_image_pretrain_trainer\\test_dataset.py
linux:
pytest ./tests/st/test_trainer
/test_contrastive_language_image_pretrain_trainer/test_dataset.py
"""
import os
import numpy as np
from PIL import Image

from mindformers.mindformer_book import MindFormerBook
from mindformers.tools.register.config import MindFormerConfig
from mindformers.dataset.build_dataset import build_dataset


class TestClipPretrainDataset:
    """A test class for testing ContrastiveLanguageImagePretrainDataset classes"""
    def setup_method(self):
        """prepare for test"""
        project_path = MindFormerBook.get_project_path()

        config_path = os.path.join(
            project_path, "configs", "clip",
            "task_config", "clip_flickr8k_dataset.yaml"
        )
        config = MindFormerConfig(config_path)

        new_dataset_dir, new_annotation_dir, local_root = self.make_local_directory(config)
        self.make_dataset(new_dataset_dir, new_annotation_dir, num=100)
        self.local_root = local_root

        config.train_dataset.data_loader.dataset_dir = new_dataset_dir
        config.train_dataset.data_loader.annotation_dir = new_annotation_dir
        self.config = config

    def test_dataset(self):
        """
        Feature: ContrastiveLanguageImagePretrainDataset
        Description: A data set for contrastive language image pretrain
        Expectation: TypeError, ValueError
        """
        data_loader = build_dataset(self.config.train_dataset_task)
        for item in data_loader:
            assert item[0].shape == (32, 3, 224, 224)
            assert item[1].shape == (32, 77)

    def make_local_directory(self, config):
        """make local directory"""
        dataset_dir = config.train_dataset.data_loader.dataset_dir
        local_root = os.path.join(
            MindFormerBook.get_default_checkpoint_download_folder(),
            dataset_dir.split("/")[2]
        )

        new_dataset_dir = MindFormerBook.get_default_checkpoint_download_folder()
        for item in dataset_dir.split("/")[2:]:
            new_dataset_dir = os.path.join(new_dataset_dir, item)

        annotation_dir = config.train_dataset.data_loader.annotation_dir
        new_annotation_dir = MindFormerBook.get_default_checkpoint_download_folder()
        for item in annotation_dir.split("/")[2:]:
            new_annotation_dir = os.path.join(new_annotation_dir, item)

        os.makedirs(new_dataset_dir, exist_ok=True)
        os.makedirs(new_annotation_dir, exist_ok=True)
        return new_dataset_dir, new_annotation_dir, local_root

    def make_dataset(self, new_dataset_dir, new_annotation_dir, num):
        """make a fake Flickr8k dataset"""
        for index in range(num):
            image = Image.fromarray(np.ones((478, 269, 3)).astype(np.uint8))
            image.save(os.path.join(new_dataset_dir, f"test_image_{index}.jpg"))

        token_file = os.path.join(new_annotation_dir, "Flickr8k.token.txt")
        with open(token_file, 'w', encoding='utf-8') as filer:
            for index in range(num):
                filer.write(f"test_image_{index}.jpg#0"
                            f"   A child in a pink dress is climbing"
                            f" up a set of stairs in an entry way .\n")
                filer.write(f"test_image_{index}.jpg#1"
                            f"   A girl going into a wooden building .\n")
                filer.write(f"test_image_{index}.jpg#2"
                            f"   A little girl climbing into a wooden playhouse .\n")
                filer.write(f"test_image_{index}.jpg#3"
                            f"   A little girl climbing the stairs to her playhouse .\n")
                filer.write(f"test_image_{index}.jpg#4"
                            f"   A little girl in a pink dress going into a wooden cabin .\n")

        train_file = os.path.join(new_annotation_dir, "Flickr_8k.trainImages.txt")
        with open(train_file, 'w', encoding='utf-8') as filer:
            for index in range(num):
                filer.write(f"test_image_{index}.jpg\n")

        test_file = os.path.join(new_annotation_dir, "Flickr_8k.testImages.txt")
        with open(test_file, 'w', encoding='utf-8') as filer:
            for index in range(num):
                filer.write(f"test_image_{index}.jpg\n")

        dev_file = os.path.join(new_annotation_dir, "Flickr_8k.devImages.txt")
        with open(dev_file, 'w', encoding='utf-8') as filer:
            for index in range(num):
                filer.write(f"test_image_{index}.jpg\n")
