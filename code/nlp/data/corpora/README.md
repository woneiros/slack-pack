## NLP Corpora

This folder contains the saved lookup-corpora.

__Note:__
_Each lookup-corpus is not a collection of documents (in the conventional sense of corpus), but rather a dictionary with_ `{term: representation_vector }`

Unless a new custom `nlp.repr.Representation` has been built only gloVe lookup-corpora are contained here.

The default gloVe lookup-corpora are available for download from the following links:
 *  [gloVe trained on](https://s3.amazonaws.com/slack-pack-data/corpora/glove.6B.300d.txt): Common Crawl (42B tokens, 1.9M vocab, uncased, 300d vectors, 1.04 GB download)
 *  [gloVe trained on](https://s3.amazonaws.com/slack-pack-data/corpora/glove.42B.300d.txt): Wikipedia 2014 + Gigaword 5 (6B tokens, 400K vocab, uncased, 300d vectors, 5.03 GB download)
 *  [gloVe trained on](https://s3.amazonaws.com/slack-pack-data/corpora/glove.twitter.27B.200d.txt): Twitter (2B tweets, 27B tokens, 1.2M vocab, uncased, 200d vectors, 2.06 GB download)

The original *zipped* corpora may be downloaded from [stanfordnlp](http://nlp.stanford.edu/data/wordvecs/)
