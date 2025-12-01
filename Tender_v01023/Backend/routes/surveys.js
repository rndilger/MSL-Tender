const express = require("express");
const {body} = require("express-validator");

const surveyController = require("../controllers/surveyController");

const router = express.Router();

router.post('',
  [
    body('chop_ids').trim().not().isEmpty().withMessage("Chop IDs cannot be empty"),
  ],
  surveyController.createSurvey
);

router.get('', surveyController.getAllSurveys);

router.get('/data', surveyController.getData);

router.get('/:id', surveyController.getSurvey);

router.post('/:id',
  [
    body('name').trim().not().isEmpty().withMessage("Name cannot be empty"),
    body('email').isEmail().withMessage("Invalid email address"),
    body('selected_image_ids').isArray().withMessage("Selected image IDs must be an array")
      .not().isEmpty().withMessage("Selected image IDs cannot be empty"),
  ],
  surveyController.answerSurvey
);


module.exports = router;
