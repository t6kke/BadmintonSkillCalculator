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
	"elo"	INTEGER NOT NULL,
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
)"""
}

db_down = {
"tournaments": """DROP TABLE tournaments""",
"players": """DROP TABLE players""",
"categories": """DROP TABLE categories""",
"matches": """DROP TABLE matches""",
"games": """DROP TABLE games""",
"players_games": """DROP TABLE players_games""",
"players_matches_elo_change": """DROP TABLE players_matches_elo_change"""
}
