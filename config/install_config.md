# Topic Segmenter Installation


## Environment

Usage of a virtualenvironment is recommended (either through conda or virtualenv).

All the package specification can be found in the `config/` folder.

**With conda** create a exact copy of the environment by running `conda env create -f config/slackpack-environment.yml`

**With virtualenv (or without virtual environments at all)** just use pip `pip install -r config/slackpack-requirements.txt`


## NLTK dependencies

The following NLTK resources need to be downloaded in order to run the topic-segmenter (open `python` run `import nltk` and then run `nltk.download()` for the NLTK resource downloader window to appear):

From the *All packages*

* `averaged_perceptron_tagger`
* `punkt`
* `universal_tagset`

* (in some occasions, additionally) `wordnet`



