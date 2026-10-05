// Logger Utility - Structured Logging
export class Logger {
  constructor(name = "SahayakAI") {
    this.name = name;
    this.isDev = true;
  }

  formatMessage(level, message, data) {
    const timestamp = new Date().toISOString();
    const details = data ? ` | ${JSON.stringify(data)}` : "";
    return `[${timestamp}] [${this.name}] [${level}] ${message}${details}`;
  }

  info(message, data) {
    const formatted = this.formatMessage("INFO", message, data);
    console.log(`%c${formatted}`, "color: #3b82f6; font-weight: bold;");
  }

  warn(message, data) {
    const formatted = this.formatMessage("WARN", message, data);
    console.warn(`%c${formatted}`, "color: #f59e0b; font-weight: bold;");
  }

  error(message, error, data) {
    const errorDetails = error instanceof Error ? error.message : String(error);
    const formatted = this.formatMessage("ERROR", message, { ...data, error: errorDetails });
    console.error(`%c${formatted}`, "color: #ef4444; font-weight: bold;");
    if (error instanceof Error && error.stack && this.isDev) {
      console.error(error.stack);
    }
  }

  debug(message, data) {
    if (this.isDev) {
      const formatted = this.formatMessage("DEBUG", message, data);
      console.debug(`%c${formatted}`, "color: #6366f1; font-style: italic;");
    }
  }
}

export const logger = new Logger("SahayakAI");
