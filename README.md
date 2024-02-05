# Flask WebSocket Integration with cheshire_cat_api python

This code demonstrates a simple web server setup using Flask, integrating WebSocket communication for asynchronous task handling. The server is designed to process HTTP POST requests containing messages and user IDs, forwarding these messages via WebSocket to another service the `cheshire_cat_api` (WebSocket server), await responses, and relay these back to the HTTP client.

## Import Statements

- **Flask**: A micro web framework for Python, enabling HTTP request handling.
- **threading**: Supports concurrent execution across multiple threads.
- **queue**: Facilitates multi-producer, multi-consumer queues, essential for threaded programming.
- **json**: Handles parsing and generating JSON data.
- **time**: Provides time-related functions, primarily used here to pause execution.
- **cheshire_cat_api as ccat**: A custom or external library for WebSocket communication. [API Documentation](https://cheshire-cat-ai.github.io/docs/technical/clientlib/clientlib-python/)

## Configuration

A Flask app instance is initialized with configuration parameters for the WebSocket client (`ccat.Config`), including the base URL, port, user ID, and authentication key.

## Global Variables

- **response_events**: Maps user IDs to tuples containing a `threading.Event` and a `queue.Queue`, synchronizing HTTP request handling with WebSocket message responses.

## WebSocket Event Handlers

- **on_open()**: Triggered upon opening the WebSocket connection.
- **on_message(message)**: Parses incoming WebSocket messages, extracting content based on a specific data structure. It then stores the response in an appropriate queue and signals the waiting event.
- **on_error(exception)**: Logs exceptions occurring within the WebSocket connection.
- **on_close(status_code, message)**: Logs the closure of the WebSocket connection, along with its status code and message.

## HTTP Route and WebSocket Communication

- **send_via_websocket(user_id, message)**: Establishes a WebSocket connection using `ccat.CatClient`, sends a message, awaits a response through an event, retrieves the response from a queue, and returns it. This function manages the asynchronous part of sending messages through WebSocket and waiting for their responses.
- **@app.route('/send', methods=['POST'])**: Defines a Flask route that accepts POST requests. It extracts `user_id` and `message` from the request body, invokes `send_via_websocket` to forward the message over WebSocket, waits for the response, and returns this response as JSON.

## Main Block

- Initiates the Flask app, making it ready to accept incoming HTTP requests. The server runs in debug mode with threading enabled to manage concurrent requests efficiently.


## Key Functional Flow

1. **HTTP Request**: An HTTP client submits a POST request to `/send` with a JSON body containing `user_id` and `message`.
2. **Processing**: The server extracts these details and initiates a new thread for WebSocket communication.
3. **WebSocket Communication**: The message is forwarded to a WebSocket server using the specified `user_id`. The server waits for a response without engaging in busy waiting, leveraging an event mechanism.
4. **Response Handling**: Upon receiving a response from the WebSocket server, the `on_message` handler processes the message, stores it in a queue, and signals the event.
5. **HTTP Response**: The thread handling the original HTTP request retrieves the WebSocket response from the queue and sends it back to the client as JSON.

This setup enables asynchronous message processing via WebSockets within a synchronous HTTP request-response framework, ideal for applications requiring real-time data exchange with external services or systems.
