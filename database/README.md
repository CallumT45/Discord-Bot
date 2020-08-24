# Bot Databases

There are three databases with this database:

- Assignments
- Cards
- Would you rather

To run your own version of the app, you must create a version of assignments database, see [AssignmentDB.py](../cogs/extraClasses/AssignmentDB.py) in extraClasses.

The other databases come prepopulated from web scrapers.

### Assignments

Assignments has one table assignments with columns `due_date`, `assignment_details`, `guild_id` and `channel_id`. `guild_id` is used to sort assignments via server or dm and `channel_id` is used to message the correct channel on assignment due.

### Cards

Cards has two tables `response` and `prompts`:

- prompts has columns `index`, `Prompt Cards`, `Special` and `Set`
  - Sample response `(3103, 'In L.A. County Jail, word is you can trade 200 cigarettes for ______.', None, 'CAH Base Set')`
- response has columns `index`, `Response Cards`, and `Set.1`
  - Sample response `(12005, 'Huffing and puffing and blowing my stepdad.', 'Absurd Box Expansion')`

### Would you rather

Wyr has only one table wyr, with one column `questions`. Sample response: `Would you rather...Win 10 Million Dollars or Win a Nobel Prize`
