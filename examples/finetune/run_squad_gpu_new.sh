#!/bin/bash
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

echo "=============================================================================================================="
echo "Please run the script as: "
echo "bash scripts/run_squad_gpu.sh"
echo "for example: bash scripts/run_squad_gpu.sh"
echo "assessment_method include: [Accuracy]"
echo "=============================================================================================================="

mkdir -p ms_log
CUR_DIR=`pwd`
export GLOG_log_dir=${CUR_DIR}/ms_log
export GLOG_logtostderr=0
python transformer/trainer/trainer.py  \
    --auto_model="bert_squad" \
    --device_target="GPU" \
    --device_id=0 \
    --epoch_num=3 \
    --num_class=2 \
    --vocab_size=30522 \
    --embedding_size=768 \
    --num_layers=12 \
    --num_heads=12 \
    --seq_length=384 \
    --max_position_embeddings=512 \
    --train_data_shuffle="true" \
    --eval_data_shuffle="false" \
    --train_batch_size=2 \
    --eval_batch_size=1 \
    --vocab_file_path="./vocab.txt" \
    --save_checkpoint_path="./squad_ckpt" \
    --load_checkpoint_path="./checkpoint/bert_base1.ckpt" \
    --train_data_path="./squad_data/train.mindrecord"

python transformer/tasks/question_answering.py \
    --auto_model="bert_squad" \
    --eval_json_path="./squad_data/dev-v1.1.json" \
    --load_checkpoint_path="./checkpoint/bert_base1.ckpt" \
    --vocab_file_path="./vocab.txt"
