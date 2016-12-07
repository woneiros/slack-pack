# For our internal toolbox imports
import os
import sys
import logging
path_to_here = os.path.abspath('.')
NLP_PATH = path_to_here[:path_to_here.index('slack-pack') + 10] + '/code/'
sys.path.append(NLP_PATH)


from nlp.text import extractor as xt
from nlp.models.message_classification import SimpleClassifier
from nlp.utils.model_output_management import OutputHelper
from nlp.models.similarity_calculation import MessageSimilarity
from nlp.models.summarization import TFIDF as Model
from nlp.grammar import tokenizer as nt
from nlp.viz.cloud import Wordcloud

logger = logging.getLogger('runner_log')
logger.setLevel(logging.DEBUG)
LOGFILE = 'log/runner_log'

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# create console handler, set level of logging and add formatter
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

# create file handler, set level of logging and add formatter
fh = logging.handlers.TimedRotatingFileHandler(LOGFILE, when='M', interval=1)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
fh.suffix = '%Y-%m-%d_%H-%M-%S.log'

# add handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

FONT_PATH = NLP_PATH + 'nlp/data/font/Ranga-Regular.ttf'
IMG_FOLDER = NLP_PATH + 'nlp/data/img/'
if __name__ == "__main__":
    casdb = xt.CassandraExtractor(cluster_ips=['54.175.189.47'],
                              session_keyspace='test_keyspace',
                              table_name='awaybot_messages')
    teams = casdb.list_teams()
    channels=casdb.list_channels()
    msg_sim = MessageSimilarity()
    for team in teams:
        for channel in channels:
            for p in xrange(1, 13, 1):
                msg_stream = casdb.get_messages(type_of_query='hour', periods=p, channel=channel, min_words=5)
                classifier = SimpleClassifier(message_similarity=msg_sim)
                classified_window = classifier.classify_stream(msg_stream, low_threshold=.4, high_threshold=.7, low_step=.05, high_step=.02, max_messages=10000, verbose=False)
                image_loader = OutputHelper()
                if len(classified_window) == 0:
                    # Create a sdb item that records '0' images for that particular channel and duration
                    image_loader.updateImageCount(team, channel, p, 'hours')
                    continue

                # Create a model using the corpus
                uni_model = Model(window=classified_window, cleaner=nt.SimpleCleaner())
                # bigram_model = Model(window=classified_window, cleaner=nt.SimpleCleaner(), n_grams=2)  # if we wanted a bigram model

                viz_topics = 0
                for t, topic in enumerate(classified_window):  # one(?) per topic
                    if len(topic) >= 3:
                        # Generate the viz out of the model
                        try:
                            viz = Wordcloud(model=uni_model, document_id=t, max_words=10, font=FONT_PATH)
                        except:
                            logger.warning("Failed to generate word cloud for {}".format(viz_path),exc_info=True)
                            continue
                        viz_topics += 1
                        logger.info('topic {} for {} duration {} hour(s) has length {}'.format(t, channel, p, len(topic)))
                        viz_path = IMG_FOLDER + 'cloud_topic_{}_{}_{}_{}.png'.format(channel, 'hours', p, viz_topics)
                        viz.save_png(viz_path, title='Topic {}'.format(viz_topics))

                        # Call image_loader with: img_path + starter_message_url + team + channel + duration + duration_unit
                        image_loader.add_viz(viz_path, topic.start_message.url, topic.start_message.team, channel, p, 'hours')
                        # TODO: parameter-ize the duration unit
                if viz_topics:
                    image_loader.upload()
                else:
                    # Create a sdb item that records '0' images for that particular channel and duration
                    image_loader.updateImageCount(team, channel, p, 'hours')
                logger.info(
                    'Updloaded {} Images for channel {} and '
                    'duration: {} {}'.format(viz_topics, channel, p, 'hour(s)'))
            for p in xrange(1, 8, 1):
                msg_stream = casdb.get_messages(type_of_query='day', periods=p, channel=channel, min_words=5)
                classifier = SimpleClassifier(message_similarity=msg_sim)
                classified_window = classifier.classify_stream(msg_stream, low_threshold=.4, high_threshold=.7, low_step=.05, high_step=.02, max_messages=10000, verbose=False)
                image_loader = OutputHelper()
                if len(classified_window) == 0:
                    # Create a sdb item that records '0' images for that particular channel and duration
                    image_loader.updateImageCount(team, channel, p, 'days')
                    continue

                # Create a model using the corpus
                uni_model = Model(window=classified_window, cleaner=nt.SimpleCleaner())
                # bigram_model = Model(window=classified_window, cleaner=nt.SimpleCleaner(), n_grams=2)  # if we wanted a bigram model

                viz_topics = 0
                for t, topic in enumerate(classified_window):  # one(?) per topic
                    if len(topic) >= 5:
                        try:
                            viz = Wordcloud(model=uni_model, document_id=t, max_words=10, font=FONT_PATH)
                        except:
                            logger.warning("Failed to generate word cloud for {}".format(viz_path),exc_info=True)
                            continue
                        viz_topics += 1
                        logger.info('topic {} for {} duration {} day(s) has length {}'.format(t, channel, p, len(topic)))
                        viz_path = IMG_FOLDER + 'cloud_topic_{}_{}_{}_{}.png'.format(channel, 'days', p, viz_topics)
                        viz.save_png(viz_path, title='Topic {}'.format(viz_topics))

                        # Call image_loader with: img_path + starter_message_url + team + channel + duration + duration_unit
                        image_loader.add_viz(viz_path, topic.start_message.url, topic.start_message.team, channel, p, 'days')
                        # TODO: parameter-ize the duration unit
                if viz_topics:
                    image_loader.upload()
                else:
                    # Create a sdb item that records '0' images for that particular channel and duration
                    image_loader.updateImageCount(team, channel, p, 'days')
                logger.info(
                    'Updloaded {} Images for channel {} and '
                    'duration: {} {}'.format(viz_topics, channel, p, 'day(s)'))
            for p in xrange(1, 7, 1):
                msg_stream = casdb.get_messages(type_of_query='week', periods=p, channel=channel, min_words=5)
                classifier = SimpleClassifier(message_similarity=msg_sim)
                classified_window = classifier.classify_stream(msg_stream, low_threshold=.4, high_threshold=.7, low_step=.05, high_step=.02, max_messages=10000, verbose=False)
                image_loader = OutputHelper()
                if len(classified_window) == 0:
                    image_loader.updateImageCount(team, channel, p, 'weeks')
                    continue

                # Create a model using the corpus
                uni_model = Model(window=classified_window, cleaner=nt.SimpleCleaner())
                # bigram_model = Model(window=classified_window, cleaner=nt.SimpleCleaner(), n_grams=2)  # if we wanted a bigram model

                viz_topics = 0
                for t, topic in enumerate(classified_window):  # one(?) per topic
                    if len(topic) >= 10:
                        try:
                            viz = Wordcloud(model=uni_model, document_id=t, max_words=10, font=FONT_PATH)
                        except:
                            logger.warning("Failed to generate word cloud for {}".format(viz_path),exc_info=True)
                            continue
                        viz_topics += 1
                        logger.info('topic {} for {} duration {} week(s) has length {}'.format(t, channel, p, len(topic)))
                        viz_path = IMG_FOLDER + 'cloud_topic_{}_{}_{}_{}.png'.format(channel, 'weeks', p, viz_topics)
                        viz.save_png(viz_path, title='Topic {}'.format(viz_topics))

                        # Call image_loader with: img_path + starter_message_url + team + channel + duration + duration_unit
                        image_loader.add_viz(viz_path, topic.start_message.url, topic.start_message.team, channel, p, 'weeks')
                        # TODO: parameter-ize the duration unit
                if viz_topics:
                    image_loader.upload()
                else:
                    # Create a sdb item that records '0' images for that particular channel and duration
                    image_loader.updateImageCount(team, channel, p, 'weeks')
                logger.info(
                    'Updloaded {} Images for channel {} and '
                    'duration: {} {}'.format(viz_topics, channel, p, 'week(s)'))
