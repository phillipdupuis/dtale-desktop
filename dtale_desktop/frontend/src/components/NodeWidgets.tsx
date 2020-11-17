import React, { Fragment, useState, ReactNode, useEffect } from "react";
import styled from "styled-components";
import { Button, Typography } from "antd";
import {
  LineChartOutlined,
  TableOutlined,
  DotChartOutlined,
  PictureOutlined,
  ProfileOutlined,
} from "@ant-design/icons";
import { Node, Settings } from "../store/state";
import { ActionDispatch } from "../store/actions";
import {
  openDtaleView,
  killDtaleInstance,
  clearCachedData,
  openProfileReport,
} from "../store/backend";

type BaseButtonProps = {
  dispatch: ActionDispatch;
  dataId: Node["dataId"];
  updating: Node["updating"];
};

const DtaleButton: React.FC<
  BaseButtonProps & {
    page: "table" | "charts" | "describe" | "correlations";
    icon: ReactNode;
  }
> = ({ dispatch, dataId, updating, page, icon }) => {
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (loading && !updating) {
      setLoading(false);
    }
  }, [updating]);

  return (
    <Button
      icon={icon}
      style={{ textTransform: "capitalize" }}
      size="small"
      loading={loading}
      disabled={updating && !loading}
      onClick={() => {
        setLoading(true);
        openDtaleView(dispatch, dataId, page);
      }}
    >
      {page}
    </Button>
  );
};

const DtaleTableButton: React.FC<BaseButtonProps> = (props) => (
  <DtaleButton page="table" icon={<TableOutlined />} {...props} />
);

const DtaleChartsButton: React.FC<BaseButtonProps> = (props) => (
  <DtaleButton page="charts" icon={<LineChartOutlined />} {...props} />
);

const DtaleDescribeButton: React.FC<BaseButtonProps> = (props) => (
  <DtaleButton page="describe" icon={<PictureOutlined />} {...props} />
);

const DtaleCorrelationsButton: React.FC<BaseButtonProps> = (props) => (
  <DtaleButton page="correlations" icon={<DotChartOutlined />} {...props} />
);

const PandasProfileReportButton: React.FC<BaseButtonProps> = ({
  dispatch,
  dataId,
  updating,
}) => (
  <Button
    size="small"
    onClick={() => openProfileReport(dispatch, dataId)}
    icon={<ProfileOutlined />}
  >
    Profile
  </Button>
);

const ShutdownButton: React.FC<BaseButtonProps> = ({
  dispatch,
  dataId,
  updating,
}) => {
  return (
    <Button
      danger
      size="small"
      title="shut down"
      onClick={() => killDtaleInstance(dispatch, dataId)}
      loading={updating}
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
  settings: Settings;
  dispatch: ActionDispatch;
}> = ({ node, settings, dispatch }) => {
  const props = { dispatch, dataId: node.dataId, updating: node.updating };
  return (
    <NodeActionsContainer>
      <div className="node-action-buttons">
        {node.dtaleUrl ? <ShutdownButton {...props} /> : null}
        <DtaleTableButton {...props} />
        <DtaleChartsButton {...props} />
        <DtaleCorrelationsButton {...props} />
        <DtaleDescribeButton {...props} />
        {settings.disableProfileReports ? null : (
          <PandasProfileReportButton {...props} />
        )}
      </div>
      <div className="node-action-link">
        {node.dtaleUrl ? (
          <a href={node.dtaleUrl} target="_blank" rel="noopener noreferrer">
            {node.dtaleUrl}
          </a>
        ) : (
          <div className="node-action-link-placeholder">...</div>
        )}
      </div>
    </NodeActionsContainer>
  );
};

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
          onClick={() => clearCachedData(dispatch, node.dataId)}
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
