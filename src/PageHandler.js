import React from 'react'
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

export default function PageHandler() {
    return (
            <Fragment>
        <Router>
          <Switch>
            <Route exact path="/">
                <Main />
            </Route>         
              <App />
          </Switch>
        </Router>
    </Fragment>
    )
}
