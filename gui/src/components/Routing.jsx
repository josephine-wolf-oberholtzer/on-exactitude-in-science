import React from "react";
import { Route, Switch } from "react-router-dom";
import Fetcher from "./Fetcher";

const Routing = () => (
	<Switch>
		<Route
			exact
			path="/:label(artist|company|master|release|track)/:id"
			component={Fetcher}
		/>
		<Route
			exact
			path="/random/:label(artist|company|master|release|track)"
			component={Fetcher}
		/>
		<Route exact path="/random" component={Fetcher} />
		<Route exact path="/" component={Fetcher} />
		<Route path="*" component={Fetcher} />
	</Switch>
);

export default Routing;
