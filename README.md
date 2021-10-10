# Government_Grants_API

Final product hosted using Heroku. Can be accessed at the following link: https://ggrantsapi.herokuapp.com/

This is just little API I created as a personal project. It's purpose it to make a quick way for me to filter through grants with a UI and functionality that I myself am familiar with. There already exists an official API for https://www.grants.gov/, this only exists to serve as an practice of Node.js, Express.js, Python, Pandas, Heroku Development, etc. Currently, there only exists 2 API methods both of which are POSTS. More info can be found in the API Documentation in the link I mentioned above. 

## How to run locally: 

  1. Install node.js
  2. Install python3 and pip

Then run the following commands:

`npm install`

This will install all node.js packages/dependencies

`pip install -r requirements.txt`

This will install all python packages/dependencies

`python3 pyscripts/download_xml.py`

This web app doesn't really have an official database. It just maintains a file of grants that were recently published that is updated daily at 6:30 AM. We need to run this so on launch, the web app has a up-to-date dataset.

`npm start`

This just starts the '.js' file that acts as the server. This can also be substituted with `node server.js`.

The app should be running if all went well and can be visited at localhost:5000.

Please note that for deploying publically, make sure to have a build pack for both Python and Node.js. (This is a multi-pack build).
 

