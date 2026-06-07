"""
Test: WebSocket Connection

Behavior: The system should support WebSocket connections for real-time
communication between frontend and backend.

This proves the WebSocket endpoint exists and can handle connections.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


def test_websocket_connection_established():
    """WebSocket connection should be established successfully."""
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # Send a test message
        websocket.send_json({"type": "ping", "data": "hello"})
        
        # Receive response
        response = websocket.receive_json()
        
        # Verify response structure
        assert "type" in response
        assert response["type"] == "echo"


def test_websocket_echo_message():
    """WebSocket should echo back messages."""
    client = TestClient(app)
    
    with client.websocket_connect("/ws") as websocket:
        # Send a message
        test_message = {"type": "test", "content": "Hello, AgentForge!"}
        websocket.send_json(test_message)
        
        # Receive echo
        response = websocket.receive_json()
        
        # Verify echo
        assert response["type"] == "echo"
        assert response["original"] == test_message


def test_websocket_disconnect_handling():
    """WebSocket should handle disconnection gracefully."""
    client = TestClient(app)
    
    # Connect and disconnect
    with client.websocket_connect("/ws") as websocket:
        websocket.send_json({"type": "ping"})
        response = websocket.receive_json()
        assert response is not None
    
    # Connection should be closed after exiting context
    # No exception means graceful disconnect
