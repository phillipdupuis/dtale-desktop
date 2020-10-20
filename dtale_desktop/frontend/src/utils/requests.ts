interface SharedParams {
  url: string;
  resolve: (data: any) => any;
  reject: (error: string) => any;
  params?: { [k: string]: string };
  onStart?: () => any;
  onFinish?: () => any;
}

interface ReadParams extends SharedParams {
  method: "GET";
  body?: undefined;
}

interface WriteParams extends SharedParams {
  method: "POST";
  body: Object;
}

export type RequestParams = ReadParams | WriteParams;

export const httpRequest = async ({
  method,
  url,
  body,
  params,
  resolve,
  reject,
  onStart,
  onFinish,
}: RequestParams) => {
  if (onStart) {
    onStart();
  }
  if (params) {
    url = `${url}?${new URLSearchParams(params).toString()}`;
  }
  try {
    const response = await fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      const data = await response.json();
      throw new Error(`${response.statusText}: ${data.detail}`);
    }
    const data = await response.json();
    resolve(data);
  } catch (error) {
    reject(error.message);
  }
  if (onFinish) {
    onFinish();
  }
};

export const openNewTab = (url: string) => {
  try {
    window.open(url);
  } catch (error) {
    // do nothing
  }
};
