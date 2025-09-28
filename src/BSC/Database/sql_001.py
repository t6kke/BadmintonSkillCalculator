db_up = {
"tournaments": """CREATE TABLE "tournaments" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"date"	TEXT,
	"location"	TEXT,
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
	"description"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"matches": """CREATE TABLE "matches" (
	"id"	INTEGER NOT NULL UNIQUE,
	"tournament_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	FOREIGN KEY("category_id") REFERENCES "categories"("id"),
	FOREIGN KEY("tournament_id") REFERENCES "tournaments"("id"),
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
"report_ListTournaments": """CREATE VIEW "report_ListTournaments" AS
	SELECT
	*
	FROM tournaments
	ORDER BY date ASC
""",
"report_ELOStandings": """CREATE VIEW "report_EloStandings" AS
	SELECT
	p.id as player_id,
	p.name AS player_name,
	pce.elo AS ELO,
	c.id AS category_id,
	c.name AS category_name,
	c.description AS category_description
	FROM players p
	JOIN players_categories_elo pce ON p.id = pce.player_id
	JOIN categories c ON c.id = pce.category_id
	ORDER BY c.name, pce.elo DESC
""",
"report_TournamentResults": """CREATE VIEW "report_TournamentResults" AS
	SELECT
	t.id AS tournament_id,
	t.name AS tournament_name,
	c.name AS category_name,
	c.description AS category_description,
	teams.team_name,
	count(g.id) AS nbr_of_matches,
	SUM(IIF(CASE WHEN teams.team_nbr = 1 THEN g.compeditor_one_score ELSE g.compeditor_two_score END > CASE WHEN teams.team_nbr = 1 THEN g.compeditor_two_score ELSE g.compeditor_one_score END, 1, 0)) AS victories,
	SUM(teams.points_for) AS points_for,
	SUM(teams.points_against) AS points_against,
	SUM(teams.points_for - teams.points_against) AS point_difference
	FROM (
		SELECT
		g.id,
		g.match_id,
		1 AS team_nbr,
		GROUP_CONCAT(p.name, ' + ') AS team_name,
		g.compeditor_one_score AS points_for,
		g.compeditor_two_score AS points_against
		FROM games g
		JOIN players_games pg ON g.id = pg.game_id AND pg.compeditor_nbr = 1
		JOIN players p ON p.id = pg.player_id
		GROUP BY g.id
		UNION ALL
		SELECT
		g.id,
		g.match_id,
		2 AS team_nbr,
		GROUP_CONCAT(p.name, ' + ') AS team_name,
		g.compeditor_two_score AS points_for,
		g.compeditor_one_score AS points_against
		FROM games g
		JOIN players_games pg ON g.id = pg.game_id AND pg.compeditor_nbr = 2
		JOIN players p ON p.id = pg.player_id
		GROUP BY g.id
	) teams
	JOIN games g ON g.id = teams.id
	JOIN matches m ON m.id = teams.match_id
	JOIN tournaments t ON t.id = m.tournament_id
	JOIN categories c ON c.id = m.category_id
	GROUP BY teams.team_name, t.id
	ORDER BY victories DESC, point_difference DESC
"""
}

db_down = {
"tournaments": """DROP TABLE tournaments""",
"players": """DROP TABLE players""",
"categories": """DROP TABLE categories""",
"matches": """DROP TABLE matches""",
"games": """DROP TABLE games""",
"players_categories_elo": """DROP TABLE players_categories_elo""",
"players_games": """DROP TABLE players_games""",
"players_matches_elo_change": """DROP TABLE players_matches_elo_change""",
"report_ListTournaments": """DROP VIEW report_ListTournaments""",
"report_ELOStandings": """DROP VIEW report_EloStandings""",
"report_TournamentResults": """DROP VIEW report_TournamentResults"""
}
