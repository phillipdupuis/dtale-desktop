import React from "react";
import { Layout, Button, Space, PageHeader, Spin } from "antd";
import {
  GithubOutlined as GithubIcon,
  ApiOutlined as ApiIcon,
} from "@ant-design/icons";
import {
  ActionDispatch,
  setOpenModal,
  setSelectedSource,
} from "../store/actions";
import { RootState, Source } from "../store/state";
import { SourceList } from "../components/SourceList";
import { SourceConfigEditor } from "../components/SourceConfigEditor";
import { LayoutEditor } from "../components/LayoutEditor";
import { ThemeController } from "../components/ThemeController";
import styled from "styled-components";

const { Content } = Layout;

const StyledContent = styled(Content)`
  width: 95vw;
  margin: 0 auto;
  min-height: 100vh;
  margin-bottom: 20px;
`;

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

const templateDataSource = (): Source => ({
  id: "",
  name: "",
  packageName: "",
  packagePath: "",
  nodes: undefined,
  nodesFullyLoaded: false,
  error: null,
  visible: true,
  editable: true,
  listPaths: listPathsTemplate,
  getData: getDataTemplate,
  saveData: "",
});

export const MainPage: React.FC<{
  state: RootState;
  dispatch: ActionDispatch;
}> = ({ state, dispatch }) => {
  const appIsLoaded: boolean =
    state.settings !== undefined && state.sources !== undefined;
  const sourcesExist: boolean =
    state.sources !== undefined && state.sources.length > 0;

  return (
    <Layout>
      <StyledContent>
        <PageHeader
          title={
            <Space>
              <span
                dangerouslySetInnerHTML={{
                  __html: state.settings?.appHeader || "...",
                }}
              />
              <Button
                icon={<GithubIcon />}
                shape="circle-outline"
                title="github"
                href="https://github.com/phillipdupuis/dtale-desktop"
                target="_blank"
                rel="noopener noreferrer"
              />
              <Button
                icon={<ApiIcon />}
                shape="circle-outline"
                title="API documentation"
                href="/docs"
                target="_blank"
                rel="noopener noreferrer"
              />
              <ThemeController />
            </Space>
          }
          subTitle=""
          extra={
            <Space>
              {appIsLoaded &&
              sourcesExist &&
              !state.settings?.disableEditLayout ? (
                <Button onClick={() => dispatch(setOpenModal("layoutEditor"))}>
                  Edit Layout
                </Button>
              ) : null}
              {appIsLoaded && !state.settings!.disableAddDataSources ? (
                <Button
                  type="primary"
                  onClick={() =>
                    dispatch(setSelectedSource(templateDataSource()))
                  }
                >
                  Add Data Source
                </Button>
              ) : null}
            </Space>
          }
        />
        {appIsLoaded ? (
          <SourceList
            settings={state.settings!}
            sources={state.sources!}
            dispatch={dispatch}
          />
        ) : (
          <Spin />
        )}
        {appIsLoaded && state.selectedSource ? (
          <SourceConfigEditor
            source={state.selectedSource}
            dispatch={dispatch}
            templates={(state.sources || []).map((s) => ({
              id: s.id,
              name: s.name,
              listPaths: s.listPaths,
              getData: s.getData,
            }))}
          />
        ) : null}
        {appIsLoaded && sourcesExist && !state.settings!.disableEditLayout ? (
          <LayoutEditor state={state} dispatch={dispatch} />
        ) : null}
      </StyledContent>
    </Layout>
  );
};
