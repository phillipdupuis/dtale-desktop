import React, { Dispatch } from "react";
import { omit } from "lodash";
import {
  ActionDispatch,
  addSources,
  updateSettings,
  updateNode,
  updateSource,
  setSourceUpdating,
  setSelectedSource,
  setNodeUpdating,
  setOpenModal,
} from "../store/actions";
import { Source, Node } from "../store/state";
import { httpRequest, openNewTab } from "./requests";

type GetHandler<ExtraParams extends Record<string, any>> = (
  params: { dispatch: ActionDispatch } & ExtraParams
) => void;

type PostHandler<
  BodyType extends any,
  ExtraParams extends Record<string, any>
> = (
  params: { dispatch: ActionDispatch; body: BodyType } & ExtraParams
) => void;

const getSettings: GetHandler<{}> = ({ dispatch }) => {
  httpRequest({
    method: "GET",
    url: "/settings/",
    resolve: (settings) => dispatch(updateSettings(settings)),
    reject: (error) => null,
  });
};

const getSources: GetHandler<{}> = ({ dispatch }) => {
  httpRequest({
    method: "GET",
    url: "/source/list/",
    resolve: (sources) => dispatch(addSources(sources)),
    reject: (error) => null,
  });
};

const getSourceNodes: GetHandler<{ sourceId: string; limit?: number }> = ({
  dispatch,
  sourceId,
  limit,
}) => {
  httpRequest({
    method: "GET",
    url: `/source/${sourceId}/load-nodes/`,
    params: limit === undefined ? {} : { limit: limit },
    onStart: () => dispatch(setSourceUpdating(sourceId, true)),
    resolve: (data) => dispatch(updateSource(data)),
    reject: (error) => alert(error),
    onFinish: () => dispatch(setSourceUpdating(sourceId, false)),
  });
};

const getNodeDtaleView: GetHandler<{
  dataId: Node["dataId"];
  page: "table" | "charts" | "describe" | "correlations";
}> = ({ dispatch, dataId, page }) => {
  const urlProp = {
    table: "dtaleUrl" as const,
    charts: "dtaleChartsUrl" as const,
    describe: "dtaleDescribeUrl" as const,
    correlations: "dtaleCorrelationsUrl" as const,
  }[page];
  httpRequest({
    method: "GET",
    url: `/node/view/${dataId}/`,
    onStart: () => dispatch(setNodeUpdating(dataId, true)),
    resolve: (node: Node) => {
      if (node[urlProp]) {
        openNewTab(node[urlProp]!);
      }
      dispatch(updateNode(node));
    },
    reject: (error) => alert(error),
    onFinish: () => dispatch(setNodeUpdating(dataId, false)),
  });
};

const getNodeDtaleShutdown: GetHandler<{ dataId: Node["dataId"] }> = ({
  dispatch,
  dataId,
}) => {
  httpRequest({
    method: "GET",
    url: `node/kill/${dataId}/`,
    onStart: () => dispatch(setNodeUpdating(dataId, true)),
    resolve: (data: Node) => dispatch(updateNode(data)),
    reject: (error) => alert(error),
    onFinish: () => dispatch(setNodeUpdating(dataId, false)),
  });
};

const getNodeProfileReport: GetHandler<{ dataId: Node["dataId"] }> = ({
  dispatch,
  dataId,
}) => {
  openNewTab(`/node/profile-report/${dataId}`);
  httpRequest({
    method: "GET",
    url: `/node/watch-profile-report-builder/${dataId}/`,
    resolve: (data) => {
      if (data.ok) {
        dispatch(updateNode(data.node));
      }
    },
    reject: (error) => alert(error),
  });
};

const getNodeClearCache: GetHandler<{ dataId: Node["dataId"] }> = ({
  dispatch,
  dataId,
}) => {
  httpRequest({
    method: "GET",
    url: `/node/clear-cache/${dataId}/`,
    resolve: (data) => dispatch(updateNode(data)),
    reject: (error) => alert(error),
  });
};

const postSourceListLayoutChanges: PostHandler<
  Array<Pick<Source, "id" | "visible" | "sortValue">>,
  {}
> = ({ dispatch, body }) => {
  httpRequest({
    method: "POST",
    url: "/source/update-layout/",
    body: body,
    resolve: (data) => {
      data.forEach((s: Source) => dispatch(updateSource(s)));
      dispatch(setOpenModal(null));
    },
    reject: (error) => null,
  });
};

const createOrUpdateSource = (
  dispatch: ActionDispatch,
  source: Source,
  handleError: Dispatch<React.SetStateAction<string | null>>,
  action: "create" | "update"
): void => {
  // We never want to post the "nodes" because we do not want to accidentally overwrite the server-side data.
  httpRequest({
    method: "POST",
    url: `/source/${action}/`,
    body: omit(source, ["nodes"]),
    resolve: (data: Source) => {
      if (action === "update") {
        dispatch(updateSource(data));
      } else {
        dispatch(addSources([data]));
      }
      dispatch(setSelectedSource(null));
    },
    reject: (error) => handleError(error),
  });
};

const postSourceUpdate: PostHandler<
  Source,
  { handleError: Dispatch<React.SetStateAction<string | null>> }
> = ({ dispatch, body, handleError }) => {
  createOrUpdateSource(dispatch, body, handleError, "update");
};

const postSourceCreate: PostHandler<
  Source,
  { handleError: Dispatch<React.SetStateAction<string | null>> }
> = ({ dispatch, body, handleError }) => {
  createOrUpdateSource(dispatch, body, handleError, "create");
};

export const backend = {
  get: {
    settings: getSettings,
    sources: getSources,
    sourceNodes: getSourceNodes,
    nodeDtaleView: getNodeDtaleView,
    nodeDtaleShutdown: getNodeDtaleShutdown,
    nodeProfileReport: getNodeProfileReport,
    nodeClearCache: getNodeClearCache,
  },
  post: {
    sourceListLayoutChanges: postSourceListLayoutChanges,
    sourceUpdate: postSourceUpdate,
    sourceCreate: postSourceCreate,
  },
};
