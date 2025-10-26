"""Test for top-level page.py exception handling coverage."""

from unittest.mock import Mock, patch

from questionary_extended.page import Page


def test_page_run_get_all_state_exception_fallback():
    """Test Page.run() exception handling when state.get_all_state() fails (lines 21-24)."""

    # Create a page
    page = Page("test_page")

    # Create a mock state that will raise an exception when get_all_state is called
    mock_state = Mock()
    mock_state.get_all_state.side_effect = Exception("get_all_state not implemented")

    # Mock the QuestionaryBridge to avoid actual questionary interaction
    with patch("questionary_extended.page.QuestionaryBridge") as mock_bridge_class:
        mock_bridge = Mock()
        mock_bridge_class.return_value = mock_bridge

        # Set the page's state to our mock state
        page.state = mock_state

        # Run the page - this should trigger the exception handling
        result = page.run()

        # Verify that the fallback empty dict is returned
        assert result == {}

        # Verify that the bridge was called correctly
        mock_bridge_class.assert_called_once_with(mock_state)
        mock_bridge.run.assert_called_once_with(page.components)


def test_page_run_get_all_state_success():
    """Test Page.run() when state.get_all_state() succeeds."""

    # Create a page
    page = Page("test_page")

    # Create a mock state that returns data when get_all_state is called
    mock_state = Mock()
    expected_data = {"field1": "value1", "field2": "value2"}
    mock_state.get_all_state.return_value = expected_data

    # Mock the QuestionaryBridge
    with patch("questionary_extended.page.QuestionaryBridge") as mock_bridge_class:
        mock_bridge = Mock()
        mock_bridge_class.return_value = mock_bridge

        # Set the page's state to our mock state
        page.state = mock_state

        # Run the page
        result = page.run()

        # Verify that the actual state data is returned
        assert result == expected_data

        # Verify that the bridge was called correctly
        mock_bridge_class.assert_called_once_with(mock_state)
        mock_bridge.run.assert_called_once_with(page.components)
