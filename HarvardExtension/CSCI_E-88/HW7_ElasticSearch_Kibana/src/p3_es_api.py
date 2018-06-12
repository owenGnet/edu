
from random import randint
import collections
import uuid

from elasticsearch import Elasticsearch


#Make sure you have at least 5-15 different values for each of the event fields (except UUID - UUID has to be, well, a UUID for each event :-) ),
#but vary it in time - say, 5 variations of URLs for one hour, than 10 for another hour, then back to 5… to simulate more"realistic" data
#where you do not see the same users/URLs all the time

# return an n count deque of timestamp string values in format of 'YYYY-MM-DD HH:MM:SS'
def get_all_timestamps(count):
    Timepoint = collections.namedtuple('Timepoint', 'year month day hour minute second')
    # generate timepoints on Nov 9th, 2017, >= 2am and < 11am, increase hour span for problem 3, anticipating p4 queries
    time_points = (Timepoint(year=2017, month=11, day=9,
                             hour=randint(2, 11), minute=randint(0, 59), second=randint(0, 59)) for i in range(count))

    # below doesn't handle February, but that's ok for this problem
    return collections.deque('{year}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}'.format(
        year=t.year, month=t.month,  day=t.day if t.month in [4,6,9,11] else randint(1,31), hour=t.hour,
        minute=t.minute, second=t.second) for t in time_points)

# generate a list of user-ids in format of u##, zero-filled from the left as appropriate to total count
def get_userids(count):
    return ['u' + str.zfill('{}'.format(i), len(str(count))) for i in range(1, count+1)]

# generate the list of events and insert them to hw6_7 table
def generate_events(num_events):
    # increase url count to 5
    urls=['yahoo.com','google.com','harvard.edu','nytimes.com','cambridgema.gov','baidu.com','amazon.com','ebay.com','cnn.com']
    # total of six countries
    countries=['Jamaica','Japan','Jordan','Fiji','Finland','France']
    # 5 possible browsers
    browsers = ['Opera','Firefox','Edge','Chrome','Vivaldi']
    # 6 operating system values
    os = ['Windows 7','Windows 10','Mac OS X 10.12','Mac OS X 10.10','Windows Me','CentOS 7.4']
    # 8 http response values
    responses = [200,302,400,401,403,404,500,502,503,504]

    es = Elasticsearch(http_auth=('elastic', 'changeme'))
    user_id_count = 20
    uids = get_userids(user_id_count)
    stamps = get_all_timestamps(num_events)
    events = []
    for stamp in stamps:
        # A7, Problem 2, event format: <uuid><timestamp><url><ua_country><userId><ua_browser><ua_os><response_status><TTFB>
        Event = collections.namedtuple('Event', 'event_uuid event_time url country user_id browser os response ttfb_ms')
        # randomly assign an url, country, user_id, browser, os, response, and ttfb value to each event
        # for Problem 3, don't know that is necessary but add in some logic to weight url/country/user ids by time
        #  all the timestamps are in hours 2-11 of one day, if the hour = 6 or 7, supply values from beginning of each list
        stamp_hour = stamp[12]
        events.append(Event(event_uuid=uuid.uuid4(),
                            event_time=stamp,
                            url=urls[randint(0, len(urls)-3) if stamp_hour in ['5','6'] else randint(0, len(urls)-1)],
                            country=countries[randint(0, len(countries)-4) if stamp_hour in ['5','6']  else randint(0, len(countries)-1)],
                            user_id = uids[randint(0, user_id_count)-11 if stamp_hour in ['5','6']  else randint(0, user_id_count)-1],
                            browser=browsers[randint(0, len(browsers)-1)],
                            os=os[randint(0, len(os)-1)],
                            response=responses[randint(0, len(responses)-1)],
                            ttfb_ms=randint(200, 400)))

    # iterate through the above events and create PUT strings for inserting the data into elasticsearch
    for i, event in enumerate(events):
        doc = """
{{
  "uuid": "{uuid}",
  "event_time": "{event_time}",
  "url": "{url}",
  "country": "{country}",
  "user_id": "{user_id}",
  "browser": "{browser}",
  "os": "{os}",
  "response_status": {response},
  "ttfb": {ttfb_ms}
}} """.format(uuid=event.event_uuid,
                event_time=event.event_time,
                url=event.url,
                country=event.country,
                user_id=event.user_id,
                browser=event.browser,
                os=event.os,
                response=event.response,
                ttfb_ms=event.ttfb_ms
            )

        id = '{}'.format(str.zfill(str(i + 1), 4))
        res = es.index(index='a7_problem2', doc_type='doc', id=id, body=doc)
        print('id {} "created" status: {}'.format(id, res['created']))

generate_events(5000)

