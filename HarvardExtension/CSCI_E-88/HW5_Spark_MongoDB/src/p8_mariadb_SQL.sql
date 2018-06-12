
USE test;

-- Query 1: get count of unique URLs by hour
SELECT A.event_hour,COUNT(DISTINCT A.url) as cnt
FROM (
	SELECT MID(event_time, 12, 2) as event_hour, url
	FROM problem8_str
) A
GROUP BY A.event_hour
ORDER BY A.event_hour;


-- Query 2: get count of unique visitors per URL by hour
SELECT A.event_hour, A.url, COUNT( DISTINCT A.userid) as cnt
FROM (
	SELECT MID(event_time, 12, 2) as event_hour, url, userid
	FROM problem8_str
) A
GROUP BY A.event_hour, A.url
ORDER BY A.event_hour, A.url;


-- Query 3: get count of unique (by userId) clicks per URL by hour
SELECT A.event_hour, A.url, A.userid,  COUNT(*) FROM (
	SELECT MID(event_time, 12, 2) as event_hour, url, userid
	FROM problem8_str
) A
GROUP BY A.event_hour, A.url, A.userid
ORDER BY A.event_hour, A.url , A.userid;

-- Report 1: Daily count of unique URLs
SELECT A.daily_day,COUNT(DISTINCT A.url) as cnt
FROM (
	SELECT LEFT(event_time, 10) as daily_day, url
	FROM problem8_str
) A
GROUP BY A.daily_day
ORDER BY A.daily_day;


-- Report 2: Daily count of unique visitors
SELECT A.daily_day,COUNT(DISTINCT A.userid) as cnt
FROM (
	SELECT LEFT(event_time, 10) as daily_day, userid
	FROM problem8_str
) A
GROUP BY A.daily_day
ORDER BY A.daily_day;




