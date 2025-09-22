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
"report_ELOStandings": """CREATE VIEW "report_EloStandings" AS
	SELECT p.name, pce.elo, c.name, c.description
	FROM players p
	JOIN players_categories_elo pce ON p.id = pce.player_id
	JOIN categories c ON c.id = pce.category_id
	ORDER BY c.name, pce.elo DESC
""",
"report_TournamentResults": """CREATE VIEW "report_TournamentResults" AS
	SELECT DISTINCT p.name, pce.elo, c.name, c.description ,statistics.nbr_matches, statistics.victories, statistics.TournamentName
	FROM matches m
	JOIN players_matches_elo_change pm ON m.id = pm.match_id
	JOIN players p ON p.id = pm.player_id
	JOIN players_categories_elo pce ON p.id = pce.player_id
	JOIN (
		SELECT
		p.id,
		p.name,
		t.id as TournamentID,
		t.name as TournamentName,
		count(g.id) as nbr_matches,
		SUM(IIF(CASE pg.compeditor_nbr WHEN '1' THEN g.compeditor_one_score ELSE g.compeditor_two_score END > CASE pg.compeditor_nbr WHEN '1' THEN g.compeditor_two_score ELSE g.compeditor_one_score END, 1, 0)) victories
		FROM players p
		JOIN players_games pg ON p.id = pg.player_id
		JOIN games g ON pg.game_id = g.id
		JOIN matches m ON m.id = g.match_id
		JOIN tournaments t ON t.id = m.tournament_id
		group by p.name, TournamentID
	) statistics ON statistics.id = p.id
	JOIN categories c ON c.id = pce.category_id
	ORDER BY statistics.victories DESC
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
"players_matches_elo_change": """DROP TABLE players_matches_elo_change"""
}
