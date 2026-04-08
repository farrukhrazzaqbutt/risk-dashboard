const PREFIX = "[risk-dashboard]";

function ts() {
  return new Date().toISOString();
}

export const log = {
  debug: (...args) => {
    if (import.meta.env.DEV) {
      console.debug(ts(), PREFIX, ...args);
    }
  },
  info: (...args) => {
    console.info(ts(), PREFIX, ...args);
  },
  warn: (...args) => {
    console.warn(ts(), PREFIX, ...args);
  },
  error: (...args) => {
    console.error(ts(), PREFIX, ...args);
  },
};
