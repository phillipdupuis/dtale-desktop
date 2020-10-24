export type DataNode = {
  sourceId: string;
  path: string;
  dataId: string;
  dtaleUrl: null | string;
  dtaleChartsUrl: null | string;
  error?: string;
  visible: boolean;
};

export type DataSource = {
  id: string;
  name: string;
  packageName: string;
  packagePath: string;
  nodes?: { [k: string]: DataNode };
  nodesFullyLoaded: boolean;
  error: null | string;
  visible: boolean;
  editable: boolean;
  listPaths: string;
  getData: string;
  saveData: string;
  loading?: boolean;
};

export type RootState = {
  sources?: DataSource[];
  selectedSource: DataSource | null;
  openModal: null | "filters";
};

export const initialState: RootState = {
  sources: undefined,
  selectedSource: null,
  openModal: null,
};
