import questionary

from questionary_extended.core.component_wrappers import Component
from tests.helpers.questionary_helpers import mock_questionary_with_types


def test_component_various_types_and_config():
    """Test component creation with various types and configuration using DI."""
    with mock_questionary_with_types(
        password="PWD",
        autocomplete="AC", 
        path="PATH"
    ) as mock_q:
        
        # Test password component with config filtering
        c_pwd = Component(
            "p", "password", message="m", when="cond", enhanced_validation=True
        )
        res1 = c_pwd.create_questionary_component()
        assert res1.ask() == "PWD"
        
        # Verify internal questionary_config filtered out control keys
        assert (
            "when" not in c_pwd.questionary_config
            and "enhanced_validation" not in c_pwd.questionary_config
        )
        
        # Test autocomplete component
        c_ac = Component("a", "autocomplete", message="m", choices=["x"])
        res2 = c_ac.create_questionary_component()
        assert res2.ask() == "AC"
        
        # Test path component
        c_path = Component("pth", "path", message="m")
        res3 = c_path.create_questionary_component()
        assert res3.ask() == "PATH"
        
        # Verify calls were made with correct arguments
        mock_q.password.assert_called_once_with(message="m")
        mock_q.autocomplete.assert_called_once_with(message="m", choices=["x"])
        mock_q.path.assert_called_once_with(message="m")
