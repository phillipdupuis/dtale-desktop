const themes = {
  light: {
    stylesheet: "/themes/antd.min.css",
    border: "1px solid #d9d9d9",
    hoverBgColor: "#d3ecfa",
  },
  dark: {
    stylesheet: "/themes/antd.dark.min.css",
    border: "1px solid #434343",
    hoverBgColor: "#196997",
  },
};

export type Theme = keyof typeof themes;

type ThemeProps = typeof themes[Theme];

const updateStylesheet = (stylesheet: ThemeProps["stylesheet"]): void => {
  const link = document.getElementById(
    "antd-stylesheet-link"
  ) as HTMLLinkElement;
  if (link.href !== stylesheet) {
    link.href = stylesheet;
  }
};

/**
 * Rather than use react context, we're gonna be lazy and just use css variables
 * for updating our non ant-design components when the theme is modified.
 * You lose intellisense, yes, but it's nice and simple and performant otherwise?
 */
const updateCssVariables = (props: ThemeProps): void => {
  const rootStyles = document.documentElement.style;
  rootStyles.setProperty("--styled-border", props.border);
  rootStyles.setProperty("--styled-hover-bg-color", props.hoverBgColor);
};

export const getTheme = (): Theme => {
  return (
    (localStorage.getItem("theme") as Theme) ||
    ((window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light") as Theme)
  );
};

export const setTheme = (theme: Theme): void => {
  localStorage.setItem("theme", theme);
  const props = themes[theme];
  updateStylesheet(props.stylesheet);
  updateCssVariables(props);
};

export const initializeTheme = (): Theme => {
  const theme = getTheme();
  setTheme(theme);
  return theme;
};

export const toggleTheme = (): Theme => {
  const newTheme = getTheme() === "dark" ? "light" : "dark";
  setTheme(newTheme);
  return newTheme;
};
