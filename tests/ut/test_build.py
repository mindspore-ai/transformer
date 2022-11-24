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
Test module for testing the interface used for xformer.
How to run this:
python tests/ut/test_build.py
"""

from dataclasses import dataclass
from typing import Callable

from mindspore.nn import AdamWeightDecay, CosineDecayLR, Accuracy,\
    TrainOneStepWithLossScaleCell, L1Loss
from mindspore.train.callback import LossMonitor, TimeMonitor
from mindspore import Parameter, Tensor

from xformer.tools import logger
from xformer.tools import XFormerConfig, XFormerRegister, XFormerModuleType
from xformer.common.lr import build_lr
from xformer.common.optim import build_optim
from xformer.common.loss import build_loss
from xformer.common.metric import build_metric
from xformer.trainer import build_trainer, BaseTrainer
from xformer.models import build_model, BaseModel
from xformer.dataset import build_dataset, build_sampler, check_dataset_config, \
    build_dataset_loader, build_mask, build_transforms, BaseDataset
from xformer.pipeline import build_pipeline
from xformer.wrapper import build_wrapper
from xformer.processor import build_processor


@XFormerRegister.register(XFormerModuleType.DATASET_LOADER)
class TestDataLoader:
    """Test DataLoader API For Register."""
    def __init__(self, dataset_dir=None):
        self.dataset_dir = dataset_dir


@XFormerRegister.register(XFormerModuleType.DATASET_SAMPLER)
class TestSampler:
    """Test Sampler API For Register."""
    def __init__(self):
        pass


@XFormerRegister.register(XFormerModuleType.TRANSFORMS)
class TestTransforms1:
    """Test Transforms API For Register."""
    def __init__(self):
        pass


@XFormerRegister.register(XFormerModuleType.TRANSFORMS)
class TestTransforms2:
    """Test Transforms API For Register."""
    def __init__(self):
        pass


@XFormerRegister.register(XFormerModuleType.MASK_POLICY)
class TestModelMask:
    """Test Model Mask API For Register."""
    def __init__(self):
        pass


@XFormerRegister.register(XFormerModuleType.MODULES)
class TestAttentionModule:
    """Test Module API For Register."""
    def __init__(self):
        pass


@XFormerRegister.register(XFormerModuleType.DATASET)
class TestDataset(BaseDataset):
    """Test Dataset API For Register."""
    def __init__(self, dataset_config: dict = None):
        super(TestDataset, self).__init__(dataset_config)
        self.config = dataset_config

    def __new__(cls, dataset_config: dict = None):
        if dataset_config is not None:
            build_dataset_loader(dataset_config.data_loader)
            logger.info("Test Build DataLoader Success")
            build_sampler(dataset_config.sampler)
            logger.info("Test Build Sampler Success")
            build_transforms(dataset_config.transforms)
            logger.info("Test Build Transforms Success")
            build_mask(dataset_config.mask_policy)
            logger.info("Test Build Mask Policy Success")
        else:
            build_dataset_loader(class_name='TestDataLoader')
            logger.info("Test Build DataLoader Success")
            build_sampler(class_name='TestSampler')
            logger.info("Test Build Sampler Success")
            build_transforms(class_name='TestTransforms1')
            logger.info("Test Build Transforms Success")
            build_mask(class_name='TestModelMask')
            logger.info("Test Build Mask Policy Success")


@XFormerRegister.register(XFormerModuleType.MODELS)
class TestModel(BaseModel):
    """Test Model API For Register."""
    def __init__(self, config: dict = None):
        super(TestModel, self).__init__()
        self.config = config
        self.params = Parameter(Tensor([0.1]))

    def construct(self, *inputs, **kwargs):
        pass


@XFormerRegister.register(XFormerModuleType.TOKENIZER)
class TestTokenizer:
    """Test Tokenizer API For Register."""
    def __init__(self):
        pass


@XFormerRegister.register(XFormerModuleType.CONFIG)
@dataclass
class TestTextConfig:
    """Test TextConfig API For Register."""
    seq_length: int = 12


@XFormerRegister.register(XFormerModuleType.CONFIG)
@dataclass
class TestVisionConfig:
    """Test VisionConfig API For Register."""
    seq_length: int = 12


@XFormerRegister.register(XFormerModuleType.CONFIG)
@dataclass
class TestModelConfig:
    """Test ModelConfig API For Register."""
    batch_size: int = 2
    embed_dim: int = 768
    text_config: Callable = TestTextConfig
    vision_config: Callable = TestVisionConfig


@XFormerRegister.register(XFormerModuleType.OPTIMIZER)
class TestAdamWeightDecay(AdamWeightDecay):
    """Test AdamWeightDecay API For Register."""
    def __init__(self, params, learning_rate=1e-3, beta1=0.9, beta2=0.999, eps=1e-6, weight_decay=0.0):
        super(TestAdamWeightDecay, self).__init__(params, learning_rate=learning_rate,
                                                  beta1=beta1, beta2=beta2, eps=eps,
                                                  weight_decay=weight_decay)
        self.param = params


@XFormerRegister.register(XFormerModuleType.LR)
class TestCosineDecayLR(CosineDecayLR):
    """Test CosineDecayLR API For Register."""
    def __init__(self, min_lr, max_lr, decay_steps):
        super(TestCosineDecayLR, self).__init__(min_lr, max_lr, decay_steps)
        self.lr = max_lr


@XFormerRegister.register(XFormerModuleType.WRAPPER)
class TestTrainOneStepWithLossScaleCell(TrainOneStepWithLossScaleCell):
    """Test TrainOneStepWithLossScaleCell API For Register."""
    def __init__(self, network, optimizer, scale_sense):
        super(TestTrainOneStepWithLossScaleCell, self).__init__(network, optimizer, scale_sense)
        self.scale_sense = scale_sense


@XFormerRegister.register(XFormerModuleType.METRIC)
class TestAccuracy(Accuracy):
    """Test Accuracy API For Register."""
    def __init__(self, eval_type='classification'):
        super(TestAccuracy, self).__init__(eval_type)
        self.eval = eval_type


@XFormerRegister.register(XFormerModuleType.LOSS)
class TestL1Loss(L1Loss):
    """Test L1Loss API For Register."""
    def __init__(self, reduction='mean'):
        super(TestL1Loss, self).__init__(reduction)
        self.reduction = reduction


@XFormerRegister.register(XFormerModuleType.CALLBACK)
class TestLLossMonitor(LossMonitor):
    """Test LossMonitor API For Register."""
    def __init__(self, per_print_times=1):
        super(TestLLossMonitor, self).__init__(per_print_times)
        self.print = per_print_times


@XFormerRegister.register(XFormerModuleType.CALLBACK)
class TestTimeMonitor(TimeMonitor):
    """Test TimeMonitor API For Register."""
    def __init__(self, data_size=1):
        super(TestTimeMonitor, self).__init__(data_size)
        self.data_size = data_size


@XFormerRegister.register(XFormerModuleType.PIPELINE)
class TestPipeline:
    """Test Pipeline API For Register."""
    def __init__(self):
        pass


@XFormerRegister.register(XFormerModuleType.PROCESSOR)
class TestProcessor:
    """Test Processor API For Register."""
    def __init__(self):
        pass


@XFormerRegister.register(XFormerModuleType.TRAINER)
class TestTaskTrainer(BaseTrainer):
    """Test TimeMonitor API For Register."""
    def __init__(self, model_name='vit'):
        super(TestTaskTrainer, self).__init__(model_name)
        self.model_name = model_name


def test_build_from_config(config: dict = None):
    """ Test build API from config. """
    # build dataset
    check_dataset_config(config)
    build_dataset(config.train_dataset_task)

    logger.info("Test Build Dataset Success")

    # build model
    model = build_model(config.model)
    logger.info("Test Build Network Success")

    # build lr
    lr = build_lr(config.lr_schedule)
    logger.info("Test Build LR Success")

    # build optimizer
    if lr is not None:
        optimizer = build_optim(config.optimizer, default_args={"params": model.trainable_params(),
                                                                "learning_rate": lr})
    else:
        optimizer = build_optim(config.optimizer, default_args={"params": model.trainable_params()})
    logger.info("Test Build Optimizer Success")

    # build wrapper
    build_wrapper(config.runner_wrapper,
                  default_args={"network": model, "optimizer": optimizer})
    logger.info("Test Build Wrapper Success")

    build_loss(config.loss)
    logger.info("Test Build Loss Success")

    build_metric(config.metric)
    logger.info("Test Build Metric Success")

    build_processor(config.processor)
    logger.info("Test Build Processor Success")

    # build trainer
    build_trainer(config.trainer)
    logger.info("Test Build Trainer Success")

    # build pipeline
    build_pipeline(config.pipeline)
    logger.info("Test Build Pipeline Success")


def test_build_from_class_name():
    """ Test build API from class name. """
    # build dataset
    build_dataset(class_name='TestDataset')
    logger.info("Test Build Dataset Success")
    # build model
    model = build_model(class_name='TestModel')
    logger.info("Test Build Network Success")
    # build lr
    lr = build_lr(class_name='TestCosineDecayLR', min_lr=0., max_lr=0.001, decay_steps=1000)
    logger.info("Test Build LR Success")
    # build optimizer
    if lr is not None:
        optimizer = build_optim(class_name='TestAdamWeightDecay',
                                params=model.trainable_params(), learning_rate=lr)
    else:
        optimizer = build_optim(class_name='TestAdamWeightDecay', params=model.trainable_params())
    logger.info("Test Build Optimizer Success")

    # build loss
    build_loss(class_name='TestL1Loss')
    logger.info("Test Build Loss Success")

    # build metric
    build_metric(class_name='TestAccuracy')
    logger.info("Test Build Metric Success")

    # build wrapper
    scale_sense = Tensor(1.0)
    build_wrapper(class_name='TestTrainOneStepWithLossScaleCell',
                  network=model, optimizer=optimizer, scale_sense=scale_sense)
    logger.info("Test Build Wrapper Success")

    # build processor
    build_processor(class_name='TestProcessor')
    logger.info("Test Build Processor Success")

    # build trainer
    build_trainer(class_name='TestTaskTrainer')
    logger.info("Test Build Trainer Success")

    # build pipeline
    build_pipeline(class_name='TestPipeline')
    logger.info("Test Build Pipeline Success")


if __name__ == "__main__":
    import os

    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    yaml_path = os.path.join(path, 'tests', 'ut', 'test_build.yaml')
    test_config = XFormerConfig(yaml_path)
    test_build_from_config(test_config)
    test_build_from_class_name()
