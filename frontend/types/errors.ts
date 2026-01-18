/** Generic body type for error context */
type ErrorBodyContext = object | undefined;

/** Type guard to check if body has a table property */
function hasTable(body: ErrorBodyContext): body is { table: string } {
  return (
    body !== undefined && "table" in body && typeof body.table === "string"
  );
}

/** Type guard to check if body has an id property */
function hasId(body: ErrorBodyContext): body is { id: string | number } {
  return (
    body !== undefined &&
    "id" in body &&
    (typeof body.id === "string" || typeof body.id === "number")
  );
}

/**
 * Create a NotFound error using Nuxt's createError
 */
export function createNotFoundError(
  endpoint: string,
  method: string,
  body: ErrorBodyContext,
  originalError: unknown,
  customMessage?: string,
) {
  const table = hasTable(body) ? body.table : undefined;
  const id = hasId(body) ? body.id : undefined;
  const resource = table ? table : endpoint;
  const itemId = id || "Item";
  const finalMessage = customMessage || `${itemId} not found in ${resource}`;

  return createError({
    statusCode: 404,
    statusMessage: finalMessage,
    data: {
      name: "NotFoundError",
      table,
      id,
      endpoint,
      method,
      originalError:
        originalError instanceof Error
          ? {
              name: originalError.name,
              message: originalError.message,
              stack: originalError.stack,
            }
          : originalError,
    },
  });
}

/**
 * Create an API error using Nuxt's createError
 */
export function createApiError(
  endpoint: string,
  method: string,
  body: ErrorBodyContext,
  originalError: unknown,
  customMessage?: string,
) {
  const table = hasTable(body) ? body.table : undefined;
  const operation = table ? `fetch ${table}` : `call ${endpoint}`;
  const baseErrorMessage =
    originalError instanceof Error ? originalError.message : "Unknown error";

  const finalMessage =
    customMessage || `Failed to ${operation}: ${baseErrorMessage}`;

  return createError({
    statusCode: 500,
    statusMessage: finalMessage,
    data: {
      name: "ApiError",
      table,
      endpoint,
      method,
      originalError:
        originalError instanceof Error
          ? {
              name: originalError.name,
              message: originalError.message,
              stack: originalError.stack,
            }
          : originalError,
    },
  });
}

/**
 * Custom error class for "not found" errors
 * Used when API returns a 404 or indicates resource not found
 */
export class NotFoundError extends Error {
  public readonly table?: string;
  public readonly id?: string | number;
  public readonly endpoint: string;
  public readonly method: string;
  public readonly originalError: unknown;
  public readonly body?: ErrorBodyContext;

  constructor(
    endpoint: string,
    method: string,
    body: ErrorBodyContext,
    originalError: unknown,
    customMessage?: string,
  ) {
    const table = hasTable(body) ? body.table : undefined;
    const id = hasId(body) ? body.id : undefined;

    const resource = table ? table : endpoint;
    const itemId = id || "Item";
    const finalMessage = customMessage || `${itemId} not found in ${resource}`;

    super(finalMessage);

    this.name = "NotFoundError";
    this.table = table;
    this.id = id;
    this.endpoint = endpoint;
    this.method = method;
    this.body = body;
    this.originalError = originalError;

    Object.setPrototypeOf(this, NotFoundError.prototype);

    console.error(this.toJSON());
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      table: this.table,
      id: this.id,
      endpoint: this.endpoint,
      method: this.method,
      stack: this.stack,
      originalError:
        this.originalError instanceof Error
          ? {
              name: this.originalError.name,
              message: this.originalError.message,
              stack: this.originalError.stack,
            }
          : this.originalError,
    };
  }
}

/**
 * Custom error class for API-related errors
 * Provides structured error information with context about the API call
 */
export class ApiError extends Error {
  public readonly table?: string;
  public readonly endpoint: string;
  public readonly method: string;
  public readonly originalError: unknown;
  public readonly body?: ErrorBodyContext;

  constructor(
    endpoint: string,
    method: string,
    body: ErrorBodyContext,
    originalError: unknown,
    customMessage?: string,
  ) {
    const table = hasTable(body) ? body.table : undefined;

    const operation = table ? `fetch ${table}` : `call ${endpoint}`;
    const baseErrorMessage =
      originalError instanceof Error ? originalError.message : "Unknown error";

    const finalMessage =
      customMessage || `Failed to ${operation}: ${baseErrorMessage}`;

    super(finalMessage);

    this.name = "ApiError";
    this.table = table;
    this.endpoint = endpoint;
    this.method = method;
    this.body = body;
    this.originalError = originalError;

    Object.setPrototypeOf(this, ApiError.prototype);

    console.error(this.toJSON());
  }

  /**
   * Convert to JSON for logging/debugging
   */
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      table: this.table,
      endpoint: this.endpoint,
      method: this.method,
      stack: this.stack,
      originalError:
        this.originalError instanceof Error
          ? {
              name: this.originalError.name,
              message: this.originalError.message,
              stack: this.originalError.stack,
            }
          : this.originalError,
    };
  }
}
