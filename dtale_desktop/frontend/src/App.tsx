import React, { useEffect, useReducer } from "react";
import "antd/dist/antd.css";
import "./App.css";
import { MainPage } from "./pages/MainPage";
import { addSources, updateSettings } from "./store/actions";
import { reducer } from "./store/reducers";
import { initialState } from "./store/state";
import { backend } from "./utils/interface";

const App: React.FC<{}> = () => {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    if (state.sources === undefined) {
      backend.get.sources({ dispatch });
    }
    if (state.settings === undefined) {
      backend.get.settings({ dispatch });
    }
  }, []);

  return <MainPage state={state} dispatch={dispatch} />;
};

export default App;
