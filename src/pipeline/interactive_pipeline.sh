#!/bin/bash
# Runs the entire pipeline on the provided data
# Created on 1 May 2020

######CONSTANTS

PIPELINE_DIR="/home/kikuchio/nlp/src"
#INPUT_PATH="${PIPELINE_DIR}/data/tmp/pipeline_data.jsonl"
INPUT_PATH="data/tmp/pipeline_data.jsonl"
DOC_PREDS_OUTPUT="data/tmp/doc_preds.jsonl"
SEN_PREDS_OUTPUT="data/tmp/sen_preds.jsonl"

#####FUNCTIONS

usage() {
  echo "interactive_pipeline: run the entire pipeline, consisting of document retrieval,
  sentence selection, and rte on the provided data"
  echo -e "\nUsage: interactive_pipeline.sh"
}

clean_up() {
  exit 0
}

######MAIN

trap clean_up SIGINT SIGTERM SIGHUP

cd "$PIPELINE_DIR"
rm "$DOC_PREDS_OUTPUT" "$SEN_PREDS_OUTPUT" &> /dev/null

case "$1" in
  "--help")
    usage 
      exit 0
        ;;
esac

# run doc retrieval
#export PYTHONPATH="/home/kikuchio/nlp/src/" 
#echo "======= running document retrieval"
#/opt/conda/bin/python -u -m pipeline.doc_ret --dataset "$INPUT_PATH"
#
## run sentence selection
#echo "======= running sentence selection"
#/opt/conda/bin/python -u -m pipeline.sen_ret 
/opt/conda/bin/python -u -m pipeline.ret_pipeline --dataset "$INPUT_PATH"
