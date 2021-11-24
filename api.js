const path = require('path');
const express = require('express');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const session = require('express-session');



app = express();
const SetupSimpleExpressServer = (app) => {
    app.use(express.static(path.join(__dirname, '../public')));
    app.use(bodyParser.json());
    app.use(bodyParser.urlencoded({ extended: true }));
    app.use(cookieParser());
    app.use(session({
        secret: 'keyboard cat',
        resave: false,
        saveUninitialized: true,
        cookie: { secure: false }
    }));
    app.use((req, res, next) => {
        res.locals.user = req.user;
        next();
    });
}

SetupSimpleExpressServer(app);

app.listen(3000, () => {
    console.log('listening on port 3000');
});

app.get('/', (req, res) => {
    res.json({sj: "bruh"});
});