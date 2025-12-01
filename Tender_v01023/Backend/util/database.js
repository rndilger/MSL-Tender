const sqlite3 = require('sqlite3').verbose();

const db = new sqlite3.Database('./db/surveys.db', sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE, (err) => {
  if (err) {
    console.error('Could not connect to database', err);
  } else {
    console.log('Connected to the SQLite database.');
    db.run(`CREATE TABLE IF NOT EXISTS surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chop_ids TEXT NOT NULL
        )`, (err) => {
      if (err) {
        console.error('Error creating table', err);
      } else {
        console.log('Surveys table is ready.');
      }
    });
  }
});

module.exports = db;
