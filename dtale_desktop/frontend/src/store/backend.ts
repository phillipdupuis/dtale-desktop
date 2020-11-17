import React from "react";
import { omit } from "lodash";
import {
  Action,
  setSourceUpdating,
  setNodeUpdating,
  setSelectedSource,
  setOpenModal,
} from "./actions";
import { Source, Node } from "./state";

export const clientIdentifier: string = String(Date.now());

type Dispatcher = React.Dispatch<Action>;

type BackendRequestProps = {
  dispatch: Dispatcher;
  url: string;
  body?: Object;
  params?: Record<string, any>;
  onStart?: () => void;
  onFinish?: () => void;
  onAfterResolve?: (data: Action | Action[]) => void;
  errorHandler?: (error: string) => void;
};

const backendRequest = ({
  dispatch,
  url,
  body,
  params,
  onStart,
  onFinish,
  onAfterResolve,
  errorHandler,
}: BackendRequestProps): void => {
  if (onStart) {
    onStart();
  }
  if (params) {
    url = `${url}?${new URLSearchParams(params).toString()}`;
  }
  fetch(url, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      "Content-Type": "application/json",
      "Client-Id": clientIdentifier,
    },
    body: JSON.stringify(body),
  })
    .then((response) => response.json())
    .then((data) => {
      if (Array.isArray(data)) {
        data.forEach((action) => dispatch(action));
      } else {
        dispatch(data);
      }
      if (onAfterResolve) {
        onAfterResolve(data);
      }
    })
    .catch((error) => (errorHandler ? errorHandler(error) : alert(error)))
    .finally(() => {
      if (onFinish) {
        onFinish();
      }
    });
};

export const getSettings = (dispatch: Dispatcher): void =>
  backendRequest({ dispatch, url: "/settings/" });

export const getSources = (dispatch: Dispatcher): void =>
  backendRequest({ dispatch, url: "/source/list/" });

export const getSourceNodes = (
  dispatch: Dispatcher,
  sourceId: Source["id"],
  limit?: number
): void =>
  backendRequest({
    dispatch,
    url: `/source/${sourceId}/load-nodes/`,
    params: limit === undefined ? {} : { limit: limit },
    onStart: () => dispatch(setSourceUpdating(sourceId, true)),
    onFinish: () => dispatch(setSourceUpdating(sourceId, false)),
  });

const dtalePageToPropMap = {
  table: "dtaleUrl" as const,
  charts: "dtaleChartsUrl" as const,
  describe: "dtaleDescribeUrl" as const,
  correlations: "dtaleCorrelationsUrl" as const,
};

export const openDtaleView = (
  dispatch: Dispatcher,
  dataId: Node["dataId"],
  page: "table" | "charts" | "describe" | "correlations"
): void =>
  backendRequest({
    dispatch,
    url: `/node/view/${dataId}/`,
    onStart: () => dispatch(setNodeUpdating(dataId, true)),
    onFinish: () => dispatch(setNodeUpdating(dataId, false)),
    onAfterResolve: (data) => {
      // @ts-ignore
      const url: string | undefined = data.node[dtalePageToPropMap[page]];
      if (url) {
        window.open(url);
      }
    },
  });

export const killDtaleInstance = (
  dispatch: Dispatcher,
  dataId: Node["dataId"]
): void =>
  backendRequest({
    dispatch,
    url: `/node/kill/${dataId}/`,
    onStart: () => dispatch(setNodeUpdating(dataId, true)),
    onFinish: () => dispatch(setNodeUpdating(dataId, false)),
  });

export const clearCachedData = (
  dispatch: Dispatcher,
  dataId: Node["dataId"]
): void =>
  backendRequest({
    dispatch,
    url: `/node/clear-cache/${dataId}/`,
  });

export const updateLayout = (
  dispatch: Dispatcher,
  changes: Array<Pick<Source, "id" | "visible" | "sortValue">>
) =>
  backendRequest({
    dispatch,
    url: "/source/update-layout/",
    body: changes,
    onAfterResolve: () => dispatch(setOpenModal(null)),
  });

export const createSource = (
  dispatch: Dispatcher,
  source: Source,
  errorHandler: (error: string) => void
): void =>
  backendRequest({
    dispatch,
    url: "/source/create/",
    body: omit(source, ["nodes"]),
    onAfterResolve: () => dispatch(setSelectedSource(null)),
    errorHandler: errorHandler,
  });

export const updateSource = (
  dispatch: Dispatcher,
  source: Source,
  errorHandler: (error: string) => void
): void =>
  backendRequest({
    dispatch,
    url: "/source/update/",
    body: omit(source, ["nodes"]),
    onAfterResolve: () => dispatch(setSelectedSource(null)),
    errorHandler: errorHandler,
  });

export const openProfileReport = (
  dispatch: Dispatcher,
  dataId: Node["dataId"]
) => {
  window.open(`/node/profile-report/${dataId}/`);
  backendRequest({
    dispatch,
    url: `/node/watch-profile-report-builder/${dataId}/`,
  });
};

type WebSocketMessageData =
  | { type: "notification"; payload: string }
  | { type: "action"; payload: Action | Action[] };

const webSocketEndpoint = (): string => {
  const host = window.location.host;
  return "ws://localhost:5000/ws/" + clientIdentifier + "/";
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${host}/ws/${clientIdentifier}/`;
};

export const openWebSocketConnection = (dispatch: Dispatcher): WebSocket => {
  const ws = new WebSocket(webSocketEndpoint());
  ws.onmessage = (event) => {
    const msg: WebSocketMessageData = JSON.parse(event.data);
    if (msg.type === "action") {
      if (Array.isArray(msg.payload)) {
        msg.payload.forEach((action) => dispatch(action));
      } else {
        dispatch(msg.payload);
      }
    } else if (msg.type === "notification") {
      alert(msg.payload);
    }
  };
  return ws;
};
