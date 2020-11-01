import React, { Fragment, useState, ReactNode } from "react";
import styled from "styled-components";
import { Node } from "../store/state";
import { ActionDispatch, updateNode } from "../store/actions";
import { Button, Typography } from "antd";
import { httpRequest, openNewTab } from "../utils/requests";
import {
  LineChartOutlined,
  TableOutlined,
  DotChartOutlined,
  PictureOutlined,
  ProfileOutlined,
} from "@ant-design/icons";

const DtaleButton: React.FC<{
  dispatch: ActionDispatch;
  node: Node;
  page: "table" | "charts" | "describe" | "correlations";
  urlProp:
    | "dtaleUrl"
    | "dtaleChartsUrl"
    | "dtaleDescribeUrl"
    | "dtaleCorrelationsUrl";
  icon: ReactNode;
}> = ({ dispatch, node, page, urlProp, icon }) => {
  const [loading, setLoading] = useState<boolean>(false);
  return (
    <Button
      icon={icon}
      style={{ display: "inline-block", textTransform: "capitalize" }}
      size="small"
      onClick={() => {
        httpRequest({
          method: "GET",
          url: `/node/view/${node.dataId}/`,
          resolve: (data: Node) => {
            openNewTab(data[urlProp]!);
            dispatch(updateNode(data));
          },
          reject: (error: string) =>
            dispatch(updateNode({ ...node, error: error })),
          onStart: () => setLoading(true),
          onFinish: () => setLoading(false),
        });
      }}
      loading={loading}
    >
      {page}
    </Button>
  );
};

const DtaleTableButton: React.FC<{
  dispatch: ActionDispatch;
  node: Node;
}> = ({ dispatch, node }) => (
  <DtaleButton
    dispatch={dispatch}
    node={node}
    page="table"
    urlProp="dtaleUrl"
    icon={<TableOutlined />}
  />
);

const DtaleChartsButton: React.FC<{
  dispatch: ActionDispatch;
  node: Node;
}> = ({ dispatch, node }) => (
  <DtaleButton
    dispatch={dispatch}
    node={node}
    page="charts"
    urlProp="dtaleChartsUrl"
    icon={<LineChartOutlined />}
  />
);

const DtaleDescribeButton: React.FC<{
  dispatch: ActionDispatch;
  node: Node;
}> = ({ dispatch, node }) => (
  <DtaleButton
    dispatch={dispatch}
    node={node}
    page="describe"
    urlProp="dtaleDescribeUrl"
    icon={<PictureOutlined />}
  />
);

const DtaleCorrelationsButton: React.FC<{
  dispatch: ActionDispatch;
  node: Node;
}> = ({ dispatch, node }) => (
  <DtaleButton
    dispatch={dispatch}
    node={node}
    page="correlations"
    urlProp="dtaleCorrelationsUrl"
    icon={<DotChartOutlined />}
  />
);

const PandasProfileReportButton: React.FC<{
  dispatch: ActionDispatch;
  node: Node;
}> = ({ dispatch, node }) => (
  <Button
    size="small"
    onClick={() => {
      openNewTab(`/node/profile-report/${node.dataId}/`);
      httpRequest({
        method: "GET",
        url: `/node/watch-profile-report-builder/${node.dataId}/`,
        resolve: (data) => {
          if (data.ok) {
            dispatch(updateNode(data.node));
          }
        },
        reject: (error) => null,
      });
    }}
    icon={<ProfileOutlined />}
  >
    Profile
  </Button>
);

export const ShutdownButton: React.FC<{
  dispatch: ActionDispatch;
  node: Node;
}> = ({ dispatch, node }) => {
  const [loading, setLoading] = useState<boolean>(false);
  return (
    <Button
      danger
      size="small"
      title="shut down"
      onClick={() => {
        setLoading(true);
        httpRequest({
          method: "GET",
          url: `node/kill/${node.dataId}/`,
          resolve: (data: Node) => {
            dispatch(updateNode(data));
            setLoading(false);
          },
          reject: (error) => {
            const newNode = { ...node, error: error };
            dispatch(updateNode(newNode));
            setLoading(false);
          },
        });
      }}
      disabled={!node.dtaleUrl}
      loading={loading}
    >
      Shut down
    </Button>
  );
};

const NodeActionsContainer = styled.div`
  margin-top: 0;
  margin-bottom: auto;
  display: grid;
  grid-template-columns: 1fr;
  grid-gap: 5px;
  grid-template-areas:
    "buttons"
    "link";
  .node-action-buttons {
    grid-area: "buttons";
    align-self: end;
    margin-left: auto;
    margin-right: 0;
    button {
      margin-right: 3px;
    }
    button:last-child {
      margin-right: 0px;
    }
  }
  .node-action-link {
    grid-area: "link";
    align-self: end;
    margin-left: auto;
    margin-right: 0;
  }
  .node-action-link-placeholder {
    color: transparent;
  }
`;

export const DataViewerButtons: React.FC<{
  node: Node;
  dispatch: ActionDispatch;
}> = (props) => (
  <NodeActionsContainer>
    <div className="node-action-buttons">
      {props.node.dtaleUrl ? <ShutdownButton {...props} /> : null}
      <DtaleTableButton {...props} />
      <DtaleChartsButton {...props} />
      <DtaleCorrelationsButton {...props} />
      <DtaleDescribeButton {...props} />
      <PandasProfileReportButton {...props} />
    </div>
    <div className="node-action-link">
      {props.node.dtaleUrl ? (
        <a href={props.node.dtaleUrl} target="_blank" rel="noopener noreferrer">
          {props.node.dtaleUrl}
        </a>
      ) : (
        <div className="node-action-link-placeholder">...</div>
      )}
    </div>
  </NodeActionsContainer>
);

const StyledCacheDisplay = styled.div`
  .clear-cache-button {
    border: none;
    background: none;
    padding: 0;
    margin-left: 5px;
    cursor: pointer;
  }
  .cache-placeholder {
    color: transparent;
  }
`;

export const CacheButtons: React.FC<{
  dispatch: ActionDispatch;
  node: Node;
}> = ({ dispatch, node }) => (
  <StyledCacheDisplay>
    {!node.lastCachedAt ? (
      <div className="cache-placeholder">...</div>
    ) : (
      <Fragment>
        <Typography.Text type="secondary">
          {`Cached at ${new Date(node.lastCachedAt).toLocaleString()}`}
        </Typography.Text>
        <button
          className="clear-cache-button"
          onClick={() => {
            httpRequest({
              method: "GET",
              url: `/node/clear-cache/${node.dataId}/`,
              resolve: (data: Node) => {
                dispatch(updateNode(data));
              },
              reject: (error) => {
                dispatch(updateNode({ ...node, error: error }));
              },
            });
          }}
        >
          <Typography.Text
            type="danger"
            underline
            className="clear-cache-button"
          >
            clear cache
          </Typography.Text>
        </button>
      </Fragment>
    )}
  </StyledCacheDisplay>
);
