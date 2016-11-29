
def classify_stream(message_stream, distance=dist_m2m, max_messages=20, max_active_topics=5,
                    low_threshold=.4, high_threshold=.7, low_step=.05, high_step=.02, verbose=True):
    """Classifies an entire stream of messages by predicting the topic to be appended to

    Parameters
    ----------
    message_stream : iterable of |message|s
        Iterator or list of messages
    distance : callable, optional
        Distance measure between two texts
    max_messages : int, optional
        Maximum amount of messages to classify (for debugging and illustration purposes)
    max_active_topics : int, optional
        Maximum amount of (most-recent) topics a message can be compared to for similarity
    low_threshold : float, optional
        Description
    high_threshold : float, optional
        Description
    low_step : float, optional
        Description
    high_step : float, optional
        Description
    verbose : bool, optional
        Print the classification stream (defaults to True - while construction)

    Returns
    -------
    list(tuples(|message|, str))
        Window (as list of topics)
    """
    topics = []
    for m, msg in enumerate(message_stream):
        if m > max_messages:
            m -= 1
            break

        if verbose:
            print '#{:>3}\033[33m ==> {}\033[0m'.format(m, msg.text.encode('ascii', 'ignore'))

        if len(topics) == 0:
            topics.insert(0, [(msg, 'First message')] )
            if verbose:
                print '\t First message (new 0)\n'

        else:
            # We will sequentially try to append to each topic ...
            #    as time goes by it is harder to append to a topic

            low_th = low_threshold
            high_th = high_threshold
            topic_scores = []  # in case no topic is close

            for t in xrange(max_active_topics):
                tp_len = len(topics[t])
                distances = map(lambda x: distance(msg.text, x[0].text), topics[t])

                # Assign a non-linear score (very close messages score higher)
                score = sum([ 0 if d < low_th else 1 if d < high_th else 3 for d in distances ])

                # Very large topics (> 10) should be harder to append to,
                #   since the odds of a casual match are higher
                if (tp_len < 3):
                    if (score > 0):
                        reason = 'len({}) < 3 and distances({})'.format(tp_len, distances)
                        _topic = topics.pop(t)  # pop from topic queue
                        _topic.append( (msg, reason) )
                        topics.insert(0, _topic)  # append to first topic
                        if verbose:
                            print '\t inserted to #{} : {}\n'.format(t, reason)
                        break

                elif (tp_len < 10):
                    if (score > (tp_len - (2 - tp_len/15.) )):
                        reason = 'len({}) < 10 and distances({})'.format(tp_len, distances)
                        _topic = topics.pop(t)  # pop from topic queue
                        _topic.append( (msg, 'len({}) < 10 and distances({})'.format(tp_len, distances)) )
                        topics.insert(0, _topic)  # append to first topic
                        if verbose:
                            print '\t inserted to #{} : {}\n'.format(t, reason)
                        break

                else:
                    if (score > tp_len*1.5):
                        reason = 'len({}) > 10 and distances({})'.format(tp_len, distances)
                        _topic = topics.pop(t)  # pop from topic queue
                        _topic.append( (msg, 'len({}) > 10 and distances({})'.format(tp_len, distances)) )
                        topics.insert(0, _topic)  # append to first topic
                        if verbose:
                            print '\t inserted to #{} : {}\n'.format(t, reason)
                        break

                topic_scores.append( (tp_len,score) )  # append score to topic_scores

                # else try with next topic --> harder
                low_th += low_step if low_th+low_step < high_th else high_step
                high_th += high_step
            else:
                # If no topic was suitable --> Start new topic
                topics.insert(0, [(msg, 'No similar topics (to 0) scores:({})'.format(topic_scores))] )
                if verbose:
                    print '\t No similar topics (new 0) scores:({})\n'.format(topic_scores)

    print '... Done, processed {} messages'.format(m)
    return topics
