import React, { useEffect, useReducer } from "react";
import { MainPage } from "./pages/MainPage";
import { reducer } from "./store/reducers";
import { initialState } from "./store/state";
import {
  getSettings,
  getSources,
  openWebSocketConnection,
} from "./store/backend";

const App: React.FC<{}> = () => {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    if (state.settings === undefined) {
      getSettings(dispatch);
    }
    if (state.sources === undefined) {
      getSources(dispatch);
    }
  }, []);

  useEffect(() => {
    if (state.settings?.enableWebsocketConnections) {
      openWebSocketConnection(dispatch);
    }
    if (state.settings?.appTitle) {
      document.title = state.settings.appTitle;
    }
  }, [state.settings]);

  return <MainPage state={state} dispatch={dispatch} />;
};

export default App;
