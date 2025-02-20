# Badminton Skill Calculator

This is for learing purpose for my own software development skills.
Not specifical meant for Badminton but I will use it to handle various badminton tournaments and competitions I take part in.

I'm using some basic ELO calculations setup to learn more about how ELO raking works and how best to implement it for my situation.

## ELO Ranking Logic

Still under investigation, need additional development for first level on real world implementation. After that I can learn more on how to implement the ELO calculations and impementation for our usecase. More details will follow here.

## Completed functionality

- reads in excel file in specific tournament format that it's developed for.
- creates team objects and does not create duplicates if the team members order changes from tournament to tournament.
- does ELO calculation game by game basis from first game of first tournament to last game of last tournament in scanned scope.

## Future Development

None of the points are in any specific priority order. I will work on any given topic that I'm interested in or if there is dependecy on it. 

List is not just code improvements but also project functionalities

### Near Future

- Various minor improvements in codes marked with TODO
- main.py needs restructuring specifically '''convertGameTeamToTeam()''' function.
- general code restructuring review and changes where it would make sense.
- Store data of scanned tournaments in DB and keep track of ELO over time without having to reimport and calculate all data over again.
- Generate some kind of HTML for static website content in case it's interesting for other compeditors.
- Add ELO confidence value and use it to handle ELO gain/loss.

### Far Future

- Import game results(data) from Tournamentsoftare.com competition results, some webscraping probably needed.
- Handle players separately from Teams. Currently it's only looking at a team.
- Handle players ranks through different competiontion categories(only applicable for official badminton tournaments)

## For Learning

I might also write this project, with potentially limited scope, in other languages for learing purpose.
