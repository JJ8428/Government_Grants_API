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
    // Script goes to grants gov website (the official one) and updates its database
    spawn('python3', ['pyscripts/download_xml.py']);
});

/*
    DO THE FOLLOWING BEFORE RUNNING THE APP:
        1. Ensure python3 is installed and run the command: pip install -r requirements.txt to install all python dependencies
        2. Then run 'npm install' to install all node.js dependencies
    Not many dependencies are installed for either language/framework if you converned with keeping your env clean

    Can be ran locally using 'npm start' or 'node server.js' 
*/

// Also please be aware that this uses both Node.js and Python3, so if hosting on Heroku, make sure treat this as a multi-pack build


const app = express();
app.use(express.json());
app.set('view engine', 'ejs'); // EJS engine, but I certainly learn React or Vue for future projects

app.get('/', (req, res) => {
    res.render('main'); // The front page
});

app.get('/form', (req, res) => {
    res.render('form'); // Form to make example calls to the API
})

app.get('/api_doc', (req, res) => {
    res.render('api_doc'); // Contains info regarding the 2 API methods provided
});

/*
    For info as to what the req.body should contain, please read the '/api_doc' page
    Contains detailed info as to what each variable in the JSON obj should be
    Obviously secret_key will be excluded
*/

// POST method | No secret key
app.post('/filter_grants_1/', (req, res) => {
    const { title_keyword, desc_keyword, sf_or_both, eligibility, category, agency, week, form } = req.body;
    console.log('===', '\n', req. url, '\n', req.body, '\n==='); // Print req.body in terminal
    const pythonProcess = spawn('python3', ['pyscripts/filter_grants1.py', title_keyword, desc_keyword, sf_or_both, eligibility, category, agency, week, form]);
    let process_output = '';
    pythonProcess.stdout.on('data', (data) => {
        process_output += data;
    });
    // As soon as stream of data ends, send the response
    // Treat as a stream since the output may take time to generate
    pythonProcess.on('close', () => { 
        res.status(200).send(process_output);
    });
    pythonProcess.on('error', () => {
        res.status(401).send('Error in the following GET request to /filter_grants_1/...');
    });
});

// POST method w/ secret key
app.post('/filter_grants_2/', (req, res) => {
    const { title_keyword, desc_keyword, sf_or_both, eligibility, category, agency, week, email, secret_key } = req.body;
    console.log('===', '\n', req. url, '\n', req.body, '\n==='); // Print req.body in terminal
    if (secret_key != 'i_wuv_DHEC') { // Change when deploying publically
        res.status(401).send({
            Status: 'Error, incorrect secret_key!',
        });
    }
    else {
        // This script will email the data automatically
        spawn('python3', ['pyscripts/filter_grants2.py', title_keyword, desc_keyword, sf_or_both, eligibility, category, agency, week, email]);
        res.status(200).send({
            Status: 'Correct secret_key, will be sending data.',
        });
    }
});

port_num = process.env.PORT || 5000; // Note to self: process.env.PORT is necessary when hosting publically
app.listen(port_num, () => {
    console.log(`Listening on Port ${port_num}`); 
});
