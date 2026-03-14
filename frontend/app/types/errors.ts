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

function serializeOriginalError(originalError: unknown) {
  return originalError instanceof Error
    ? {
        name: originalError.name,
        message: originalError.message,
        stack: originalError.stack,
      }
    : originalError;
}

abstract class BaseApiError extends Error {
  public readonly table?: string;
  public readonly endpoint: string;
  public readonly method: string;
  public readonly originalError: unknown;
  public readonly body?: ErrorBodyContext;

  constructor(
    message: string,
    endpoint: string,
    method: string,
    body: ErrorBodyContext,
    originalError: unknown,
  ) {
    super(message);
    this.table = hasTable(body) ? body.table : undefined;
    this.endpoint = endpoint;
    this.method = method;
    this.body = body;
    this.originalError = originalError;
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      table: this.table,
      endpoint: this.endpoint,
      method: this.method,
      stack: this.stack,
      originalError: serializeOriginalError(this.originalError),
    };
  }
}

export class NotFoundError extends BaseApiError {
  public readonly id?: string | number;

  constructor(
    endpoint: string,
    method: string,
    body: ErrorBodyContext,
    originalError: unknown,
    customMessage?: string,
  ) {
    const table = hasTable(body) ? body.table : undefined;
    const id = hasId(body) ? body.id : undefined;
    const resource = table ?? endpoint;
    const itemId = id || "Item";

    super(
      customMessage || `${itemId} not found in ${resource}`,
      endpoint,
      method,
      body,
      originalError,
    );

    this.name = "NotFoundError";
    this.id = id;
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }

  override toJSON() {
    return {
      ...super.toJSON(),
      id: this.id,
    };
  }
}

export class ApiError extends BaseApiError {
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

    super(
      customMessage || `Failed to ${operation}: ${baseErrorMessage}`,
      endpoint,
      method,
      body,
      originalError,
    );

    this.name = "ApiError";
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}
