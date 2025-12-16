db_up = {
"tournaments": """CREATE TABLE "tournaments" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"start_date"	TEXT,
	"end_date"	TEXT,
	"location"	TEXT,
	"external_url" TEXT,
	"has_internal_result" BOOLEAN NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"players": """CREATE TABLE "players" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"categories": """CREATE TABLE "categories" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"categories_metadata": """CREATE TABLE "categories_metadata" (
	"id"	INTEGER NOT NULL UNIQUE,
	"category_id"	INTEGER NOT NULL,
	"info_type"	TEXT NOT NULL,
	"info_text"	TEXT NOT NULL,
	FOREIGN KEY("category_id") REFERENCES "categories"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"leagues": """CREATE TABLE "leagues" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"leagues_metadata": """CREATE TABLE "leagues_metadata" (
	"id"	INTEGER NOT NULL UNIQUE,
	"league_id"	INTEGER NOT NULL,
	"info_type"	TEXT NOT NULL,
	"info_text"	TEXT NOT NULL,
	FOREIGN KEY("league_id") REFERENCES "leagues"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"matches": """CREATE TABLE "matches" (
	"id"	INTEGER NOT NULL UNIQUE,
	"tournament_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	"league_id"	INTEGER NOT NULL,
	"winner_compeditor_nbr" INTEGER NOT NULL,
	FOREIGN KEY("category_id") REFERENCES "categories"("id"),
	FOREIGN KEY("tournament_id") REFERENCES "tournaments"("id"),
	FOREIGN KEY("league_id") REFERENCES "leagues"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"games": """CREATE TABLE "games" (
	"id"	INTEGER NOT NULL UNIQUE,
	"match_id"	INTEGER NOT NULL,
	"game_count"	INTEGER NOT NULL,
	"compeditor_one_score"	INTEGER NOT NULL,
	"compeditor_two_score"	INTEGER NOT NULL,
	FOREIGN KEY("match_id") REFERENCES "matches"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"players_categories_elo": """CREATE TABLE "players_categories_elo" (
	"player_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	"elo"	INTEGER NOT NULL,
	UNIQUE("player_id","category_id")
)""",
"players_games": """CREATE TABLE "players_games" (
	"player_id"	INTEGER NOT NULL,
	"game_id"	INTEGER NOT NULL,
	"compeditor_nbr"	INTEGER NOT NULL,
	UNIQUE("player_id","game_id")
)""",
"players_matches_elo_change": """CREATE TABLE "players_matches_elo_change" (
	"player_id"	INTEGER NOT NULL,
	"match_id"	INTEGER NOT NULL,
	"player_start_elo"	INTEGER NOT NULL,
	"player_elo_change"	INTEGER NOT NULL,
	UNIQUE("player_id","match_id")
)""",
"report_ListAllTournaments": """CREATE VIEW "report_ListAllTournaments" AS
	SELECT
	*
	FROM tournaments
	ORDER BY start_date ASC
""",
"report_ListInternalResultTournaments": """CREATE VIEW "report_ListInternalResultTournaments" AS
	SELECT
	*
	FROM tournaments
	WHERE has_internal_result = true
	ORDER BY start_date ASC
""",
"report_ELOStandings": """CREATE VIEW "report_EloStandings" AS
	SELECT
	p.id as player_id,
	p.name AS player_name,
	pce.elo AS ELO,
	c.id AS category_id,
	c.name AS category_name,
	COUNT(c.id) as nbr_of_matches,
	date('now','start of month','-12 month') as date_limit_on_nbr_of_matches
	FROM players p
	JOIN players_matches_elo_change pmec ON p.id = pmec.player_id
	JOIN matches m ON m.id = pmec.match_id
	JOIN tournaments t ON m.tournament_id = t.id
	JOIN categories c ON c.id = m.category_id
	JOIN players_categories_elo pce ON p.id = pce.player_id AND c.id = pce.category_id
	WHERE t.start_date >= date('now','start of month','-12 month')
	group by c.id, p.id
	order by c.id, pce.elo DESC
""",
"report_TournamentResults": """CREATE VIEW "report_TournamentResults" AS
	SELECT
	t.id AS tournament_id,
	t.name AS tournament_name,
	c.name AS category_name,
	teams.team_name,
	count(g.id) AS nbr_of_matches,
	--SUM(IIF(CASE WHEN teams.team_nbr = 1 THEN g.compeditor_one_score ELSE g.compeditor_two_score END > CASE WHEN teams.team_nbr = 1 THEN g.compeditor_two_score ELSE g.compeditor_one_score END, 1, 0)) AS victories,
	SUM(CASE WHEN teams.team_nbr = teams.winner_compeditor_nbr THEN 1 ELSE 0 END) as victories,
	SUM(teams.points_for) AS points_for,
	SUM(teams.points_against) AS points_against,
	SUM(teams.points_for - teams.points_against) AS point_difference
	FROM (
		SELECT
		fg.id,
		fg.match_id,
		1 AS team_nbr,
		m.winner_compeditor_nbr as winner_compeditor_nbr,
		GROUP_CONCAT(p.name, ' + ') AS team_name,
		fg.compeditor_one_score AS points_for,
		fg.compeditor_two_score AS points_against
		FROM (
			SELECT
			id,
			match_id,
			MAX(game_count),
			sum(compeditor_one_score) as compeditor_one_score,
			sum(compeditor_two_score) as compeditor_two_score
			FROM
			games
			group by match_id) fg
		JOIN players_games pg ON fg.id = pg.game_id AND pg.compeditor_nbr = 1
		JOIN players p ON p.id = pg.player_id
		JOIN matches m ON fg.match_id = m.id
		GROUP BY fg.match_id
		UNION ALL
		SELECT
		fg.id,
		fg.match_id,
		2 AS team_nbr,
		m.winner_compeditor_nbr as winner_compeditor_nbr,
		GROUP_CONCAT(p.name, ' + ') AS team_name,
		fg.compeditor_two_score AS points_for,
		fg.compeditor_one_score AS points_against
		FROM (
			SELECT
			id,
			match_id,
			MAX(game_count),
			sum(compeditor_one_score) as compeditor_one_score,
			sum(compeditor_two_score) as compeditor_two_score
			FROM
			games
			group by match_id) fg
		JOIN players_games pg ON fg.id = pg.game_id AND pg.compeditor_nbr = 2
		JOIN players p ON p.id = pg.player_id
		JOIN matches m ON fg.match_id = m.id
		GROUP BY fg.match_id
	) teams
	JOIN games g ON g.id = teams.id
	JOIN matches m ON m.id = teams.match_id
	JOIN tournaments t ON t.id = m.tournament_id
	JOIN categories c ON c.id = m.category_id
	WHERE t.has_internal_result = true
	GROUP BY teams.team_name, t.id
	ORDER BY victories DESC, point_difference DESC
"""
}

db_down = {
"tournaments": """DROP TABLE tournaments""",
"players": """DROP TABLE players""",
"categories": """DROP TABLE categories""",
"categories_metadata": """DROP TABLE categories_metadata""",
"leagues": """DROP TABLE leagues""",
"leagues_metadata": """DROP TABLE leagues_metadata""",
"matches": """DROP TABLE matches""",
"games": """DROP TABLE games""",
"players_categories_elo": """DROP TABLE players_categories_elo""",
"players_games": """DROP TABLE players_games""",
"players_matches_elo_change": """DROP TABLE players_matches_elo_change""",
"report_ListAllTournaments": """DROP VIEW report_ListAllTournaments""",
"report_ListInternalResultTournaments": """DROP VIEW report_ListInternalResultTournaments""",
"report_ELOStandings": """DROP VIEW report_EloStandings""",
"report_TournamentResults": """DROP VIEW report_TournamentResults"""
}
