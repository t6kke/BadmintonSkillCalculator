db_up = {
"tournaments": """CREATE TABLE "tournaments" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"date"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"players": """CREATE TABLE "players" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"compeditors": """CREATE TABLE "compeditors" (
	"id"	INTEGER NOT NULL UNIQUE,
	"elo"	INTEGER NOT NULL,
	"type"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"categories": """CREATE TABLE "categories" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"players_compeditors": """CREATE TABLE "players_compeditors" (
	"player_id"	INTEGER NOT NULL,
	"compeditor_id"	INTEGER NOT NULL,
	FOREIGN KEY("player_id") REFERENCES "players"("id"),
	UNIQUE("player_id","compeditor_id"),
	FOREIGN KEY("compeditor_id") REFERENCES "compeditors"("id")
)""",
"matches": """CREATE TABLE "matches" (
	"id"	INTEGER NOT NULL UNIQUE,
	"tournament_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	FOREIGN KEY("category_id") REFERENCES "categories"("id"),
	FOREIGN KEY("tournament_id") REFERENCES "tournaments"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"compeditors_matches": """CREATE TABLE "compeditors_matches" (
	"comp_id"	INTEGER NOT NULL,
	"match_id"	INTEGER NOT NULL,
	FOREIGN KEY("match_id") REFERENCES "matches"("id"),
	UNIQUE("comp_id","match_id"),
	FOREIGN KEY("comp_id") REFERENCES "compeditors"("id")
)""",
"games": """CREATE TABLE "games" (
	"id"	INTEGER NOT NULL UNIQUE,
	"match_id"	INTEGER NOT NULL,
	"game_coutn"	INTEGER NOT NULL,
	"compeditor_one_score"	INTEGER NOT NULL,
	"compeditor_two_score"	INTEGER NOT NULL,
	FOREIGN KEY("match_id") REFERENCES "matches"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)"""
}

db_down = {
"tournaments": """DROP TABLE tournaments""",
"players": """DROP TABLE players""",
"compeditors": """DROP TABLE compeditors""",
"categories": """DROP TABLE categories""",
"players_compeditors": """DROP TABLE players_compeditors""",
"matches": """DROP TABLE matches""",
"compeditors_matches": """DROP TABLE compeditors_matches""",
"games": """DROP TABLE games"""
}
