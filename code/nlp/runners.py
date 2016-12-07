import os, sys


# For our internal toolbox imports
import os, sys
path_to_here = os.path.abspath('.')
NLP_PATH = path_to_here[:path_to_here.index('slack-pack') + 10] + '/code/'
sys.path.append(NLP_PATH)


from nlp.text import extractor as xt
from nlp.models.massage_classification import SimpleClassifier
from nlp.utils.model_output_management import OutputHelper



FONT_PATH = '~/slack-pack/code/nlp/data/font/Ranga-Regular.ttf'
IMG_FOLDER = '~/slack-pack/code/nlp/data/img/'

if name == "main":
	casdb = xt.CassandraExtractor(cluster_ips=['54.175.189.47'],
                              session_keyspace='test_keyspace',
                              table_name='awaybot_messages')

    classifier = SimpleClassifier()

	for channel in channels:
		for p in xrange(7):
			msg_stream = casdb.get_messages(type_of_query='day', periods=p, channel=channel, min_words=5)
			classified_window = classifier.classify_stream(msg_stream, low_threshold=.4, high_threshold=.7, low_step=.05, high_step=.02, max_messages=30)

            # Create a model using the corpus
            uni_model = Model(window=classified_window, cleaner=nt.SimpleCleaner())
            # bigram_model = Model(window=classified_window, cleaner=nt.SimpleCleaner(), n_grams=2)  # if we wanted a bigram model

            image_loader = OutputHelper()

            for t, topic in enumerate(classified_window):  # one(?) per topic

                viz_path = IMG_FOLDER + 'cloud_topic{}.png'.format(t)

                # Generate the viz out of the model
                viz = Wordcloud(model=uni_model, t, max_words=10, font=FONT_PATH)
                viz.save_png(viz_path)

                # Call image_loader with: img_path + starter_message_url + team + channel + duration + duration_unit
                image_loader.add_viz(viz_path, topic.starter_message.url, topic.starter_message.team, channel, p, 'day')
                # TODO: parameter-ize the duration unit

            image_loader.upload()
