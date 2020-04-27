#!/usr/bin/env python
"""
Preprocess the SNLI dataset and word embeddings to be used by the ESIM model.
"""
# Aurelien Coet, 2018.

import os
import pickle
import argparse
import fnmatch
import json

from rte.coetaur0.esim.fever_data import Preprocessor


def preprocess_SNLI_data(inputdir,
                         embeddings_file,
                         targetdir,
                         lowercase=False,
                         ignore_punctuation=False,
                         num_words=None,
                         stopwords=[],
                         labeldict={},
                         bos=None,
                         eos=None,
                         testing=False,
                         concat_premises=True):
    """
    Preprocess the data from the SNLI corpus so it can be used by the
    ESIM model.
    Compute a worddict from the train set, and transform the words in
    the sentences of the corpus to their indices, as well as the labels.
    Build an embedding matrix from pretrained word vectors.
    The preprocessed data is saved in pickled form in some target directory.

    Args:
        inputdir: The path to the directory containing the NLI corpus.
        embeddings_file: The path to the file containing the pretrained
            word vectors that must be used to build the embedding matrix.
        targetdir: The path to the directory where the preprocessed data
            must be saved.
        lowercase: Boolean value indicating whether to lowercase the premises
            and hypotheseses in the input data. Defautls to False.
        ignore_punctuation: Boolean value indicating whether to remove
            punctuation from the input data. Defaults to False.
        num_words: Integer value indicating the size of the vocabulary to use
            for the word embeddings. If set to None, all words are kept.
            Defaults to None.
        stopwords: A list of words that must be ignored when preprocessing
            the data. Defaults to an empty list.
        bos: A string indicating the symbol to use for beginning of sentence
            tokens. If set to None, bos tokens aren't used. Defaults to None.
        eos: A string indicating the symbol to use for end of sentence tokens.
            If set to None, eos tokens aren't used. Defaults to None.
        testing: indicates to the dataset preprocessor whether it is
            preprocessing testing data (which does not contain labels),
            or training and dev data (which contain labels).
        concat_premises: concatenate the sentences together or keep them separate.
    """
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

    # Retrieve the train, dev and test data files from the dataset directory.
    train_file = ""
    dev_file = ""
    test_file = ""
    for file in os.listdir(inputdir):
        if fnmatch.fnmatch(file, "train*.jsonl"):
            train_file = file
        elif fnmatch.fnmatch(file, "dev*.jsonl"):
            dev_file = file
        elif fnmatch.fnmatch(file, "sen_preds.jsonl"):
            test_file = file
            print("test file is ", test_file)

    preprocessor = Preprocessor(lowercase=lowercase,
                                ignore_punctuation=ignore_punctuation,
                                num_words=num_words,
                                stopwords=stopwords,
                                labeldict=labeldict,
                                bos=bos,
                                eos=eos, concat_premises=concat_premises)

    # -------------------- Train data preprocessing -------------------- #
    if not testing:
        print(20 * "=", " Preprocessing train set ", 20 * "=")
        print("\t* Reading data...")
        data = preprocessor.read_data(os.path.join(inputdir, train_file))

        print("\t* Computing worddict and saving it...")
        preprocessor.build_worddict(data)
        with open(os.path.join(targetdir, "worddict.pkl"), "wb") as pkl_file:
            pickle.dump(preprocessor.worddict, pkl_file)

        print("\t* Transforming words in premises and hypotheses to indices...")
        transformed_data = preprocessor.transform_to_indices(data)
        print("\t* Saving result...")
        with open(os.path.join(targetdir, "train_data.pkl"), "wb") as pkl_file:
            pickle.dump(transformed_data, pkl_file)

        # -------------------- Validation data preprocessing -------------------- #
        print(20 * "=", " Preprocessing dev set ", 20 * "=")
        print("\t* Reading data...")
        data = preprocessor.read_data(os.path.join(inputdir, dev_file))

        print("\t* Transforming words in premises and hypotheses to indices...")
        transformed_data = preprocessor.transform_to_indices(data)
        print("\t* Saving result...")
        with open(os.path.join(targetdir, "dev_data.pkl"), "wb") as pkl_file:
            pickle.dump(transformed_data, pkl_file)

        # -------------------- Embeddings preprocessing -------------------- #
        print(20 * "=", " Preprocessing embeddings ", 20 * "=")
        print("\t* Building embedding matrix and saving it...")
        embed_matrix = preprocessor.build_embedding_matrix(embeddings_file)
        with open(os.path.join(targetdir, "embeddings.pkl"), "wb") as pkl_file:
            pickle.dump(embed_matrix, pkl_file)

    # -------------------- Test data preprocessing -------------------- #
    # since the test dataset depends on the predictions by the earlier stages
    # of the pipeline, we don't yet have the predicted evidence on which
    # the rte part is to be run, therefore we cannot preprocess the test
    # dataset without making sure that we ran the previous stages.
    if testing:
        with open(os.path.join(targetdir, "worddict.pkl"), "rb") as pkl_file:
            preprocessor.worddict = pickle.load(pkl_file)

        print(20 * "=", " Preprocessing test set ", 20 * "=")
        print("\t* Reading data...")

        # here, test_file should contain predicted evidence
        data = preprocessor.read_data(os.path.join(inputdir, test_file), testing)

        print("\t* Transforming words in premises and hypotheses to indices...")
        transformed_data = preprocessor.transform_to_indices(data)
        print("\t* Saving result...")
        with open(os.path.join(targetdir, "test_data.pkl"), "wb") as pkl_file:
            pickle.dump(transformed_data, pkl_file)


if __name__ == "__main__":
    default_config = "../../config/preprocessing/fever_preprocessing.json"
    default_sen_config = "../../config/sentence_params.json"

    parser = argparse.ArgumentParser(description="Preprocess the SNLI dataset")
    parser.add_argument(
        "--config",
        default=default_config,
        help="Path to a configuration file for preprocessing SNLI"
    )
    parser.add_argument(
        "--sentence_config",
        default=default_sen_config,
        help="Path to a configuration file for sentence params"
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.realpath(__file__))

    if args.config == default_config:
        config_path = os.path.join(script_dir, args.config)
    else:
        config_path = args.config

    sen_config_path = args.sentence_config
    if args.sentence_config == default_sen_config:
        sen_config_path = os.path.join(script_dir, args.sentence_config)

    with open(os.path.normpath(config_path), "r") as cfg_file:
        config = json.load(cfg_file)
    with open(os.path.normpath(sen_config_path), "r") as sen_cfg_file:
        sen_config = json.load(sen_cfg_file)

    print("Config is: ", config)
    print("Sentence config is: ", sen_config)

    preprocess_SNLI_data(
        os.path.normpath(os.path.join(script_dir, config["data_dir"])),
        os.path.normpath(os.path.join(script_dir, config["embeddings_file"])),
        os.path.normpath(os.path.join(script_dir, config["target_dir"])),
        lowercase=config["lowercase"],
        ignore_punctuation=config["ignore_punctuation"],
        num_words=config["num_words"],
        stopwords=config["stopwords"],
        labeldict=config["labeldict"],
        bos=config["bos"],
        eos=config["eos"],
        testing=config["testing"],
        concat_premises=sen_config["premises_concat"]
    )
