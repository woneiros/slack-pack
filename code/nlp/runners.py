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
	for channel in channels:
		for i in xrange(1,7, 1):
			msg_stream = smc.get_messages(type_of_query='day', periods=i, channel=channel, min_words=5)
			window_us = classify_stream(msg_stream, distance=dist_m2m, low_threshold=.4, high_threshold=.7, low_step=.05, high_step=.02, max_messages=30)

