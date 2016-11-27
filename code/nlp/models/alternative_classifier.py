
def classify_stream(message_stream, max_messages=20, low_threshold=.7, high_threshold=.85, low_step=.05, high_step=.02, verbose=True):
    topics = []
    for m, msg in enumerate(message_stream):
        if m > max_messages:
            break

        if verbose:
            print '#{:>3}\033[33m ==> {}\033[0m'.format(m, msg.text)

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

            for t in xrange(len(topics)):
                tp_len = len(topics[t])
                distances = map(lambda x: dist_m2m(msg.text, x[0].text), topics[t])

                # Assign a non-linear score (very close messages score higher)
                score = sum([ 0 if d < low_th else 1 if d < high_th else 3 for d in distances ])

                # Very large topics (> 10) should be harder to append to,
                #   since the odds of a casual match are higher
                if (tp_len < 3) and (score > 0):
                    reason = 'len({}) < 3 and distances({})'.format(tp_len, distances)
                    _topic = topics.pop(t)  # pop from topic queue
                    _topic.append( (msg, reason) )
                    topics.insert(0, _topic)  # append to first topic
                    if verbose:
                        print '\t inserted to #{} : {}\n'.format(t, reason)
                    break

                elif (tp_len < 10) and (score > 10):
                    reason = 'len({}) < 10 and distances({})'.format(tp_len, distances)
                    _topic = topics.pop(t)  # pop from topic queue
                    _topic.append( (msg, 'len({}) < 10 and distances({})'.format(tp_len, distances)) )
                    topics.insert(0, _topic)  # append to first topic
                    if verbose:
                        print '\t inserted to #{} : {}\n'.format(t, reason)
                    break

                elif (tp_len > 10) and (score > tp_len*1.5):
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
                topics.insert(0, [(msg, 'No similar topics (new 0) scores:({})'.format(topic_scores))] )
                if verbose:
                    print '\t No similar topics (new 0) scores:({})\n'.format(topic_scores)

    print '... Done, processed {} messages'.format(m)
    return topics