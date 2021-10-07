const express = require('express');
const scheduler = require('node-schedule');
const spawn = require('child_process').spawn;

// Update data everyday at 6:30:00 AM everyday
var rule = new scheduler.RecurrenceRule();
rule.hour = 6;
rule.minute = 30;
rule.second = 00;
rule.dayOfWeek = new scheduler.Range(0, 6);
scheduler.scheduleJob(rule, function() {
    spawn('python3', ['pyscripts/download_xml.py']);
});

const app = express();
app.use(express.json());
app.set('view engine', 'ejs');

app.get('/', (req, res) => {
    res.render('main');
});

app.get('/api_doc', (req, res) => {
    res.render('api_doc');
});

app.post('/filter_grants_1/', (req, res) => {
    const { title_keyword, desc_keyword, sf_or_both, eligibility, category, agency, week, form } = req.body;
    console.log('===', '\n', req. url, '\n', req.params, '\n===');
    const pythonProcess = spawn('python3', ['pyscripts/filter_grants1.py', title_keyword, desc_keyword, sf_or_both, eligibility, category, agency, week, form]);
    let process_output = '';
    pythonProcess.stdout.on('data', (data) => {
        process_output += data;
    });
    pythonProcess.on('close', () => {
        res.status(200).send(process_output);
    });
    pythonProcess.on('error', () => {
        res.status(401).send('Error in the following GET request to /filter_grants_1/...');
    });
});

app.post('/filter_grants_2/', (req, res) => {
    const { title_keyword, desc_keyword, sf_or_both, eligibility, category, agency, week, email, secret_key } = req.body;
    console.log('===', '\n', req. url, '\n', req.params, '\n===');
    if (secret_key != 'this is changed') {
        res.status(401).send({
            Status: 'Error, incorrect secret_key!',
        });
    }
    else {
        spawn('python3', ['pyscripts/filter_grants2.py', title_keyword, desc_keyword, sf_or_both, eligibility, category, agency, week, email]);
        res.status(200).send({
            Status: 'Correct secret_key, will be sending data.',
        });
    }
});

port_num = 5000;
app.listen(port_num, () => {
    console.log(`Listening on Port ${port_num}`);
});
