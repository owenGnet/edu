use Movies
go

/*
SELECT TOP 10 COUNT(*) OVER() AS Cnt, * FROM raw_movies;
SELECT TOP 10 COUNT(*) OVER() AS Cnt, * FROM movie_actors;
SELECT TOP 10 COUNT(*) OVER() AS Cnt, * FROM movie_countries;
SELECT TOP 10 COUNT(*) OVER() AS Cnt, * FROM movie_directors;
SELECT TOP 10 COUNT(*) OVER() AS Cnt, * FROM movie_genres;
*/

--Where there is no AudienceRating, substitute the mean value over all movies 
DECLARE @AvgAudRating DECIMAL(6,1);
SET @AvgAudRating = (SELECT AVG(CAST(m.rtAudienceRating AS float)) FROM raw_movies m
	WHERE CAST(rtAudienceRating AS float) > 0 ) --max of 5, min of 1.5 in this dataset
--SELECT @AvgAudRating	-- average = 3.3900

--For StarPower, try to weigh by the number of films by that country in the dataset
--	Values range from 1.0 for countries w/few entries, e.g. Greece only has 3, to 0.33 for USA with over 6k
;WITH cteCountry 
AS (
	select movieID, country, 
		CAST(1 - COUNT(*) OVER (PARTITION BY country)/(COUNT(*) OVER() * 1.0) AS DECIMAL(18,2)) as CountryFactor
	from movie_countries 
)
--movie_actors has a Ranking = order in which they appear on IMDB for a given movie
--	Grab a subset containing only actors who were given billing w/in top 3 movies
--	Tom Cruise is included in Minory Report because he had top billing, ranking = 1
--		but not included for Tropic Thunder where his ranking = 16 since he only had a cameo
,cteMostPop
AS (
	SELECT actorID, actorName, COUNT(*) As MostPopCount
	FROM movie_actors
	WHERE ranking < 4 
	GROUP BY actorID, actorName
)
--Similar to above, but include rankings from 4 to 7 inclusive
--	These will receive less weighting when calculating StarPower, vs. above
--	'not_applicaple' was a manual cleanup step, where I updated certain rows in movie_actors
--		to have that value if there was no valid actor name in the data - only affected 2 records below
,cteQuitePop
AS (
	SELECT actorID, actorName, COUNT(*) As QuitePopCount
	FROM movie_actors
	WHERE ranking BETWEEN 4 AND 7 AND actorID <> 'not_applicable'
	GROUP BY actorID, actorName
)
--For TotalPopCount, any appearance in the top 3 ranking is given twice the weight of appearance in 4-7
,cteStarPower AS
(
	SELECT mp.actorName, (MostPopCount * 2) + ISNULL(QuitePopCount, 0) AS TotalPopCount
	FROM cteMostPop mp
	LEFT JOIN cteQuitePop qp ON qp.actorID = mp.actorID
)
-- Now getting into even more arbitrary and ad-hoc calculations, with a strong emphasis on "arbitrary"
--	Playing around to get a gut feel for what might make sense given a business domain = movie ratings
--	MovieStarPowerWCntry is the numeric value most of the previous calculations were aiming for
,cte1 AS
(
	SELECT m.id, m.title, m.year, c.country, d.directorName, a.actorName, a.ranking, m.rtAllCriticsRating
		,SUM(sp.TotalPopCount) OVER (PARTITION BY m.id) As MovieStarPower
		,SUM(sp.TotalPopCount) OVER (PARTITION BY m.id) * c.CountryFactor As MovieStarPowerWCntry
		,CASE WHEN CAST(m.rtAudienceRating AS DECIMAL(6,1)) = 0 
			THEN @AvgAudRating ELSE CAST(m.rtAudienceRating AS DECIMAL(6,1)) 
			END AS AudienceRating
	FROM raw_movies m
	INNER JOIN movie_actors a ON a.movieID = m.id AND a.ranking < 4	--have to have appeared in top 3 billing at least once
	INNER JOIN cteStarPower sp ON sp.actorName = a.actorName	--but rank 4 to 7 still counts in popularity
	INNER JOIN cteCountry c ON c.movieID = m.id
	INNER JOIN movie_directors d ON d.movieID = m.id
	WHERE 1=1
--		AND m.id < 100
		AND ISNUMERIC(m.rtAllCriticsRating) = 1 AND CAST(m.rtAllCriticsRating AS float) > 0
		AND ISNULL(m.note, '') <> 'bad_actor_ranking' --account for bad data, or at least bad data in terms of my model
)
-- Include the top 3 actor names for each movie in the dataset, don't really now if these will be useful in model generation
--	Some movies don't even list 3 people, use placeholder values in that scenario.
,cte2 AS
(
	SELECT id, title, year, country, directorName	 
		,[1] AS Actor1
		,ISNULL([2], CASE WHEN id % 2 = 0 THEN 'George Spelvin' ELSE 'Georgette Spelvin' END) AS Actor2
		,ISNULL([3], CASE WHEN id % 2 = 0 THEN 'Georgette Spelvin' ELSE 'George Spelvin' END) AS Actor3
		,rtAllCriticsRating, MovieStarPower, MovieStarPowerWCntry, AudienceRating
		--KEY LINE HERE = after my early models showed MovieStarPowerWCntry having almost no predictive ability I felt
		--	it necessary to add in AudienceRating... and kept on reducing impact of MovieStarPowerWCntry until it had
		--	very little weighting in the final value. Oh well.
		,(MovieStarPowerWCntry/100) + AudienceRating AS StarAud
	FROM cte1
	PIVOT (
		MAX(actorName)
		FOR ranking IN ([1],[2],[3])
	)
	AS pvt
)
--movie_genres has one-to-many between movies and 20 possible genres, e.g. Crime, Musical, Film-Noir
--	Each movie has at least one, highest has 8 (for 'Gwoemul', Korean movie better known as 'The Host' in US)
--	Goal is to wind up with three movie genres that movie is tagged with, where the top 3 "rarest" genres are included
--	Rarity is calc based on number of movies for that genre in the dataset, idea is that if a movie is tagged with both
--		'Drama' (5076 movies) and 'Western' (261), it is more important that the 'Western' tag be included since that
--		would likely have a greater affect on a critic's evaluation vs. it being a Drama
-- Next 4 queries all deal with this genre calculation.
,cteGenreRnk AS (
	SELECT A.genre, ROW_NUMBER() OVER (ORDER BY cnt) AS rnk
	FROM (
		SELECT genre, COUNT(*) as cnt
		FROM movie_genres
		GROUP BY genre
	) A
)
,cteGenres AS
(
	SELECT g.movieID, g.genre, rnk.rnk, ROW_NUMBER() OVER (PARTITION BY g.movieID ORDER BY rnk.rnk) AS FinalRank
	FROM movie_genres g
	INNER JOIN cteGenreRnk rnk ON rnk.genre = g.genre
)
,cteTopGenreRnk AS
(
	SELECT rm.id, rm.title, rm.Year, g.genre, g.FinalRank--, g.rnk
	FROM raw_movies rm
	LEFT JOIN cteGenres g ON g.movieID = rm.id
	WHERE 1=1
		AND g.FinalRank <= 3
)
,cteGenrePivot AS
(
	SELECT id, title, year	 
		,[1] AS Genre1
		,COALESCE([2], [1]) AS Genre2	--if only one genre, put that here
		,COALESCE([3], [1]) AS Genre3	--if only two genre tags, put most-rare here
	FROM cteTopGenreRnk
	PIVOT (
		MAX(genre)
		FOR FinalRank IN ([1],[2],[3])
	)
	AS pvt
)
SELECT c2.*, p.Genre1, p.Genre2, p.Genre3
	--bonus feature = presuming female given names more likely to end with letter 'a', 
	--	throw into the mix the likelihood that top billed is an actress
	,CASE WHEN SUBSTRING(c2.actor1, CHARINDEX(' ', c2.actor1, 0)-1, 1) = 'a' Then 'T'
		ELSE 'F' End AS Actor1NameEndsInA
FROM cte2 c2 
INNER JOIN cteGenrePivot p ON p.id = c2.id
--WHERE Actor1 LIKE '%van damme%' OR Actor2 LIKE '%van damme%' OR Actor3 LIKE '%van damme%'
