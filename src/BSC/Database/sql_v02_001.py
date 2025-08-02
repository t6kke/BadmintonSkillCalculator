db_up = {
"tournaments": """CREATE TABLE "tournaments" (
	"id"	INTEGER NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"date"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"users": """CREATE TABLE "users" (
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
	"player_one_score"	INTEGER NOT NULL,
	"player_two_score"	INTEGER NOT NULL,
	FOREIGN KEY("match_id") REFERENCES "matches"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)""",
"users_games": """CREATE TABLE "users_games" (
	"users_id"	INTEGER NOT NULL,
	"games_id"	INTEGER NOT NULL,
	"comp_nbr"	INTEGER NOT NULL,
	UNIQUE("users_id","games_id")
)""",
"users_matches_elo_change": """CREATE TABLE "users_matches_elo_change" (
	"users_id"	INTEGER NOT NULL,
	"matches_id"	INTEGER NOT NULL,
	"user_start_elo"	INTEGER NOT NULL,
	"user_elo_change"	INTEGER NOT NULL,
	UNIQUE("users_id","matches_id")
)"""
}

db_down = {
"tournaments": """DROP TABLE tournaments""",
"users": """DROP TABLE users""",
"categories": """DROP TABLE categories""",
"matches": """DROP TABLE matches""",
"games": """DROP TABLE games""",
"users_games": """DROP TABLE users_games""",
"users_matches_elo_change": """DROP TABLE users_matches_elo_change"""
}
