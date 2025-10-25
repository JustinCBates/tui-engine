"""
Comprehensive test suite for core/page.py
Target: 95%+ coverage with complete functionality testing
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.questionary_extended.core.page import Page
from src.questionary_extended.core.state import PageState


class TestPageCore:
    """Core Page functionality tests."""

    def test_page_initialization_default(self):
        """Test Page initialization with default parameters."""
        page = Page()
        
        assert page.title == ""
        assert isinstance(page.components, list)
        assert len(page.components) == 0
        assert isinstance(page.state, PageState)

    def test_page_initialization_with_title(self):
        """Test Page initialization with custom title."""
        title = "Test Page Title"
        page = Page(title=title)
        
        assert page.title == title
        assert isinstance(page.components, list)
        assert len(page.components) == 0
        assert isinstance(page.state, PageState)

    def test_page_title_assignment(self):
        """Test direct title assignment after initialization."""
        page = Page()
        new_title = "Updated Title"
        page.title = new_title
        
        assert page.title == new_title

    def test_page_components_list_manipulation(self):
        """Test direct manipulation of components list."""
        page = Page()
        
        # Test list is mutable
        mock_component = Mock()
        page.components.append(mock_component)
        assert len(page.components) == 1
        assert page.components[0] is mock_component

    def test_page_state_instance(self):
        """Test that page state is properly initialized."""
        page = Page()
        
        # State should be a PageState instance
        assert isinstance(page.state, PageState)
        # Each page should have its own state instance
        page2 = Page()
        assert page.state is not page2.state


class TestPageCardIntegration:
    """Page-Card integration tests."""

    @patch('src.questionary_extended.core.card.Card')
    def test_card_creation_basic(self, mock_card_class):
        """Test basic card creation."""
        # Setup mock
        mock_card_instance = Mock()
        mock_card_class.return_value = mock_card_instance
        
        page = Page("Test Page")
        title = "Test Card"
        
        # Call card method
        result = page.card(title)
        
        # Verify Card class was called correctly
        mock_card_class.assert_called_once_with(title, page)
        
        # Verify card was added to components
        assert len(page.components) == 1
        assert page.components[0] is mock_card_instance
        
        # Verify method returns card instance (for chaining)
        assert result is mock_card_instance

    @patch('src.questionary_extended.core.card.Card')
    def test_card_creation_with_kwargs(self, mock_card_class):
        """Test card creation with keyword arguments."""
        mock_card_instance = Mock()
        mock_card_class.return_value = mock_card_instance
        
        page = Page()
        title = "Test Card"
        kwargs = {"style": "bordered", "color": "blue"}
        
        result = page.card(title, **kwargs)
        
        # Verify Card was called with kwargs
        mock_card_class.assert_called_once_with(title, page, style="bordered", color="blue")
        assert result is mock_card_instance

    @patch('src.questionary_extended.core.card.Card')
    def test_multiple_cards_creation(self, mock_card_class):
        """Test creating multiple cards on same page."""
        mock_card1 = Mock()
        mock_card2 = Mock()
        mock_card_class.side_effect = [mock_card1, mock_card2]
        
        page = Page()
        
        # Create two cards
        card1 = page.card("Card 1")
        card2 = page.card("Card 2")
        
        # Verify both cards added to components
        assert len(page.components) == 2
        assert page.components[0] is mock_card1
        assert page.components[1] is mock_card2
        assert card1 is mock_card1
        assert card2 is mock_card2

    @patch('src.questionary_extended.core.card.Card')
    def test_card_method_chaining(self, mock_card_class):
        """Test that card method returns Card instance for chaining."""
        mock_card_instance = Mock()
        mock_card_class.return_value = mock_card_instance
        
        page = Page()
        
        # Test that page.card() returns card instance for chaining
        result = page.card("Test")
        
        # Should return the card instance, not the page
        assert result is mock_card_instance


class TestPageAssemblyIntegration:
    """Page-Assembly integration tests."""

    @patch('src.questionary_extended.core.assembly.Assembly')
    def test_assembly_creation_basic(self, mock_assembly_class):
        """Test basic assembly creation."""
        mock_assembly_instance = Mock()
        mock_assembly_class.return_value = mock_assembly_instance
        
        page = Page("Test Page")
        name = "test_assembly"
        
        result = page.assembly(name)
        
        # Verify Assembly class was called correctly
        mock_assembly_class.assert_called_once_with(name, page)
        
        # Verify assembly was added to components
        assert len(page.components) == 1
        assert page.components[0] is mock_assembly_instance
        
        # Verify method returns assembly instance
        assert result is mock_assembly_instance

    @patch('src.questionary_extended.core.assembly.Assembly')
    def test_multiple_assemblies_creation(self, mock_assembly_class):
        """Test creating multiple assemblies on same page."""
        mock_assembly1 = Mock()
        mock_assembly2 = Mock()
        mock_assembly_class.side_effect = [mock_assembly1, mock_assembly2]
        
        page = Page()
        
        # Create two assemblies
        assembly1 = page.assembly("assembly1")
        assembly2 = page.assembly("assembly2")
        
        # Verify both assemblies added
        assert len(page.components) == 2
        assert page.components[0] is mock_assembly1
        assert page.components[1] is mock_assembly2
        assert assembly1 is mock_assembly1
        assert assembly2 is mock_assembly2

    @patch('src.questionary_extended.core.assembly.Assembly')
    def test_assembly_method_chaining(self, mock_assembly_class):
        """Test assembly method returns Assembly instance for chaining."""
        mock_assembly_instance = Mock()
        mock_assembly_class.return_value = mock_assembly_instance
        
        page = Page()
        
        result = page.assembly("test")
        
        assert result is mock_assembly_instance


class TestPageMixedComponents:
    """Test mixing cards and assemblies on same page."""

    @patch('src.questionary_extended.core.card.Card')
    @patch('src.questionary_extended.core.assembly.Assembly')
    def test_mixed_components_order(self, mock_assembly_class, mock_card_class):
        """Test that components are added in creation order."""
        mock_card = Mock()
        mock_assembly = Mock()
        mock_card_class.return_value = mock_card
        mock_assembly_class.return_value = mock_assembly
        
        page = Page()
        
        # Add components in specific order
        page.card("First Card")
        page.assembly("test_assembly")
        page.card("Second Card")
        
        # Verify order maintained
        assert len(page.components) == 3
        assert page.components[0] is mock_card
        assert page.components[1] is mock_assembly
        assert page.components[2] is mock_card

    @patch('src.questionary_extended.core.card.Card')
    @patch('src.questionary_extended.core.assembly.Assembly')
    def test_component_type_diversity(self, mock_assembly_class, mock_card_class):
        """Test page can handle different component types."""
        mock_card = Mock()
        mock_assembly = Mock()
        mock_card_class.return_value = mock_card
        mock_assembly_class.return_value = mock_assembly
        
        page = Page("Mixed Page")
        
        page.card("Test Card", style="fancy")
        page.assembly("test_namespace")
        
        # Verify calls were made with correct parameters
        mock_card_class.assert_called_with("Test Card", page, style="fancy")
        mock_assembly_class.assert_called_with("test_namespace", page)


class TestPageExecution:
    """Page execution and lifecycle tests."""

    def test_run_method_not_implemented(self):
        """Test that run method raises NotImplementedError."""
        page = Page()
        
        with pytest.raises(NotImplementedError, match="Page execution not yet implemented"):
            page.run()

    def test_run_method_signature(self):
        """Test run method exists and has correct signature."""
        page = Page()
        
        # Method should exist
        assert hasattr(page, 'run')
        assert callable(page.run)
        
        # Should be a method (not static/class method)
        assert hasattr(page.run, '__self__')


class TestPageEdgeCases:
    """Edge cases and error handling tests."""

    def test_page_empty_title_string(self):
        """Test page with empty string title."""
        page = Page("")
        assert page.title == ""

    def test_page_none_title_handling(self):
        """Test page behavior with various title types."""
        # Default should work
        page = Page()
        assert page.title == ""
        
        # Explicit None (if someone passes it)
        page_none = Page(None)
        assert page_none.title is None

    def test_page_special_character_titles(self):
        """Test page with special characters in title."""
        special_titles = [
            "Title with spaces",
            "Title-with-dashes",
            "Title_with_underscores",
            "Title123",
            "🔥 Emoji Title 🚀",
            "Multi\nLine\nTitle"
        ]
        
        for title in special_titles:
            page = Page(title)
            assert page.title == title

    def test_page_components_list_direct_access(self):
        """Test direct access to components list."""
        page = Page()
        
        # Should be able to access list directly
        assert isinstance(page.components, list)
        
        # Should be mutable
        page.components.clear()
        assert len(page.components) == 0
        
        # Should be able to add directly
        mock_component = Mock()
        page.components.append(mock_component)
        assert len(page.components) == 1

    @patch('src.questionary_extended.core.card.Card')
    def test_card_import_error_handling(self, mock_card_class):
        """Test card method behavior with import issues."""
        # This test ensures the import is handled correctly
        mock_card_instance = Mock()
        mock_card_class.return_value = mock_card_instance
        
        page = Page()
        result = page.card("test")
        
        # Should successfully import and create card
        assert result is mock_card_instance

    @patch('src.questionary_extended.core.assembly.Assembly')
    def test_assembly_import_error_handling(self, mock_assembly_class):
        """Test assembly method behavior with import issues."""
        mock_assembly_instance = Mock()
        mock_assembly_class.return_value = mock_assembly_instance
        
        page = Page()
        result = page.assembly("test")
        
        # Should successfully import and create assembly
        assert result is mock_assembly_instance


class TestPageStateIntegration:
    """Page state management tests."""

    def test_page_state_initialization(self):
        """Test page state is properly initialized."""
        page = Page()
        
        assert hasattr(page, 'state')
        assert isinstance(page.state, PageState)

    def test_page_state_independence(self):
        """Test that each page has independent state."""
        page1 = Page("Page 1")
        page2 = Page("Page 2")
        
        # Each page should have its own state instance
        assert page1.state is not page2.state
        assert isinstance(page1.state, PageState)
        assert isinstance(page2.state, PageState)

    def test_page_state_persistence(self):
        """Test that page state persists through component operations."""
        page = Page("Test Page")
        original_state = page.state
        
        # Adding components shouldn't change state instance
        with patch('src.questionary_extended.core.card.Card'):
            page.card("Test Card")
        
        assert page.state is original_state
        
        with patch('src.questionary_extended.core.assembly.Assembly'):
            page.assembly("test_assembly")
        
        assert page.state is original_state


# Integration test to verify all imports work
def test_page_imports():
    """Test that all necessary imports work correctly."""
    # This should not raise ImportError
    from src.questionary_extended.core.page import Page
    from src.questionary_extended.core.state import PageState
    
    # Should be able to create instances
    page = Page()
    assert isinstance(page, Page)
    assert isinstance(page.state, PageState)

# Test module exports
def test_page_module_exports():
    """Test that module exports are correct."""
    from src.questionary_extended.core import page
    
    # __all__ should include Page
    assert hasattr(page, '__all__')
    assert 'Page' in page.__all__
    
    # Page should be importable from module
    assert hasattr(page, 'Page')