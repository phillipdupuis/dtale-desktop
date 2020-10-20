import React, { useEffect, useReducer } from "react";
import { Layout, Button, PageHeader, Spin } from "antd";
import "antd/dist/antd.css";
import "./App.css";
import SourceList from "./components/SourceList";
import ConfigEditor from "./components/SourceConfigEditor";
import { addSources, setSelectedSource } from "./store/actions";
import { reducer } from "./store/reducers";
import { initialState, DataSource } from "./store/state";
import { httpRequest } from "./utils/requests";

const { Content } = Layout;

const listPathsTemplate: string = `from typing import Iterable


def main() -> Iterable[str]:
    """
    Return an iterable of paths identifying where data is located, such as file paths or URLs.
    These paths will be passed to your function in get_data.py.
    """
    raise NotImplementedError()
`;

const getDataTemplate: string = `import pandas as pd


def main(path: str) -> pd.DataFrame:
    """
    Given a path, retrieve that data and return it as a pandas dataframe
    """
    raise NotImplementedError()
`;

const templateDataSource = (): DataSource => ({
  id: "",
  name: "",
  packageName: "",
  nodes: undefined,
  nodesFullyLoaded: false,
  error: null,
  visible: true,
  editable: true,
  listPaths: listPathsTemplate,
  getData: getDataTemplate,
  saveData: "",
});

const App = () => {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    httpRequest({
      method: "GET",
      url: "/source/list/",
      resolve: (sources) => dispatch(addSources(sources)),
      reject: (error) => null,
    });
  }, []);

  return (
    <Layout className="layout">
      <Content style={{ width: "100vw" }}>
        <PageHeader
          title="D-Tale Desktop"
          className="site-page-header"
          subTitle=""
          extra={[
            <Button
              key="newDataSource"
              type="primary"
              onClick={() => {
                dispatch(setSelectedSource(templateDataSource()));
              }}
            >
              Add Data Source
            </Button>,
          ]}
        />
        <div style={{ width: "100%" }}>
          {state.sources === undefined ? (
            <Spin />
          ) : (
            <SourceList sources={state.sources} dispatch={dispatch} />
          )}
        </div>
        {state.selectedSource ? (
          <ConfigEditor source={state.selectedSource} dispatch={dispatch} />
        ) : null}
      </Content>
    </Layout>
  );
};

export default App;
