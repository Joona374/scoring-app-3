export class Question {
  constructor(raw_json) {
    this.id = raw_json.id;
    this.type = raw_json.type;
    this.text = raw_json.text;
    this.next_question_id = raw_json.next_question_id;
    this.last_question = raw_json.last_question;
    this.options = raw_json.options;
  }
}
