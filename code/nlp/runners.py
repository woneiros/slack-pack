import os, sys
from nlp.text import extractor as xt


os.path.expanduser('~/slack-pack/code')
sys.path.append(NLP_PATH)

from nlp.models.massage_classification import SimpleClassier as smc
from nlp.utils.model_output_management import OutputHelper as oh


if name == "main":
	casdb = xt.CassandraExtractor(cluster_ips=['54.175.189.47'],
                              session_keyspace='test_keyspace',
                              table_name='awaybot_messages')

    classifier = smc()

	for channel in channels:
		for i in xrange(1,7, 1):
			msg_stream = casdb.get_messages(type_of_query='day', periods=i, channel=channel, min_words=5)
			window_us = classifier.classify_stream(msg_stream, low_threshold=.4, high_threshold=.7, low_step=.05, high_step=.02, max_messages=30)

            # Process the window into a corpus
            corpus = Corpus()

            # Create a model using the corpus
            model = Model(  )

            image_loader = ImaLoad()

            for topic in window_us: # one per topic

                # Generate the viz out od the model
                viz = Wordcloud( --- )

                # Call image_loader
                image_loader.add_viz(viz.viz_path, viz.starter_message)

            image_loader.upload()
