const fs = require('fs');
const csv = require('csv-parser');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const db = require("../util/database");

const createSurvey = (req, res) => {
  const {chop_ids} = req.body;
  const sql = `INSERT INTO surveys (chop_ids) VALUES (?)`;

  db.run(sql, [chop_ids], function (err) {
    if (err) {
      res.status(500).send({message: "Failed to create survey", error: err.message});
      return;
    }
    const surveyId = this.lastID;

    const dirPath = './db/surveys';
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, {recursive: true});
    }

    const filePath = `${dirPath}/survey${surveyId}.csv`;
    const chopIdGroups = chop_ids.split(',');

    const data = [];
    for (let i = 0; i < chopIdGroups.length; i += 4) {
      data.push({
        chop_id_1: chopIdGroups[i],
        chop_id_2: chopIdGroups[i + 1] || '',
        chop_id_3: chopIdGroups[i + 2] || '',
        chop_id_4: chopIdGroups[i + 3] || ''
      });
    }

    const csvWriter = createCsvWriter({
      path: filePath,
      header: [
        {id: 'chop_id_1', title: 'CHOP_ID_1'},
        {id: 'chop_id_2', title: 'CHOP_ID_2'},
        {id: 'chop_id_3', title: 'CHOP_ID_3'},
        {id: 'chop_id_4', title: 'CHOP_ID_4'}
      ]
    });

    csvWriter.writeRecords(data)
      .then(() => {
        res.status(201).send({message: "Survey created with CSV", id: surveyId});
      })
      .catch((error) => {
        console.error('Error writing CSV:', error);
        res.status(500).send({message: "Failed to create CSV for survey", error: error.message});
      });
  });
};
const answerSurvey = (req, res) => {
  const {name, email, selected_image_ids} = req.body;
  const surveyId = req.params.id;
  const dirPath = './db/responses';
  const filePath = `${dirPath}/survey${surveyId}.csv`;

  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, {recursive: true});
  }

  fs.access(filePath, fs.constants.F_OK, (err) => {
    const headers = [
      {id: 'name', title: 'NAME'},
      {id: 'email', title: 'EMAIL'}
    ];

    selected_image_ids.forEach((_, index) => {
      headers.push({id: `chop_id_${index + 1}`, title: `CHOP_ID_${index + 1}`});
    });

    const csvWriter = createCsvWriter({
      path: filePath,
      header: headers,
      append: !err
    });

    const dataEntry = {
      name: name,
      email: email
    };
    selected_image_ids.forEach((chopId, index) => {
      dataEntry[`chop_id_${index + 1}`] = chopId;
    });

    csvWriter.writeRecords([dataEntry])
      .then(() => {
        res.send({message: "Survey response recorded successfully"});
      })
      .catch((error) => {
        res.status(500).send({
          message: "Failed to record survey response",
          error: error.message
        });
      });
  });
};

const getSurvey = (req, res) => {
  const id = req.params.id;
  const sql = "SELECT * FROM surveys WHERE id = ?";

  db.get(sql, [id], (err, row) => {
    if (err) {
      res.status(500).send({message: "Failed to retrieve survey", error: err.message});
      return;
    }
    if (row) {
      res.status(200).send(row);
    } else {
      res.status(404).send({message: "Survey not found"});
    }
  });
};

const getAllSurveys = (req, res) => {
  const sql = "SELECT * FROM surveys";

  db.all(sql, (err, rows) => {
    if (err) {
      res.status(500).send({message: "Failed to retrieve surveys", error: err.message});
      return;
    }
    res.status(200).send(rows);

  });
};


const getData = (req, res) => {
  const results = [];

  fs.createReadStream('./db/data.csv')
    .pipe(csv())
    .on('data', (data) => results.push(data))
    .on('end', () => {
      res.json(results);
    })
    .on('error', (error) => {
      res.status(500).send({
        message: 'Failed to read and parse the CSV file',
        error: error.message
      });
    });
};

module.exports = {
  createSurvey,
  getSurvey,
  getData,
  getAllSurveys,
  answerSurvey
};
