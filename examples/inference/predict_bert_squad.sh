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
echo "for example: bash scripts/predict_bert_squad.sh"
echo "assessment_method include: [Accuracy]"
echo "=============================================================================================================="

mkdir -p ms_log
CUR_DIR=`pwd`

export GLOG_log_dir=${CUR_DIR}/ms_log
export GLOG_logtostderr=0

python -m transformer.tasks.question_answering \
    --auto_model="bert_squad" \
    --eval_json_path="/squad_path/dev-v1.1.json" \
    --checkpoint_prefix='squad' \
    --load_checkpoint_path="./squad_ckpt" \
    --vocab_file_path="./vocab.txt" \
    --embedding_size=768 \
    --num_layers=12 \
    --num_heads=12 > squad_eval.txt 2>&1 &