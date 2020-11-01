import React, { useEffect, useReducer } from "react";
import "antd/dist/antd.css";
import "./App.css";
import { MainPage } from "./pages/MainPage";
import { addSources, updateSettings } from "./store/actions";
import { reducer } from "./store/reducers";
import { initialState } from "./store/state";
import { httpRequest } from "./utils/requests";

const App: React.FC<{}> = () => {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    if (state.sources === undefined) {
      httpRequest({
        method: "GET",
        url: "/source/list/",
        resolve: (sources) => dispatch(addSources(sources)),
        reject: (error) => null,
      });
    }
    if (state.settings === undefined) {
      httpRequest({
        method: "GET",
        url: "/settings/",
        resolve: (settings) => dispatch(updateSettings(settings)),
        reject: (error) => null,
      });
    }
  }, []);

  return <MainPage state={state} dispatch={dispatch} />;
};

export default App;
