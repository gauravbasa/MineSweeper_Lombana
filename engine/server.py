import asyncio
import json

import websockets

from board import Board

# One shared game, one board, for all connected clients.
board = Board(width=9, height=9, num_mines=10)
connected_clients = set()


async def broadcast_state():
    """Send the current board state to every connected client."""
    if not connected_clients:
        return
    message = json.dumps({
        "type": "state",
        **board.state_dict(),
    })
    await asyncio.gather(
        *(client.send(message) for client in connected_clients)
    )


async def handle_message(raw_message):
    """Apply one incoming event to the board."""
    global board
    try:
        data = json.loads(raw_message)
    except json.JSONDecodeError:
        print("Received invalid JSON:", raw_message)
        return

    msg_type = data.get("type")
    x = data.get("x")
    y = data.get("y")

    if msg_type == "reveal" and x is not None and y is not None:
        board.reveal(x, y)
    elif msg_type == "flag" and x is not None and y is not None:
        board.toggle_flag(x, y)
    elif msg_type == "reset":
        board = Board(width=9, height=9, num_mines=10)
    else:
        print("Unknown or incomplete message:", data)


async def handle_client(websocket):
    """Handle one connected client (Unity or the AI) for its whole session."""
    connected_clients.add(websocket)
    print(f"Client connected. Total clients: {len(connected_clients)}")

    try:
        # Send them the current state right away
        await websocket.send(json.dumps({
            "type": "state",
            **board.state_dict(),
        }))

        async for raw_message in websocket:
            await handle_message(raw_message)
            await broadcast_state()

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        print(f"Client disconnected. Total clients: {len(connected_clients)}")


async def main():
    host = "localhost"
    port = 8765
    async with websockets.serve(handle_client, host, port):
        print(f"Minesweeper engine server running on ws://{host}:{port}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())